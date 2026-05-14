"""
Install manifest — versioned record of what TuxBellum installed into a WINEPREFIX.

Stored as JSON inside the managed prefix: ``<WINEPREFIX>/tuxbellum_manifest.json``.

Schema versioning enables forward-compatible migration when the manifest format
changes across TuxBellum releases.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

MANIFEST_FILENAME = "tuxbellum_manifest.json"
CURRENT_SCHEMA_VERSION = 1


@dataclass
class InstallManifest:
    """Complete record of a TuxBellum-managed Bellum installation."""

    # ── Identity ─────────────────────────────────────────────────────────
    schema_version: int = CURRENT_SCHEMA_VERSION
    tuxbellum_version: str = ""
    installed_at: str = ""  # ISO 8601

    # ── Core paths ───────────────────────────────────────────────────────
    wineprefix: str = ""
    proton_version: str = ""
    proton_path: str = ""

    # ── GPU and rendering ────────────────────────────────────────────────
    gpu_type: str = ""
    is_amd_gpu: bool = False
    dxvk_version: str = ""
    dxvk_source: str = ""  # "bundled" or "downloaded"
    fsr_enabled: bool = False

    # ── Generated artifacts ──────────────────────────────────────────────
    launcher_path: str = ""
    desktop_entry_path: str = ""  # ~/.local/share/applications/Bellum.desktop
    desktop_shortcut_path: str = ""  # ~/Desktop/Bellum.desktop
    appmenu_entry_path: str = ""  # same as desktop_entry_path on most desktops
    icon_path: str = ""

    # ── Registry edits applied ───────────────────────────────────────────
    registry_edits: list[str] = field(default_factory=list)

    # ── Owned files and directories (for clean uninstall) ────────────────
    owned_files: list[str] = field(default_factory=list)
    owned_directories: list[str] = field(default_factory=list)

    # ── Launch options (from settings) ───────────────────────────────────
    launch_options: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def now(cls, **overrides: Any) -> InstallManifest:
        """Create a manifest with ``installed_at`` set to the current UTC time."""
        return cls(installed_at=datetime.now(UTC).isoformat(), **overrides)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InstallManifest:
        # Only pass fields the dataclass knows about (forward-compat)
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, text: str) -> InstallManifest:
        return cls.from_dict(json.loads(text))


def manifest_path(wineprefix: str) -> str:
    """Return the canonical manifest path inside a WINEPREFIX."""
    return os.path.join(wineprefix, MANIFEST_FILENAME)


def manifest_exists(wineprefix: str) -> bool:
    """Check whether a manifest exists in the given prefix."""
    return os.path.isfile(manifest_path(wineprefix))
