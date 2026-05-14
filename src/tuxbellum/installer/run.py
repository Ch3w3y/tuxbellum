"""Installation orchestrator — drives the step-based engine."""

import os
from dataclasses import dataclass
from pathlib import Path

from tuxbellum.core.logging import Logger
from tuxbellum.engine.context import InstallContext
from tuxbellum.engine.executor import run_plan
from tuxbellum.engine.planner import build_install_plan
from tuxbellum.installer.launcher import download_launcher_installer


@dataclass
class InstallConfig:
    wineprefix: str = ""
    proton_path: str = ""
    gpu_type: str = ""
    is_amd_gpu: bool = False
    launcher_installer: str = ""
    resource_root: str = ""
    cache_dir: str = ""
    is_fsr41: bool = False


def run_installation(config: InstallConfig, logger: Logger) -> None:
    """Execute the full Bellum installation pipeline via the step engine."""
    original_env = os.environ.copy()
    try:
        os.environ["PROTONPATH"] = config.proton_path
        os.environ["WINEPREFIX"] = config.wineprefix
        os.environ["WINEARCH"] = "win64"
        os.environ["STEAM_APP_PATH"] = config.wineprefix
        os.environ["STEAM_APPID"] = "1"
        os.environ["STEAM_COMPAT_DATA_PATH"] = config.wineprefix
        os.environ["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.join(
            os.environ.get("HOME", str(Path.home())),
            ".steam",
            "steam",
        )
        os.environ["GAMEID"] = "1"

        logger.info("Starting Installation")
        print()

        # Build context
        ctx = InstallContext(
            wineprefix=config.wineprefix,
            resource_root=config.resource_root,
            cache_dir=config.cache_dir,
            gpu_type=config.gpu_type,
            is_amd_gpu=config.is_amd_gpu,
            is_fsr41=config.is_fsr41,
            proton_path=config.proton_path,
            launcher_exe=config.launcher_installer,
            logger=logger,
        )

        # Download launcher if not already provided
        if not config.launcher_installer:
            state = download_launcher_installer(config.cache_dir, logger)
            ctx.launcher_exe = state.installer_path
            ctx.put("launcher_state", state)

        # Execute the plan
        plan = build_install_plan()
        results = run_plan(plan, ctx)

        # Report results
        for r in results:
            if r.failed:
                logger.info(f"[FAIL] {r.name}: {r.message}")
                # Re-raise the last error so the GUI can catch it
                raise r.error or RuntimeError(r.message)
            else:
                logger.info(f"[OK] {r.name}")

    finally:
        os.environ.clear()
        os.environ.update(original_env)
