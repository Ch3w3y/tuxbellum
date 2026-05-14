"""Tests for rootless launcher changes — user-local bin, no pkexec."""

import os

from tuxbellum.config.paths import PathManager


class TestUserLocalBin:
    def test_returns_expected_path(self):
        result = PathManager.user_local_bin()
        assert result.endswith(".local/bin")
        assert result.startswith("/")

    def test_path_is_under_home(self):
        result = PathManager.user_local_bin()
        home = os.path.expanduser("~")
        assert result.startswith(home)
