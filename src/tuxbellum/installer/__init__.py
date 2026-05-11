"""Installer modules for the Bellum Linux Installer."""

from tuxbellum.installer.desktop import copy_icon, generate_desktop_files
from tuxbellum.installer.dll_overrides import update_dlls
from tuxbellum.installer.dxvk import install_dxvk
from tuxbellum.installer.fsr import copy_fsr41_upgrade_dll, upgrade_fsr
from tuxbellum.installer.launch_vars import (
    generate_launch_vars_amd,
    generate_launch_vars_file,
    generate_launch_vars_nvidia,
)
from tuxbellum.installer.launcher import (
    LauncherInstallerState,
    cleanup_launcher_installer,
    download_launcher_installer,
)
from tuxbellum.installer.precheck import (
    PrecheckResult,
    check_proton,
    check_umu_run,
    check_wine_binaries,
    check_wine_version,
    check_winetricks,
    detect_gpu_type,
    run_prechecks,
    validate_wineprefix,
    validate_wineprefix_with_gui,
    validate_wineprefix_with_gui_for_uninstall,
)
from tuxbellum.installer.proton import (
    ensure_proton,
    get_proton_install_path,
    get_proton_url,
    get_proton_user_settings_path,
    patch_proton_settings,
)
from tuxbellum.installer.uninstall import (
    UninstallConfig,
    run_uninstallation,
)
from tuxbellum.installer.wineprefix import init_wineprefix, install_winedlls
from tuxbellum.installer.wrappers import generate_launcher_wrapper

uninstall_pick_wineprefix = validate_wineprefix_with_gui_for_uninstall
from tuxbellum.installer.run import (
    InstallConfig,
    run_installation,
)

__all__ = [
    "ensure_proton",
    "get_proton_url",
    "get_proton_install_path",
    "patch_proton_settings",
    "get_proton_user_settings_path",
    "init_wineprefix",
    "install_winedlls",
    "PrecheckResult",
    "run_prechecks",
    "validate_wineprefix",
    "check_wine_binaries",
    "check_wine_version",
    "check_umu_run",
    "check_winetricks",
    "check_proton",
    "detect_gpu_type",
    "validate_wineprefix_with_gui",
    "validate_wineprefix_with_gui_for_uninstall",
    "install_dxvk",
    "copy_fsr41_upgrade_dll",
    "upgrade_fsr",
    "download_launcher_installer",
    "cleanup_launcher_installer",
    "LauncherInstallerState",
    "update_dlls",
    "generate_launcher_wrapper",
    "generate_desktop_files",
    "copy_icon",
    "generate_launch_vars_amd",
    "generate_launch_vars_nvidia",
    "generate_launch_vars_file",
    "UninstallConfig",
    "run_uninstallation",
    "uninstall_pick_wineprefix",
    "InstallConfig",
    "run_installation",
]
