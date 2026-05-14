# TuxBellum v4 Backlog

This document turns the v4 plan into a concrete implementation backlog.

It is organized in execution order, with each milestone designed to leave the project in a working state.

## Guiding Rule

At every milestone:

1. `main` must still produce a working release
2. AppImage and AUR packaging must still function
3. user-visible behavior should only change when the replacement path is already ready

## Decisions (2026-05-14)

- **Migration strategy**: Fresh start. v4 is a clean break — existing `games.json` installs are not migrated. Users reinstall through the new flow.
- **M4 split**: Milestone 4 split into M4a (extract steps + InstallContext, keep old `run_installation` as thin wrapper) and M4b (reentrancy, stage logging, result reporting).
- **Testing milestone**: Inserted M3.5 dedicated to test infrastructure (fixtures, mocks, coverage gate) after M3 rootless launcher.
- **Sprint 1 scope** (current): M0 (audit) + M1 (commands) + M9 partial (CI artifact verification). Foundation layer only.

---

## Milestone 0: Freeze and Audit

### Goal

Create a stable baseline before structural changes.

### Tasks

1. Create a release checklist document.
2. Add a dependency inventory document as a single source of truth.
3. Record the exact current install flow from GUI click to generated launcher.
4. Record every filesystem path currently written by the installer.
5. Record every command currently executed during install and uninstall.

### Deliverables

1. `docs/RELEASE_CHECKLIST.md`
2. `docs/INSTALL_FLOW.md`
3. `docs/OWNED_PATHS_AUDIT.md`

### Files to inspect/update

1. [src/tuxbellum/app/main_window.py](/home/daryn/tuxbellum/src/tuxbellum/app/main_window.py:122)
2. [src/tuxbellum/installer/run.py](/home/daryn/tuxbellum/src/tuxbellum/installer/run.py:31)
3. [src/tuxbellum/installer/precheck.py](/home/daryn/tuxbellum/src/tuxbellum/installer/precheck.py:37)
4. [src/tuxbellum/installer/uninstall.py](/home/daryn/tuxbellum/src/tuxbellum/installer/uninstall.py:18)
5. [src/tuxbellum/installer/wrappers.py](/home/daryn/tuxbellum/src/tuxbellum/installer/wrappers.py:12)

## Milestone 1: Replace the Command Layer

### Goal

Make failures explicit and diagnosable.

### Tasks

1. Introduce `CommandResult`.
2. Replace `run_command()` with structured execution helpers.
3. Capture stdout/stderr for all commands.
4. Add helpers for:
   1. `run_checked`
   2. `run_streaming`
   3. `run_capture`
5. Make caller intent explicit:
   1. allowed failure
   2. required success
   3. ignored output

### Deliverables

1. new module `src/tuxbellum/core/commands.py`
2. migration of current callers off `core/system.py`
3. improved error messages with command, exit code, and stderr

### Files to create

1. `src/tuxbellum/core/commands.py`

### Files to refactor

1. [src/tuxbellum/core/system.py](/home/daryn/tuxbellum/src/tuxbellum/core/system.py:17)
2. [src/tuxbellum/installer/precheck.py](/home/daryn/tuxbellum/src/tuxbellum/installer/precheck.py:181)
3. [src/tuxbellum/installer/run.py](/home/daryn/tuxbellum/src/tuxbellum/installer/run.py:66)
4. [src/tuxbellum/installer/dxvk.py](/home/daryn/tuxbellum/src/tuxbellum/installer/dxvk.py:12)
5. [src/tuxbellum/installer/wineprefix.py](/home/daryn/tuxbellum/src/tuxbellum/installer/wineprefix.py:17)
6. [src/tuxbellum/installer/wrappers.py](/home/daryn/tuxbellum/src/tuxbellum/installer/wrappers.py:99)

### Acceptance Criteria

1. No installer path depends on silent command failures.
2. User-facing errors include the failed stage and failed command.
3. Tests cover success, timeout, and missing-binary behaviors.

## Milestone 2: Define Install State and Manifest

### Goal

Stop guessing what TuxBellum installed.

### Tasks

1. Introduce a versioned install manifest schema.
2. Store manifest inside the managed prefix.
3. Track all owned files and generated entries.
4. Replace `games.json` as the source of install state.
5. Add load/save/validate helpers for the manifest.

### Deliverables

