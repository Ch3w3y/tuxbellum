"""AstarteLauncher installer download and cleanup."""

import os
from dataclasses import dataclass

from tuxbellum.config.versions import LAUNCHER_INSTALLER_URL
from tuxbellum.core.logging import Logger
from tuxbellum.core.system import RunMode, run_command


@dataclass
class LauncherInstallerState:
    installer_path: str = ""
    downloaded: bool = False
    download_dir: str = ""


def download_launcher_installer(workdir: str, logger: Logger) -> LauncherInstallerState:
    """Download AstarteLauncher-amd64-installer.exe using wget."""
    download_dir = os.path.join(workdir, "installer-cache")
    filename = "AstarteLauncher-amd64-installer.exe"
    dest = os.path.join(download_dir, filename)

    os.makedirs(download_dir, exist_ok=True)
    logger.info(f"Downloading AstarteLauncher installer: {filename}")

    run_command(
        RunMode.SILENT,
        ["wget", "-O", dest, LAUNCHER_INSTALLER_URL],
    )

    if not os.path.isfile(dest):
        raise RuntimeError("download verification failed: launcher installer not found")

    return LauncherInstallerState(
        installer_path=dest,
        downloaded=True,
        download_dir=download_dir,
    )


def cleanup_launcher_installer(state: LauncherInstallerState, logger: Logger) -> None:
    """Remove the downloaded installer and its directory."""
    if not state.downloaded or not state.installer_path:
        return

    logger.info("Cleaning up downloaded launcher installer...")
    try:
        os.remove(state.installer_path)
    except FileNotFoundError:
        pass
    except OSError:
        logger.warn("Failed to remove launcher installer")

    if state.download_dir:
        try:
            os.rmdir(state.download_dir)
        except OSError:
            pass
