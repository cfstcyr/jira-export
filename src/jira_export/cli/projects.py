import logging
from typing import Annotated

import typer
from pydantic import SecretStr
from rich.table import Table

from jira_export.console import console
from jira_export.models.app_state import AppState
from jira_export.models.config import ProjectNotFoundError
from jira_export.models.project import LoadedProject

projects = typer.Typer(name="projects", no_args_is_help=True)

logger = logging.getLogger(__name__)


@projects.command("list")
def list_projects(ctx: typer.Context):
    app_state: AppState = ctx.obj
    config = app_state.load_config()

    table = Table(title="Projects")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("User", style="magenta")
    table.add_column("Domain", style="green")
    table.add_column("Project", style="yellow")

    for project_id, project in config.projects.items():
        table.add_row(project_id, project.user, project.domain, project.project)

    console.print(table)


@projects.command("add")
def add_project(
    ctx: typer.Context,
    project_id: Annotated[
        str, typer.Option("--project-id", "-p", help="Unique project ID", prompt=True)
    ],
    user: Annotated[
        str, typer.Option("--user", "-u", help="Jira username/email", prompt=True)
    ],
    domain: Annotated[
        str,
        typer.Option(
            "--domain",
            "-d",
            help="Jira domain (e.g., example.atlassian.net)",
            prompt=True,
        ),
    ],
    project: Annotated[
        str,
        typer.Option(
            "--project", "-P", help="Jira project key (e.g., PROJ)", prompt=True
        ),
    ],
    api_key: Annotated[
        str,
        typer.Option(
            "--api-key",
            "-k",
            help="Jira API token (will be stored securely)",
            prompt=True,
            hide_input=True,
        ),
    ],
):
    app_state: AppState = ctx.obj
    config = app_state.load_config()

    if project_id in config.projects and not typer.confirm(
        f"Project ID '{project_id}' already exists. Overwrite?", abort=True
    ):
        raise typer.Exit(code=1)

    new_project = LoadedProject(
        user=user,
        domain=domain,
        project=project,
        api_key=SecretStr(api_key),
    )

    new_project.save()
    config.projects[project_id] = new_project.unload()
    config.save(app_state.config_file)

    console.print(f"[green]Success:[/green] Project '{project_id}' added.")


@projects.command("test")
def test_project(
    ctx: typer.Context,
    project_id: Annotated[
        str, typer.Option("--project-id", "-p", help="Unique project ID", prompt=True)
    ],
):
    app_state: AppState = ctx.obj
    config = app_state.load_config()

    try:
        project = config.get_and_load_project(project_id)
    except ProjectNotFoundError as e:
        e.render(config)
        raise typer.Exit(code=1)

    jira = project.get_jira()

    try:
        my_self = jira.myself()
        console.print(
            f"[green]Success:[/green] Authenticated as '{my_self['displayName']}'"
        )
    except Exception as e:
        logger.error("Failed to authenticate: %s", e)
        raise typer.Exit(code=1)
