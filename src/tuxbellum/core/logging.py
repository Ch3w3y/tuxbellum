"""Structured colored logging for the Bellum Linux Installer."""

from pathlib import Path
from typing import TextIO


class Color:
    BOLD = "\033[1m"
    RED = "\033[31m"
    BOLD_RED = "\033[1;31m"
    YELLOW = "\033[33m"
    BOLD_YELLOW = "\033[1;33m"
    GREEN = "\033[32m"
    BOLD_GREEN = "\033[1;32m"
    BLUE = "\033[34m"
    BOLD_BLUE = "\033[1;34m"
    CYAN = "\033[36m"
    BOLD_CYAN = "\033[1;36m"
    GRAY_BOLD = "\033[90m"
    RESET = "\033[0m"


class Logger:
    def __init__(self, log_path: str = ""):
        self.log_file: TextIO | None = None
        if log_path:
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            self.log_file = open(log_path, "a", encoding="utf-8")

    def close(self) -> None:
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    def info(self, msg: str) -> None:
        self._log("INFO", msg)

    def warn(self, msg: str) -> None:
        self._log("WARN", msg)

    def error(self, msg: str) -> None:
        self._log("ERROR", msg)

    def command(self, msg: str) -> None:
        self._log("CMD", msg)

    def _log(self, level: str, msg: str) -> None:
        if not msg:
            return

        level_colors = {
            "ERROR": f"{Color.BOLD_RED}[ERROR]{Color.RESET}",
            "WARN": f"{Color.BOLD_YELLOW}[WARN]{Color.RESET}",
            "INFO": f"{Color.BOLD_BLUE}[INFO]{Color.RESET}",
            "CMD": f"{Color.BOLD_BLUE}[CMD]{Color.RESET}",
        }
        prefix = level_colors.get(level, "")
        base = f"{Color.GRAY_BOLD}[TuxBellum]{Color.RESET}:{prefix}"
        indent = " " * (len("[TuxBellum]:") + len(f"[{level}]"))

        for i, line in enumerate(self._split_lines(msg, 125)):
            p = base if i == 0 else indent
            out = f"{p}  {line}"
            print(out)
            if self.log_file:
                self.log_file.write(out + "\n")
                self.log_file.flush()

    @staticmethod
    def _split_lines(s: str, max_len: int) -> list[str]:
        if len(s) <= max_len:
            return [s]
        lines: list[str] = []
        start = 0
        while start < len(s):
            end = min(start + max_len, len(s))
            if end >= len(s):
                lines.append(s[start:])
                break
            space = s.rfind(" ", start, end)
            if space == -1 or space <= start:
                lines.append(s[start:end])
                start = end
            else:
                lines.append(s[start:space])
                start = space + 1
        return lines


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Color.RESET}"
