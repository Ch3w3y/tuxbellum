"""Planner — builds the ordered sequence of install steps."""

from collections.abc import Callable

from tuxbellum.engine.context import InstallContext

# Type alias for a step function
InstallStep = Callable[[InstallContext], None]


def build_install_plan() -> list[tuple[str, InstallStep]]:
    """
    Return the ordered, named sequence of install steps.

    Uses lazy imports to avoid circular dependencies with the installer
    package (which imports from this module via run.py).
    """
    from tuxbellum.engine.steps import (  # noqa: PLC0415
        apply_dxvk,
        apply_fsr,
        apply_tuning,
        ensure_proton,
        generate_desktop,
        generate_launcher,
        init_prefix,
        install_dlls,
        run_launcher,
        validate_host,
        verify_launcher,
        write_manifest,
    )

    return [
        ("validate_host", validate_host),
        ("ensure_proton", ensure_proton),
        ("init_prefix", init_prefix),
        ("install_dlls", install_dlls),
        ("run_launcher", run_launcher),
        ("verify_launcher", verify_launcher),
        ("apply_dxvk", apply_dxvk),
        ("apply_tuning", apply_tuning),
        ("apply_fsr", apply_fsr),
        ("generate_launcher", generate_launcher),
        ("generate_desktop", generate_desktop),
        ("write_manifest", write_manifest),
    ]
