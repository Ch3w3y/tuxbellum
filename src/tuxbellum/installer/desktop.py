"""Desktop integration — .desktop file, icon, and system registration."""

import os
import shutil

from tuxbellum.core.logging import Logger
from tuxbellum.core.system import RunMode, look_path, run_command


def copy_icon(icon_path: str) -> None:
    """Copy the Bellum icon into ~/.local/share/icons/hicolor/256x256/apps/."""
    if not icon_path:
        raise RuntimeError("icon path is empty")
    dest = os.path.join(
        os.environ.get("HOME", os.path.expanduser("~")),
        ".local",
        "share",
        "icons",
        "hicolor",
        "256x256",
        "apps",
        "bellum.png",
    )
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(icon_path, dest)


def generate_desktop_files(
    wineprefix: str,
    icon_path: str,
    gpu_type: str,
    logger: Logger,
) -> None:
    """Write Bellum.desktop to apps dir and Desktop, mark trusted, update db."""
    home = os.environ.get("HOME", os.path.expanduser("~"))
    apps_dir = os.path.join(home, ".local", "share", "applications")
    icon_dir = os.path.join(home, ".local", "share", "icons", "hicolor", "256x256", "apps")

    os.makedirs(apps_dir, exist_ok=True)

    if gpu_type == "AMD":
        comment = "Launch Bellum via Wine"
    elif gpu_type == "NVIDIA":
        comment = "Launch Bellum via Proton (NVIDIA optimized)"
    else:
        raise RuntimeError(f"unsupported GPU type for desktop file: {gpu_type}")

    installed_icon = os.path.join(icon_dir, "bellum.png") if icon_path else ""

    content = (
        "[Desktop Entry]\n"
        "Name=Bellum\n"
        f"Comment={comment}\n"
        "Exec=Bellum\n"
        f"Icon={installed_icon}\n"
        "Type=Application\n"
        "Categories=Game;\n"
        "Terminal=false\n"
        f"Path={wineprefix}\n"
    )

    desktop_file = os.path.join(apps_dir, "Bellum.desktop")
    with open(desktop_file, "w") as fh:
        fh.write(content)
    os.chmod(desktop_file, 0o755)

    desktop_dest = os.path.join(home, "Desktop", "Bellum.desktop")
    if os.path.isdir(os.path.join(home, "Desktop")):
        shutil.copy2(desktop_file, desktop_dest)
        os.chmod(desktop_dest, 0o755)

    if look_path("gio"):
        _gio_set(desktop_file, "metadata::trusted", "true")
        if os.path.isfile(desktop_dest):
            _gio_set(desktop_dest, "metadata::trusted", "true")

    if look_path("update-desktop-database"):
        run_command(
            RunMode.SILENT,
            ["update-desktop-database", apps_dir],
        )


def _gio_set(file: str, key: str, value: str) -> None:
    run_command(
        RunMode.SILENT,
        ["gio", "set", file, key, value],
    )
