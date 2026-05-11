"""GUI directory picker with terminal fallback."""

import os
import subprocess
from dataclasses import dataclass


@dataclass
class DirectoryPickerResult:
    path: str = ""
    success: bool = False
    error: str = ""


def pick_directory(initial_path: str = "") -> DirectoryPickerResult:
    """Open picker for selecting install directory."""
    return _try_picker("Select Install Directory", initial_path)


def pick_directory_existing(initial_path: str = "") -> DirectoryPickerResult:
    """Open picker for selecting existing directory."""
    return _try_picker("Select Directory", initial_path)


def _try_picker(title: str, initial_path: str = "") -> DirectoryPickerResult:
    tools = [
        (
            "yad",
            ["yad", "--directory", f"--title={title}"]
            + ([f"--filename={initial_path}"] if initial_path else []),
        ),
        (
            "kdialog",
            ["kdialog", "--getexistingdirectory", f"--title={title}"]
            + ([initial_path] if initial_path else []),
        ),
        ("zenity", ["zenity", "--file-selection", "--directory", f"--title={title}"]),
    ]

    for name, args in tools:
        if not _exists(name):
            continue
        try:
            env = os.environ.copy()
            if name == "zenity" and initial_path:
                env["Zenity_FileSelector_Dir"] = initial_path
            result = subprocess.run(
                [a for a in args if a],
                capture_output=True,
                text=True,
                env=env,
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                if path:
                    return DirectoryPickerResult(path=path, success=True)
            elif result.returncode == 1:
                return DirectoryPickerResult(error="Selection cancelled by user")
        except Exception:
            continue

    print("\nNo GUI directory picker found. Using terminal input.")
    try:
        path = input("Enter directory path (or press Enter for current dir): ").strip()
        if not path:
            path = os.getcwd()
        return DirectoryPickerResult(path=path, success=True)
    except (KeyboardInterrupt, EOFError):
        return DirectoryPickerResult(error="Input cancelled")


def _exists(name: str) -> bool:
    try:
        subprocess.check_output(["which", name], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def validate_directory(path: str) -> tuple[bool, str]:
    """Validate directory for WINEPREFIX usage."""
    path = path.rstrip("/")
    if not path.startswith("/"):
        return False, "Path must be absolute (start with /). Example: /games"
    parent = os.path.dirname(path) or "/"
    if not os.path.isdir(parent):
        return False, f"Parent directory '{parent}' does not exist."
    bellum_path = os.path.join(path, "Bellum")
    if os.path.isdir(bellum_path):
        return (
            False,
            f"Bellum already installed at '{bellum_path}'. Uninstall first.",
        )
    return True, ""
