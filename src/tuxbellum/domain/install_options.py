"""
Install options — user choices captured at install time.

These are the decisions the user makes in the Install dialog before
the pipeline starts.  They feed into `InstallConfig` and eventually
into `InstallManifest.launch_options`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InstallOptions:
    """User-facing install choices."""

    wineprefix: str = ""
    is_fsr41: bool = False
    gamescope: bool = False
    gamemode: bool = False
    hdr: bool = False
    nvapi: bool = False
