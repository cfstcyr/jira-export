import logging

import keyring
from jira import JIRA
from pydantic import BaseModel, SecretStr

from jira_export.constants import APP_NAME

logger = logging.getLogger(__name__)


class _Project(BaseModel):
    user: str
    domain: str
    project: str

    @property
    def _project_key(self) -> str:
        return f"{APP_NAME}-{self.domain}-{self.project}"

    def set_api_key(self, api_key: SecretStr):
        keyring.set_password(self._project_key, self.user, api_key.get_secret_value())

    def get_api_key(self) -> SecretStr:
        secret = keyring.get_password(self._project_key, self.user)

        if secret is None:
            raise ValueError(
                f"API key for project ID '{self._project_key}' not found in keyring."
            )

        return SecretStr(secret)


class Project(_Project):
    api_key: None = None

    def load(self) -> "LoadedProject":
        api_key = self.get_api_key()
        return LoadedProject(**self.model_dump(exclude={"api_key"}), api_key=api_key)


class LoadedProject(_Project):
    api_key: SecretStr

    def get_jira(self) -> JIRA:
        logger.debug("Creating JIRA client for project %s", self.project)
        return JIRA(
            server=f"https://{self.domain}",
            basic_auth=(self.user, self.api_key.get_secret_value()),
        )

    def save(self):
        self.set_api_key(self.api_key)

    def unload(self) -> "Project":
        return Project(**self.model_dump(exclude={"api_key"}))
