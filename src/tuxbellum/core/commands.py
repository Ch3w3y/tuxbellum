"""
Structured command execution — explicit, testable, diagnosable.

Replaces the legacy `core/system.py:run_command()` with intent-revealing
helpers that make failure handling explicit at every call site.

Usage
-----

Required success — raises on any failure:
    result = run_checked(["tar", "-xzf", archive, "-C", tmp])

Allowed failure — caller inspects exit_code:
    result = run_allowed_failure(["wineboot", "--end-session"])
    if result.exit_code != 0:
        logger.warn(f"wineboot cleanup returned {result.exit_code}")

Streaming output — callback receives each line:
    exit_code = run_streaming(["proton", "run", launcher], on_line=logger.info)

Capture output — caller needs stdout/stderr:
    result = run_capture(["wine", "--version"])
    version = result.stdout.strip()
"""

from __future__ import annotations

import subprocess
import threading
from collections.abc import Callable
from dataclasses import dataclass

# ── Data types ───────────────────────────────────────────────────────────────


@dataclass
class CommandResult:
    """Outcome of a completed or timed-out command."""

    args: list[str]
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        """True when the command succeeded (exit_code == 0 and not timed out)."""
        return self.exit_code == 0 and not self.timed_out


class CommandError(RuntimeError):
    """Raised by `run_checked` when a command fails or times out."""

    def __init__(self, result: CommandResult, label: str = "") -> None:
        self.result = result
        self.label = label
        reason = "timed out" if result.timed_out else f"exit code {result.exit_code}"
        if label:
            msg = f"{label} failed ({reason}): {' '.join(result.args)}"
        else:
            msg = f"Command failed ({reason}): {' '.join(result.args)}"
        if result.stderr:
            msg += f"\nstderr: {result.stderr[-500:]}"
        super().__init__(msg)


# ── Execution helpers ────────────────────────────────────────────────────────


def run_checked(
    args: list[str],
    *,
    label: str = "",
    timeout: int = 3600,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    stdin: str | None = None,
) -> CommandResult:
    """
    Run a command that **must** succeed.  Raises `CommandError` on failure.

    Returns the `CommandResult` with captured stdout/stderr so callers
    can inspect output after a successful run.

    `label` provides human-readable context in the error message
    (e.g. `"DXVK extraction"` instead of the raw command).
    """
    result = _run(args, timeout=timeout, cwd=cwd, env=env, stdin=stdin, capture=True)
    if not result.ok:
        raise CommandError(result, label=label)
    return result


def run_allowed_failure(
    args: list[str],
    *,
    timeout: int = 3600,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    """
    Run a command whose failure is acceptable.  Never raises.

    Callers inspect `result.ok` or `result.exit_code` to decide.
    Useful for cleanup, best-effort operations, and post-mortem diagnostics.
    """
    return _run(args, timeout=timeout, cwd=cwd, env=env, stdin=None, capture=True)


def run_capture(
    args: list[str],
    *,
    timeout: int = 300,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    stdin: str | None = None,
) -> CommandResult:
    """
    Run and capture stdout/stderr.  Caller decides how to handle exit codes.

    Useful for commands like `wine --version` where the output
    is more important than the exit code.
    """
    return _run(args, timeout=timeout, cwd=cwd, env=env, stdin=stdin, capture=True)


def run_streaming(
    args: list[str],
    *,
    on_line: Callable[[str], None] | None = None,
    timeout: int = 3600,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    log_path: str = "",
) -> int:
    """
    Run a command, streaming stdout line-by-line via `on_line`.

    Returns the exit code (or -1 on timeout).  Suitable for long-running
    interactive commands like `proton run <launcher>`.
    """
    if not args:
        return 0

    if log_path:
        log_file = open(log_path, "a")

    try:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=cwd,
            env=env,
        )

        assert proc.stdout is not None

        def _stream() -> None:
            for line in proc.stdout:  # type: ignore[union-attr]
                stripped = line.rstrip("\n")
                if on_line:
                    on_line(stripped)
                else:
                    print(stripped)
                if log_path:
                    log_file.write(stripped + "\n")

        t = threading.Thread(target=_stream, daemon=True)
        t.start()

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            return -1
        finally:
            t.join(timeout=5)

        return proc.returncode

    except FileNotFoundError:
        return -1
    finally:
        if log_path:
            log_file.close()


# ── Internal ─────────────────────────────────────────────────────────────────


def _run(
    args: list[str],
    *,
    timeout: int,
    cwd: str | None,
    env: dict[str, str] | None,
    stdin: str | None,
    capture: bool,
) -> CommandResult:
    """Shared implementation for `run_checked`, `run_allowed_failure`, and `run_capture`."""
    if not args:
        return CommandResult(args=args, exit_code=0)

    kwargs: dict = {}
    if cwd is not None:
        kwargs["cwd"] = cwd
    if env is not None:
        kwargs["env"] = env
    if stdin is not None:
        kwargs["input"] = stdin

    try:
        if capture:
            proc = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
                **kwargs,
            )
            return CommandResult(
                args=args,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )
        else:
            proc = subprocess.run(args, timeout=timeout, **kwargs)
            return CommandResult(args=args, exit_code=proc.returncode)

    except subprocess.TimeoutExpired:
        return CommandResult(args=args, exit_code=-1, timed_out=True)
    except FileNotFoundError:
        return CommandResult(
            args=args,
            exit_code=-1,
            stderr=f"Command not found: {args[0]}",
        )
