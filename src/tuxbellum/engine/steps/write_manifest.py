"""Write install manifest — record the completed installation."""

import os

from tuxbellum.config.paths import path_mgr
from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.domain.install_manifest import InstallManifest
from tuxbellum.domain.install_state import save_manifest
from tuxbellum.engine.context import InstallContext


def step(ctx: InstallContext) -> None:
    """Persist the install manifest inside the managed WINEPREFIX."""
    home = os.environ.get("HOME", os.path.expanduser("~"))
    desktop_entry = os.path.join(home, ".local", "share", "applications", "Bellum.desktop")
    desktop_shortcut = os.path.join(home, "Desktop", "Bellum.desktop")
    icon = os.path.join(
        home, ".local", "share", "icons", "hicolor", "256x256", "apps", "bellum.png"
    )
    launcher = os.path.join(path_mgr.user_local_bin(), "Bellum")

    dxvk_source = "bundled"
    dxvk_archive = os.path.join(
        ctx.resource_root, "packages", f"dxvk-{DEFAULT_VERSIONS.dxvk_ver}.tar.gz"
    )
    if not os.path.isfile(dxvk_archive):
        dxvk_source = "downloaded"

    manifest = InstallManifest.now(
        tuxbellum_version="4.0.4",
        wineprefix=ctx.wineprefix,
        proton_version=ctx.proton_version,
        proton_path=ctx.proton_path,
        gpu_type=ctx.gpu_type,
        is_amd_gpu=ctx.is_amd_gpu,
        dxvk_version=DEFAULT_VERSIONS.dxvk_ver,
        dxvk_source=dxvk_source,
        fsr_enabled=ctx.is_fsr41,
        launcher_path=launcher,
        desktop_entry_path=desktop_entry,
        desktop_shortcut_path=desktop_shortcut,
        icon_path=icon,
        owned_files=[launcher, desktop_entry, desktop_shortcut, icon],
        owned_directories=[ctx.wineprefix, os.path.dirname(ctx.proton_path)],
        launch_options={
            "gamescope": False,
            "gamemode": False,
            "hdr": False,
            "nvapi": False,
        },
    )

    save_manifest(manifest, ctx.wineprefix)
    if ctx.logger:
        ctx.logger.info(f"[OK] Install manifest written to {ctx.wineprefix}")
        ctx.logger.info(
            f"[OK] Game launcher installed: {os.path.join(path_mgr.user_local_bin(), 'Bellum')}"
        )
