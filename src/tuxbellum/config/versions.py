from dataclasses import dataclass, field


@dataclass(frozen=True)
class Binaries:
    wine: str = "/usr/bin/wine"
    wineboot: str = "/usr/bin/wineboot"
    msidb: str = "/usr/bin/msidb"
    winecfg: str = "/usr/bin/winecfg"
    wineserver: str = "/usr/bin/wineserver"


@dataclass(frozen=True)
class Versions:
    proton_ver: str = "proton-cachyos-10.0-20260424-slr-x86_64"
    proton_base_url: str = "https://github.com/CachyOS/proton-cachyos/releases/download"
    wine_ver: str = "wine-11.8"
    winetricks_ver: str = "20250102-modified"
    dxvk_ver: str = "2.7.1-3-521-low-latency"
    vkd3d_ver: str = "2.14"
    fsr_path: str = "packages/fsr4"
    binaries: Binaries = field(default_factory=Binaries)


DEFAULT_VERSIONS = Versions()
LAUNCHER_INSTALLER_URL = "https://auto-updater.astarte.industries/astartelauncher/windows-amd64/AstarteLauncher-amd64-installer.exe"
