"""Install Wine DLLs — winetricks for required components."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.wineprefix import install_winedlls


def step(ctx: InstallContext) -> None:
    """Install all required Wine DLLs via winetricks."""
    install_winedlls(ctx.logger)
