import logging
import sys
from pathlib import Path

import toml
from pydantic import BaseModel, Field
from rich.panel import Panel

from jira_export.console import console
from jira_export.models.project import LoadedProject, Project

logger = logging.getLogger(__name__)


class ProjectNotFoundError(Exception):
    project_id: str

    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project with ID '{project_id}' not found in config.")

    def render(self, config: "Config"):
        console.print(
            Panel(
                f"[yellow]Available projects: [italic]{', '.join(config.projects.keys())}[/]"
                "\n\n"
                f"[bold]Use '{Path(sys.argv[0]).name} projects add -p {self.project_id}'[/]",
                title="[red]Error[/red]",
                subtitle=str(self),
                style="red",
            )
        )


class Config(BaseModel):
    projects: dict[str, Project] = Field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "Config":
        if not path.exists():
            logger.debug("Config file %s does not exist. Returning empty config.", path)
            return cls()

        logger.debug("Loading config file %s", path)
        with path.open() as f:
            data = toml.load(f)

        return cls.model_validate(data)

    def save(self, path: Path):
        path.parent.mkdir(exist_ok=True, parents=True)

        logger.debug("Saving config file %s", path)
        with path.open("w") as f:
            toml.dump(self.model_dump(), f)

    def get_project(self, project_id: str) -> Project:
        project = self.projects.get(project_id)

        if not project:
            raise ProjectNotFoundError(project_id=project_id)

        return project

    def get_and_load_project(self, project_id: str) -> LoadedProject:
        return self.get_project(project_id).load()
