"""
InstallContext — shared mutable state for an install run.

All step functions receive a single InstallContext and mutate it as they
progress through the pipeline.  This decouples steps from each other and
eliminates the need for a long parameter list.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tuxbellum.core.logging import Logger


@dataclass
class InstallContext:
    """Mutable state for a TuxBellum install run."""

    # ── User-provided ────────────────────────────────────────────────────
    wineprefix: str = ""
    resource_root: str = ""
    cache_dir: str = ""
    gpu_type: str = ""
    is_amd_gpu: bool = False
    is_fsr41: bool = False

    # ── Resolved during run ──────────────────────────────────────────────
    proton_version: str = ""
    proton_path: str = ""
    launcher_exe: str = ""

    # ── Logger ───────────────────────────────────────────────────────────
    logger: Logger | None = None

    # ── Opaque state (launcher installer cleanup handle, etc.) ───────────
    _state: dict[str, Any] = field(default_factory=dict)

    def put(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def pop(self, key: str, default: Any = None) -> Any:
        return self._state.pop(key, default)
