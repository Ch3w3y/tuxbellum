"""GTK4 application entry point for the Bellum Linux Installer."""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gio, Gtk  # noqa: E402

from tuxbellum.app.main_window import MainWindow
from tuxbellum.i18n.locale import setup_gettext

_ = setup_gettext()
VERSION = "3.0.9"


class BellumApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="io.github.ch3w3y.tuxbellum",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.window: MainWindow | None = None

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self)
        self.window.present()


def main():
    app = BellumApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
