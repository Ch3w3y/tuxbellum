import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GLib", "2.0")

import json
import os
import threading
from typing import Any

from gi.repository import GdkPixbuf, GLib, Gtk  # noqa: E402

from tuxbellum.app.install_dialog import InstallDialog  # noqa: E402
from tuxbellum.app.progress_dialog import InstallProgressDialog  # noqa: E402
from tuxbellum.app.settings_dialog import SettingsDialog  # noqa: E402
from tuxbellum.config.manager import ConfigManager  # noqa: E402
from tuxbellum.config.paths import path_mgr  # noqa: E402
from tuxbellum.i18n.locale import setup_gettext  # noqa: E402

_tr = setup_gettext()
VERSION = "3.0.9"

CONFIG_DIR = path_mgr.user_config("tuxbellum")
GAMES_JSON = path_mgr.user_config("tuxbellum", "games.json")
os.makedirs(CONFIG_DIR, exist_ok=True)


class MainWindow(Gtk.ApplicationWindow):
    """Main application window for the Bellum Linux Installer."""

    def __init__(self, **kwargs):
        """Initialize the window."""
        super().__init__(**kwargs)
        self.set_title("TuxBellum")
        self.set_default_size(500, 400)
        self.connect("close-request", self._on_close)

        self.cfg = ConfigManager()
        self.games: list[dict[str, Any]] = []
        self._load_games()
        self._build_ui()

    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_halign(Gtk.Align.CENTER)
        self.set_child(vbox)

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

        self.btn_launch = Gtk.Button(label=_tr("Launch Bellum"))
        self.btn_launch.set_size_request(280, 48)
        self.btn_launch.connect("clicked", self._on_launch)
        self.btn_launch.set_sensitive(bool(self.games))
        vbox.append(self.btn_launch)

        btn_install = Gtk.Button(label=_tr("Install Astarte Launcher"))
        btn_install.set_size_request(280, 48)
        btn_install.connect("clicked", self._on_install)
        vbox.append(btn_install)

        btn_settings = Gtk.Button(label=_tr("Settings"))
        btn_settings.set_size_request(280, 48)
        btn_settings.connect("clicked", self._on_settings)
        vbox.append(btn_settings)

        btn_exit = Gtk.Button(label=_tr("Exit"))
        btn_exit.set_size_request(280, 48)
        btn_exit.connect("clicked", self._on_close)
        vbox.append(btn_exit)

    def _load_games(self):
        if os.path.exists(GAMES_JSON):
            try:
                with open(GAMES_JSON) as f:
                    self.games = json.load(f)
                if not isinstance(self.games, list):
                    self.games = []
            except (json.JSONDecodeError, FileNotFoundError):
                self.games = []

    def _save_games(self):
        with open(GAMES_JSON, "w") as f:
            json.dump(self.games, f, indent=2)

    def _add_game(self, data: dict[str, Any]):
        self.games = [
            {
                "gameid": "bellum",
                "title": "Bellum",
                "install_dir": data.get("install_dir", ""),
                "wineprefix": data.get("wineprefix", ""),
                "fsr41": data.get("fsr41", False),
                "gamescope": data.get("gamescope", False),
                "gamemode": data.get("gamemode", False),
                "hdr": data.get("hdr", False),
                "nvapi": data.get("nvapi", False),
                "shortcut_desktop": data.get("shortcut_desktop", False),
                "shortcut_appmenu": data.get("shortcut_appmenu", False),
                "shortcut_steam": data.get("shortcut_steam", False),
            }
        ]
        self._save_games()
        if hasattr(self, "btn_launch"):
            self.btn_launch.set_sensitive(True)

    def _on_install(self, _btn):
        dialog = InstallDialog(transient_for=self)
        dialog.set_modal(True)
        dialog.present()
        dialog.connect("response", self._on_install_response)

    def _on_launch(self, _btn):
        if not self.games:
            return
        game = self.games[0]
        cmd = ["/usr/local/bin/Bellum"]

        if game.get("gamescope"):
            gamescope_args = [
                "gamescope",
                "-f",
                "--force-grab-cursor",
            ]
            if game.get("hdr"):
                gamescope_args.extend(["--hdr-enabled", "--hdr-itm-enable"])
            gamescope_args.append("--")
            cmd = gamescope_args + cmd

        if game.get("gamemode"):
            cmd = ["gamemoderun"] + cmd

        env = os.environ.copy()
        if game.get("hdr"):
            env["DXVK_HDR"] = "1"
        if game.get("nvapi"):
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

    def _start_installation(self, data: dict[str, Any]):
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
                from tuxbellum.core.gpu import detect_gpu
                from tuxbellum.core.logging import Logger
                from tuxbellum.installer.run import InstallConfig, run_installation

                wineprefix = data.get("wineprefix", "")
                resource_root = path_mgr.app_data_root()
                cache_dir = path_mgr.launcher_cache_dir()
                log_file = os.path.join(path_mgr.logs_dir(), "installer.log")
                os.makedirs(os.path.dirname(log_file), exist_ok=True)

                logger = Logger(log_file)
                progress.set_log_dest(log_file)

                progress.set_status(_tr("Detecting GPU..."), 0.05)
                progress.append_log("Detecting GPU...")
                gpu_type, _ = detect_gpu()
                if not gpu_type:
                    gpu_type = "Unknown"

                progress.append_log(f"GPU: {gpu_type}")

                progress.set_status(_tr("Running prechecks..."), 0.10)
                progress.append_log("Running prechecks...")
                from tuxbellum.installer.precheck import run_prechecks

                result = run_prechecks(
                    wineprefix,
                    "",
                    False,
                    data.get("fsr41", False),
                    resource_root,
                    logger,
                )

                config = InstallConfig(
                    wineprefix=result.wineprefix,
                    proton_path=result.proton_path,
                    gpu_type=result.gpu_type,
                    is_amd_gpu=result.is_amd_gpu,
                    launcher_installer=result.launcher_installer,
                    resource_root=resource_root,
                    cache_dir=cache_dir,
                    is_fsr41=data.get("fsr41", False),
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
                    GLib.idle_add(self._add_game, data)
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

            # Sync launch flags to the active game entry
            if self.games:
                game = self.games[0]
                for key in ("gamescope", "gamemode", "fsr41", "hdr", "nvapi"):
                    game[key] = self.cfg.get_bool(key)
                self._save_games()
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
