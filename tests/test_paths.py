"""Tests for tuxbellum.config.paths."""

import os
from pathlib import Path
from unittest.mock import patch

from tuxbellum.config.paths import PathManager


def test_app_data_root_prefers_appdir(tmp_path):
    appdir = tmp_path / "AppDir"
    bundled = appdir / "usr" / "share" / "tuxbellum"
    bundled.mkdir(parents=True)
    (bundled / "packages").mkdir()

    with patch.dict(os.environ, {"APPDIR": str(appdir)}, clear=False):
        assert PathManager.app_data_root() == str(bundled)


def test_user_paths_respect_xdg(tmp_path):
    env = {
        "HOME": str(tmp_path),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
    }
    with patch.dict(os.environ, env, clear=False):
        assert PathManager.user_data("icons") == str(tmp_path / "data" / "icons")
        assert PathManager.user_config("tuxbellum") == str(tmp_path / "config" / "tuxbellum")
        assert PathManager.user_cache("tuxbellum") == str(tmp_path / "cache" / "tuxbellum")


def test_bundled_path_joins_data_root():
    root = PathManager.app_data_root()
    assert Path(PathManager.bundled_path("packages")).is_absolute()
    assert str(Path(root) / "packages") == PathManager.bundled_path("packages")
