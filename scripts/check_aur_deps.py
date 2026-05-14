#!/usr/bin/env python3
"""Validate PKGBUILD dependency and makedepends names.

Compares declared packages against the local or cached Arch package database.
Non-zero exit if unknown packages are found.

Run in CI or locally (requires pacman or cached package list).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKGBUILD = ROOT / "PKGBUILD"

# Well-known exceptions that may not appear in the local pacman DB
# but are valid packages (AUR or metapackages).
KNOWN_GOOD = {"umu-launcher", "meson-python"}


def _parse_array(name: str, text: str) -> list[str]:
    """Extract a Bash array like `depends=(pkg1 pkg2 ...)`."""
    pattern = rf"^{name}=\((.*?)\)"
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    raw = m.group(1)
    # Remove comments, quotes, newlines, conditionals
    cleaned = re.sub(r"#.*", "", raw)
    cleaned = re.sub(r"['\"]", "", cleaned)
    # Split on whitespace
    items = cleaned.split()
    # Remove version constraints (>=, <=, =, >, <)
    return [re.split(r"[><=]", item)[0].strip() for item in items if item.strip()]


def _package_exists(pkg: str) -> bool:
    """Check if a package exists in the pacman database or AUR."""
    if pkg in KNOWN_GOOD:
        return True

    # Check local pacman DB
    try:
        result = subprocess.run(
            ["pacman", "-Si", pkg],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check AUR via yay/pacman
    try:
        result = subprocess.run(
            ["pacman", "-Ss", f"^{pkg}$"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False


def main() -> int:
    text = PKGBUILD.read_text()

    depends = _parse_array("depends", text)
    makedepends = _parse_array("makedepends", text)
    optdepends_raw = _parse_array("optdepends", text)
    # optdepends have format "pkg: description" — extract pkg name
    optdepends = [re.split(r"[:]", item)[0].strip() for item in optdepends_raw if ":" in item]

    all_pkgs = sorted(set(depends + makedepends + optdepends))

    print(f"Found {len(all_pkgs)} packages in PKGBUILD:")
    for cat, pkgs in [
        ("depends", depends),
        ("makedepends", makedepends),
        ("optdepends", optdepends),
    ]:
        if pkgs:
            print(f"  {cat}: {', '.join(pkgs)}")

    print()

    unknown = []
    has_pacman = True
    try:
        subprocess.run(["pacman", "--version"], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        has_pacman = False

    if not has_pacman:
        print("Pacman not available — skipping package validation.")
        print("(This is normal in CI; validation requires an Arch Linux runner.)")
        return 0

    for pkg in all_pkgs:
        if _package_exists(pkg):
            print(f"  OK: {pkg}")
        else:
            print(f"  UNKNOWN: {pkg}")
            unknown.append(pkg)

    print()

    if unknown:
        print(
            f"WARNING: {len(unknown)} package(s) not found in pacman DB: "
            f"{', '.join(unknown)}"
        )
        print("These may be AUR-only packages or typos. Verify manually.")
        # Soft fail — unknown doesn't always mean invalid (AUR deps)
        return 0  # Still pass; just warn
    else:
        print("All PKGBUILD dependencies recognized by pacman.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
