"""Validate host — GPU detection and preflight checks."""

from tuxbellum.core.gpu import detect_gpu
from tuxbellum.engine.context import InstallContext
from tuxbellum.installer.precheck import run_prechecks


def step(ctx: InstallContext) -> None:
    """Detect GPU and run all system prechecks."""
    if ctx.logger:
        ctx.logger.info("Detecting GPU...")

    gpu_type, _ = detect_gpu()
    if not gpu_type:
        gpu_type = "Unknown"

    # Derive is_amd_gpu from detection if not already set
    gpu_lower = gpu_type.lower()
    if not ctx.is_amd_gpu:
        ctx.is_amd_gpu = "amd" in gpu_lower or "radeon" in gpu_lower

    ctx.gpu_type = gpu_type

    if ctx.logger:
        ctx.logger.info(f"GPU: {gpu_type}")

    # Run prechecks (wine, winetricks, umu, proton, etc.)
    if ctx.logger:
        ctx.logger.info("Running prechecks...")

    result = run_prechecks(
        ctx.wineprefix,
        "",
        False,
        ctx.is_fsr41,
        ctx.resource_root,
        ctx.logger,
    )

    # Pull resolved values from precheck result
    ctx.wineprefix = result.wineprefix
    ctx.proton_path = result.proton_path
    ctx.proton_version = result.proton_ver
    ctx.gpu_type = result.gpu_type
    ctx.is_amd_gpu = result.is_amd_gpu
    ctx.launcher_exe = result.launcher_installer
