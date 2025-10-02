from unittest.mock import MagicMock

from jira_export.models.project_item import ProjectItem


def test_from_issue():
    mock_issue = MagicMock()
    mock_issue.key = "TEST-1"
    mock_issue.fields.summary = "Summary"
    mock_issue.fields.status.name = "Open"
    mock_issue.fields.assignee.displayName = "Assignee"
    mock_issue.fields.reporter.displayName = "Reporter"
    mock_issue.fields.description = "Desc"
    item = ProjectItem.from_issue(mock_issue)
    assert item.key == "TEST-1"
    assert item.summary == "Summary"
    assert item.status == "Open"
    assert item.assignee == "Assignee"
    assert item.reporter == "Reporter"
    assert item.description == "Desc"


def test_from_issue_none_fields():
    mock_issue = MagicMock()
    mock_issue.key = "TEST-1"
    mock_issue.fields.summary = "Summary"
    mock_issue.fields.status = None
    mock_issue.fields.assignee = None
    mock_issue.fields.reporter = None
    mock_issue.fields.description = None
    item = ProjectItem.from_issue(mock_issue)
    assert item.status is None
    assert item.assignee is None
    assert item.reporter is None
    assert item.description is None