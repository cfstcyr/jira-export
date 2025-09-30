from dataclasses import dataclass
from pathlib import Path

from jira_export.models.config import Config


@dataclass
class AppState:
    config_file: Path

    def load_config(self) -> Config:
        return Config.load(self.config_file)
