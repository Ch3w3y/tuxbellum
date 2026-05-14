"""Verify launcher — check AstarteLauncher.exe exists after install."""

import os

from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.launcher import cleanup_launcher_installer


def _find_launcher(wineprefix: str) -> str:
    """Find AstarteLauncher.exe regardless of Wine path casing."""
    # Canonical path (most Wine builds preserve Windows casing)
    canonical = os.path.join(
        wineprefix,
        "drive_c/users/steamuser/AppData/Local",
        "Astarte Industries/Astarte Launcher/AstarteLauncher.exe",
    )
    if os.path.isfile(canonical):
        return canonical

    # Fallback: search case-insensitively for the AppData subtree
    appdata_base = os.path.join(wineprefix, "drive_c", "users", "steamuser")
    if not os.path.isdir(appdata_base):
        return ""

    for entry in os.scandir(appdata_base):
        if entry.is_dir() and entry.name.lower() in ("appdata", "application data"):
            local = os.path.join(entry.path, "Local")
            if not os.path.isdir(local):
                local = os.path.join(entry.path, "local")
            candidate = os.path.join(
                local,
                "Astarte Industries/Astarte Launcher/AstarteLauncher.exe",
            )
            if os.path.isfile(candidate):
                return candidate

    return ""


def step(ctx: InstallContext) -> None:
    """Verify that the Astarte Launcher executable was installed."""
    installed_exe = _find_launcher(ctx.wineprefix)

    if not installed_exe:
        exit_code = ctx.get("launcher_exit_code", "unknown")
        expected = os.path.join(
            ctx.wineprefix,
            "drive_c/users/steamuser/AppData/Local",
            "Astarte Industries/Astarte Launcher/AstarteLauncher.exe",
        )
        raise RuntimeError(
            f"Launcher installation failed (exit code {exit_code})"
            f" — executable not found at {expected}"
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
