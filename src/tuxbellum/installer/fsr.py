"""FSR 4.1 upgrade — DLL copy and post-install plugin registration."""

import os
import shutil

from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.logging import Logger
from tuxbellum.core.system import RunMode, run_command


def copy_fsr41_upgrade_dll(workdir: str, logger: Logger) -> None:
    """Copy amdxcffx64.dll into protonfixes upscalers cache."""
    fs_path = os.path.join(workdir, "packages", "fsr4")
    source = os.path.join(fs_path, "amdxcffx64.dll")
    if not os.path.isfile(source):
        logger.warn(f"FSR 4.1 DLL not found: {source}")
        return

    home = os.environ.get("HOME", os.path.expanduser("~"))
    target_dir = os.path.join(home, ".cache", "protonfixes", "upscalers")
    os.makedirs(target_dir, exist_ok=True)

    target = os.path.join(target_dir, "amdxcffx64_v4.1.0_69A0952A304a000.dll")
    shutil.copy2(source, target)
    logger.info(f"[OK] Copied FSR 4.1.0 DLL to {target}")


def upgrade_fsr(
    wineprefix: str,
    workdir: str,
    gpu_type: str,
    logger: Logger,
) -> None:
    """Copy FSR DLLs into the game WINEPREFIX plugins and register override."""
    gpu_lower = gpu_type.lower()
    if "amd" not in gpu_lower and "radeon" not in gpu_lower:
        return

    fs_path = os.path.join(workdir, "packages", "fsr4")
    if not os.path.isdir(fs_path):
        logger.warn(f"FSR 4.1.0 directory not found: {fs_path}, skipping upgrade")
        return

    logger.info("Upgrading to FSR 4.1.0")

    fg_dll = "amd_fidelityfx_framegeneration_dx12.dll"
    d3d_dll = "D3D12Core.dll"

    drive = os.path.join(wineprefix, "drive_c")
    prog_files = "Program Files"

    fg_target_dir = os.path.join(
        drive,
        prog_files,
        "Astarte Industries",
        "Bellum",
        "Project_Bellum",
        "Plugins",
        "AMD",
        "FSR",
        "Source",
        "fidelityfx-sdk",
        "Kits",
        "FidelityFX",
        "signedbin",
    )
    d3d_target_dir = os.path.join(
        drive,
        prog_files,
        "Astarte Industries",
        "Bellum",
        "Project_Bellum",
        "Binaries",
        "Win64",
        "D3D12",
        "x64",
    )

    run_command(
        RunMode.SILENT,
        ["mkdir", "-p", fg_target_dir, d3d_target_dir],
    )

    fg_src = os.path.join(fs_path, fg_dll)
    if os.path.isfile(fg_src):
        shutil.copy2(fg_src, os.path.join(fg_target_dir, fg_dll))
        logger.info(f"[OK] Copied {fg_dll}")

    d3d_src = os.path.join(fs_path, d3d_dll)
    if os.path.isfile(d3d_src):
        shutil.copy2(d3d_src, os.path.join(d3d_target_dir, d3d_dll))
        logger.info(f"[OK] Copied {d3d_dll}")

    # Register amdxcffx64 override
    run_command(
        RunMode.SILENT,
        [
            DEFAULT_VERSIONS.binaries.wine,
            "reg",
            "add",
            r"HKEY_CURRENT_USER\Software\Wine\DllOverrides",
            "/v",
            "amdxcffx64",
            "/d",
            "native",
            "/f",
        ],
    )
    logger.info("FSR 4.1.0 Upgrade Complete!")
