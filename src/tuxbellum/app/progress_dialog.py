"""Install progress dialog with live log streaming."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GLib", "2.0")
from gi.repository import GLib, Gtk  # noqa: E402

from tuxbellum.i18n.locale import setup_gettext

_ = setup_gettext()


class InstallProgressDialog(Gtk.Dialog):
    """Modal dialog showing real-time installation progress."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("Installing Bellum"))
        self.set_default_size(600, 400)
        self.set_modal(True)

        self._log_dest = ""
        self._build_ui()

    def _build_ui(self):
        content = self.get_content_area()
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.append(vbox)

        self.status_label = Gtk.Label(label=_("Starting installation..."))
        self.status_label.set_halign(Gtk.Align.START)
        vbox.append(self.status_label)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_hexpand(True)
        vbox.append(self.progress_bar)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(250)

        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.set_monospace(True)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled.set_child(self.log_view)
        vbox.append(scrolled)

        self.btn_close = Gtk.Button(label=_("Close"))
        self.btn_close.set_sensitive(False)
        self.btn_close.connect("clicked", lambda b: self.response(Gtk.ResponseType.OK))
        self.btn_close.set_halign(Gtk.Align.CENTER)
        vbox.append(self.btn_close)

    def set_log_dest(self, path: str) -> None:
        self._log_dest = path

    def set_status(self, text: str, fraction: float = 0.0) -> None:
        GLib.idle_add(self.status_label.set_text, text)
        GLib.idle_add(self.progress_bar.set_fraction, fraction)

    def append_log(self, text: str) -> None:
        def _append():
            buf = self.log_view.get_buffer()
            end = buf.get_end_iter()
            buf.insert(end, text + "\n")
            mark = buf.get_insert()
            self.log_view.scroll_to_mark(mark, 0.0, False, 0.0, 0.0)

        GLib.idle_add(_append)

    def set_complete(self, success: bool, error_msg: str = "") -> None:
        if success:
            GLib.idle_add(self.status_label.set_text, _("Installation complete!"))
            GLib.idle_add(self.progress_bar.set_fraction, 1.0)
        else:
            GLib.idle_add(self.status_label.set_text, _("Installation failed"))
            if error_msg:
                GLib.idle_add(self.append_log, f"ERROR: {error_msg}")
        GLib.idle_add(self.btn_close.set_sensitive, True)
