"""
Dependency specification — explicit strategy for every artifact.

Categorizes every dependency as bundled, downloaded, or system with
the resolution strategy TuxBellum uses at install time.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DepCategory(Enum):
    BUNDLED = "bundled"  # Shipped in the release package
    DOWNLOADED = "downloaded"  # Fetched at install time
    SYSTEM = "system"  # Required on the host


@dataclass(frozen=True)
class DependencySpec:
    name: str
    category: DepCategory
    version: str = ""
    url: str = ""
    path_hint: str = ""  # Bundled: relative to resource_root; Downloaded: cache subdir
    checksum: str = ""  # SHA256 (empty = not verified yet)
    optional: bool = False
    description: str = ""


# ── Canonical dependency registry ────────────────────────────────────────────


DEPENDENCIES: list[DependencySpec] = [
    # ── Bundled ──────────────────────────────────────────────────────────
    DependencySpec(
        name="dxvk-low-latency",
        category=DepCategory.BUNDLED,
        version="2.7.1-3-521-low-latency",
        path_hint="packages/dxvk-{version}.tar.gz",
        description="Vulkan-based D3D translation for AMD GPUs",
    ),
    DependencySpec(
        name="winetricks-modified",
        category=DepCategory.BUNDLED,
        version="20250102-modified",
        path_hint="packages/winetricks-{version}.tar.gz",
        description="Patched winetricks for Bellum compatibility",
    ),
    DependencySpec(
        name="fsr4-dlls",
        category=DepCategory.BUNDLED,
        path_hint="packages/fsr4/",
        description="AMD FSR 4.1 DLLs (amdxcffx64, ffx_fsr4_api_x64)",
    ),
    DependencySpec(
        name="launcher-icon",
        category=DepCategory.BUNDLED,
        path_hint="packages/launcher_1_256x256x32.png",
        description="Desktop entry icon",
    ),
    DependencySpec(
        name="app-icon",
        category=DepCategory.BUNDLED,
        path_hint="data/icons/bellum.png",
        description="TuxBellum GTK window logo",
    ),
    # ── Downloaded ───────────────────────────────────────────────────────
    DependencySpec(
        name="proton-cachyos",
        category=DepCategory.DOWNLOADED,
        version="proton-cachyos-10.0-20260424-slr-x86_64",
        url="https://github.com/CachyOS/proton-cachyos/releases/download",
        description="Proton-CachyOS Wine/Proton runtime",
    ),
    DependencySpec(
        name="dxvk-upstream",
        category=DepCategory.DOWNLOADED,
        version="2.7.1",
        url="https://github.com/doitsujin/dxvk/releases/download",
        path_hint="dxvk/",
        description="Fallback DXVK download when bundled missing",
    ),
    DependencySpec(
        name="astarte-launcher",
        category=DepCategory.DOWNLOADED,
        url="https://auto-updater.astarte.industries/astartelauncher/windows-amd64/AstarteLauncher-amd64-installer.exe",
        path_hint="launcher/",
        description="Bellum's official Astarte Launcher installer",
    ),
    # ── System ───────────────────────────────────────────────────────────
    DependencySpec(
        name="wine",
        category=DepCategory.SYSTEM,
        version=">=11.0",
        description="Windows compatibility layer",
    ),
    DependencySpec(
        name="winetricks",
        category=DepCategory.SYSTEM,
        description="DLL/component installer",
    ),
    DependencySpec(
        name="umu-launcher",
        category=DepCategory.SYSTEM,
        version=">=1.3.0",
        description="Proton container launcher",
    ),
    DependencySpec(
        name="wget",
        category=DepCategory.SYSTEM,
        description="HTTP downloads",
    ),
    DependencySpec(
        name="tar",
        category=DepCategory.SYSTEM,
        description="Archive extraction",
    ),
    DependencySpec(
        name="mesa-utils",
        category=DepCategory.SYSTEM,
        optional=True,
        description="GPU detection via glxinfo",
    ),
    DependencySpec(
        name="gamescope",
        category=DepCategory.SYSTEM,
        optional=True,
        description="Compositor for HDR, resolution scaling",
    ),
    DependencySpec(
        name="gamemode",
        category=DepCategory.SYSTEM,
        optional=True,
        description="CPU/GPU performance governor",
    ),
]


def get_dependency(name: str) -> DependencySpec | None:
    for dep in DEPENDENCIES:
        if dep.name == name:
            return dep
    return None


def get_by_category(category: DepCategory) -> list[DependencySpec]:
    return [d for d in DEPENDENCIES if d.category == category]
