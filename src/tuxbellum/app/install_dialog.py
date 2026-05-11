"""Install configuration dialog for the Bellum Linux Installer."""

import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from tuxbellum.config.manager import ConfigManager
from tuxbellum.i18n.locale import setup_gettext

_ = setup_gettext()


class InstallDialog(Gtk.Dialog):
    """Dialog for configuring Bellum installation options."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("Install Bellum"))
        self.set_resizable(False)
        self.set_default_size(480, 520)

        self.cfg = ConfigManager()
        self._build_ui()

    def _build_ui(self):
        content = self.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(8)
        grid.set_column_spacing(8)
        content.append(grid)

        row = 0

        # ── Install Directory ──
        label = Gtk.Label(label=_("Install Directory"))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, row, 3, 1)
        row += 1

        default_dir = self.cfg.get_install_dir()
        self.entry_dir = Gtk.Entry(text=os.path.join(default_dir, "Bellum"))
        self.entry_dir.set_hexpand(True)
        btn_browse = Gtk.Button.new_from_icon_name("folder-open-symbolic")
        btn_browse.connect("clicked", self._on_browse_dir)
        btn_browse.set_size_request(48, -1)

        dir_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        dir_box.append(self.entry_dir)
        dir_box.append(btn_browse)
        grid.attach(dir_box, 0, row, 3, 1)
        row += 1

        # ── Wine Prefix ──
        label = Gtk.Label(label=_("Wine Prefix"))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, row, 3, 1)
        row += 1

        default_prefix = os.path.join(
            os.path.expanduser("~"), "Games", "Bellum", "wineprefix"
        )
        self.entry_prefix = Gtk.Entry(text=default_prefix)
        self.entry_prefix.set_hexpand(True)
        btn_browse2 = Gtk.Button.new_from_icon_name("folder-open-symbolic")
        btn_browse2.connect("clicked", self._on_browse_prefix)
        btn_browse2.set_size_request(48, -1)

        prefix_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        prefix_box.append(self.entry_prefix)
        prefix_box.append(btn_browse2)
        grid.attach(prefix_box, 0, row, 3, 1)
        row += 1

        # ── Separator ──
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep, 0, row, 3, 1)
        row += 1

        # ── Performance Options ──
        label = Gtk.Label(label=_("Performance Options"))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, row, 3, 1)
        row += 1

        self.chk_fsr41 = Gtk.CheckButton(label=_("FSR 4.1 Upgrade"))
        self.chk_fsr41.set_active(self.cfg.get_bool("fsr41"))
        grid.attach(self.chk_fsr41, 0, row, 2, 1)
        row += 1

        self.chk_gamescope = Gtk.CheckButton(label=_("Gamescope (Gamer Mode)"))
        self.chk_gamescope.set_active(self.cfg.get_bool("gamescope"))
        grid.attach(self.chk_gamescope, 0, row, 2, 1)
        row += 1

        self.chk_gamemode = Gtk.CheckButton(label=_("Gamemode"))
        self.chk_gamemode.set_active(self.cfg.get_bool("gamemode"))
        grid.attach(self.chk_gamemode, 0, row, 2, 1)
        row += 1

        self.chk_hdr = Gtk.CheckButton(label=_("HDR"))
        self.chk_hdr.set_active(self.cfg.get_bool("hdr"))
        grid.attach(self.chk_hdr, 0, row, 2, 1)
        row += 1

        self.chk_nvapi = Gtk.CheckButton(label=_("NVAPI Override"))
        self.chk_nvapi.set_active(self.cfg.get_bool("nvapi"))
        grid.attach(self.chk_nvapi, 0, row, 2, 1)
        row += 1

        # ── Separator ──
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep2, 0, row, 3, 1)
        row += 1

        # ── Shortcuts ──
        label = Gtk.Label(label=_("Shortcuts"))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, row, 3, 1)
        row += 1

        self.chk_desktop = Gtk.CheckButton(label=_("Desktop shortcut"))
        self.chk_desktop.set_active(True)
        grid.attach(self.chk_desktop, 0, row, 2, 1)
        row += 1

        self.chk_appmenu = Gtk.CheckButton(label=_("App menu shortcut"))
        self.chk_appmenu.set_active(True)
        grid.attach(self.chk_appmenu, 0, row, 2, 1)
        row += 1

        self.chk_steam = Gtk.CheckButton(label=_("Steam shortcut"))
        grid.attach(self.chk_steam, 0, row, 2, 1)
        row += 1

        # ── Buttons ──
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_margin_top(12)
        btn_box.set_halign(Gtk.Align.CENTER)

        btn_cancel = Gtk.Button(label=_("Cancel"))
        btn_cancel.connect(
            "clicked", lambda b: self.response(Gtk.ResponseType.CANCEL)
        )
        btn_cancel.set_size_request(140, -1)
        btn_box.append(btn_cancel)

        btn_install = Gtk.Button(label=_("Install"))
        btn_install.connect(
            "clicked", lambda b: self.response(Gtk.ResponseType.OK)
        )
        btn_install.set_size_request(140, -1)
        btn_box.append(btn_install)

        content.append(btn_box)

    # ── GTK4 FILE DIALOGS (async) ──
    def _on_browse_dir(self, btn):
        dialog = Gtk.FileDialog()
        dialog.set_title(_("Select Install Directory"))
        dialog.select_folder(self, None, self._on_dir_selected)

    def _on_dir_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.entry_dir.set_text(
                    os.path.join(folder.get_path(), "Bellum")
                )
        except Exception:  # noqa: S110
            pass  # user cancelled

    def _on_browse_prefix(self, btn):
        dialog = Gtk.FileDialog()
        dialog.set_title(_("Select Wine Prefix Folder"))
        dialog.select_folder(self, None, self._on_prefix_selected)

    def _on_prefix_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.entry_prefix.set_text(folder.get_path())
        except Exception:  # noqa: S110
            pass

    # ── DATA ──
    def get_install_data(self) -> dict[str, object]:
        return {
            "install_dir": self.entry_dir.get_text().strip(),
            "wineprefix": self.entry_prefix.get_text().strip(),
            "fsr41": self.chk_fsr41.get_active(),
            "gamescope": self.chk_gamescope.get_active(),
            "gamemode": self.chk_gamemode.get_active(),
            "hdr": self.chk_hdr.get_active(),
            "nvapi": self.chk_nvapi.get_active(),
            "shortcut_desktop": self.chk_desktop.get_active(),
            "shortcut_appmenu": self.chk_appmenu.get_active(),
            "shortcut_steam": self.chk_steam.get_active(),
        }
