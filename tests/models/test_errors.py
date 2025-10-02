from jira_export.models.errors import ProjectNotFoundError
from jira_export.models.config import Config
from jira_export.models.project import Project


def test_project_not_found_error():
    config = Config()
    config.projects["alpha"] = Project(user="test", domain="test", project="TEST")
    error = ProjectNotFoundError("beta", config)
    assert "beta" in str(error)
    assert "Available projects" in str(error)