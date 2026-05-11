"""Precheck validations — WINEPREFIX, Wine, GPU, Proton, winetricks."""

import os
import re
from dataclasses import dataclass
from pathlib import Path

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.system import (
    run_command,
    run_command_with_output,
    RunMode,
    look_path,
    ask_bool,
    is_dir,
    is_writable,
)
from tuxbellum.core.logging import Logger, colorize, Color
from tuxbellum.core.gpu import detect_gpu
from tuxbellum.core.gui_picker import pick_directory, pick_directory_existing, validate_directory
from tuxbellum.installer.proton import ensure_proton, get_proton_install_path, get_proton_url


@dataclass
class PrecheckResult:
    wineprefix: str = ""
    wineprefix_source: str = ""
    use_existing: bool = False
    force_wine_version: bool = False
    launcher_installer: str = ""
    gpu_type: str = ""
    is_amd_gpu: bool = False
    proton_ver: str = ""
    proton_path: str = ""


def validate_wineprefix(
    wineprefix_arg: str,
    logger: Logger,
) -> tuple[str, str, bool]:
    """Validate/resolve the WINEPREFIX path.

    Returns ``(wineprefix, source, use_existing)``.
    """
    wineprefix = ""
    source = ""
    use_existing = False

    if wineprefix_arg:
        wineprefix = wineprefix_arg.rstrip("/")
        if not wineprefix.endswith("Bellum"):
            wineprefix = os.path.join(wineprefix, "Bellum")
        source = "argument"
        logger.info(colorize(f"WINEPREFIX: {wineprefix}", Color.BOLD_YELLOW))

    elif os.environ.get("WINEPREFIX"):
        wineprefix = os.environ["WINEPREFIX"]
        source = "environment variable"
        logger.info(
            colorize(f"WINEPREFIX is already set to: {wineprefix}", Color.BOLD_YELLOW)
        )
        if ask_bool("Do you want to use this path? (Y/n): "):
            use_existing = True
        else:
            logger.info("Enter the desired WINEPREFIX path (e.g. /path/to/wineprefix):")
            wineprefix = input().strip()
            source = "user input"

    else:
        logger.info("Select the directory where you want to install Bellum...")
        logger.info("This will create a new WINEPREFIX named 'Bellum' in the selected location.")
        print()
        result = pick_directory()
        if not result.success:
            raise RuntimeError(f"directory selection cancelled or failed: {result.error}")
        selected = result.path.rstrip("/")
        wineprefix = os.path.join(selected, "Bellum")
        source = "GUI picker"
        logger.info(colorize(f"WINEPREFIX: {wineprefix}", Color.BOLD_YELLOW))

    wineprefix = wineprefix.rstrip("/")

    if not wineprefix.startswith("/"):
        raise RuntimeError(f"WINEPREFIX must be an absolute path (starting with /): {wineprefix}")

    parent = wineprefix
    while not is_dir(parent) and parent != "/":
        parent = os.path.dirname(parent)

    if not is_dir(parent):
        raise RuntimeError(f"WINEPREFIX path is not on a valid mounted filesystem: {wineprefix}")

    if is_dir(wineprefix):
        try:
            entries = os.listdir(wineprefix)
        except OSError:
            entries = []
        if entries:
            logger.info(f"WINEPREFIX directory already exists at {wineprefix}")
            logger.warn("If you want to reinstall, please uninstall the existing installation first.")
            raise RuntimeError(f"WINEPREFIX directory '{wineprefix}' already exists")

    if not is_writable(parent):
        raise RuntimeError(f"WINEPREFIX parent directory is not writable: {parent}")

    logger.info("[OK] WINEPREFIX path is valid and writable")

    if _is_ssd(parent, logger):
        logger.info("[OK] WINEPREFIX device is an SSD/NVME (optimal performance)")
    else:
        logger.warn("WINEPREFIX device is NOT an SSD/NVME (may have performance issues)")
        if not ask_bool(
            "Astarte Developers strongly recommend using NVMe or SSD for the game. "
            "Are you sure you want to proceed? (Y/n): "
        ):
            raise RuntimeError("installation cancelled by user")

    return wineprefix, source, use_existing


