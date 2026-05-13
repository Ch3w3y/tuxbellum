"""Proton package management — download, extract, patch user_settings.py."""

import os
import shutil
import tarfile
import tempfile

from tuxbellum.config.paths import path_mgr
from tuxbellum.config.versions import DEFAULT_VERSIONS
from tuxbellum.core.logging import Logger
from tuxbellum.core.system import RunMode, run_command


def get_proton_url(proton_ver: str, proton_base_url: str) -> str:
    """
    Build the download URL for a Proton .tar.xz release.

    Strips ``proton-`` prefix and ``-x86_64`` suffix for the directory component.
    """
    prefix = proton_ver
    if prefix.startswith("proton-"):
        prefix = prefix[7:]
    if prefix.endswith("-x86_64"):
        prefix = prefix[:-7]
    return f"{proton_base_url}/{prefix}/{proton_ver}.tar.xz"


def get_proton_install_path(proton_ver: str) -> str:
    """Return the directory where this Proton version is/will be installed."""
    return path_mgr.proton_install_path(proton_ver)


def get_proton_user_settings_path(proton_dir: str) -> str:
    """Find user_settings.py or user_settings.sample.py in *proton_dir*."""
    settings = os.path.join(proton_dir, "user_settings.py")
    if os.path.isfile(settings):
        return settings
    sample = os.path.join(proton_dir, "user_settings.sample.py")
    if os.path.isfile(sample):
        return sample
    return ""


def patch_proton_settings(settings_file: str, is_amd: bool, is_fsr41: bool) -> None:
    """
    Patch Proton user_settings.py with GPU-specific options.

    Raises RuntimeError on failure.
    """
    if not settings_file or not os.path.isfile(settings_file):
        raise RuntimeError(f"settings file not found: {settings_file}")

    file_dir = os.path.dirname(settings_file)
    file_base = os.path.basename(settings_file)
    target_file = os.path.join(file_dir, "user_settings.py")

    # Handle .sample.py
    if file_base.endswith(".sample.py"):
        if os.path.isfile(target_file):
            settings_file = target_file
        else:
            os.rename(settings_file, target_file)
            settings_file = target_file

    # Desired settings
    desired: dict[str, str] = {
        "PROTON_ENABLE_NVAPI": "1",
        "PROTON_DLSS_UPGRADE": "1",
        "MALLOC_ARENA_MAX": "1",
        "PROTON_VKD3D_HEAP": "1",
        "VKD3D_CONFIG": "descriptor_heap",
        "PROTON_DXVK_D3D8": "1",
        "PROTON_NVIDIA_LIBS": "1",
    }

    if is_amd:
        val = "4.1.0" if is_fsr41 else "1"
        desired["PROTON_FSR4_UPGRADE"] = val
        desired["PROTON_FSR4_RDNA3_UPGRADE"] = val

    # Read original
    with open(settings_file) as fh:
        lines = fh.readlines()

    found_keys: set[str] = set()
    in_block = False
    patched: list[str] = []

    for line in lines:
        if "user_settings = {" in line:
            in_block = True
            patched.append(line)
            continue

        if in_block and line.strip() == "}":
            # Insert missing keys before closing brace
            for key, value in desired.items():
                if key not in found_keys:
                    patched.append(f'    "{key}": "{value}",\n')
            in_block = False
            patched.append(line)
            continue

        if in_block:
            matched = False
            for key in desired:
                pattern = f'"{key}":'
                if pattern in line:
                    indent = ""
                    for ch in line:
                        if ch in (" ", "\t"):
                            indent += ch
                        else:
                            break
                    patched.append(f'{indent}"{key}": "{desired[key]}",\n')
                    found_keys.add(key)
                    matched = True
                    break
            if matched:
                continue

        patched.append(line)

    # Write via temp + atomic rename
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=os.path.dirname(settings_file), prefix="user_settings.patched."
    )
    try:
        with os.fdopen(tmp_fd, "w") as fh:
            fh.writelines(patched)
        os.rename(tmp_path, settings_file)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def ensure_proton(
    proton_dir: str,
    proton_ver: str,
    package_root: str,
    is_amd: bool,
    is_fsr41: bool,
    logger: Logger,
) -> None:
    """Download, extract, and patch a Proton installation."""
    actual_dir = get_proton_install_path(proton_ver)
    proton_url = get_proton_url(proton_ver, DEFAULT_VERSIONS.proton_base_url)

    dir_exists = os.path.isdir(actual_dir)
    settings_file = get_proton_user_settings_path(actual_dir)

    if not dir_exists or not settings_file:
        logger.info("Proton directory not found, checking for cached version...")

        # Remove empty directory
        if dir_exists:
            try:
                entries = os.listdir(actual_dir)
            except OSError:
                entries = []
            if not entries:
                logger.info("Proton directory is empty, removing...")
                shutil.rmtree(actual_dir)
                dir_exists = False

        if not dir_exists:
            # Check for cached proton in packages/
            cached_pattern = os.path.join(package_root, "proton-*")
            import glob as _glob

            matches = _glob.glob(cached_pattern)
            for match in matches:
                if match.endswith(proton_ver) and os.path.isfile(
                    os.path.join(match, "user_settings.py")
                ):
                    logger.info(f"Found cached Proton in {match}")
                    logger.info(f"Copying cached Proton from {match} to {actual_dir}...")
                    _copy_directory(match, actual_dir)
                    settings_file = get_proton_user_settings_path(actual_dir)
                    if settings_file:
                        break

        if not settings_file:
            logger.info(f"Downloading Proton {proton_ver}...")
            tmp = tempfile.mkdtemp(prefix="proton.")
            try:
                archive_path = os.path.join(tmp, f"{proton_ver}.tar.xz")
                run_command(
                    RunMode.SILENT,
                    ["wget", "-O", archive_path, proton_url],
                    logger._log_path if hasattr(logger, "_log_path") else "",
                )
                if not os.path.isfile(archive_path):
                    raise RuntimeError("archive not found after download")

                logger.info(f"Extracting Proton to {actual_dir}...")
                os.makedirs(actual_dir, exist_ok=True)
                _extract_tar_xz_strip(archive_path, actual_dir, 1)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)

    # Verify/patch settings
    settings_file = get_proton_user_settings_path(actual_dir)
    if not settings_file:
        raise RuntimeError("Proton user settings file missing after setup")
    try:
        patch_proton_settings(settings_file, is_amd, is_fsr41)
    except Exception:
        logger.error("Failed to patch Proton user settings, removing and would re-download")
        shutil.rmtree(actual_dir, ignore_errors=True)
        raise


def _extract_tar_xz_strip(archive_path: str, dest_dir: str, strip: int) -> None:
    """Extract .tar.xz, stripping *strip* leading path components."""
    with tarfile.open(archive_path, "r:xz") as tf:
        for member in tf.getmembers():
            parts = member.name.split("/")
            if len(parts) <= strip:
                continue
            member.name = "/".join(parts[strip:])
            if member.name == "":
                # Skip the directory entry itself after stripping
                if member.isdir():
                    continue
                # Edge case: a file directly at the archive root
                member.name = "."
            tf.extract(member, dest_dir)


def _copy_directory(src: str, dst: str) -> None:
    """Recursive directory copy (replicates Go's filepath.Walk)."""
    shutil.copytree(src, dst, dirs_exist_ok=True)
