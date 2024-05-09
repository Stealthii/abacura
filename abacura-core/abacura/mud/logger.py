"""
Logging module for sessions
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from abacura import Config


class AbacuraLogger:
    def __init__(self, name: str, config: Config) -> None:
        if config.get_specific_option(name, "log_dir"):
            logfile = Path(config.get_specific_option(name, "log_dir")).expanduser()
            self.logfile = logfile.joinpath(datetime.now().strftime(config.get_specific_option(name, "log_file")))
        else:
            self.logfile = None

        if self.logfile:
            logging.basicConfig(filename=self.logfile, filemode="a", level=logging.DEBUG)
            self.logger = logging.getLogger("abacura-kallisti")
        else:
            self.logger = None

    def info(self, msg: str, **kwargs: Any) -> None:
        if self.logger:
            self.logger.info(msg, *kwargs)

    def warn(self, msg: str, **kwargs: Any) -> None:
        if self.logger:
            self.logger.warning(msg, *kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        if self.logger:
            self.logger.error(msg, *kwargs)
