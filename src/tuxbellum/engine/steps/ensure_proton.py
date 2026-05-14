"""Ensure Proton is available — download, extract, and patch if needed."""

from tuxbellum.config.paths import path_mgr
from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.proton import ensure_proton, get_proton_install_path, patch_proton_settings


def step(ctx: InstallContext) -> None:
    """Ensure Proton-CachyOS is downloaded, extracted, and patched."""
    if ctx.logger:
        ctx.logger.info("Ensuring Proton is available...")

    proton_ver = ctx.proton_version or DEFAULT_VERSIONS.proton_ver
    proton_dir = get_proton_install_path(proton_ver)
    package_root = path_mgr.app_data_root()

    ensure_proton(
        proton_dir,
        proton_ver,
        package_root,
        ctx.is_amd_gpu,
        ctx.is_fsr41,
        ctx.logger,
    )

    ctx.proton_path = get_proton_install_path(proton_ver)
    ctx.proton_version = proton_ver

    patch_proton_settings(ctx.proton_path)
