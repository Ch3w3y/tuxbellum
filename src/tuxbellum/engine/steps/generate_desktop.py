"""Generate desktop entries — .desktop files, icon, and launch vars."""

import os

from tuxbellum.config.paths import path_mgr
from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.desktop import copy_icon, generate_desktop_files
from tuxbellum.installer.launch_vars import generate_launch_vars_file


def step(ctx: InstallContext) -> None:
    """Create .desktop files, copy icon, and write launch variables."""
    icon_path = path_mgr.bundled_path("launcher_1_256x256x32.png")
    copy_icon(icon_path)
    generate_desktop_files(ctx.wineprefix, icon_path, ctx.gpu_type, ctx.logger)
    generate_launch_vars_file(ctx.wineprefix, ctx.gpu_type, ctx.is_fsr41)
