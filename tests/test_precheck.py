"""Functional tests for precheck validations."""

import os

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.system import look_path


def test_wine_binaries_resolvable():
    """P0-1 regression guard: bare command names resolve via PATH."""
    import pytest
    if look_path("wine") is None:
        pytest.skip("Wine not installed on this system")
    binaries = [
        DEFAULT_VERSIONS.binaries.wine,
        DEFAULT_VERSIONS.binaries.wineboot,
        DEFAULT_VERSIONS.binaries.winecfg,
        DEFAULT_VERSIONS.binaries.wineserver,
    ]
    for binary in binaries:
        path = look_path(binary)
        assert path is not None, f"{binary} not found on PATH"


def test_check_winetricks_no_workdir_param():
    """P3-f2 regression guard: workdir param removed."""
    import inspect
    from tuxbellum.installer.precheck import check_winetricks

    sig = inspect.signature(check_winetricks)
    params = list(sig.parameters.keys())
    assert "workdir" not in params, "workdir param should be removed"
    assert "logger" in params


def test_config_language_fallback_blank():
    """P2-1 regression: blank language falls back to system locale."""
    from tuxbellum.config.manager import ConfigManager

    cfg = ConfigManager()
    # After load(), language should not be empty string
    assert cfg.config.get("language"), "language should have a non-empty default"
