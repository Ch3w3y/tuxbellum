#!/usr/bin/env python3
"""Check for new releases of TuxBellum dependencies.

Used by CI/CD weekly schedule. Outputs dependency_updates.txt if new versions
are found, which triggers an automated PR.
"""
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

DEPS = {
    "proton-cachyos": {
        "url": "https://api.github.com/repos/CachyOS/proton-cachyos/releases/latest",
        "pattern": r"proton-cachyos-([\d.]+-\d+)",
    },
    "dxvk": {
        "url": "https://api.github.com/repos/doitsujin/dxvk/releases/latest",
        "pattern": r"v?([\d.]+)",
    },
    "umu-launcher": {
        "url": "https://api.github.com/repos/Open-Wine-Components/umu-launcher/releases/latest",
        "pattern": r"v?([\d.]+)",
    },
    "vkd3d-proton": {
        "url": "https://api.github.com/repos/HansKristian-Work/vkd3d-proton/releases/latest",
        "pattern": r"v?([\d.]+)",
    },
    "winetricks": {
        "url": "https://api.github.com/repos/Winetricks/winetricks/releases/latest",
        "pattern": r"v?([\d.]+)",
    },
    "wine": {
        "url": "https://api.github.com/repos/wine-mirror/wine/releases/latest",
        "pattern": r"wine-([\d.]+)",
    },
}

VERSIONS_FILE = Path("src/tuxbellum/config/versions.py")


def fetch_latest(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "tuxbellum-ci"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def check_deps() -> list[str]:
    updates = []
    versions_src = VERSIONS_FILE.read_text()

    for name, cfg in DEPS.items():
        try:
            release = fetch_latest(cfg["url"])
            tag = release.get("tag_name", "")
            match = re.search(cfg["pattern"], tag)
            if match:
                latest = match.group(1)
                updates.append(f"{name}: latest={latest} tag={tag}")
        except (urllib.error.URLError, KeyError, re.error):
            updates.append(f"{name}: CHECK_FAILED")

    return updates


if __name__ == "__main__":
    results = check_deps()
    if results:
        Path("dependency_updates.txt").write_text("\n".join(results) + "\n")
        print("Updates found:")
        for r in results:
            print(f"  {r}")
    else:
        print("No updates found.")