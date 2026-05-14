# Install Flow

Exact sequence from GUI click to generated launcher. Current as of v3.0.9.

## Entry Point

User clicks **"Install Astarte Launcher"** in `main_window.py:81`.

## Flow

### Phase 0: GUI & Pre-flight

1. **Install dialog** (`install_dialog.py`)
   - User chooses WINEPREFIX path, FSR 4.1 toggle, GPU type
   - Dialog returns `InstallData` dict

2. **NVMe check** (`main_window.py:149-165`)
   - `_is_ssd()` checks if parent dir of WINEPREFIX is on SSD
   - Warns if not — user can still proceed

3. **Progress dialog** (`main_window.py:171-177`)
   - Modal `InstallProgressDialog` shown
   - Background thread spawned for actual install

### Phase 1: Detection (`main_window.py:182-195`)

```
→ detect_gpu()          (core/gpu.py)
→ run_prechecks()       (installer/precheck.py)
```

**`run_prechecks()` sub-flow**:

| Step | File:Line | Action |
|---|---|---|
| 1 | `precheck.py:74` | `detect_gpu_type()` — parse GPU vendor |
| 2 | `precheck.py:88` | `check_winetricks()` — ensure winetricks available; build from source if missing |
| 3 | `precheck.py:97` | `check_wine_binaries()` — verify `wine`, `wineboot`, `msidb`, `winecfg`, `wineserver` on PATH |
| 4 | `precheck.py:104` | `check_wine_version()` — `wine --version` ≥ 11.0 |
| 5 | `precheck.py:109` | `check_umu_run()` — `umu-run --version` ≥ 1.3.0 |
| 6 | `precheck.py:119` | `check_proton()` — ensure Proton available; download if missing |
| 7 | `precheck.py:136` | Resolve launcher installer (provided path or `download_launcher_installer()`) |

### Phase 2: Install Config

```python
InstallConfig(
    wineprefix=...,
    proton_path=...,
    gpu_type=...,
    is_amd_gpu=...,
    launcher_installer=...,
    resource_root=path_mgr.app_data_root(),
    cache_dir=path_mgr.launcher_cache_dir(),
    is_fsr41=...,
)
```

### Phase 3: Install Pipeline (`run.py:31-97`)

`run_installation()` sets env vars then calls `_run_pipeline()`:

| Step | File:Line | Command / Action | Mode | Checked? |
|---|---|---|---|---|
| 0 | `run.py:50-60` | Set env: `PROTONPATH`, `WINEPREFIX`, `WINEARCH=win64`, `STEAM_APP_PATH`, `STEAM_APPID`, `STEAM_COMPAT_DATA_PATH`, `GAMEID` | env set | N/A |
| 1 | `run.py:74` | `init_wineprefix()` — `umu-run wineboot --init` | SILENT checked | ✅ (RuntimeError) |
| 2 | `run.py:75` | `install_winedlls()` — `wine msidb ...` + `winetricks -q` per DLL (`vcrun2022`, `d3dcompiler_47`, `faudio`, `dotnet48`, `mfc140`) | SILENT checked | ✅ (RuntimeError per DLL) |
| 3 | `run.py:79` | `wineboot --end-session` | SILENT | ❌ (intentional — cleanup) |
| 4 | `run.py:80` | `wineboot -k` | SILENT | ❌ (intentional — cleanup) |
| 5 | `run.py:81` | `wineserver -w` | SILENT | ❌ (intentional — cleanup) |
| 6 | `run.py:84` | `proton run <launcher_exe>` (Astarte Launcher GUI) | STREAM | ⚠️ (exit code captured but only for error message; actual check: `os.path.isfile(installed_exe)`) |
| 7 | `run.py:91-93` | Verify `AstarteLauncher.exe` exists in prefix | filesystem | ✅ (RuntimeError if missing) |
| 8 | `run.py:96` | `winetricks win11` | SILENT checked via `_check_run` | ✅ |
| 9 | `run.py:99` | `install_dxvk()` — `tar -xzf dxvk.tar.gz` + `dxvk_setup.sh install` + `cp dxvk.conf` | SILENT checked | ✅ (checked post-`fef460a`) |
| 10 | `run.py:102-106` | `winetricks grabfullscreen=y windowmanagerdecorated=n mwo=disabled` | SILENT checked via `_check_run` | ✅ |
| 11 | `run.py:108-109` | `winetricks remove_mono` (AMD only) | SILENT checked via `_check_run` | ✅ |
| 12 | `run.py:114` | `copy_icon()` — copy launcher PNG to `~/.local/share/icons/...` | filesystem | N/A |
| 13 | `run.py:115` | `generate_desktop_files()` — write `.desktop` files | filesystem | N/A |
| 14 | `run.py:116` | `generate_launcher_wrapper()` — write `/usr/local/bin/Bellum` (via pkexec if non-root) | STREAM (pkexec) | ❌ (unchecked — see error consistency review) |
| 15 | `run.py:119` | `generate_launch_vars_file()` — write `launch_vars.env` to WINEPREFIX | filesystem | N/A |
| 16 | `run.py:121-135` | `wine reg add ... DirectInput RawInput=1` | SILENT checked via `_check_run` | ✅ |
| 17 | `run.py:137` | `update_dlls()` — `wine reg add ... DllOverrides` for d3d12, d3d12core, d3d10core, d3d9, d3d8 + app-specific overrides | SILENT | ❌ (unchecked — see error consistency review) |
| 18 | `run.py:139-140` | `upgrade_fsr()` (AMD + FSR 4.1 only) — `mkdir -p <fsr dir>` + copy DLLs + `wine reg add amdxcffx64` | SILENT (mkdir + reg) | ❌ (unchecked for both) |
| 19 | `run.py:142` | `wineboot --end-session` | SILENT checked via `_check_run` | ✅ |

### Phase 4: Post-Install

- `_add_game()` writes `games.json` to `~/.config/tuxbellum/games.json`
- "Launch Bellum" button becomes enabled
- User can now launch via the button or `Bellum` CLI wrapper

## Uninstall Flow

User triggers from GUI (via `uninstall.py`).

| Step | File:Line | Action |
|---|---|---|
| 1 | `uninstall.py:40-44` | Confirm WINEPREFIX exists |
| 2 | `uninstall.py:46-49` | User confirmation prompt |
| 3 | `uninstall.py:63` | `_remove_launcher_binaries()` — `rm /usr/local/bin/Bellum` |
| 4 | `uninstall.py:67` | `_remove_desktop_entries()` — rm `.desktop` files + `update-desktop-database` |
| 5 | `uninstall.py:79` | `_remove_icon()` — rm icon from `~/.local/share/icons/` |
| 6 | `uninstall.py:87` | `_remove_proton()` — `rm -rf` Proton install dir |
| 7 | `uninstall.py:107` | `_remove_wineprefix()` — `rm -rf` entire WINEPREFIX |
