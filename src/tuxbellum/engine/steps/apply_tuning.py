"""Apply tuning — Wine registry tweaks and DLL overrides."""

from tuxbellum.core.commands import run_checked
from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.dll_overrides import update_dlls


def step(ctx: InstallContext) -> None:
    """Apply Wine tuning: win11 mode, fullscreen, DllOverrides, DirectInput."""
    if ctx.logger:
        ctx.logger.info("Configuring WINEPREFIX with things Bellum likes")

    run_checked(["winetricks", "win11"], label="winetricks win11")

    run_checked(
        ["winetricks", "grabfullscreen=y", "windowmanagerdecorated=n", "mwo=disabled"],
        label="winetricks tuning",
    )

    if ctx.is_amd_gpu:
        run_checked(["winetricks", "remove_mono"], label="winetricks remove_mono")

    # DirectInput RawInput
    run_checked(
        [
            "wine",
            "reg",
            "add",
            r"HKCU\Software\Wine\DirectInput",
            "/v",
            "RawInput",
            "/t",
            "REG_DWORD",
            "/d",
            "1",
            "/f",
        ],
        label="wine reg DirectInput",
    )

    # DllOverrides
    update_dlls(ctx.logger)

    run_checked(["wineboot", "--end-session"], label="wineboot final")
