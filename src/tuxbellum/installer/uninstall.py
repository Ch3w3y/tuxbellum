"""Uninstall workflow — remove launcher, desktop entries, Proton, and WINEPREFIX."""

import os
from dataclasses import dataclass

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.commands import run_allowed_failure
from tuxbellum.core.logging import Color, Logger, colorize
from tuxbellum.core.system import ask_bool, is_dir
from tuxbellum.domain.install_state import delete_manifest, discover_manifest
from tuxbellum.installer.proton import get_proton_install_path


@dataclass
class UninstallConfig:
    wineprefix: str = ""
    gpu_type: str = ""


def run_uninstallation(config: UninstallConfig, logger: Logger) -> None:
    """Execute the full uninstall pipeline."""
    logger.info(f"GPU Type: {config.gpu_type}")
    logger.info("Starting uninstallation phase...")
    print()

    if not config.wineprefix:
        raise RuntimeError("WINEPREFIX is required. Use --wineprefix <path> or set WINEPREFIX env.")

    wineprefix_exists = is_dir(config.wineprefix)
    if not wineprefix_exists:
        logger.warn(
            colorize(f"WINEPREFIX directory not found: {config.wineprefix}", Color.BOLD_YELLOW)
        )

    # Discover manifest for smarter cleanup
    manifest = discover_manifest(config.wineprefix)

    logger.info(colorize(f"WINEPREFIX: {config.wineprefix}", Color.BOLD_YELLOW))
    print()

    if not ask_bool(
        "Are you sure you want to uninstall Bellum? This action cannot be undone. (Y/n): "
    ):
        logger.info("Uninstallation cancelled by user.")
        return

    print()
    logger.info("Proceeding with uninstallation...")
    print()

    if manifest:
        _remove_from_manifest(manifest, logger)
    else:
        _remove_launcher_binaries(logger)
        _remove_desktop_entries(logger)
        _remove_icon(logger)

    _remove_proton(config.wineprefix, logger)

    if wineprefix_exists:
        _remove_wineprefix(config.wineprefix, logger)
    else:
        logger.info(
            colorize(
                f"Skipping WINEPREFIX removal: {config.wineprefix} does not exist",
                Color.BOLD_YELLOW,
            )
        )

    logger.info("[OK] Uninstallation complete!")
    print()


def _remove_launcher_binaries(logger: Logger) -> None:
    logger.info("Removing launcher binaries...")
    from tuxbellum.config.paths import path_mgr

    bellum_path = os.path.join(path_mgr.user_local_bin(), "Bellum")
    if os.path.isfile(bellum_path):
        os.remove(bellum_path)
        logger.info(f"[OK] Removed {bellum_path}")


def _remove_desktop_entries(logger: Logger) -> None:
    logger.info("Removing desktop entries...")
    home = os.environ.get("HOME", os.path.expanduser("~"))
    apps_dir = os.path.join(home, ".local", "share", "applications")

    for p in [
        os.path.join(apps_dir, "Bellum.desktop"),
        os.path.join(home, "Desktop", "Bellum.desktop"),
    ]:
        if os.path.isfile(p):
            os.remove(p)
            logger.info(f"[OK] Removed {p}")

    if is_dir(apps_dir):
        run_allowed_failure(["update-desktop-database", apps_dir])


def _remove_icon(logger: Logger) -> None:
    logger.info("Removing launcher icon...")
    home = os.environ.get("HOME", os.path.expanduser("~"))
    icon = os.path.join(
        home, ".local", "share", "icons", "hicolor", "256x256", "apps", "bellum.png"
    )
    if os.path.isfile(icon):
        os.remove(icon)
        logger.info(f"[OK] Removed {icon}")


def _remove_proton(wineprefix: str, logger: Logger) -> None:
    logger.info("Removing Proton directory...")
    proton_path = get_proton_install_path(DEFAULT_VERSIONS.proton_ver)
    if is_dir(proton_path):
        logger.info(f"Removing Proton directory: {proton_path}")
        import shutil

        shutil.rmtree(proton_path, ignore_errors=True)
        logger.info("[OK] Removed Bellum Proton directory")

    parent = os.path.dirname(proton_path)
    if _is_empty_dir(parent):
        import shutil

        shutil.rmtree(parent, ignore_errors=True)
        grandparent = os.path.dirname(parent)
        if _is_empty_dir(grandparent):
            shutil.rmtree(grandparent, ignore_errors=True)


def _remove_wineprefix(wineprefix: str, logger: Logger) -> None:
    import shutil

    shutil.rmtree(wineprefix, ignore_errors=True)
    logger.info(colorize(f"[OK] Removed WINEPREFIX: {wineprefix}", Color.BOLD_YELLOW))


def _is_empty_dir(path: str) -> bool:
    if not is_dir(path):
        return False
    try:
        return len(os.listdir(path)) == 0
    except OSError:
        return False


def _remove_from_manifest(manifest, logger: Logger) -> None:
    """Remove all tracked files from a manifest, then delete the manifest."""
    logger.info("Removing files tracked by install manifest...")
    for f in manifest.owned_files:
        if os.path.isfile(f):
            os.remove(f)
            logger.info(f"[OK] Removed {f}")
        elif os.path.islink(f):
            os.unlink(f)
            logger.info(f"[OK] Removed symlink {f}")

    for d in manifest.owned_directories:
        if is_dir(d):
            import shutil

            shutil.rmtree(d, ignore_errors=True)
            logger.info(f"[OK] Removed directory {d}")

    delete_manifest(manifest.wineprefix)
    logger.info("[OK] Removed install manifest")
