"""Initialize WINEPREFIX — bootstrap a fresh prefix with Proton."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.wineprefix import init_wineprefix


def step(ctx: InstallContext) -> None:
    """Bootstrap the WINEPREFIX with Proton."""
    init_wineprefix(ctx.proton_path, ctx.wineprefix, ctx.logger)
