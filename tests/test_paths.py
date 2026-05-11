"""Tests for tuxbellum.config.paths — XDG path management."""
import os
from pathlib import Path
from unittest.mock import patch

from tuxbellum.config.paths import PathManager


def test_path_manager_creates_dirs(tmp_path):
    with patch.dict(os.environ, {"HOME": str(tmp_path), "XDG_DATA_HOME": ""}):
        pm = PathManager()
        assert pm.data_dir.exists()


def test_path_manager_wineprefix_default(tmp_path):
    with patch.dict(os.environ, {"HOME": str(tmp_path), "XDG_DATA_HOME": ""}):
        pm = PathManager()
        assert "wineprefix" in str(pm.wineprefix).lower() or pm.wineprefix.suffix == ""


def test_path_manager_flatpak_mode(tmp_path):
    with patch.dict(
        os.environ,
        {"HOME": str(tmp_path), "XDG_DATA_HOME": "", "FLATPAK_ID": "io.github.ch3w3y.tuxbellum"},
    ):
        pm = PathManager()
        assert pm.is_flatpak