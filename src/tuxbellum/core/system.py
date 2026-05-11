"""System command execution utilities."""

import enum
import os
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path


class RunMode(enum.Enum):
    SILENT = "silent"
    LOG = "log"
    STREAM = "stream"


def run_command(
    mode: RunMode,
    args: list[str],
    log_path: str = "",
    on_line: Callable[[str], None] | None = None,
    timeout: int = 3600,
) -> int:
    """Execute a command. Returns exit code or -1 on timeout/error."""
    if not args:
        return 0

    kwargs: dict = {}

    if log_path and mode == RunMode.SILENT:
        log_file = open(log_path, "a")
        kwargs["stdout"] = log_file
        kwargs["stderr"] = log_file
    elif log_path and mode == RunMode.STREAM:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
    elif mode == RunMode.SILENT:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL

    try:
        if mode == RunMode.STREAM and kwargs.get("stdout") == subprocess.PIPE:
            proc = subprocess.Popen(args, **kwargs, text=True, bufsize=1)

            def _stream():
                assert proc.stdout is not None
                for line in proc.stdout:
                    line = line.rstrip("\n")
                    if on_line:
                        on_line(line)
                    else:
                        print(line)
                    if log_path:
                        with open(log_path, "a") as lf:
                            lf.write(line + "\n")

            t = threading.Thread(target=_stream, daemon=True)
            t.start()
            proc.wait(timeout=timeout)
            t.join(timeout=5)
            return proc.returncode
        else:
            result = subprocess.run(args, timeout=timeout, **kwargs)
            return result.returncode
    except subprocess.TimeoutExpired:
        return -1
    finally:
        if log_path and mode == RunMode.SILENT and "log_file" in dir():
            log_file.close()


def run_command_with_output(args: list[str], timeout: int = 300) -> tuple[str, int | None]:
    """Execute and capture output. Returns (stdout, exit_code)."""
    if not args:
        return "", 0
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.returncode
    except FileNotFoundError:
        return f"Command not found: {args[0]}", -1
    except subprocess.TimeoutExpired:
        return "Command timed out", -1


def look_path(name: str) -> str:
    """Check PATH. Returns resolved path or empty string."""
    try:
        path = subprocess.check_output(["which", name], stderr=subprocess.DEVNULL, text=True)
        return path.strip()
    except subprocess.CalledProcessError:
        return ""


def is_dir(path: str) -> bool:
    return Path(path).is_dir()


def is_writable(path: str) -> bool:
    test_file = Path(path) / f".write_test_{os.getpid()}"
    try:
        test_file.touch()
        test_file.unlink()
        return True
    except (OSError, PermissionError):
        return False


def ask_bool(prompt: str, silent: bool = False) -> bool:
    """Prompt y/n. Empty = yes. Silent = auto-yes."""
    if silent:
        return True
    try:
        answer = input(prompt).strip().lower()
        if answer in ("", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Invalid input. Enter y/yes or n/no.")
        return ask_bool(prompt, silent)
    except (KeyboardInterrupt, EOFError):
        return False
