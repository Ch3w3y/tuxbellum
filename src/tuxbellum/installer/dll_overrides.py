"""DLL overrides — system-wide and per-app registry entries."""

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.system import run_command, RunMode
from tuxbellum.core.logging import Logger


def update_dlls(logger: Logger) -> None:
    """Set DLL override registry keys for the current WINEPREFIX."""

    wine = DEFAULT_VERSIONS.binaries.wine
    system_dlls = ["d3d12", "d3d12core", "d3d10core", "d3d9", "d3d8"]

    logger.info("Setting DLL overrides")

    for dll in system_dlls:
        run_command(
            RunMode.SILENT,
            [
                wine, "reg", "add",
                r"HKEY_CURRENT_USER\Software\Wine\DllOverrides",
                "/v", dll, "/d", "native,builtin", "/f",
            ],
        )

    app_dlls = ["d3d11", "dxgi"]
    for dll in app_dlls:
        run_command(
            RunMode.SILENT,
            [
                wine, "reg", "add",
                r"HKCU\Software\Wine\AppDefaults\AstarteLauncher.exe\DllOverrides",
                "/v", dll, "/d", "builtin", "/f",
            ],
        )
        run_command(
            RunMode.SILENT,
            [
                wine, "reg", "add",
                r"HKCU\Software\Wine\AppDefaults\Bellum-Win64-Shipping.exe\DllOverrides",
                "/v", dll, "/d", "native", "/f",
            ],
        )
