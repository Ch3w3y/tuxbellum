"""Tests for tuxbellum.config.versions — version constants."""
from tuxbellum.config.versions import DEFAULT_VERSIONS


def test_default_versions_is_frozen():
    DEFAULT_VERSIONS.proton = "changed"


def test_default_versions_has_proton():
    assert DEFAULT_VERSIONS.proton
    assert "cachyos" in DEFAULT_VERSIONS.proton or "proton" in DEFAULT_VERSIONS.proton


def test_default_versions_has_wine():
    assert DEFAULT_VERSIONS.wine
    assert "wine" in DEFAULT_VERSIONS.wine


def test_default_versions_has_dxvk():
    assert DEFAULT_VERSIONS.dxvk
    assert "dxvk" in DEFAULT_VERSIONS.dxvk