def validate_wineprefix_with_gui(logger: Logger) -> str:
    """Open GUI picker, validate, create Bellum directory. Returns WINEPREFIX path."""
    print()
    logger.info("Select the directory where you want to install Bellum...")
    logger.info("This will create a new WINEPREFIX named 'Bellum' in the selected location.")
    import time
    time.sleep(2)

    result = pick_directory()
    if not result.success:
        raise RuntimeError(f"directory selection cancelled or failed: {result.error}")

    logger.info(colorize(f"Selected directory: {result.path}", Color.BOLD_YELLOW))
    print()
    wineprefix_path = os.path.join(result.path, "Bellum")

    valid, err_msg = validate_directory(wineprefix_path)
    if not valid:
        raise RuntimeError(f"directory validation failed: {err_msg}")

    logger.info("[OK] Directory validation passed")
    print()

    if not is_dir(wineprefix_path):
        logger.info(f"Creating Bellum directory at {wineprefix_path}...")
        os.makedirs(wineprefix_path, exist_ok=True)
        logger.info("[OK] Bellum directory created successfully")
        print()

    return wineprefix_path


def validate_wineprefix_with_gui_for_uninstall(logger: Logger) -> str:
    """Pick an existing Bellum WINEPREFIX for uninstallation."""
    print()
    logger.info("Select the Bellum WINEPREFIX directory to uninstall...")
    logger.info("This will uninstall Bellum from the selected location.")
    print()

    result = pick_directory_existing()
    if not result.success:
        raise RuntimeError(f"directory selection cancelled or failed: {result.error}")

    logger.info(colorize(f"Selected directory: {result.path}", Color.BOLD_YELLOW))
    print()

    if not is_dir(result.path):
        raise RuntimeError(f"selected directory does not exist: {result.path}")

    try:
        entries = os.listdir(result.path)
    except OSError:
        entries = []
    if not entries:
        logger.warn(f"WINEPREFIX directory {result.path} appears to be empty or invalid")
        if not ask_bool("Are you sure you want to proceed with uninstallation? (Y/n): "):
            raise RuntimeError("uninstallation cancelled by user")

    logger.info(colorize(f"[OK] WINEPREFIX found at {result.path}", Color.BOLD_YELLOW))
    print()
    return result.path


def check_wine_binaries(logger: Logger) -> None:
    """Verify required Wine binaries exist on disk."""
    required = [
        DEFAULT_VERSIONS.binaries.wine,
        DEFAULT_VERSIONS.binaries.wineboot,
        DEFAULT_VERSIONS.binaries.msidb,
        DEFAULT_VERSIONS.binaries.winecfg,
        DEFAULT_VERSIONS.binaries.wineserver,
    ]
    missing = [b for b in required if not os.path.isfile(b)]
    if missing:
        logger.error("Required Wine binaries not found:")
        for b in missing:
            logger.error(f"  - {b}")
        raise RuntimeError("missing Wine binaries")
    logger.info("[OK] All required Wine binaries found")


def check_wine_version(logger: Logger, force: bool = False) -> None:
    """Compare installed Wine version against the required version."""
    installed = _get_wine_version(logger)
    required = DEFAULT_VERSIONS.wine_ver.removeprefix("wine-")
    if not installed:
        raise RuntimeError("Wine binary not found in PATH")
    if installed != required:
        if not force:
            logger.error(
                f"Wine version mismatch. Installed: wine-{installed}, Required: {required}"
            )
            raise RuntimeError(f"wine version mismatch: installed {installed}, required {required}")
        logger.warn(f"Wine version mismatch. Installed: wine-{installed}, Required: {required}")
        logger.warn("Proceeding with wine-1.0 due to --force-wine-version flag (not recommended)")
    else:
        logger.info(f"[OK] Wine {required} stable found")


def check_umu_run(logger: Logger) -> None:
    """Ensure umu-run is on PATH."""
    if not look_path("umu-run"):
        logger.error(
            "umu-run binary not found in PATH.\n"
            "Grab latest umu-launcher-1.3.0 for your distro: "
            "https://github.com/Open-Wine-Components/umu-launcher/releases/tag/1.3.0"
        )
        raise RuntimeError("umu-run not found")
    logger.info(f"[OK] umu-run binary found: {look_path('umu-run')}")


