"""Apply FSR 4.1 — for AMD GPUs with FSR enabled."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.fsr import upgrade_fsr


def step(ctx: InstallContext) -> None:
    """Copy FSR DLLs and register overrides (AMD + FSR 4.1 only)."""
    if ctx.is_amd_gpu and ctx.is_fsr41:
        upgrade_fsr(ctx.wineprefix, ctx.resource_root, ctx.gpu_type, ctx.logger)
