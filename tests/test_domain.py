"""Tests for tuxbellum.domain — manifest, options, and state management."""

import json
import os
from unittest.mock import patch

from tuxbellum.domain.install_manifest import (
    CURRENT_SCHEMA_VERSION,
    InstallManifest,
    manifest_exists,
    manifest_path,
)
from tuxbellum.domain.install_options import InstallOptions
from tuxbellum.domain.install_state import (
    StateError,
    delete_manifest,
    discover_manifest,
    save_manifest,
)


# ── InstallManifest ──────────────────────────────────────────────────────────


class TestInstallManifest:
    def test_now_sets_installed_at(self):
        m = InstallManifest.now(wineprefix="/tmp/prefix")
        assert m.installed_at
        assert "T" in m.installed_at  # ISO 8601
        assert m.wineprefix == "/tmp/prefix"
        assert m.schema_version == CURRENT_SCHEMA_VERSION

    def test_round_trip_json(self):
        m = InstallManifest.now(
            tuxbellum_version="4.0.3",
            wineprefix="/tmp/pfx",
            proton_version="proton-cachyos-10.0",
            proton_path="/tmp/proton",
            gpu_type="AMD Radeon",
            is_amd_gpu=True,
            dxvk_version="2.7.1",
            dxvk_source="bundled",
            fsr_enabled=True,
            launcher_path="/home/user/.local/bin/Bellum",
            desktop_entry_path="/home/user/.local/share/applications/Bellum.desktop",
            icon_path="/home/user/.local/share/icons/bellum.png",
            registry_edits=["d3d11=native", "dxgi=native"],
            owned_files=["/tmp/pfx/dxvk.conf"],
            owned_directories=["/tmp/pfx"],
            launch_options={"gamemode": True, "hdr": False},
        )

        json_str = m.to_json()
        restored = InstallManifest.from_json(json_str)

        assert restored.wineprefix == m.wineprefix
        assert restored.proton_version == m.proton_version
        assert restored.gpu_type == m.gpu_type
        assert restored.is_amd_gpu is True
        assert restored.fsr_enabled is True
        assert restored.launcher_path == m.launcher_path
        assert restored.registry_edits == m.registry_edits
        assert restored.owned_files == m.owned_files
        assert restored.launch_options == {"gamemode": True, "hdr": False}
        assert restored.schema_version == CURRENT_SCHEMA_VERSION

    def test_from_dict_ignores_unknown_fields(self):
        """Forward-compat: extra fields in JSON are silently dropped."""
        data = {
            "schema_version": 1,
            "wineprefix": "/tmp/pfx",
            "future_field": "should be ignored",
            "another_new_thing": 42,
        }
        m = InstallManifest.from_dict(data)
        assert m.wineprefix == "/tmp/pfx"
        assert not hasattr(m, "future_field")

    def test_defaults_are_sensible(self):
        m = InstallManifest()
        assert m.schema_version == CURRENT_SCHEMA_VERSION
        assert m.wineprefix == ""
        assert m.registry_edits == []
        assert m.owned_files == []
        assert m.owned_directories == []
        assert m.launch_options == {}


# ── InstallOptions ───────────────────────────────────────────────────────────


class TestInstallOptions:
    def test_defaults(self):
        opts = InstallOptions()
        assert opts.wineprefix == ""
        assert opts.is_fsr41 is False
        assert opts.gamescope is False

    def test_partial_construction(self):
        opts = InstallOptions(wineprefix="/tmp/pfx", is_fsr41=True)
        assert opts.wineprefix == "/tmp/pfx"
        assert opts.is_fsr41 is True
        assert opts.gamescope is False


# ── manifest_path / manifest_exists ──────────────────────────────────────────


class TestManifestPath:
    def test_returns_expected_path(self):
        assert manifest_path("/tmp/pfx") == "/tmp/pfx/tuxbellum_manifest.json"

    def test_exists_detects_file(self, tmp_path):
        pfx = tmp_path / "pfx"
        pfx.mkdir()
        (pfx / "tuxbellum_manifest.json").write_text("{}")
        assert manifest_exists(str(pfx)) is True

    def test_exists_missing(self, tmp_path):
        pfx = tmp_path / "empty"
        pfx.mkdir()
        assert manifest_exists(str(pfx)) is False


# ── install_state ────────────────────────────────────────────────────────────


class TestInstallState:
    def test_save_and_discover(self, tmp_path):
        pfx = str(tmp_path / "pfx")
        os.makedirs(pfx)

        m = InstallManifest.now(
            wineprefix=pfx,
            tuxbellum_version="4.0.3",
            proton_version="test-proton",
        )
        save_manifest(m, pfx)

        discovered = discover_manifest(pfx)
        assert discovered is not None
        assert discovered.wineprefix == pfx
        assert discovered.proton_version == "test-proton"

    def test_discover_returns_none_when_missing(self, tmp_path):
        pfx = str(tmp_path / "empty")
        os.makedirs(pfx)
        assert discover_manifest(pfx) is None

    def test_discover_raises_on_corrupt_json(self, tmp_path):
        pfx = str(tmp_path / "pfx")
        os.makedirs(pfx)
        (tmp_path / "pfx" / "tuxbellum_manifest.json").write_text("not json")

        with patch("tuxbellum.domain.install_state.manifest_exists", return_value=True):
            import pytest

            with pytest.raises(StateError, match="Failed to load manifest"):
                discover_manifest(pfx)

    def test_schema_too_new_raises(self, tmp_path):
        pfx = str(tmp_path / "pfx")
        os.makedirs(pfx)

        m = InstallManifest(
            schema_version=999,  # far future
            wineprefix=pfx,
        )
        save_manifest(m, pfx)

        import pytest

        with pytest.raises(StateError, match="schema version 999 is newer"):
            discover_manifest(pfx)

    def test_delete_manifest(self, tmp_path):
        pfx = str(tmp_path / "pfx")
        os.makedirs(pfx)
        m = InstallManifest.now(wineprefix=pfx)
        save_manifest(m, pfx)
        assert manifest_exists(pfx)

        assert delete_manifest(pfx) is True
        assert not manifest_exists(pfx)

    def test_delete_manifest_missing(self, tmp_path):
        pfx = str(tmp_path / "empty")
        os.makedirs(pfx)
        assert delete_manifest(pfx) is False

    def test_manifest_missing_wineprefix_raises(self, tmp_path):
        pfx = str(tmp_path / "pfx")
        os.makedirs(pfx)

        m = InstallManifest(wineprefix="")  # empty
        save_manifest(m, pfx)

        import pytest

        with pytest.raises(StateError, match="missing wineprefix"):
            discover_manifest(pfx)
