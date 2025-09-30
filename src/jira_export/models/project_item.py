from dataclasses import dataclass

from jira import Issue


@dataclass
class ProjectItem:
    key: str
    summary: str
    status: str | None
    assignee: str | None
    reporter: str | None
    description: str | None

    @classmethod
    def from_issue(cls, issue: Issue) -> "ProjectItem":
        return cls(
            key=issue.key,
            summary=issue.fields.summary,
            status=issue.fields.status.name if issue.fields.status else None,
            assignee=issue.fields.assignee.displayName
            if issue.fields.assignee
            else None,
            reporter=issue.fields.reporter.displayName
            if issue.fields.reporter
            else None,
            description=issue.fields.description,
        )
