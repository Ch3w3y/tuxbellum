"""Generate launcher wrapper — ~/.local/bin/Bellum."""

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.wrappers import generate_launcher_wrapper


def step(ctx: InstallContext) -> None:
    """Create the Bellum launcher wrapper script."""
    generate_launcher_wrapper(
        ctx.wineprefix,
        ctx.proton_path,
        ctx.gpu_type,
        ctx.logger,
    )