def check_winetricks(workdir: str, logger: Logger) -> None:
    """Locate or extract winetricks."""
    if look_path("winetricks"):
        logger.info(f"[OK] winetricks binary found: {look_path('winetricks')}")
        return

    logger.warn("winetricks binary not found, attempting to install from local archive...")
    archive = os.path.join(
        workdir, "packages", f"winetricks-{DEFAULT_VERSIONS.winetricks_ver}.tar.gz"
    )
    if not os.path.isfile(archive):
        logger.error(f"winetricks binary not found in PATH and {archive} not found")
        raise RuntimeError("winetricks not found")

    logger.info(f"Extracting {archive} into packages/.tmp/winetricks/...")
    tmp_base = os.path.join(workdir, "packages", ".tmp")
    os.makedirs(tmp_base, exist_ok=True)
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="winetricks.", dir=tmp_base)

    run_command(RunMode.SILENT, ["tar", "-xzf", archive, "-C", tmp_dir])

    if not is_dir(tmp_dir):
        raise RuntimeError("winetricks extraction failed")

    logger.info("Installing winetricks...")
    run_command(RunMode.STREAM, ["sudo", "make", "install"], log_path="")

    if not look_path("winetricks"):
        raise RuntimeError("winetricks installation failed")

    logger.info("Running winetricks self-update...")
    result = run_command(
        RunMode.STREAM, ["sudo", "winetricks", "--self-update"], log_path=""
    )
    if result != 0:
        raise RuntimeError("winetricks self-update failed")
    logger.info("[OK] winetricks installed and updated successfully")

    logger.info("Cleaning up extracted winetricks directory...")
    import shutil
    shutil.rmtree(os.path.join(workdir, "packages", ".tmp"), ignore_errors=True)


def check_proton(
    package_root: str,
    gpu_type: str,
    is_fsr41: bool,
    logger: Logger,
) -> tuple[str, str]:
    """Ensure Proton is downloaded and patched. Returns ``(proton_ver, proton_path)``."""
    gpu_lower = gpu_type.lower()
    is_amd = "amd" in gpu_lower or "radeon" in gpu_lower

    if not look_path("wget"):
        raise RuntimeError("Proton is missing and wget is not available to download it.")

    logger.info("[OK] wget found for Proton download")
    proton_ver = DEFAULT_VERSIONS.proton_ver
    get_proton_url(proton_ver, DEFAULT_VERSIONS.proton_base_url)
    proton_dir = get_proton_install_path(proton_ver)
    ensure_proton(proton_dir, proton_ver, is_amd, is_fsr41, logger)
    return proton_ver, proton_dir


def detect_gpu_type(logger: Logger) -> str:
    """Return the GPU vendor string (NVIDIA / AMD / Intel / ...)."""
    gpu_type, err = detect_gpu()
    if err:
        raise RuntimeError(f"failed to detect GPU type: {err}")
    if not gpu_type:
        raise RuntimeError("GPU detection returned no result")
    logger.info(f"GPU Vendor: {gpu_type}")
    return gpu_type


def run_prechecks(
    wineprefix_arg: str,
    launcher_installer_path: str,
    force_wine_version: bool,
    fsr41: bool,
    logger: Logger,
) -> PrecheckResult:
    """Orchestrate all prechecks and return a populated *PrecheckResult*."""
    logger.info("Starting precheck phase...")
    print()

    gpu_type = detect_gpu_type(logger)
    is_amd = "amd" in gpu_type.lower() or "radeon" in gpu_type.lower()

    wineprefix, _, _ = validate_wineprefix(wineprefix_arg, logger)
    check_wine_binaries(logger)
    check_wine_version(logger, force_wine_version)
    check_umu_run(logger)

    if launcher_installer_path:
        if not os.path.isfile(launcher_installer_path):
            raise RuntimeError(f"launcher installer not found: {launcher_installer_path}")
        logger.info(f"[OK] Launcher installer found: {launcher_installer_path}")
    elif not look_path("wget"):
        raise RuntimeError("launcher installer not provided and wget not available")
    else:
        logger.info("[OK] wget found for launcher installer download")

    check_winetricks(".", logger)

    package_root = os.path.abspath("./packages")
    proton_ver, proton_path = check_proton(package_root, gpu_type, fsr41, logger)

    logger.info("[OK] All prechecks passed!")
    print()

    return PrecheckResult(
        wineprefix=wineprefix,
        gpu_type=gpu_type,
        is_amd_gpu=is_amd,
        proton_ver=proton_ver,
        proton_path=proton_path,
        force_wine_version=force_wine_version,
        launcher_installer=launcher_installer_path,
    )


def _is_ssd(path: str, logger: Logger) -> bool:
    try:
        output, _ = run_command_with_output(["lsblk", "-no", "rota", os.path.dirname(path)])
        return output.strip() == "0"
    except Exception:
        pass

    try:
        output, _ = run_command_with_output(["df", "-P", path])
        lines = output.split("\n")
        if len(lines) >= 2:
            fields = lines[1].split()
            if fields:
                dev = os.path.basename(fields[0])
                return dev.startswith("nvme") or dev.startswith("sd") or dev.startswith("vd")
    except Exception:
        pass

    return False


def _get_wine_version(logger: Logger) -> str:
    os.environ["WINEPREFIX"] = os.path.join(str(Path.home()), ".wine")
    try:
        output, _ = run_command_with_output(["wine", "--version"])
        m = re.search(r"wine-([0-9.]+)", output)
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""
