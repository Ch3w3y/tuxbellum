"""Tests for tuxbellum.config.versions."""

from dataclasses import FrozenInstanceError

import pytest

from tuxbellum.config.versions import DEFAULT_VERSIONS


def test_default_versions_is_frozen():
    with pytest.raises(FrozenInstanceError):
        DEFAULT_VERSIONS.proton_ver = "changed"


def test_default_versions_has_proton():
    assert DEFAULT_VERSIONS.proton_ver
    assert "proton" in DEFAULT_VERSIONS.proton_ver


def test_default_versions_has_wine():
    assert DEFAULT_VERSIONS.wine_ver
    assert "wine" in DEFAULT_VERSIONS.wine_ver


def test_default_versions_has_dxvk():
    assert DEFAULT_VERSIONS.dxvk_ver
    assert DEFAULT_VERSIONS.dxvk_ver[0].isdigit()
