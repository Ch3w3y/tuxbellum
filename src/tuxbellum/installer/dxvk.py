"""DXVK installation — AMD GPU only."""

import os
import shutil
import tempfile

from tuxbellum.config.paths import path_mgr
from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.commands import run_checked
from tuxbellum.core.logging import Logger
from tuxbellum.core.system import look_path


def install_dxvk(gpu_type: str, resource_root: str, logger: Logger) -> None:
    """Install DXVK into the current WINEPREFIX.  No-op for non-AMD GPUs."""
    gpu_lower = gpu_type.lower()
    if "amd" not in gpu_lower and "radeon" not in gpu_lower:
        logger.info(f"Skipping DXVK installation for non-AMD GPU: {gpu_type}")
        return

    archive = _resolve_dxvk_archive(resource_root, logger)

    logger.info("Installing DXVK...")
    tmp = tempfile.mkdtemp(prefix="dxvk.")

    try:
        # Extract
        run_checked(
            ["tar", "-xzf", archive, "-C", tmp],
            label="DXVK extraction",
        )

        # Locate dxvk_setup.sh — may be inside a subdirectory
        install_dir = tmp
        if not os.path.isfile(os.path.join(install_dir, "dxvk_setup.sh")):
            try:
                entries = os.listdir(tmp)
            except OSError:
                entries = []
            for entry in entries:
                candidate = os.path.join(tmp, entry)
                if os.path.isdir(candidate) and os.path.isfile(
                    os.path.join(candidate, "dxvk_setup.sh")
                ):
                    install_dir = candidate
                    break

        setup = os.path.join(install_dir, "dxvk_setup.sh")
        if not os.path.isfile(setup):
            raise RuntimeError("DXVK setup script not found after extraction")

        run_checked([setup, "install"], label="DXVK setup script")

        # Copy dxvk.conf
        wineprefix = os.environ.get("WINEPREFIX", "")
        if not wineprefix:
            raise RuntimeError("WINEPREFIX not set")
        conf_src = os.path.join(install_dir, "dxvk.conf")
        conf_dst = os.path.join(wineprefix, "dxvk.conf")
        shutil.copy2(conf_src, conf_dst)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    logger.info("[OK] DXVK installed")


def _resolve_dxvk_archive(resource_root: str, logger: Logger) -> str:
    bundled = os.path.join(
        resource_root,
        "packages",
        f"dxvk-{DEFAULT_VERSIONS.dxvk_ver}.tar.gz",
    )
    if os.path.isfile(bundled):
        return bundled

    if not look_path("wget"):
        raise RuntimeError(f"DXVK archive not found and wget is unavailable: {bundled}")

    version = _official_dxvk_version(DEFAULT_VERSIONS.dxvk_ver)
    cache_dir = path_mgr.user_cache("tuxbellum", "dxvk")
    os.makedirs(cache_dir, exist_ok=True)
    archive = os.path.join(cache_dir, f"dxvk-{version}.tar.gz")
    if os.path.isfile(archive):
        logger.warn(f"Bundled DXVK archive missing, using cached upstream DXVK {version}")
        return archive

    url = f"https://github.com/doitsujin/dxvk/releases/download/v{version}/dxvk-{version}.tar.gz"
    logger.warn(f"Bundled DXVK archive missing, downloading upstream DXVK {version} instead")
    try:
        run_checked(["wget", "-O", archive, url], label="DXVK download")
    except RuntimeError:
        raise RuntimeError(f"DXVK download failed: {url}")
    return archive


def _official_dxvk_version(version: str) -> str:
    parts = version.split("-")
    return parts[0] if parts else version
