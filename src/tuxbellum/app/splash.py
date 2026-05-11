"""Game launch splash window."""

import os
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, GdkPixbuf  # noqa: E402

from tuxbellum.config.paths import path_mgr
from tuxbellum.i18n.locale import setup_gettext

_ = setup_gettext()


class SplashWindow(Gtk.Window):
    def __init__(self, title: str = "TuxBellum"):
        super().__init__()
        self.set_title(title)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(280, -1)
        self._build_ui()

    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(vbox)

        # Icon
        icon_path = path_mgr.get_icon("bellum.png")
        if icon_path and os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_path)
                scaled = pixbuf.scale_simple(
                    80, 80, GdkPixbuf.InterpType.BILINEAR
                )
                image = Gtk.Image.new_from_pixbuf(scaled)
            except Exception:  # noqa: S110
                image = Gtk.Image.new_from_icon_name(
                    "applications-games-symbolic"
                )
        else:
            image = Gtk.Image.new_from_icon_name(
                "applications-games-symbolic"
            )

        image.set_pixel_size(80)
        image.set_margin_top(20)
        image.set_margin_start(20)
        image.set_margin_end(20)
        image.set_margin_bottom(10)
        vbox.append(image)

        self.label = Gtk.Label(label=_("Starting Bellum..."))
        self.label.set_margin_start(20)
        self.label.set_margin_end(20)
        self.label.set_margin_bottom(20)
        vbox.append(self.label)

    def set_status(self, text: str):
        self.label.set_text(text)
