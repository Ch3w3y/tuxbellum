import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GLib", "2.0")

import os
import threading

from gi.repository import GdkPixbuf, GLib, Gtk  # noqa: E402

from tuxbellum.app.install_dialog import InstallDialog  # noqa: E402
from tuxbellum.app.progress_dialog import InstallProgressDialog  # noqa: E402
from tuxbellum.app.settings_dialog import SettingsDialog  # noqa: E402
from tuxbellum.config.manager import ConfigManager  # noqa: E402
from tuxbellum.config.paths import path_mgr  # noqa: E402
from tuxbellum.domain.install_manifest import InstallManifest  # noqa: E402
from tuxbellum.domain.install_state import discover_manifest  # noqa: E402
from tuxbellum.i18n.locale import setup_gettext  # noqa: E402

_tr = setup_gettext()
VERSION = "4.0.5"

CONFIG_DIR = path_mgr.user_config("tuxbellum")
os.makedirs(CONFIG_DIR, exist_ok=True)


class MainWindow(Gtk.ApplicationWindow):
    """Main application window for TuxBellum."""

    def __init__(self, **kwargs):
        """Initialize the window."""
        super().__init__(**kwargs)
        self.set_title("TuxBellum")
        self.set_default_size(500, 400)
        self.connect("close-request", self._on_close)

        self.cfg = ConfigManager()
        self.manifest: InstallManifest | None = None
        self._discover_install()
        self._build_ui()

    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_halign(Gtk.Align.CENTER)
        self.set_child(vbox)

        # Logo
        logo_path = path_mgr.get_icon("bellum.png")
        if not logo_path or not os.path.exists(logo_path):
            dev_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "data", "icons", "bellum.png"
            )
            dev_path = os.path.abspath(dev_path)
            if os.path.exists(dev_path):
                logo_path = dev_path
        if logo_path and os.path.exists(logo_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 400, 400, True)
            logo = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            logo = Gtk.Image.new_from_icon_name("image-missing")
            logo.set_pixel_size(128)
        vbox.append(logo)

        # State label
        if self.manifest:
            state_text = _tr("Bellum is installed")
            state_detail = _tr(f"WINEPREFIX: {self.manifest.wineprefix}")
        else:
            state_text = _tr("Bellum is not installed")
            state_detail = _tr("Use the button below to install.")

        label_state = Gtk.Label(label=state_text)
        label_state.set_markup(f"<b>{state_text}</b>")
        vbox.append(label_state)

        label_detail = Gtk.Label(label=state_detail)
        label_detail.set_wrap(True)
        vbox.append(label_detail)

        # Launch button (only when installed)
        self.btn_launch = Gtk.Button(label=_tr("Launch Bellum"))
        self.btn_launch.set_size_request(280, 48)
        self.btn_launch.connect("clicked", self._on_launch)
        self.btn_launch.set_sensitive(self.manifest is not None)
        self.btn_launch.set_visible(self.manifest is not None)
        vbox.append(self.btn_launch)

        # Install button (always visible)
        btn_install = Gtk.Button(
            label=_tr("Reinstall / Repair") if self.manifest else _tr("Install Bellum")
        )
        btn_install.set_size_request(280, 48)
        btn_install.connect("clicked", self._on_install)
        vbox.append(btn_install)

        # Post-install hint
        if self.manifest:
            hint = Gtk.Label(label=_tr("Launch Bellum from your desktop or app menu."))
            hint.set_wrap(True)
            vbox.append(hint)

        # Settings button
        btn_settings = Gtk.Button(label=_tr("Settings"))
        btn_settings.set_size_request(280, 48)
        btn_settings.connect("clicked", self._on_settings)
        vbox.append(btn_settings)

        # Exit
        btn_exit = Gtk.Button(label=_tr("Exit"))
        btn_exit.set_size_request(280, 48)
        btn_exit.connect("clicked", self._on_close)
        vbox.append(btn_exit)

    def _discover_install(self):
        """Try to find an existing TuxBellum-managed installation."""
        wineprefix = self.cfg.get("last_wineprefix", "")
        if wineprefix:
            self.manifest = discover_manifest(wineprefix)

    def _on_install_complete(self, wineprefix: str):
        """Handle completion of a successful installation."""
        self.cfg.set("last_wineprefix", wineprefix)
        self.cfg.save()
        self.manifest = discover_manifest(wineprefix)
        if hasattr(self, "btn_launch"):
            self.btn_launch.set_sensitive(self.manifest is not None)

    def _on_install(self, _btn):
        dialog = InstallDialog(transient_for=self)
        dialog.set_modal(True)
        dialog.present()
        dialog.connect("response", self._on_install_response)

    def _on_launch(self, _btn):
        if not self.manifest:
            return
        cmd = [self.manifest.launcher_path]

        launch_opts = self.manifest.launch_options

        if launch_opts.get("gamescope"):
            gamescope_args = [
                "gamescope",
                "-f",
                "--force-grab-cursor",
            ]
            if launch_opts.get("hdr"):
                gamescope_args.extend(["--hdr-enabled", "--hdr-itm-enable"])
            gamescope_args.append("--")
            cmd = gamescope_args + cmd

        if launch_opts.get("gamemode"):
            cmd = ["gamemoderun"] + cmd

        env = os.environ.copy()
        if launch_opts.get("hdr"):
            env["DXVK_HDR"] = "1"
        if launch_opts.get("nvapi"):
            env["PROTON_ENABLE_NVAPI"] = "1"
            env["DXVK_ENABLE_NVAPI"] = "1"

        import subprocess

        try:
            subprocess.Popen(cmd, env=env, start_new_session=True)
        except Exception as e:
            self._show_error(f"Failed to launch Bellum: {e}")

    def _on_install_response(self, dialog: Gtk.Dialog, response_id: int):
        if response_id == Gtk.ResponseType.OK:
            data = dialog.get_install_data()
            wineprefix = data.get("wineprefix", "")

            # Check NVMe
            import os

            from tuxbellum.installer.precheck import _is_ssd

            parent = wineprefix.rstrip("/")
            while not os.path.isdir(parent) and parent != "/":
                parent = os.path.dirname(parent)

            if not _is_ssd(parent, None):
                dialog_confirm = Gtk.MessageDialog(
                    transient_for=self,
                    modal=True,
                    message_type=Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text=_tr(
                        "Astarte Developers strongly recommend using NVMe or SSD "
                        "for the game.\n\nAre you sure you want to proceed?"
                    ),
                )

                def _on_response(d, resp):
                    d.destroy()
                    if resp == Gtk.ResponseType.YES:
                        self._start_installation(data)

                dialog_confirm.connect("response", _on_response)
                dialog_confirm.present()
                dialog.destroy()
                return

            self._start_installation(data)
        dialog.destroy()

    def _start_installation(self, data: dict[str, str]):
        self.set_sensitive(False)

        progress = InstallProgressDialog(transient_for=self)
        progress.set_modal(True)

        def _on_progress_response(dlg, response_id):
            self.set_sensitive(True)
            dlg.destroy()

        progress.connect("response", _on_progress_response)
        progress.present()

        def _run():
            try:
                from tuxbellum.core.logging import Logger
                from tuxbellum.installer.run import InstallConfig, run_installation

                wineprefix = data.get("wineprefix", "")
                resource_root = path_mgr.app_data_root()
                cache_dir = path_mgr.launcher_cache_dir()
                log_file = os.path.join(path_mgr.logs_dir(), "installer.log")
                os.makedirs(os.path.dirname(log_file), exist_ok=True)

                logger = Logger(log_file)
                progress.set_log_dest(log_file)

                progress.set_status(_tr("Starting installation..."), 0.05)
                progress.append_log("Starting installation...")

                config = InstallConfig(
                    wineprefix=wineprefix,
                    resource_root=resource_root,
                    cache_dir=cache_dir,
                    is_fsr41=data.get("fsr41", "") in ("true", "True", True),
                )

                progress.set_status(_tr("Installing Bellum..."), 0.15)

                import time

                _install_done = [False]

                def _monitor_log():
                    if os.path.exists(log_file):
                        last_pos = 0
                        while not _install_done[0]:
                            try:
                                with open(log_file) as f:
                                    f.seek(last_pos)
                                    new = f.read()
                                    if new:
                                        for line in new.rstrip().split("\n"):
                                            progress.append_log(line)
                                    last_pos = f.tell()
                            except Exception:
                                pass
                            time.sleep(0.3)

                t = threading.Thread(target=_monitor_log, daemon=True)
                t.start()

                try:
                    run_installation(config, logger)
                    _install_done[0] = True
                    t.join(timeout=2)

                    progress.set_complete(True)
                    GLib.idle_add(self._on_install_complete, wineprefix)
                except Exception as exc:
                    _install_done[0] = True
                    t.join(timeout=2)
                    progress.append_log(str(exc))
                    progress.set_complete(False, str(exc))

                logger.close()

            except Exception as outer_exc:
                import traceback

                progress.append_log(traceback.format_exc())
                progress.set_complete(False, str(outer_exc))

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def _on_settings(self, _btn):
        dialog = SettingsDialog(transient_for=self)
        dialog.set_modal(True)
        dialog.present()
        dialog.connect("response", self._on_settings_response)

    def _on_settings_response(self, dialog: Gtk.Dialog, response_id: int):
        if response_id == Gtk.ResponseType.OK:
            dialog.save_config()
            self.cfg.load()

            # Sync launch flags to the manifest
            if self.manifest:
                for key in ("gamescope", "gamemode", "fsr41", "hdr", "nvapi"):
                    self.manifest.launch_options[key] = self.cfg.get_bool(key)
                from tuxbellum.domain.install_state import save_manifest

                save_manifest(self.manifest, self.manifest.wineprefix)
        dialog.destroy()

    def _on_close(self, *_args):
        self.get_application().quit()
        return False

    def _show_error(self, msg: str):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=msg,
        )
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()
