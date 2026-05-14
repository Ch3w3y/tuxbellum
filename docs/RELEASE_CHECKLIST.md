# TuxBellum Release Checklist

Use this checklist when cutting a new release.

## Before Tagging

- [ ] `pyproject.toml` — bump `version` field
- [ ] `meson.build` — bump `version` in `project()` call
- [ ] `PKGBUILD` — bump `pkgver`
- [ ] `Makefile` — bump `VERSION ?=` default
- [ ] `src/tuxbellum/app/main_window.py` — bump `VERSION` constant
- [ ] `data/tuxbellum.metainfo.xml` — add `<release>` entry with version, date, description
- [ ] `README.md` — update any version references if applicable
- [ ] Run `pytest tests/ -m "not gtk4"` — all tests pass
- [ ] Run `ruff check src/` — no lint errors
- [ ] Run `black --check src/` — formatting passes
- [ ] Build and smoke-test locally: `make build && tuxbellum`

## Tag and Push

- [ ] `git tag v<version>`
- [ ] `git push origin v<version>`
- [ ] Wait for CI lint + test jobs to pass
- [ ] Wait for CI release job to publish tarball + AppImage

## Verify Release Artifacts

- [ ] Download release tarball from GitHub Releases — verify it contains expected structure
- [ ] Download AppImage from GitHub Releases
- [ ] `chmod +x TuxBellum-<version>-x86_64.AppImage`
- [ ] Run AppImage — verify it starts, GUI renders, logo shows
- [ ] Verify `app_data_root()` resolves correctly inside AppImage

## AUR

- [ ] Wait for CI `aur-update` job to push updated PKGBUILD
- [ ] Verify AUR package page shows correct version and dependencies
- [ ] Test AUR install: `yay -S tuxbellum`

## Post-Release

- [ ] Update `docs/TUXBELLUM_V4_BACKLOG.md` if this release affects the backlog
- [ ] Announce release on relevant channels
