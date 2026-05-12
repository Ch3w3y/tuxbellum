
## README.md Install Methods Cleanup — 2026-05-12

**Decision:** Removed pip/curl deployment sections and made AppImage the primary install method.

**What changed:**
- Removed "Install Script (Recommended)" section (curl pipe bash)
- Removed "Manual Installation (Pip)" section (git clone + pip install)
- Promoted AppImage to primary position with "(Recommended)" label
- Added note: "No system GTK4 packages required — everything is bundled"
- Added explicit reference to Runtime Dependencies for AppImage users
- AUR section preserved as-is

**Rationale:** With PyInstaller-based AppImage bundling the full application including GTK4, there is no need for pip-based or shell-script-based install methods. The AppImage is self-contained and the simplest distribution path.
