import pytest
from unittest.mock import patch

from pydantic import SecretStr

from jira_export.models.project import Project, LoadedProject
from jira_export.constants import APP_NAME


def test_project_load():
    project = Project(user="test@example.com", domain="test.atlassian.net", project="TEST")
    with patch("keyring.get_password", return_value="secret"):
        loaded = project.load()
        assert isinstance(loaded, LoadedProject)
        assert loaded.api_key.get_secret_value() == "secret"


def test_loaded_project_get_jira():
    loaded = LoadedProject(
        user="test@example.com",
        domain="test.atlassian.net",
        project="TEST",
        api_key=SecretStr("secret"),
    )
    with patch("jira_export.models.project.JIRA") as mock_jira:
        jira = loaded.get_jira()
        mock_jira.assert_called_once_with(
            server="https://test.atlassian.net", basic_auth=("test@example.com", "secret")
        )


def test_project_set_api_key():
    project = Project(user="test@example.com", domain="test.atlassian.net", project="TEST")
    with patch("jira_export.models.project.keyring.set_password") as mock_set:
        project.set_api_key(SecretStr("secret"))
        mock_set.assert_called_once_with(
            f"{APP_NAME}-test.atlassian.net-TEST", "test@example.com", "secret"
        )


def test_project_get_api_key():
    project = Project(user="test@example.com", domain="test.atlassian.net", project="TEST")
    with patch("jira_export.models.project.keyring.get_password", return_value="secret") as mock_get:
        api_key = project.get_api_key()
        assert api_key == SecretStr("secret")
        mock_get.assert_called_once_with(f"{APP_NAME}-test.atlassian.net-TEST", "test@example.com")


def test_project_get_api_key_not_found():
    project = Project(user="test@example.com", domain="test.atlassian.net", project="TEST")
    with patch("jira_export.models.project.keyring.get_password", return_value=None):
        with pytest.raises(ValueError):
            project.get_api_key()


def test_project_delete_api_key():
    project = Project(user="test@example.com", domain="test.atlassian.net", project="TEST")
    with patch("jira_export.models.project.keyring.delete_password") as mock_delete:
        project.delete_api_key()
        mock_delete.assert_called_once_with(f"{APP_NAME}-test.atlassian.net-TEST", "test@example.com")


def test_loaded_project_save():
    loaded = LoadedProject(
        user="test@example.com",
        domain="test.atlassian.net",
        project="TEST",
        api_key=SecretStr("secret"),
    )
    with patch("keyring.set_password") as mock_set:
        loaded.save()
        mock_set.assert_called_once_with(f"{APP_NAME}-test.atlassian.net-TEST", "test@example.com", "secret")


def test_loaded_project_unload():
    loaded = LoadedProject(
        user="test@example.com",
        domain="test.atlassian.net",
        project="TEST",
        api_key=SecretStr("secret"),
    )
    unloaded = loaded.unload()
    assert isinstance(unloaded, Project)
    assert unloaded.api_key is None
    assert unloaded.user == "test@example.com"


def test_project_to_rich():
    project = Project(user="test@example.com", domain="test.atlassian.net", project="TEST")
    panel = project.to_rich("alpha")
    assert panel.title == "Project: alpha"
    assert "test@example.com" in str(panel.renderable)