from dataclasses import dataclass, field
from pathlib import Path

from jira_export.models.config import Config


@dataclass
class AppState:
    __config: Config | None = field(default=None, init=False)
    config_file: Path

    def load_config(self) -> Config:
        if self.__config is None:
            self.__config = Config.load(self.config_file)

        return self.__config
