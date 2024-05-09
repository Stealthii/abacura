"""Abacura configuration module"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tomlkit import TOMLDocument, parse

DEFAULT_GLOBAL_CONFIG = {
    "module_paths": [],
    "css_path": Path(__file__).parent / "css/abacura.css",
    "ga": True,
}


class Config:
    """Base configuration class"""

    _config_file: str
    name = "config"

    def __init__(self, config: str | None = None) -> None:
        super().__init__()
        config = config or "~/.abacura"
        p = Path(config).expanduser()
        if not p.is_file():
            with p.open("w", encoding="UTF-8"):
                pass
        self._config_file = config
        self.reload()

    def reload(self) -> None:
        """Reload configuration file from disk"""
        cfile = Path(self._config_file).expanduser()
        try:
            self._config = parse(cfile.open(encoding="UTF-8").read())

        except Exception as config_exception:
            raise (config_exception)

    def get_specific_option(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value for section, global, or default"""

        if section in self.config and key in self.config[section]:
            return self.config[section][key]

        if "global" in self.config and key in self.config["global"]:
            return self.config["global"][key]

        if key in DEFAULT_GLOBAL_CONFIG:
            return DEFAULT_GLOBAL_CONFIG[key]

        return default

    def data_directory(self, section: str) -> Path:
        """Returns the per-session repository of save files for persistence"""
        if (
            section in self.config
            and "data_directory" in self.config[section]
            and isinstance(self.config[section]["data_directory"], str)
        ):
            path = Path(self.config[section]["data_directory"]).expanduser() / section
        else:
            path = Path("~/Documents/abacura").expanduser() / section

        path.mkdir(parents=True, exist_ok=True)
        return path

    def ring_log(self, section: str) -> str:
        """Returns the location of the ring log"""
        path = Path(self.data_directory(section)) / "ringlog.db"
        return path.as_posix()

    @property
    def config(self) -> TOMLDocument:
        return self._config