1. `src/tuxbellum/domain/install_manifest.py`
2. manifest versioning strategy
3. manifest discovery logic

### Manifest fields

1. prefix path
2. TuxBellum version
3. Proton version/path
4. DXVK version/source
5. FSR enabled state
6. generated launcher path
7. desktop entry paths
8. icon path
9. applied registry edits
10. owned files/directories

### Files to create

1. `src/tuxbellum/domain/install_manifest.py`
2. `src/tuxbellum/domain/install_options.py`
3. `src/tuxbellum/domain/install_state.py`

### Files to refactor

1. [src/tuxbellum/app/main_window.py](/home/daryn/tuxbellum/src/tuxbellum/app/main_window.py:87)
2. [src/tuxbellum/config/manager.py](/home/daryn/tuxbellum/src/tuxbellum/config/manager.py:7)
3. [src/tuxbellum/installer/uninstall.py](/home/daryn/tuxbellum/src/tuxbellum/installer/uninstall.py:46)

### Acceptance Criteria

1. Install state can be discovered without `games.json`.
2. Uninstall can operate from manifest data.
3. Future migrations can be implemented from manifest version.

## Milestone 3: Make the Installer Rootless

### Goal

Remove privileged writes from the default path.

### Tasks

1. Stop writing `/usr/local/bin/Bellum`.
2. Generate a user-owned launcher under XDG data or `~/.local/bin`.
3. Update `.desktop` generation to point directly at the user-owned launcher.
4. Remove `pkexec` from the default install flow.
5. Update uninstall to remove only per-user artifacts.

### Deliverables

1. per-user launcher script
2. per-user desktop entry
3. no root prompt during normal install

### Files to refactor

1. [src/tuxbellum/installer/wrappers.py](/home/daryn/tuxbellum/src/tuxbellum/installer/wrappers.py:87)
2. [src/tuxbellum/installer/desktop.py](/home/daryn/tuxbellum/src/tuxbellum/installer/desktop.py:28)
3. [src/tuxbellum/installer/uninstall.py](/home/daryn/tuxbellum/src/tuxbellum/installer/uninstall.py:65)
4. [src/tuxbellum/config/paths.py](/home/daryn/tuxbellum/src/tuxbellum/config/paths.py:67)

### Acceptance Criteria

1. Default install completes without root.
2. Generated launch artifacts work from desktop/app menu.
3. Uninstall removes only user-owned artifacts.

## Milestone 3.5: Test Infrastructure

### Goal

Establish the test fixtures, mocks, and coverage gate needed to sustain quality through the remaining milestones.

### Tasks

1. Create shared pytest fixtures (`conftest.py`) for Logger, temp paths, and config mocks.
2. Create reusable mocks for `run_command` / command execution.
3. Add `tmp_path`-based integration fixtures for filesystem simulation.
4. Raise coverage gate to a reachable baseline and enforce it in CI.
5. Standardize test markers (`network`, `slow`, `integration`).

### Deliverables

1. `tests/conftest.py`
2. `tests/fixtures/` (optional, if many)
3. coverage gate enforced in CI (not just advisory)

### Acceptance Criteria

1. Every new module added in M4+ has at least unit test coverage.
2. Coverage report is not advisory — failing CI if below threshold.
3. No `--override-ini` hack needed to run tests.

## Milestone 4a: Extract Steps + InstallContext

### Goal

Extract the install pipeline into named steps with a shared context object, while keeping the existing `run_installation()` as a thin wrapper. This unblocks M5 (CLI), M6 (GUI), and M8 (repair/doctor) without requiring reentrancy or stage-level reporting yet.

### Tasks

1. Create `InstallContext` dataclass holding all mutable install state.
2. Create `InstallStep` abstraction (a callable taking `InstallContext`).
3. Split `run_installation()` into named step functions.
4. `run_installation()` becomes a thin wrapper that calls steps in sequence.
5. Add stage names for logging (each step logs its name on entry/exit).

### Proposed steps

1. validate host
2. resolve prefix
3. resolve dependencies
4. ensure Proton
5. initialize prefix
6. install Winetricks DLLs
7. run Astarte installer
8. verify launcher executable
9. apply DXVK
10. apply tuning
11. apply FSR
12. generate launcher
13. generate desktop entries
14. write manifest

### Files to create

1. `src/tuxbellum/engine/context.py`
2. `src/tuxbellum/engine/planner.py`
3. `src/tuxbellum/engine/steps/` (directory, one module per step)

