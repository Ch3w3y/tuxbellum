"""Main application window for the Bellum Linux Installer."""

import json
import os
import subprocess
import sys
import threading
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gtk, Gdk, GLib, Gio  # noqa: E402

from tuxbellum.app.install_dialog import InstallDialog
from tuxbellum.app.settings_dialog import SettingsDialog
from tuxbellum.app.splash import SplashWindow
from tuxbellum.app.progress_dialog import InstallProgressDialog
from tuxbellum.config.manager import ConfigManager
from tuxbellum.config.paths import path_mgr
from tuxbellum.i18n.locale import setup_gettext

_ = setup_gettext()
VERSION = "3.0.0"

CONFIG_DIR = path_mgr.user_config("tuxbellum")
GAMES_JSON = path_mgr.user_config("tuxbellum", "games.json")
os.makedirs(CONFIG_DIR, exist_ok=True)


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("TuxBellum")
        self.set_default_size(900, 600)
        self.connect("close-request", self._on_close)

        self.games: list[dict[str, Any]] = []
        self.running_processes: dict[str, subprocess.Popen[bytes]] = {}
        self.cfg = ConfigManager()

        self._load_games()
        self._setup_css()
        self._build_ui()
        self._setup_context_menu()

        GLib.timeout_add(1000, self._check_running)

    # ── CSS ────────────────────────────────────────────
    def _setup_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            flowboxchild:selected { background: transparent; }
            .game-row {
                background-color: alpha(@theme_bg_color, 0.5);
                border: 4px solid transparent;
                color: @theme_fg_color;
            }
            flowboxchild:selected .game-row {
                background-color: alpha(@theme_bg_color, 0.5);
                border-color: @theme_selected_bg_color;
            }
            flowboxchild:selected:focus .game-row {
                background-color: @theme_selected_bg_color;
                border-color: transparent;
            }
        """)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    # ── BUILD ──────────────────────────────────────────
    def _build_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(vbox)

        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_start(10)
        toolbar.set_margin_end(10)
        toolbar.set_margin_top(10)
        toolbar.set_margin_bottom(10)

        self.btn_install = Gtk.Button.new_from_icon_name("list-add-symbolic")
        self.btn_install.set_tooltip_text("Install Bellum")
        self.btn_install.connect("clicked", self._on_install)
        toolbar.append(self.btn_install)

        self.btn_settings = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
        self.btn_settings.set_tooltip_text("Settings")
        self.btn_settings.connect("clicked", self._on_settings)
        toolbar.append(self.btn_settings)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        toolbar.append(spacer)

        self.btn_stop = Gtk.Button.new_from_icon_name("media-playback-stop-symbolic")
        self.btn_stop.set_tooltip_text("Stop")
        self.btn_stop.set_sensitive(False)
        self.btn_stop.connect("clicked", self._on_stop)
        toolbar.append(self.btn_stop)

        self.btn_play = Gtk.Button.new_from_icon_name("media-playback-start-symbolic")
        self.btn_play.set_tooltip_text("Play")
        self.btn_play.connect("clicked", self._on_play)
        toolbar.append(self.btn_play)

        vbox.append(toolbar)

        # Scrolled FlowBox
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.flowbox.set_activate_on_single_click(True)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_max_children_per_line(1)
        self.flowbox.set_min_children_per_line(1)
        self.flowbox.connect("child-activated", self._on_child_activated)
        self.flowbox.connect("selected-children-changed", self._on_selection_changed)

        # Right-click via GestureClick
        gesture = Gtk.GestureClick.new()
        gesture.set_button(3)  # right button
        gesture.connect("pressed", self._on_right_click)
        self.flowbox.add_controller(gesture)

        scrolled.set_child(self.flowbox)
        vbox.append(scrolled)

        self._populate_flowbox()

    # ── CONTEXT MENU ───────────────────────────────────
    def _setup_context_menu(self):
        self._context_menu = Gio.Menu()
        self._context_menu_title = Gio.MenuItem.new("", None)
        self._context_menu.append_item(self._context_menu_title)
        self._context_menu.append_section(None, Gio.Menu())

        self._action_play = Gio.MenuItem.new(_("Play"), "win.play")
        self._context_menu.append_item(self._action_play)

        self._action_uninstall = Gio.MenuItem.new(_("Uninstall"), "win.uninstall")
        self._context_menu.append_item(self._action_uninstall)

        self._context_menu.append_section(None, Gio.Menu())
        self._action_open = Gio.MenuItem.new(
            _("Open game location"), "win.open-location"
        )
        self._context_menu.append_item(self._action_open)

        # Actions
        play_action = Gio.SimpleAction.new("play", None)
        play_action.connect("activate", self._on_context_play)
        self.add_action(play_action)

        uninstall_action = Gio.SimpleAction.new("uninstall", None)
        uninstall_action.connect("activate", self._on_context_uninstall)
        self.add_action(uninstall_action)

        open_action = Gio.SimpleAction.new("open-location", None)
        open_action.connect("activate", self._on_context_open)
        self.add_action(open_action)

        self._popover = Gtk.PopoverMenu.new_from_model(self._context_menu)
        self._popover.set_parent(self)

    # ── FLOWBOX ────────────────────────────────────────
    def _populate_flowbox(self):
        child = self.flowbox.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.flowbox.remove(child)
            child = next_child

        if self.games:
            for game in self.games:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                row.set_margin_start(10)
                row.set_margin_end(10)
                row.set_margin_top(5)
                row.set_margin_bottom(5)

                icon = Gtk.Image.new_from_icon_name("applications-games-symbolic")
                icon.set_pixel_size(24)
                row.append(icon)

                label = Gtk.Label(label=game.get("title", ""))
                label.set_halign(Gtk.Align.START)
                label.set_hexpand(True)
                row.append(label)

                cell = Gtk.FlowBoxChild()
                cell.set_child(row)
                cell.set_can_focus(True)
                cell.get_style_context().add_class("game-row")
                self.flowbox.append(cell)
        else:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.set_margin_start(10)
            row.set_margin_end(10)
            row.set_margin_top(5)
            row.set_margin_bottom(5)

            icon = Gtk.Image.new_from_icon_name("applications-games-symbolic")
            icon.set_pixel_size(24)
            row.append(icon)

            label = Gtk.Label(label=_("Bellum — Not installed"))
            label.set_halign(Gtk.Align.START)
            label.set_hexpand(True)
            row.append(label)

            cell = Gtk.FlowBoxChild()
            cell.set_child(row)
            cell.set_can_focus(False)
            cell.get_style_context().add_class("game-row")
            self.flowbox.append(cell)

    def _selected_game(self) -> dict[str, Any] | None:
        selected = self.flowbox.get_selected_children()
        if not selected:
            return None
        idx = selected[0].get_index()
        if 0 <= idx < len(self.games):
            return self.games[idx]
        return None

    # ── GAME DATA ──────────────────────────────────────
    def _load_games(self):
        if os.path.exists(GAMES_JSON):
            try:
                with open(GAMES_JSON, "r") as f:
                    self.games = json.load(f)
                if not isinstance(self.games, list):
                    self.games = []
            except (json.JSONDecodeError, FileNotFoundError):
                self.games = []

    def _save_games(self):
        with open(GAMES_JSON, "w") as f:
            json.dump(self.games, f, indent=2)

    def _add_game(self, data: dict[str, Any]):
        game = {
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
        self.games = [game]
        self._save_games()
        self._populate_flowbox()

    # ── LAUNCH / STOP ──────────────────────────────────
    def _launch_game(self, game: dict[str, Any]):
        gameid = game.get("gameid")
        if not gameid:
            return
        if gameid in self.running_processes:
            self._show_error(
                _("{} is already running.").format(game.get("title", ""))
            )
            return

        proc = subprocess.Popen(
            [sys.executable, "-m", "tuxbellum.installer.run", "--game", gameid],
            cwd=CONFIG_DIR,
            env=os.environ.copy(),
        )
        self.running_processes[gameid] = proc
        self._update_buttons()
        self._populate_flowbox()

    def _stop_game(self, game: dict[str, Any]):
        gameid = game.get("gameid")
        if gameid in self.running_processes:
            proc = self.running_processes[gameid]
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            self.running_processes.pop(gameid, None)
            self._update_buttons()
            self._populate_flowbox()

    def _check_running(self) -> bool:
        changed = False
        for gameid, proc in list(self.running_processes.items()):
            if proc.poll() is not None:
                self.running_processes.pop(gameid, None)
                changed = True
        if changed:
            self._populate_flowbox()
        self._update_buttons()
        return True

    def _update_buttons(self):
        game = self._selected_game()
        if game and game.get("gameid") in self.running_processes:
            self.btn_play.set_icon_name("media-playback-stop-symbolic")
            self.btn_play.set_tooltip_text("Stop")
            self.btn_stop.set_sensitive(True)
        else:
            self.btn_play.set_icon_name("media-playback-start-symbolic")
            self.btn_play.set_tooltip_text("Play")
            self.btn_stop.set_sensitive(False)

    # ── SIGNAL HANDLERS ────────────────────────────────
    def _on_install(self, btn):
        dialog = InstallDialog(transient_for=self)
        dialog.set_modal(True)
        dialog.present()
        dialog.connect("response", self._on_install_response)

    def _on_install_response(self, dialog: Gtk.Dialog, response_id: int):
        if response_id == Gtk.ResponseType.OK:
            data = dialog.get_install_data()
            self._start_installation(data)
        dialog.destroy()

    def _start_installation(self, data: dict[str, Any]):
        self.set_sensitive(False)

        progress = InstallProgressDialog(transient_for=self)
        progress.set_modal(True)
        progress.present()

        def _run():
            try:
                from tuxbellum.installer.precheck import validate_wineprefix_with_gui
                from tuxbellum.installer.run import InstallConfig, run_installation
                from tuxbellum.installer.proton import get_proton_install_path
                from tuxbellum.core.gpu import detect_gpu, classify_gpu
                from tuxbellum.core.logging import Logger

                wineprefix = data.get("wineprefix", "")
                workdir = os.path.dirname(os.path.abspath(__file__))
                while not os.path.exists(os.path.join(workdir, "packages")) and workdir != "/":
                    workdir = os.path.dirname(workdir)
                if workdir == "/":
                    workdir = os.getcwd()

                log_file = os.path.join(workdir, "logs", "installer.log")
                os.makedirs(os.path.dirname(log_file), exist_ok=True)

                logger = Logger(log_file)
                progress.set_log_dest(log_file)

                progress.set_status(_("Detecting GPU..."), 0.05)
                progress.append_log("Detecting GPU...")
                gpu_type, gpu_err = detect_gpu()
                if not gpu_type:
                    gpu_type = "Unknown"

                is_amd = gpu_type == "AMD"
                progress.append_log(f"GPU: {gpu_type}")

                progress.set_status(_("Running prechecks..."), 0.10)
                progress.append_log("Running prechecks...")
                from tuxbellum.installer.precheck import run_prechecks
                result = run_prechecks(
                    wineprefix,
                    "",
                    False,
                    data.get("fsr41", False),
                    logger,
                )

                config = InstallConfig(
                    wineprefix=result.wineprefix,
                    proton_path=result.proton_path,
                    gpu_type=result.gpu_type,
                    is_amd_gpu=result.is_amd_gpu,
                    launcher_installer=result.launcher_installer,
                    workdir=workdir,
                    is_fsr41=data.get("fsr41", False),
                )

                progress.set_status(_("Installing Bellum..."), 0.15)

                import time
                _install_done = [False]

                def _monitor_log():
                    if os.path.exists(log_file):
                        last_pos = 0
                        while not _install_done[0]:
                            try:
                                with open(log_file, "r") as f:
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

            except Exception as exc:
                import traceback
                progress.append_log(traceback.format_exc())
                progress.set_complete(False, str(exc))

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def _on_settings(self, btn):
        dialog = SettingsDialog(transient_for=self)
        dialog.set_modal(True)
        dialog.present()
        dialog.connect("response", self._on_settings_response)

    def _on_settings_response(self, dialog: Gtk.Dialog, response_id: int):
        if response_id == Gtk.ResponseType.OK:
            dialog.save_config()
            self.cfg.load()
        dialog.destroy()

    def _on_play(self, btn):
        game = self._selected_game()
        if game:
            self._launch_game(game)

    def _on_stop(self, btn):
        game = self._selected_game()
        if game:
            self._stop_game(game)

    def _on_child_activated(self, flowbox, child):
        idx = child.get_index()
        if 0 <= idx < len(self.games):
            game = self.games[idx]
            if game.get("gameid") in self.running_processes:
                self._show_error(
                    _("{} is already running.").format(game.get("title", ""))
                )
            else:
                self._launch_game(game)

    def _on_selection_changed(self, *args):
        self._update_buttons()

    def _on_right_click(self, gesture, n_press, x, y):
        child = self.flowbox.get_child_at_pos(int(x), int(y))
        if not child:
            return
        self.flowbox.select_child(child)
        idx = child.get_index()
        if 0 <= idx < len(self.games):
            game = self.games[idx]
            self._context_menu_title.set_label(game.get("title", ""))
            self._popover.popup()

    def _on_context_play(self, action, param):
        game = self._selected_game()
        if game:
            self._launch_game(game)

    def _on_context_uninstall(self, action, param):
        game = self._selected_game()
        if game:
            self.games = [
                g for g in self.games if g.get("gameid") != game.get("gameid")
            ]
            self._save_games()
            self._populate_flowbox()

    def _on_context_open(self, action, param):
        game = self._selected_game()
        if game:
            path = game.get("install_dir", "")
            if path and os.path.exists(path):
                subprocess.Popen(["xdg-open", path])

    def _on_close(self, *args):
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
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
