"""WINEPREFIX initialisation — Wine bootstrap and DLL installation."""

import os
from pathlib import Path

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.commands import run_checked
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
    "webview2",
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
        ".steam",
        "steam",
    )
    os.environ["GAMEID"] = "1"

    logger.info("Initializing WINEPREFIX with Proton base")
    run_checked(
        ["umu-run", DEFAULT_VERSIONS.binaries.msidb],
        label="msidb bootstrap",
    )

    run_checked(
        [DEFAULT_VERSIONS.binaries.wineboot, "--init"],
        label="wineprefix init",
    )


def install_winedlls(logger: Logger) -> None:
    """Install every required DLL via winetricks."""
    logger.info("Installing required winedlls")
    for dll in _WINEDLLS:
        run_checked(["winetricks", "-q", dll], label=f"winetricks {dll}")
        logger.info(f"[OK] {dll}")