### Files to refactor

1. [src/tuxbellum/installer/run.py](/home/daryn/tuxbellum/src/tuxbellum/installer/run.py:71)
2. [src/tuxbellum/installer/precheck.py](/home/daryn/tuxbellum/src/tuxbellum/installer/precheck.py:308)
3. [src/tuxbellum/app/main_window.py](/home/daryn/tuxbellum/src/tuxbellum/app/main_window.py:201)

### Acceptance Criteria

1. Each step has a clear stage name.
2. `run_installation()` still works identically.
3. Steps can be imported and tested independently.

## Milestone 4b: Reentrancy and Stage Reporting

### Goal

Make each step reentrant where possible, add stage-level result reporting, and build the executor that drives steps.

### Tasks

1. Create `StepResult` dataclass (success/skipped/failed + message).
2. Create `Executor` that runs a sequence of steps and collects results.
3. Make each step safe to rerun (idempotent checks).
4. Add result reporting: which step failed, why, what to do.
5. Wire executor into CLI (M5) and GUI (M6).

### Files to create

1. `src/tuxbellum/engine/executor.py`

### Acceptance Criteria

1. Logs identify the step where failure occurred.
2. Steps can be rerun without corrupting state.
3. Executor can be driven without GTK.

## Milestone 5: CLI Frontend

### Goal

Make the installer testable and scriptable without the GUI.

### Commands

1. `tuxbellum install`
2. `tuxbellum repair`
3. `tuxbellum status`
4. `tuxbellum uninstall`
5. `tuxbellum doctor`

### Tasks

1. Add CLI argument parsing.
2. Route CLI into the shared engine.
3. Support noninteractive mode.
4. Support machine-readable output for diagnostics.

### Files to create

1. `src/tuxbellum/cli/main.py`

### Files to refactor

1. [src/tuxbellum/__main__.py](/home/daryn/tuxbellum/src/tuxbellum/__main__.py:1)
2. [pyproject.toml](/home/daryn/tuxbellum/pyproject.toml:34)

### Acceptance Criteria

1. Full install can be driven without GTK.
2. Repair and doctor can run headless.
3. GUI delegates to the same engine.

## Milestone 6: Simplify the GUI to an Installer Wizard

### Goal

Remove launcher-manager behavior and align the UX with the real product.

### Tasks

1. Remove persistent `Launch Bellum` responsibility from TuxBellum.
2. Remove `games.json`.
3. Replace main window with an installer/repair state screen.
4. Keep advanced settings behind an expandable panel.
5. Show post-install success with “Launch Bellum from your desktop/app menu”.

### New GUI modes

1. not installed
2. installed
3. repair available
4. uninstall available

### Files to refactor

1. [src/tuxbellum/app/main_window.py](/home/daryn/tuxbellum/src/tuxbellum/app/main_window.py:29)
2. [src/tuxbellum/app/install_dialog.py](/home/daryn/tuxbellum/src/tuxbellum/app/install_dialog.py:1)
3. [src/tuxbellum/app/settings_dialog.py](/home/daryn/tuxbellum/src/tuxbellum/app/settings_dialog.py:1)

### Acceptance Criteria

1. GUI no longer acts as a game launcher.
2. GUI can discover installed state from manifest.
3. New-user flow is shorter and clearer.

## Milestone 7: Standardize Dependency Resolution

### Goal

Make dependency behavior explicit, consistent, and auditable.

### Tasks

1. Create a dependency manifest module.
2. Categorize each dependency as:
   1. bundled
   2. downloaded
   3. system
3. Add checksums for downloaded artifacts.
4. Store downloaded artifacts in XDG cache.
5. Add offline behavior rules.

### Recommended policy

1. Bundle:
   1. launcher icon
   2. FSR DLLs
2. Download and verify:
   1. Proton
   2. DXVK
   3. optional patched winetricks
3. Require from system:
   1. Wine
   2. umu-run
   3. GTK runtime

### Files to create

1. `src/tuxbellum/domain/dependency_spec.py`
2. `src/tuxbellum/engine/resolve_dependencies.py`

### Files to refactor

