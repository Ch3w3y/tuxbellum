import os
from tuxbellum.config.paths import path_mgr
from tuxbellum.i18n.locale import get_system_locale


class ConfigManager:
    DEFAULT_CONFIG = {
        "language": "",
        "gamescope": "False",
        "fsr41": "False",
        "nvapi": "False",
        "gamemode": "False",
        "hdr": "False",
        "show_donate": "True",
        "donate_last": "",
        "install_dir": "~/Games",
    }

    def __init__(self):
        self.config_file = path_mgr.user_config("tuxbellum", "config.ini")
        self.config_dir = path_mgr.user_config("tuxbellum")
        self.config = dict(self.DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        # Set language default from system locale
        self.config["language"] = get_system_locale()

        if os.path.isfile(self.config_file):
            with open(self.config_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        key, val = line.split("=", 1)
                        self.config[key.strip()] = val.strip().strip('"')

        # Fill missing defaults
        for key, default in self.DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = default

    def save(self) -> None:
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "w") as f:
            for key, val in self.config.items():
                f.write(f"{key}={val}\n")

    def get(self, key: str, default: str = "") -> str:
        return self.config.get(key, default)

    def set(self, key: str, value: str) -> None:
        self.config[key] = str(value)

    def get_bool(self, key: str, default: bool = False) -> bool:
        val = self.config.get(key, str(default).lower())
        return val.lower() in ("true", "1", "yes", "on")

    def get_install_dir(self) -> str:
        d = self.config.get("install_dir", "~/Games")
        return os.path.expanduser(d)
