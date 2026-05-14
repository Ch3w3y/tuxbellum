"""Verify launcher — check AstarteLauncher.exe exists after install."""

import os

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.launcher import cleanup_launcher_installer


def step(ctx: InstallContext) -> None:
    """Verify that the Astarte Launcher executable was installed."""
    installed_exe = os.path.join(
        ctx.wineprefix,
        "drive_c/users/steamuser/AppData/Local",
        "Astarte Industries/Astarte Launcher/AstarteLauncher.exe",
    )

    if not os.path.isfile(installed_exe):
        exit_code = ctx.get("launcher_exit_code", "unknown")
        raise RuntimeError(
            f"Launcher installation failed (exit code {exit_code}):"
            f" executable not found at {installed_exe}"
        )

    if ctx.logger:
        ctx.logger.info(
            "Astarte Launcher install completed successfully! " "Few more steps to go..."
        )
        ctx.logger.warn("I'm not done! Don't launch game or close this script just yet")

    # Clean up launcher download artifacts
    state = ctx.pop("launcher_state", None)
    if state:
        cleanup_launcher_installer(state, ctx.logger)
