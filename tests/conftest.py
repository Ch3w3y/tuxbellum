"""Shared pytest fixtures for TuxBellum tests."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch

import pytest

from tuxbellum.core.logging import Logger
from tuxbellum.domain.install_manifest import InstallManifest


# ── Logger fixture ───────────────────────────────────────────────────────────


@pytest.fixture
def mock_logger() -> MagicMock:
    """A MagicMock standing in for tuxbellum.core.logging.Logger."""
    return MagicMock(spec=Logger)


# ── Temp WINEPREFIX fixture ──────────────────────────────────────────────────


@pytest.fixture
def tmp_wineprefix(tmp_path) -> str:
    """A temporary directory mimicking a WINEPREFIX."""
    pfx = tmp_path / "wineprefix"
    pfx.mkdir()
    (pfx / "drive_c").mkdir()
    return str(pfx)


# ── Mock command execution ───────────────────────────────────────────────────


@dataclass
class FakeCommandResult:
    """Configurable fake for CommandResult returned by mocked run_checked etc."""

    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    args: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


@pytest.fixture
def mock_run_checked():
    """Patch run_checked to return FakeCommandResult(exit_code=0)."""
    with patch("tuxbellum.core.commands.run_checked") as mock:
        mock.return_value = FakeCommandResult()
        yield mock


@pytest.fixture
def mock_run_checked_success():
    """run_checked returns exit_code=0."""
    with patch("tuxbellum.core.commands.run_checked") as mock:
        mock.return_value = FakeCommandResult(exit_code=0, stdout="ok")
        yield mock


@pytest.fixture
def mock_run_checked_failure():
    """run_checked returns exit_code=1."""
    with patch("tuxbellum.core.commands.run_checked") as mock:
        mock.return_value = FakeCommandResult(exit_code=1, stderr="failed")
        yield mock


# ── Config file helpers ──────────────────────────────────────────────────────


@pytest.fixture
def temp_config_dir(tmp_path) -> str:
    """A temporary XDG_CONFIG_HOME pointing at tmp_path."""
    config = tmp_path / "config"
    config.mkdir()
    with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(config)}, clear=False):
        yield str(config)


# ── Install manifest fixture ─────────────────────────────────────────────────


@pytest.fixture
def sample_manifest(tmp_wineprefix) -> InstallManifest:
    """A fully populated InstallManifest for testing."""
    return InstallManifest.now(
        tuxbellum_version="4.0.4",
        wineprefix=tmp_wineprefix,
        proton_version="proton-cachyos-10.0",
        proton_path="/tmp/proton",
        gpu_type="AMD Radeon",
        is_amd_gpu=True,
        dxvk_version="2.7.1",
        dxvk_source="bundled",
        fsr_enabled=True,
        launcher_path=f"{tmp_wineprefix}/.local/bin/Bellum",
        desktop_entry_path=f"{tmp_wineprefix}/.local/share/applications/Bellum.desktop",
        icon_path=f"{tmp_wineprefix}/.local/share/icons/bellum.png",
        registry_edits=["d3d11=native"],
        owned_files=["/tmp/test.conf"],
        owned_directories=["/tmp/test_prefix"],
        launch_options={"gamemode": True, "hdr": False},
    )
