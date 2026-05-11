"""DXVK installation — AMD GPU only."""

import os
import shutil
import tempfile

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.logging import Logger
from tuxbellum.core.system import RunMode, run_command


def install_dxvk(gpu_type: str, workdir: str, logger: Logger) -> None:
    """Install DXVK into the current WINEPREFIX.  No-op for non-AMD GPUs."""
    gpu_lower = gpu_type.lower()
    if "amd" not in gpu_lower and "radeon" not in gpu_lower:
        logger.info(f"Skipping DXVK installation for non-AMD GPU: {gpu_type}")
        return

    archive = os.path.join(workdir, "packages", f"dxvk-{DEFAULT_VERSIONS.dxvk_ver}.tar.gz")
    if not os.path.isfile(archive):
        raise RuntimeError(f"DXVK archive not found: {archive}")

    logger.info("Installing DXVK...")
    tmp = tempfile.mkdtemp(prefix="dxvk.")

    try:
        # Extract
        run_command(
            RunMode.SILENT,
            ["tar", "-xzf", archive, "-C", tmp],
        )

        # Locate dxvk_setup.sh — may be inside a subdirectory
        install_dir = tmp
        if not os.path.isfile(os.path.join(install_dir, "dxvk_setup.sh")):
            try:
                entries = os.listdir(tmp)
            except OSError:
                entries = []
            for entry in entries:
                candidate = os.path.join(tmp, entry)
                if os.path.isdir(candidate) and os.path.isfile(
                    os.path.join(candidate, "dxvk_setup.sh")
                ):
                    install_dir = candidate
                    break

        setup = os.path.join(install_dir, "dxvk_setup.sh")
        if not os.path.isfile(setup):
            raise RuntimeError("DXVK setup script not found after extraction")

        run_command(
            RunMode.SILENT,
            [setup, "install"],
        )

        # Copy dxvk.conf
        wineprefix = os.environ.get("WINEPREFIX", "")
        if not wineprefix:
            raise RuntimeError("WINEPREFIX not set")
        conf_src = os.path.join(install_dir, "dxvk.conf")
        conf_dst = os.path.join(wineprefix, "dxvk.conf")
        shutil.copy2(conf_src, conf_dst)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    logger.info("[OK] DXVK installed")
