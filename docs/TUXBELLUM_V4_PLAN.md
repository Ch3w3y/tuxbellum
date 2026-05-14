# TuxBellum v4 Plan

## Purpose

TuxBellum should be treated as a **Bellum installer and repair tool**, not as a long-lived launcher application.

The product goal is:

1. Install Bellum into a managed Wine/Proton environment.
2. Apply a known-good compatibility recipe for Linux users.
3. Generate a user-facing launcher/desktop entry.
4. Get out of the way.

After installation, users should launch Bellum directly through the installed Bellum launcher shortcut, not through TuxBellum itself.

## Product Direction

### Current Problem

The current application mixes three roles:

1. GUI app
2. installer/orchestrator
3. launcher manager

This creates fragility because:

1. install state is not managed as a first-class artifact
2. packaging assumptions leak into runtime behavior
3. system mutations are spread across many modules
4. recovery, repair, and uninstall are guess-based rather than manifest-based
5. there is no single source of truth for dependencies or install ownership

### Recommended Product Model

TuxBellum should become a **managed installer for one game** with four user-facing modes:

1. `Install`
2. `Repair`
3. `Update Compatibility Stack`
4. `Uninstall`

Optional advanced mode may expose:

1. custom prefix path
2. optional Gamescope/HDR/Gamemode/NVAPI toggles
3. FSR 4.1 enablement

The default experience for new users should be:

1. open TuxBellum
2. click Install
3. wait for setup to finish
4. launch Bellum from the generated desktop/app-menu shortcut

## Design Principles

1. **Rootless by default**: avoid `/usr/local/bin` and other privileged writes in the happy path.
2. **One managed install**: optimize for one Bellum installation per user.
3. **Idempotent steps**: installer operations must be safe to rerun.
4. **Manifest-driven ownership**: TuxBellum must know exactly what it created and modified.
5. **Single dependency policy**: every dependency must be clearly classified as bundled, downloaded, or system-provided.
6. **CLI-first core**: the installer engine must be usable without GTK.
7. **Thin GUI**: GTK should only present a wizard over the core engine.
8. **Actionable errors**: every failure must report the command, path, and stage that failed.
9. **Artifact verification**: release tarballs and AppImages must be checked in CI for required payload contents.

## Recommended Architecture

### 1. Core Installer Engine

Create a pure-Python installer engine with no GTK imports.

Suggested package layout:

```text
src/tuxbellum/
  core/
    commands.py
    logging.py
    platform.py
  domain/
    install_manifest.py
    install_options.py
    install_state.py
    dependency_spec.py
  engine/
    context.py
    planner.py
    executor.py
    repair.py
    uninstall.py
    steps/
      validate_host.py
      resolve_dependencies.py
      ensure_proton.py
      ensure_prefix.py
      install_launcher.py
      apply_winetricks.py
      apply_dxvk.py
      apply_fsr.py
      write_launchers.py
      write_manifest.py
  cli/
    main.py
  gui/
    application.py
    install_wizard.py
    repair_wizard.py
```

The core engine should own:

1. dependency resolution
2. state transitions
3. command execution
4. logging
5. manifest updates
6. rollback-safe or rerunnable steps

### 2. Install Manifest

Each managed prefix should contain a manifest file, for example:

```text
<prefix>/.tuxbellum/install-manifest.json
```

The manifest should record:

1. TuxBellum version
2. install timestamp
3. target prefix path
4. launcher executable path
5. Proton version and location
6. DXVK version and source
7. winetricks strategy used
8. FSR 4.1 enabled or not
9. launch options enabled
10. generated desktop files and wrapper paths
11. all files and directories owned by TuxBellum
12. any registry keys or prefix modifications applied

This manifest becomes the basis for:

1. uninstall
2. repair
3. migration
4. health checks

### 3. Step-Based Execution Model

Replace the monolithic `run_installation()` pipeline with explicit installer steps.

Each step should define:

1. preconditions
2. inputs
3. outputs
4. side effects
5. failure mode
6. whether it is rerunnable

Example install flow:

1. validate host prerequisites
2. resolve install location
3. resolve dependency sources
4. ensure Proton is cached/installed
5. create or validate managed prefix
6. initialize prefix
7. install winetricks DLLs
8. launch Astarte installer
9. verify launcher executable
10. apply DXVK
11. apply prefix tuning
12. apply FSR 4.1
13. generate launch vars
14. generate per-user wrapper and desktop entries
15. write manifest

### 4. Command Layer

Replace the current `run_command()` abstraction with a richer command API.

Proposed result object:

```python
@dataclass
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_ms: int
```

Requirements:

1. every command invocation must preserve stderr
2. streaming commands must still collect the final output
3. callers must explicitly decide whether non-zero exit is acceptable
4. failures must produce stage-specific error messages

This change alone will remove a large amount of misleading downstream error reporting.

### 5. Dependency Strategy

Standardize dependencies into three classes.

#### Bundled

Bundle only small or project-specific assets:

1. launcher icon
2. FSR 4.1 DLLs
3. optional custom helper scripts

