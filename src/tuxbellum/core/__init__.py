"""Core system utilities for the Bellum Linux Installer."""

from tuxbellum.core.commands import (
    CommandError,
    CommandResult,
    run_allowed_failure,
    run_capture,
    run_checked,
    run_streaming,
)
from tuxbellum.core.gpu import classify_gpu, detect_gpu
from tuxbellum.core.gui_picker import (
    DirectoryPickerResult,
    pick_directory,
    pick_directory_existing,
    validate_directory,
)
from tuxbellum.core.logging import Color, Logger, colorize
from tuxbellum.core.system import (
    RunMode,
    ask_bool,
    is_dir,
    is_writable,
    look_path,
    run_command,
    run_command_with_output,
)

__all__ = [
    # Structured command execution (v4)
    "CommandResult",
    "CommandError",
    "run_checked",
    "run_allowed_failure",
    "run_capture",
    "run_streaming",
    # Legacy (deprecated — migrate callers to structured API)
    "run_command",
    "RunMode",
    "run_command_with_output",
    # GPU
    "detect_gpu",
    "classify_gpu",
    # System utilities
    "look_path",
    "ask_bool",
    "is_dir",
    "is_writable",
    # GUI utilities
    "pick_directory",
    "pick_directory_existing",
    "validate_directory",
    "DirectoryPickerResult",
    # Logging
    "Logger",
    "Color",
    "colorize",
]
