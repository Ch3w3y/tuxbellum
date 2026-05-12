"""Settings dialog for the Bellum Linux Installer."""

import webbrowser

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from tuxbellum.config.manager import ConfigManager
from tuxbellum.i18n.locale import get_system_locale, setup_gettext

_ = setup_gettext()


class SettingsDialog(Gtk.Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("Settings"))
        self.set_resizable(False)
        self.set_default_size(400, 350)

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

        # Language
        self.lbl_lang = Gtk.Label(label=_("Language"))
        self.lbl_lang.set_halign(Gtk.Align.START)
        grid.attach(self.lbl_lang, 0, 0, 1, 1)

        self.cmb_lang = Gtk.ComboBoxText()
        self.cmb_lang.set_hexpand(True)
        self._populate_languages()
        grid.attach(self.cmb_lang, 0, 1, 1, 1)

        self.chk_gamescope = Gtk.CheckButton(label=_("Enable Gamescope"))
        self.chk_gamescope.set_active(self.cfg.get_bool("gamescope"))
        grid.attach(self.chk_gamescope, 0, 2, 1, 1)

        self.chk_gamemode = Gtk.CheckButton(label=_("Enable Gamemode"))
        self.chk_gamemode.set_active(self.cfg.get_bool("gamemode"))
        grid.attach(self.chk_gamemode, 0, 3, 1, 1)

        self.chk_fsr41 = Gtk.CheckButton(label=_("Enable FSR 4.1"))
        self.chk_fsr41.set_active(self.cfg.get_bool("fsr41"))
        grid.attach(self.chk_fsr41, 0, 4, 1, 1)

        self.chk_hdr = Gtk.CheckButton(label=_("Default HDR"))
        self.chk_hdr.set_active(self.cfg.get_bool("hdr"))
        grid.attach(self.chk_hdr, 0, 5, 1, 1)

        self.chk_nvapi = Gtk.CheckButton(label=_("Default NVAPI Override"))
        self.chk_nvapi.set_active(self.cfg.get_bool("nvapi"))
        grid.attach(self.chk_nvapi, 0, 6, 1, 1)

        self.chk_donate = Gtk.CheckButton(label=_("Show donate reminder"))
        self.chk_donate.set_active(self.cfg.get_bool("show_donate", True))
        grid.attach(self.chk_donate, 0, 7, 1, 1)

        # Support buttons
        support_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        support_box.set_margin_top(10)
        support_box.set_halign(Gtk.Align.CENTER)

        btn_kofi = Gtk.Button(label="Ko-fi")
        btn_kofi.connect(
            "clicked",
            lambda b: webbrowser.open("https://ko-fi.com/K3K210EMDU"),
        )
        support_box.append(btn_kofi)

        btn_paypal = Gtk.Button(label="PayPal")
        btn_paypal.connect(
            "clicked",
            lambda b: webbrowser.open(
                "https://www.paypal.com/donate/?business=57PP9DVD3VWAN"
                "&no_recurring=0&currency_code=USD"
            ),
        )
        support_box.append(btn_paypal)

        grid.attach(support_box, 0, 8, 1, 1)

        # Dialog buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_margin_top(12)
        btn_box.set_halign(Gtk.Align.CENTER)

        btn_cancel = Gtk.Button(label=_("Cancel"))
        btn_cancel.connect("clicked", lambda b: self.response(Gtk.ResponseType.CANCEL))
        btn_cancel.set_size_request(140, -1)
        btn_box.append(btn_cancel)

        btn_ok = Gtk.Button(label=_("Ok"))
        btn_ok.connect("clicked", lambda b: self.response(Gtk.ResponseType.OK))
        btn_ok.set_size_request(140, -1)
        btn_box.append(btn_ok)

        content.append(btn_box)

    def _populate_languages(self):
        locales = {
            "en_US": "English",
            "pt_BR": "Portuguese (Brazil)",
            "es": "Spanish",
            "de": "German",
            "fr": "French",
            "it": "Italian",
            "ja": "Japanese",
            "ko": "Korean",
            "ru": "Russian",
            "zh_CN": "Chinese (Simplified)",
        }
        current = self.cfg.get("language", "")
        if not current:
            current = get_system_locale()

        self.cmb_lang.append("", _("System Default"))
        for code, name in locales.items():
            self.cmb_lang.append(code, name)
            if current.startswith(code):
                self.cmb_lang.set_active_id(code)

        if not self.cmb_lang.get_active_id():
            self.cmb_lang.set_active_id("")

    def save_config(self):
        lang_id = self.cmb_lang.get_active_id()
        if lang_id is not None:
            self.cfg.set("language", lang_id)
        for key, widget in [
            ("gamescope", self.chk_gamescope),
            ("gamemode", self.chk_gamemode),
            ("fsr41", self.chk_fsr41),
            ("hdr", self.chk_hdr),
            ("nvapi", self.chk_nvapi),
        ]:
            self.cfg.set(key, "True" if widget.get_active() else "False")
        self.cfg.set(
            "show_donate",
            "True" if self.chk_donate.get_active() else "False",
        )
        self.cfg.save()
