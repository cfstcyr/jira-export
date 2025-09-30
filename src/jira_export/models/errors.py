import sys
from pathlib import Path
from typing import TYPE_CHECKING

from click.exceptions import UsageError
from rich.console import Console
from typer import Context

if TYPE_CHECKING:
    from jira_export.models.config import Config


class ProjectNotFoundError(UsageError):
    project_id: str

    def __init__(self, project_id: str, config: "Config", ctx: Context | None = None):
        console = Console(record=True)

        console.print(
            f"Project with ID '{project_id}' not found in config."
            "\n\n"
            f"[yellow]Available projects: [italic]{', '.join(config.projects.keys())}[/italic][/yellow]"
            "\n"
            f"Use \"{Path(sys.argv[0]).name} projects add -p {project_id}\" to add it.",
        )

        super().__init__(
            console.export_text(styles=True),
            ctx=ctx,
        )
