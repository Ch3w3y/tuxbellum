"""WINEPREFIX initialisation — Wine bootstrap and DLL installation."""

import os
from pathlib import Path

from tuxbellum.config.versions import DEFAULT_VERSIONS, LAUNCHER_INSTALLER_URL
from tuxbellum.core.system import run_command, RunMode
from tuxbellum.core.logging import Logger


_WINEDLLS = [
    "vcrun2026",
    "d3dcompiler_43",
    "d3dcompiler_47",
    "faudio",
    "msls31",
    "dotnet9",
    "dotnetdesktop9",
    "mfc140",
]


def init_wineprefix(proton_path: str, wineprefix: str, logger: Logger) -> None:
    """Bootstrap a fresh WINEPREFIX using Proton."""
    # Set required env vars
    os.environ["PROTONPATH"] = proton_path
    os.environ["WINEPREFIX"] = wineprefix
    os.environ["WINEARCH"] = "win64"
    os.environ["STEAM_APP_PATH"] = wineprefix
    os.environ["STEAM_APPID"] = "1"
    os.environ["STEAM_COMPAT_DATA_PATH"] = wineprefix
    os.environ["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.join(
        os.environ.get("HOME", str(Path.home())),
        ".steam", "steam",
    )
    os.environ["GAMEID"] = "1"

    logger.info("Initializing WINEPREFIX with Proton base")
    if run_command(
        RunMode.STREAM,
        ["umu-run", DEFAULT_VERSIONS.binaries.msidb],
    ) != 0:
        raise RuntimeError("Failed to run msidb with umu-run")
        
    if run_command(
        RunMode.STREAM,
        [DEFAULT_VERSIONS.binaries.wineboot, "--init"],
    ) != 0:
        raise RuntimeError("Failed to initialize wineprefix with wineboot")


def install_winedlls(logger: Logger) -> None:
    """Install every required DLL via winetricks."""
    logger.info("Installing required winedlls")
    for dll in _WINEDLLS:
        if run_command(
            RunMode.STREAM,
            ["winetricks", "-q", dll],
        ) != 0:
            raise RuntimeError(f"Failed to install dll via winetricks: {dll}")
        logger.info(f"[OK] {dll}")
