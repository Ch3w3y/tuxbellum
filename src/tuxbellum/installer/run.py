"""Installation orchestrator — full pipeline from precheck to desktop integration."""

import os
from dataclasses import dataclass
from pathlib import Path

from tuxbellum.core.logging import Logger
from tuxbellum.core.system import RunMode, run_command
from tuxbellum.installer.desktop import copy_icon, generate_desktop_files
from tuxbellum.installer.dll_overrides import update_dlls
from tuxbellum.installer.dxvk import install_dxvk
from tuxbellum.installer.fsr import upgrade_fsr
from tuxbellum.installer.launch_vars import generate_launch_vars_file
from tuxbellum.installer.launcher import cleanup_launcher_installer, download_launcher_installer
from tuxbellum.installer.wineprefix import init_wineprefix, install_winedlls
from tuxbellum.installer.wrappers import generate_launcher_wrapper


@dataclass
class InstallConfig:
    wineprefix: str = ""
    proton_path: str = ""
    gpu_type: str = ""
    is_amd_gpu: bool = False
    launcher_installer: str = ""
    resource_root: str = ""
    cache_dir: str = ""
    is_fsr41: bool = False


def run_installation(config: InstallConfig, logger: Logger) -> None:
    """Execute the full Bellum installation pipeline."""
    original_env = os.environ.copy()
    try:
        os.environ["PROTONPATH"] = config.proton_path
        os.environ["WINEPREFIX"] = config.wineprefix
        os.environ["WINEARCH"] = "win64"
        os.environ["STEAM_APP_PATH"] = config.wineprefix
        os.environ["STEAM_APPID"] = "1"
        os.environ["STEAM_COMPAT_DATA_PATH"] = config.wineprefix
        os.environ["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.join(
            os.environ.get("HOME", str(Path.home())),
            ".steam",
            "steam",
        )
        os.environ["GAMEID"] = "1"

        logger.info("Starting Installation")
        print()

        launcher_exe = config.launcher_installer
        if not launcher_exe:
            state = download_launcher_installer(config.cache_dir, logger)
            launcher_exe = state.installer_path
            try:
                _run_pipeline(config, launcher_exe, logger)
            finally:
                cleanup_launcher_installer(state, logger)
        else:
            _run_pipeline(config, launcher_exe, logger)
    finally:
        os.environ.clear()
        os.environ.update(original_env)


def _check_run(mode: RunMode, args: list[str]) -> None:
    if run_command(mode, args) != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}")


def _run_pipeline(config: InstallConfig, launcher_exe: str, logger: Logger) -> None:
    init_wineprefix(config.proton_path, config.wineprefix, logger)
    install_winedlls(logger)

    print()
    logger.info("Time to install the launcher! Follow the on screen prompts once the GUI pops up.")

    # Terminate the lingering system wineserver from winetricks before switching to Proton
    run_command(RunMode.SILENT, ["wineboot", "--end-session"])
    run_command(RunMode.SILENT, ["wineboot", "-k"])
    run_command(RunMode.SILENT, ["wineserver", "-w"])

    proton = os.path.join(config.proton_path, "proton")
    ret_code = run_command(RunMode.STREAM, [proton, "run", launcher_exe])

    installed_exe = os.path.join(
        config.wineprefix,
        "drive_c/users/steamuser/AppData/Local",
        "Astarte Industries/Astarte Launcher/AstarteLauncher.exe",
    )
    if not os.path.isfile(installed_exe):
        raise RuntimeError(
            f"Launcher installation failed (exit code {ret_code}):"
            f" executable not found at {installed_exe}"
        )

    logger.info("Astarte Launcher install completed successfully! Few more steps to go...")
    logger.warn("I'm not done! Don't launch game or close this script just yet")

    _check_run(RunMode.SILENT, ["winetricks", "win11"])
    print()

    install_dxvk(config.gpu_type, config.resource_root, logger)

    logger.info("Configuring WINEPREFIX with things Bellum likes")
    _check_run(
        RunMode.SILENT,
        ["winetricks", "grabfullscreen=y", "windowmanagerdecorated=n", "mwo=disabled"],
    )

    if config.is_amd_gpu:
        _check_run(RunMode.SILENT, ["winetricks", "remove_mono"])

    icon_path = os.path.join(config.resource_root, "packages", "launcher_1_256x256x32.png")
    copy_icon(icon_path)
    generate_desktop_files(config.wineprefix, icon_path, config.gpu_type, logger)
    generate_launcher_wrapper(config.wineprefix, config.proton_path, config.gpu_type, logger)
    logger.info("[OK] Game launcher installed: /usr/local/bin/Bellum")

    generate_launch_vars_file(config.wineprefix, config.gpu_type, config.is_fsr41)

    _check_run(
        RunMode.SILENT,
        [
            "wine",
            "reg",
            "add",
            r"HKCU\Software\Wine\DirectInput",
            "/v",
            "RawInput",
            "/t",
            "REG_DWORD",
            "/d",
            "1",
            "/f",
        ],
    )

    update_dlls(logger)

    if config.is_amd_gpu and config.is_fsr41:
        upgrade_fsr(config.wineprefix, config.resource_root, config.gpu_type, logger)

    _check_run(RunMode.SILENT, ["wineboot", "--end-session"])
