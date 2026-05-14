"""Doctor — diagnostic report for host and managed installs."""

import os

from tuxbellum.config.paths import path_mgr
from tuxbellum.core.system import look_path
from tuxbellum.domain.install_state import discover_manifest


def run_diagnostics(wineprefix: str = "") -> dict:
    """
    Run system and install diagnostics.

    Returns::

        {
            "healthy": bool,
            "checks": [
                {"name": "wine", "status": "ok", "detail": "/usr/bin/wine"},
                {"name": "wine", "status": "warning", "detail": "not on PATH"},
                ...
            ],
        }
    """
    checks: list[dict] = []

    # System dependencies
    for name, binary in [
        ("wine", "wine"),
        ("winetricks", "winetricks"),
        ("wget", "wget"),
        ("tar", "tar"),
    ]:
        path = look_path(binary)
        checks.append(
            {
                "name": name,
                "status": "ok" if path else "warning",
                "detail": path if path else f"{binary} not on PATH",
            }
        )

    # GTK runtime
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        checks.append({"name": "gtk4-runtime", "status": "ok", "detail": "GTK4 available"})
    except (ImportError, ValueError):
        checks.append({"name": "gtk4-runtime", "status": "warning", "detail": "GTK4 not available"})

    # Cache
    cache_dir = path_mgr.user_cache("tuxbellum")
    cache_size = 0
    if os.path.isdir(cache_dir):
        for root, _, files in os.walk(cache_dir):
            for f in files:
                try:
                    cache_size += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    checks.append(
        {
            "name": "cache",
            "status": "ok",
            "detail": f"{cache_dir} ({cache_size / (1024 * 1024):.1f} MB)",
        }
    )

    # Managed install
    if wineprefix:
        manifest = discover_manifest(wineprefix)
        if manifest:
            checks.append(
                {
                    "name": "manifest",
                    "status": "ok",
                    "detail": f"v{manifest.tuxbellum_version}, proton={manifest.proton_version}",
                }
            )

            # Check key paths
            for label, path in [
                ("launcher", manifest.launcher_path),
                ("desktop_entry", manifest.desktop_entry_path),
                ("icon", manifest.icon_path),
            ]:
                if path:
                    checks.append(
                        {
                            "name": label,
                            "status": "ok" if os.path.exists(path) else "warning",
                            "detail": path if os.path.exists(path) else f"missing: {path}",
                        }
                    )
        else:
            checks.append(
                {
                    "name": "manifest",
                    "status": "warning",
                    "detail": f"no manifest found in {wineprefix}",
                }
            )
    else:
        checks.append(
            {
                "name": "manifest",
                "status": "ok",
                "detail": "no wineprefix specified — skipping install check",
            }
        )

    healthy = all(c["status"] == "ok" for c in checks)
    return {"healthy": healthy, "checks": checks}
