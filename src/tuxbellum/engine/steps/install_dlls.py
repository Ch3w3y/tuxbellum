"""Install Wine DLLs — winetricks for required components."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.wineprefix import install_winedlls


def step(ctx: InstallContext) -> None:
    """Install all required Wine DLLs via the bundled winetricks-modified."""
    install_winedlls(ctx.winetricks_path, ctx.logger)
