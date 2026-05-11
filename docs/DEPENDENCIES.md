# TuxBellum — Dependency Tracking

## Core Dependencies

| Dependency          | Version                             | Source                                             | AUR Package           | License   | Type       |
|---------------------|-------------------------------------|----------------------------------------------------|-----------------------|-----------|------------|
| Proton-CachyOS      | proton-cachyos-10.0-20260424-slr    | https://github.com/CachyOS/proton-cachyos          | proton-cachyos        | BSD-3     | Downloaded |
| DXVK (low-latency)  | dxvk-2.7.1-3-521-low-latency        | https://github.com/doitsujin/dxvk                  | dxvk-bin              | zlib      | Bundled    |
| Winetricks (mod)    | winetricks-20250102-modified        | https://github.com/Winetricks/winetricks           | winetricks            | GPL-2     | Bundled    |
| VKD3D-Proton        | vkd3d-proton-2.14                   | https://github.com/HansKristian-Work/vkd3d-proton  | vkd3d-proton-bin      | LGPL-2.1  | Via Proton |
| umu-launcher        | umu-launcher-1.3.0                  | https://github.com/Open-Wine-Components/umu-launcher| umu-launcher         | MIT       | System     |
| Wine                | wine-11.8                           | https://gitlab.winehq.org/wine/wine                 | wine                  | LGPL-2.1  | System     |
| FSR 4.1 DLLs        | 4.1.0                               | https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK | (none — bundled) | MIT       | Bundled    |
| AstarteLauncher     | (latest, auto-updater)              | https://auto-updater.astarte.industries/astartelauncher/windows-amd64/ | (none — proprietary) | Proprietary | Downloaded |
| Mesa Utils          | (system)                            | https://gitlab.freedesktop.org/mesa/mesa           | mesa-utils            | MIT       | System     |

## Python Dependencies

| Dependency   | Version   | Source                                         | License   | Type       |
|-------------|-----------|------------------------------------------------|-----------|------------|
| PyGObject   | >=3.50    | https://gitlab.gnome.org/GNOME/pygobject       | LGPL-2.1  | System/Pip |
| pytest      | >=7.0     | https://github.com/pytest-dev/pytest           | MIT       | Dev        |
| pytest-cov  | >=4.0     | https://github.com/pytest-dev/pytest-cov       | MIT       | Dev        |
| pytest-mock | >=3.10    | https://github.com/pytest-dev/pytest-mock      | MIT       | Dev        |
| black       | >=23.0    | https://github.com/psf/black                   | MIT       | Dev        |
| ruff        | >=0.1.0   | https://github.com/astral-sh/ruff               | MIT       | Dev        |
| mypy        | >=1.5     | https://github.com/python/mypy                 | MIT       | Dev        |

## CI/CD Update Strategy

### Checking for New Releases

| Dependency       | Update Check Method                                                  | Frequency |
|------------------|----------------------------------------------------------------------|-----------|
| Proton-CachyOS   | Monitor https://github.com/CachyOS/proton-cachyos/releases for new tags | Weekly    |
| DXVK             | Check https://github.com/doitsujin/dxvk/releases for new releases    | Monthly   |
| Winetricks       | Monitor https://github.com/Winetricks/winetricks for commits         | Monthly   |
| VKD3D-Proton     | Check https://github.com/HansKristian-Work/vkd3d-proton/releases     | Monthly   |
| umu-launcher     | Check https://github.com/Open-Wine-Components/umu-launcher/releases  | Weekly    |
| Wine             | Monitor https://gitlab.winehq.org/wine/wine/-/tags for stable tags   | Weekly    |
| FSR 4.1 DLLs     | Check https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK     | Quarterly |
| AstarteLauncher  | Auto-updater handles this; verify download integrity with checksum   | Daily     |

### Update Procedure

1. **Check release notes** for breaking changes or new requirements.
2. **Update version constants** in `src/tuxbellum/config/versions.py`.
3. **Update bundled packages** in `packages/` directory.
4. **Update this file** with the new version.
5. **Test installation** end-to-end before merging.
6. **Update AUR package** dependencies (`PKGBUILD`) if applicable.

### Automated Update CI (Planned)

A GitHub Actions workflow will:
1. Run weekly to poll release APIs (GitHub, GitLab).
2. Open an automated PR with version bumps if new releases are detected.
3. Attach a summary of release notes/changelogs.
4. Require manual approval and testing before merge.
