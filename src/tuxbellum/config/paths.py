import os
from pathlib import Path

IS_FLATPAK = "FLATPAK_ID" in os.environ or os.path.exists("/.flatpak-info")


class PathManager:
    @staticmethod
    def app_data_root() -> str:
        appdir = os.getenv("APPDIR")
        if appdir:
            candidate = Path(appdir) / "usr" / "share" / "tuxbellum"
            if candidate.exists():
                return str(candidate)

        for candidate in [
            PathManager.system_data("tuxbellum"),
            Path(__file__).resolve().parents[3],
        ]:
            if (Path(candidate) / "packages").exists():
                return str(candidate)

        return str(Path(__file__).resolve().parents[3])

    @staticmethod
    def bundled_path(*paths: str) -> str:
        return str(Path(PathManager.app_data_root()).joinpath(*paths))

    @staticmethod
    def user_home(*paths: str) -> str:
        if IS_FLATPAK:
            home = Path(os.getenv("HOST_HOME", Path.home()))
        else:
            home = Path(os.getenv("HOME", str(Path.home())))
        return str(home.joinpath(*paths))

    @staticmethod
    def system_data(*paths: str) -> str:
        for data_dir in os.getenv("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"):
            p = Path(data_dir).joinpath(*paths)
            if p.exists():
                return str(p)
        return str(Path("/usr/local/share").joinpath(*paths))

    @staticmethod
    def user_data(*paths: str) -> str:
        base = Path(os.getenv("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
        return str(base.joinpath(*paths))

    @staticmethod
    def user_config(*paths: str) -> str:
        base = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
        return str(base.joinpath(*paths))

    @staticmethod
    def user_cache(*paths: str) -> str:
        base = Path(os.getenv("XDG_CACHE_HOME", str(Path.home() / ".cache")))
        return str(base.joinpath(*paths))

    @staticmethod
    def find_binary(name: str) -> str:
        paths = os.getenv("PATH", "").split(":")
        for p in paths:
            candidate = Path(p) / name
            if candidate.exists() and candidate.is_file():
                return str(candidate)
        return ""

    @staticmethod
    def get_icon(icon_name: str) -> str:
        sizes = ["128x128", "256x256", "512x512", "scalable"]
        for size in sizes:
            for base in [
                PathManager.user_data("icons", "hicolor", size, "apps", icon_name),
                PathManager.system_data("icons", "hicolor", size, "apps", icon_name),
            ]:
                if Path(base).exists():
                    return str(base)
        return ""

    @staticmethod
    def user_local_bin() -> str:
        """Return ``~/.local/bin``, ensuring the directory exists."""
        base = Path(PathManager.user_home(), ".local", "bin")
        return str(base)
    @staticmethod
    def proton_install_path(proton_ver: str) -> str:
        return PathManager.user_data("bellum", "proton", f"bellum-{proton_ver}")

    @staticmethod
    def launcher_cache_dir() -> str:
        return PathManager.user_cache("tuxbellum", "launcher")

    @staticmethod
    def logs_dir() -> str:
        return PathManager.user_cache("tuxbellum", "logs")


path_mgr = PathManager()
