"""Run Astarte Launcher installer — download and execute."""

import os

from tuxbellum.core.commands import run_allowed_failure, run_streaming
from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.launcher import (
    download_launcher_installer,
)


def step(ctx: InstallContext) -> None:
    """Download and run the Astarte Launcher installer via Proton's bundled wine."""
    # Download launcher if not already provided
    if not ctx.launcher_exe:
        if ctx.logger:
            ctx.logger.info("Downloading Astarte Launcher installer...")
        state = download_launcher_installer(ctx.cache_dir, ctx.logger)
        ctx.launcher_exe = state.installer_path
        ctx.put("launcher_state", state)

    # Use Proton's bundled wine directly — avoids pressure-vessel container
    # that blocks GUI windows on Wayland
    wine_bin = os.path.join(ctx.proton_path, "files", "bin", "wine")
    wineserver_bin = os.path.join(ctx.proton_path, "files", "bin", "wineserver")

    run_allowed_failure([wineserver_bin, "-k"])

    if ctx.logger:
        ctx.logger.info(
            "Time to install the launcher! " "Follow the on-screen prompts once the GUI pops up."
        )

    on_line = ctx.logger.info if ctx.logger else None
    ctx.put(
        "launcher_exit_code",
        run_streaming([wine_bin, ctx.launcher_exe], on_line=on_line),
    )
