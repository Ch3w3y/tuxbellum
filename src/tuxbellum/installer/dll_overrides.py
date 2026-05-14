"""DLL overrides — system-wide and per-app registry entries."""

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.commands import run_checked
from tuxbellum.core.logging import Logger


def update_dlls(logger: Logger) -> None:
    """Set DLL override registry keys for the current WINEPREFIX."""
    wine = DEFAULT_VERSIONS.binaries.wine
    system_dlls = ["d3d12", "d3d12core", "d3d10core", "d3d9", "d3d8"]

    logger.info("Setting DLL overrides")

    for dll in system_dlls:
        run_checked(
            [
                wine,
                "reg",
                "add",
                r"HKEY_CURRENT_USER\Software\Wine\DllOverrides",
                "/v",
                dll,
                "/d",
                "native,builtin",
                "/f",
            ],
            label=f"wine reg DllOverrides {dll}",
        )

    app_dlls = ["d3d11", "dxgi"]
    for dll in app_dlls:
        run_checked(
            [
                wine,
                "reg",
                "add",
                r"HKCU\Software\Wine\AppDefaults\AstarteLauncher.exe\DllOverrides",
                "/v",
                dll,
                "/d",
                "builtin",
                "/f",
            ],
            label=f"wine reg AstarteLauncher {dll}",
        )
        run_checked(
            [
                wine,
                "reg",
                "add",
                r"HKCU\Software\Wine\AppDefaults\Bellum-Win64-Shipping.exe\DllOverrides",
                "/v",
                dll,
                "/d",
                "native",
                "/f",
            ],
            label=f"wine reg Bellum {dll}",
        )
