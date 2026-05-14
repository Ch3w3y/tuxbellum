"""
Install state — discovery, loading, saving, and validation of install manifests.

Provides the API used by the GUI and uninstaller to answer:
- Is Bellum installed in this prefix?
- What did TuxBellum install there?
- Can we clean it up?
"""

from __future__ import annotations

import os

from tuxbellum.domain.install_manifest import (
    CURRENT_SCHEMA_VERSION,
    InstallManifest,
    manifest_exists,
    manifest_path,
)


class StateError(RuntimeError):
    """Raised when manifest operations fail (corrupt, missing, schema mismatch)."""


def discover_manifest(wineprefix: str) -> InstallManifest | None:
    """
    Find and load the manifest from a WINEPREFIX.

    Returns None when no manifest exists (prefix was not created by TuxBellum,
    or the install was done with a pre-v4 version).
    """
    if not manifest_exists(wineprefix):
        return None

    path = manifest_path(wineprefix)
    try:
        with open(path) as f:
            manifest = InstallManifest.from_json(f.read())
    except (OSError, ValueError) as exc:
        raise StateError(f"Failed to load manifest from {path}: {exc}") from exc

    _validate(manifest)
    return manifest


def save_manifest(manifest: InstallManifest, wineprefix: str) -> None:
    """Persist the manifest inside the managed WINEPREFIX."""
    os.makedirs(wineprefix, exist_ok=True)
    path = manifest_path(wineprefix)
    try:
        with open(path, "w") as f:
            f.write(manifest.to_json())
    except OSError as exc:
        raise StateError(f"Failed to write manifest to {path}: {exc}") from exc


def delete_manifest(wineprefix: str) -> bool:
    """Remove the manifest from a prefix.  Returns True if one was deleted."""
    path = manifest_path(wineprefix)
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


def _validate(manifest: InstallManifest) -> None:
    """Validate a loaded manifest for consistency."""
    if manifest.schema_version > CURRENT_SCHEMA_VERSION:
        raise StateError(
            f"Manifest schema version {manifest.schema_version} is newer than "
            f"this TuxBellum version supports ({CURRENT_SCHEMA_VERSION}). "
            "Upgrade TuxBellum to manage this installation."
        )

    if not manifest.wineprefix:
        raise StateError("Manifest is missing wineprefix")

    # Future schema migrations would go here, keyed on schema_version
