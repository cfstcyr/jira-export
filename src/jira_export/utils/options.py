"""Common CLI option helpers for selecting configured Jira projects."""

from typing import Annotated

import questionary
import typer

from jira_export.models.app_state import AppState

ProjectId = Annotated[
    str | None,
    typer.Option(
        "--project-id",
        "-p",
        help="Unique project ID",
        prompt=False,
    ),
]


def prompt_project_id(project_id: str | None, ctx: typer.Context) -> str:
    app_state: AppState = ctx.obj
    config = app_state.load_config()

    if project_id is None:
        choices = list(config.projects)
        if not choices:
            raise typer.BadParameter(
                "No projects configured. Run 'jira-export projects add' first.",
            )

        selected_project_id = questionary.select(
            "Select a project",
            choices=choices,
        ).ask()

        if selected_project_id is None:
            raise typer.Abort()

        return selected_project_id

    return project_id