#### Downloaded and Verified

Download versioned public artifacts into XDG cache:

1. Proton
2. DXVK
3. optionally winetricks if the modified tarball is still required

For downloaded artifacts:

1. pin version in one place
2. store source URL in one place
3. store expected checksum in one place
4. verify before use
5. cache and reuse between runs

#### System-Provided

Require these from distro packages:

1. Wine
2. umu-launcher
3. GTK runtime
4. optional Gamescope/Gamemode

This should be documented consistently across:

1. README
2. PKGBUILD
3. AppImage notes
4. runtime prechecks

### 6. Wrapper and Launch Model

Stop writing `/usr/local/bin/Bellum` as the default behavior.

Preferred model:

1. create a user-owned launcher script in `~/.local/share/tuxbellum/bin/Bellum`
2. create `~/.local/share/applications/Bellum.desktop`
3. use a desktop `Exec=` that points directly to the user-owned launcher

Advantages:

1. no `pkexec` in the happy path
2. works from AUR and AppImage consistently
3. uninstall is simpler
4. fewer support issues caused by privileged file writes

### 7. GUI Simplification

The GTK app should become a wizard, not a manager.

Recommended screens:

1. welcome / install status
2. choose install mode
3. optional advanced settings
4. progress and logs
5. complete / repair / uninstall

Remove or demote:

1. persistent Launch button
2. game library concept
3. multi-game state model

### 8. Repair Mode

Repair should become a first-class feature.

It should:

1. load the install manifest
2. verify that required files still exist
3. verify Proton/DXVK/FSR assets
4. verify desktop entries and wrapper
5. reapply missing pieces
6. report drift

This is likely more valuable than adding more front-end settings.

## UX Recommendation

### Default Install UX

Use a strongly opinionated default:

1. managed prefix under `~/Games/Bellum`
2. known-good Proton version
3. recommended DXVK
4. recommended launch tuning
5. desktop/app-menu shortcut installed

### Advanced UX

Hide advanced controls behind an expandable section:

1. custom prefix path
2. FSR 4.1 toggle
3. Gamescope
4. HDR
5. Gamemode
6. NVAPI

New users should not need to understand Wine internals to succeed.

## Testing Strategy

Current test coverage is insufficient.

Add tests in these categories:

### Unit Tests

1. manifest read/write
2. dependency resolution
3. wrapper generation
4. command result handling
5. config/state migration

### Integration Tests

1. install planner creates correct step sequence
2. repair planner detects missing assets
3. uninstall only removes owned files from manifest
4. AppImage path resolution
5. release tarball payload verification

### Release Artifact Tests in CI

CI should validate:

1. release tarball contains required bundled assets
2. AppImage contains required bundled assets
3. AppImage resolves `APPDIR/usr/share/tuxbellum`
4. PKGBUILD versions match project version
5. AUR dependency names are valid

## Migration Plan

### Phase 1: Hardening

Goal: reduce immediate fragility without changing product identity too much.

1. replace command layer
2. add proper error reporting
3. remove silent failure paths
4. unify version metadata
5. add artifact verification in CI
6. stop privileged writes in default flow

### Phase 2: Installer Core

Goal: separate engine from GUI.

1. introduce install manifest
2. implement step executor
3. move install logic out of GTK code
4. add CLI entrypoint
5. keep GTK as a thin wrapper

### Phase 3: Product Pivot

Goal: align UX with installer-only mental model.

1. remove persistent launcher-manager behavior
2. remove game list model
3. add repair mode
4. make install wizard primary

### Phase 4: Dependency Cleanup

Goal: make delivery strategy explicit and durable.

1. move large assets to verified downloads
2. keep only small required payloads bundled
3. consolidate dependency metadata into one module or manifest
4. align README, AUR, AppImage, and runtime checks

## Non-Goals

These should not be primary goals for v4:

1. becoming a generic Wine game manager
2. supporting arbitrary Windows launchers
3. supporting many installed games
4. exposing many low-level Wine toggles in the default UI

TuxBellum should stay narrowly optimized for Bellum.

## Recommended v4 Scope

If a single major release is planned, the recommended v4 minimum scope is:

1. installer-core separation
2. install manifest
3. rootless launcher generation
4. repair mode
5. standardized dependency strategy
6. release artifact validation in CI

## Immediate Next Steps

1. Create an `InstallManifest` schema and implementation.
2. Replace `run_command()` with a structured command result API.
3. Remove `/usr/local/bin/Bellum` writes and switch to a per-user launcher.
4. Refactor install flow into explicit steps with stage names.
5. Add CI checks for AppImage and release tarball payload integrity.
6. Remove `games.json` and replace it with manifest-driven install-state discovery.

## Final Recommendation

Do not continue incrementally expanding the current app as a persistent launcher-manager.

Instead:

1. keep the GTK shell only as a frontend
2. move the real product into a deterministic installer engine
3. optimize for one managed Bellum install
4. let the generated Bellum shortcut be the thing users launch every day

That is the most direct path to a less fragile product with lower support overhead.
