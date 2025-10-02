import logging
from pathlib import Path
from typing import Annotated

import typer

from jira_export.cli.export import export
from jira_export.cli.projects import projects
from jira_export.constants import APP_NAME
from jira_export.models.app_state import AppState
from jira_export.utils.setup_logs import setup_logs

app = typer.Typer(no_args_is_help=True)

app.add_typer(projects)
app.add_typer(projects, name="project", hidden=True)
app.add_typer(export)

logger = logging.getLogger(__name__)


@app.callback()
def main(
    ctx: typer.Context,
    *,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose output")
    ] = False,
    config_file: Annotated[
        str, typer.Option("--config-file", "-c", help="Configuration file")
    ] = typer.get_app_dir(APP_NAME) + "/config.toml",
):
    setup_logs(verbose=verbose)
    ctx.obj = AppState(config_file=Path(config_file))
