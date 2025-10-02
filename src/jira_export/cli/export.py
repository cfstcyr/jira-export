import logging
from enum import Enum
from typing import Annotated, cast

import typer
from jira import Issue
from jira.client import ResultList
from rich.progress import Progress

from jira_export.models.app_state import AppState
from jira_export.models.project_item import ProjectItem
from jira_export.utils.options import ProjectId, prompt_project_id

export = typer.Typer(name="export")

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    TOML = "toml"
    JSON = "json"


@export.callback(invoke_without_command=True)
def export_callback(
    ctx: typer.Context,
    project_id: ProjectId = None,
    jql: Annotated[
        str | None,
        typer.Option(
            "--jql",
            "-j",
            help="Jira Query Language (JQL) query to filter issues",
            show_default=False,
        ),
    ] = None,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help="Output format",
            show_default=True,
            case_sensitive=False,
            autocompletion=lambda: [e.value for e in OutputFormat],
        ),
    ] = OutputFormat.TOML,
):
    project_id = prompt_project_id(project_id, ctx=ctx)

    app_state: AppState = ctx.obj
    config = app_state.load_config()
    project = config.get_and_load_project(project_id)

    jira = project.get_jira()
    all_issues: list[Issue] = []
    nextToken = None

    query = f'project="{project.project}"'
    if jql:
        query = f"{query} and ({jql})"

    with Progress(transient=True) as progress:
        count = jira.approximate_issue_count(query)
        task = progress.add_task("Fetching issues...", total=count)

        while True:
            logger.debug("Fetching issues, nextToken=%s", nextToken)
            issues = cast(
                ResultList[Issue],
                jira.enhanced_search_issues(
                    query,
                    maxResults=250,
                    nextPageToken=nextToken,
                ),
            )

            all_issues.extend(issues)
            nextToken = issues.nextPageToken

            if not issues:
                break
            if not issues.nextPageToken:
                break

            progress.update(task, advance=len(issues))

    output: str
    output_dict = {
        "issues": [ProjectItem.from_issue(issue).__dict__ for issue in all_issues]
    }

    match output_format:
        case OutputFormat.TOML:
            import toml

            output = toml.dumps(output_dict)
        case OutputFormat.JSON:
            import json

            output = json.dumps(output_dict, indent=2)
        case _:
            logger.error("Unsupported output format: %s", output_format)
            raise typer.Exit(code=1)

    typer.echo(
        output.strip(),
        err=False,
    )
