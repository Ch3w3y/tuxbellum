#!/usr/bin/env python3
"""Verify version consistency across all release files.

Reads the canonical version from pyproject.toml and checks it against
every other location where the version appears.  Non-zero exit on mismatch.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def _fail(msg: str) -> None:
    print(f"  FAIL: {msg}")
    global _errors
    _errors += 1


_errors = 0


# ── Canonical version from pyproject.toml ────────────────────────────────────

def _get_pyproject_version() -> str:
    text = _read("pyproject.toml")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        print("ERROR: could not parse version from pyproject.toml")
        sys.exit(1)
    return m.group(1)


version = _get_pyproject_version()
print(f"Canonical version: {version}")
print()


# ── meson.build ──────────────────────────────────────────────────────────────

def check_meson() -> None:
    text = _read("meson.build")
    m = re.search(r"version\s*:\s*'([^']+)'", text)
    if not m:
        _fail("meson.build: could not find version string")
        return
    found = m.group(1)
    if found != version:
        _fail(f"meson.build: {found} != {version}")
    else:
        print(f"  OK: meson.build = {found}")


# ── PKGBUILD ─────────────────────────────────────────────────────────────────

def check_pkgbuild() -> None:
    text = _read("PKGBUILD")
    m = re.search(r"^pkgver=(\S+)", text, re.MULTILINE)
    if not m:
        _fail("PKGBUILD: could not find pkgver")
        return
    found = m.group(1)
    if found != version:
        _fail(f"PKGBUILD: {found} != {version}")
    else:
        print(f"  OK: PKGBUILD = {found}")


# ── Makefile ─────────────────────────────────────────────────────────────────

def check_makefile() -> None:
    text = _read("Makefile")
    m = re.search(r"^VERSION \?= (\S+)", text, re.MULTILINE)
    if not m:
        _fail("Makefile: could not find VERSION")
        return
    found = m.group(1)
    if found != version:
        _fail(f"Makefile: {found} != {version}")
    else:
        print(f"  OK: Makefile = {found}")


# ── GUI string ───────────────────────────────────────────────────────────────

def check_gui() -> None:
    text = _read("src/tuxbellum/app/main_window.py")
    m = re.search(r'^VERSION\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        _fail("main_window.py: could not find VERSION constant")
        return
    found = m.group(1)
    if found != version:
        _fail(f"main_window.py: {found} != {version}")
    else:
        print(f"  OK: main_window.py = {found}")


# ── Flatpak manifest ─────────────────────────────────────────────────────────

# ── Metainfo ─────────────────────────────────────────────────────────────────

def check_metainfo() -> None:
    text = _read("data/tuxbellum.metainfo.xml")
    m = re.search(r'<release\s+version="([^"]+)"', text)
    if not m:
        _fail("metainfo.xml: could not find latest release version")
        return
    found = m.group(1)
    if found != version:
        _fail(f"metainfo.xml latest release: {found} != {version}")
    else:
        print(f"  OK: metainfo.xml latest release = {found}")


# ── Run all ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    check_meson()
    check_pkgbuild()
    check_makefile()
    check_gui()
    check_metainfo()

    print()
    if _errors:
        print(f"{_errors} version mismatch(es) found. Fix before release.", file=sys.stderr)
        sys.exit(1)
    else:
        print("All version references consistent.")