1. [src/tuxbellum/config/versions.py](/home/daryn/tuxbellum/src/tuxbellum/config/versions.py:1)
2. [src/tuxbellum/installer/proton.py](/home/daryn/tuxbellum/src/tuxbellum/installer/proton.py:123)
3. [src/tuxbellum/installer/dxvk.py](/home/daryn/tuxbellum/src/tuxbellum/installer/dxvk.py:64)
4. [src/tuxbellum/installer/precheck.py](/home/daryn/tuxbellum/src/tuxbellum/installer/precheck.py:232)

### Acceptance Criteria

1. Every dependency has one declared strategy.
2. Runtime behavior matches release packaging.
3. README, AUR, and AppImage docs match code behavior.

## Milestone 8: Repair and Doctor Modes

### Goal

Provide recovery paths that do not require reinstall guesswork.

### Repair should verify

1. prefix exists
2. launcher exists
3. Proton exists
4. DXVK is applied
5. FSR files are present if enabled
6. launcher script exists
7. desktop entries exist
8. icon exists

### Doctor should report

1. host dependency status
2. managed install status
3. cache status
4. manifest consistency
5. recommended remediation

### Files to create

1. `src/tuxbellum/engine/repair.py`
2. `src/tuxbellum/engine/doctor.py`

### Acceptance Criteria

1. Most support issues can be reproduced or repaired through doctor/repair.
2. Uninstall no longer doubles as a repair escape hatch.

## Milestone 9: Release and Packaging Hardening

### Goal

Ensure artifacts are correct before users see them.

### CI tasks

1. Verify version consistency across:
   1. `pyproject.toml`
   2. `meson.build`
   3. `PKGBUILD`
   4. GUI version strings
2. Verify release tarball payload.
3. Verify AppImage payload.
4. Verify AUR dependency names.
5. Verify required assets exist in release outputs.

### Additional checks

1. smoke-test AppImage extraction
2. smoke-test `app_data_root()` against extracted AppImage
3. smoke-test launcher generation
4. smoke-test manifest serialization

### Files to update

1. [.github/workflows/ci.yml](/home/daryn/tuxbellum/.github/workflows/ci.yml:132)
2. [scripts/build-appimage.sh](/home/daryn/tuxbellum/scripts/build-appimage.sh:24)
3. [Makefile](/home/daryn/tuxbellum/Makefile:13)

### Acceptance Criteria

1. Missing packaged assets fail CI before release.
2. Invalid AUR dependency names fail CI before release.
3. AppImage path regressions fail CI before release.

## Milestone 10: Remove Legacy State and Dead Paths

### Goal

Delete the old launcher-manager assumptions once replacements are live.

### Tasks

1. remove `games.json`
2. remove old launch button logic
3. remove stale config keys no longer needed
4. remove old uninstall path assumptions
5. remove legacy runtime fallbacks that are only there for the old architecture

### Acceptance Criteria

1. install state exists only in manifest plus user settings
2. no dead compatibility shims remain for removed flows

## Suggested Ticket Order

### Sprint 1 (current)

1. Milestone 0: audit and freeze
2. Milestone 1: command layer
3. Milestone 9 partial: release artifact verification

### Sprint 2

1. Milestone 2: manifest
2. Milestone 3: rootless launcher
3. Milestone 3.5: test infrastructure

### Sprint 3

1. Milestone 4a: extract steps + InstallContext
2. Milestone 4b: reentrancy and stage reporting
3. Milestone 5: CLI

### Sprint 4

1. Milestone 6: GUI simplification
2. Milestone 7: dependency strategy cleanup
3. Milestone 8: repair/doctor
4. Milestone 10: legacy removal

## Recommended First Tickets (Sprint 1)

These are being implemented now:

1. `v4-001`: Introduce structured command execution API (`src/tuxbellum/core/commands.py`).
2. `v4-002`: Audit documents — RELEASE_CHECKLIST, DEPENDENCY_INVENTORY, INSTALL_FLOW, OWNED_PATHS_AUDIT, COMMAND_AUDIT.
3. `v4-003`: CI version consistency check across pyproject.toml, meson.build, PKGBUILD.
4. `v4-004`: CI AppImage/tarball payload verification.
5. `v4-005`: CI AUR dependency name validation.

## Definition of Done for v4

TuxBellum v4 is done when:

1. install is driven by a reusable engine, not GTK callbacks
2. install state is manifest-driven
3. users do not need root for normal installation
4. TuxBellum is no longer the daily launcher
5. repair and doctor exist
6. release artifacts are validated in CI
7. dependency behavior is explicit and consistent across AUR and AppImage
