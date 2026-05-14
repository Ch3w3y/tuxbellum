"""Apply DXVK — for AMD GPUs."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.dxvk import install_dxvk


def step(ctx: InstallContext) -> None:
    """Install DXVK into the WINEPREFIX (AMD only, no-op otherwise)."""
    install_dxvk(ctx.gpu_type, ctx.resource_root, ctx.logger)
