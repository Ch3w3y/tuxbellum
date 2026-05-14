"""Ensure Proton is available — download and patch if needed."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.proton import ensure_proton, patch_proton_settings


def step(ctx: InstallContext) -> None:
    """Ensure Proton-CachyOS is downloaded, extracted, and patched."""
    if ctx.logger:
        ctx.logger.info("Ensuring Proton is available...")

    ensure_proton(ctx.proton_version, ctx.logger)

    # The ensure_proton function resolves the path internally;
    # we grab it from the module for context consistency.
    from tuxbellum.installer.proton import get_proton_install_path

    ctx.proton_path = get_proton_install_path(ctx.proton_version)

    patch_proton_settings(ctx.proton_path)
