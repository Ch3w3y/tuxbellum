import gettext
import locale
import os
from pathlib import Path

from tuxbellum.config.paths import path_mgr


def get_system_locale() -> str:
    for env_var in ("LANG", "LC_MESSAGES", "LC_ALL"):
        val = os.environ.get(env_var)
        if val:
            return val.split(".")[0]
    try:
        return locale.getdefaultlocale()[0] or "en_US"
    except Exception:
        return "en_US"


def get_language_from_config() -> str | None:
    config_file = path_mgr.user_config("tuxbellum", "config.ini")
    if os.path.exists(config_file):
        with open(config_file) as f:
            for line in f:
                if line.startswith("language="):
                    return line.split("=", 1)[1].strip()
    return None


CURRENT_LANG = get_language_from_config() or get_system_locale()

LOCALE_DIR = (
    path_mgr.system_data("tuxbellum", "locales")
    if os.path.isdir(path_mgr.system_data("tuxbellum", "locales"))
    else str(Path(__file__).parent.parent.parent.parent / "locales")
)


def setup_gettext() -> callable:
    try:
        t = gettext.translation(
            "tuxbellum",
            localedir=LOCALE_DIR,
            languages=[CURRENT_LANG] if CURRENT_LANG else ["en_US"],
        )
        t.install()
        return t.gettext
    except FileNotFoundError:
        gettext.install("tuxbellum", localedir=LOCALE_DIR)
        return gettext.gettext
