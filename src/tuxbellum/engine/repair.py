"""Repair — verify and fix an existing TuxBellum installation."""

import os

from tuxbellum.config.paths import path_mgr
from tuxbellum.core.logging import Logger
from tuxbellum.domain.install_state import discover_manifest


def run_repair(wineprefix: str, logger: Logger) -> dict:
    """
    Verify and repair a TuxBellum-managed installation.

    Returns::

        {
            "repaired": True,
            "fixed": ["launcher script rebuilt"],
            "unfixed": [],
        }
    """
    manifest = discover_manifest(wineprefix)
    if not manifest:
        return {"repaired": False, "fixed": [], "unfixed": ["no manifest found"]}

    fixed: list[str] = []
    unfixed: list[str] = []

    # Check launcher script
    if not os.path.isfile(manifest.launcher_path):
        logger.info("Launcher script missing — regenerating...")
        try:
            from tuxbellum.installer.wrappers import generate_launcher_wrapper

            generate_launcher_wrapper(
                manifest.wineprefix,
                manifest.proton_path,
                manifest.gpu_type,
                logger,
            )
            fixed.append("launcher script regenerated")
        except Exception as e:
            unfixed.append(f"launcher script: {e}")

    # Check desktop entry
    if manifest.desktop_entry_path and not os.path.isfile(manifest.desktop_entry_path):
        logger.info("Desktop entry missing — regenerating...")
        try:
            icon_path = os.path.join(
                path_mgr.app_data_root(), "packages", "launcher_1_256x256x32.png"
            )
            from tuxbellum.installer.desktop import generate_desktop_files

            generate_desktop_files(manifest.wineprefix, icon_path, manifest.gpu_type, logger)
            fixed.append("desktop entry regenerated")
        except Exception as e:
            unfixed.append(f"desktop entry: {e}")

    # Check icon
    if manifest.icon_path and not os.path.isfile(manifest.icon_path):
        logger.info("Icon missing — recopying...")
        try:
            icon_src = os.path.join(
                path_mgr.app_data_root(), "packages", "launcher_1_256x256x32.png"
            )
            from tuxbellum.installer.desktop import copy_icon

            copy_icon(icon_src)
            fixed.append("icon restored")
        except Exception as e:
            unfixed.append(f"icon: {e}")

    return {
        "repaired": len(unfixed) == 0,
        "fixed": fixed,
        "unfixed": unfixed,
    }
