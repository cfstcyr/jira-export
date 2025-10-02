import pytest
from pathlib import Path
from unittest.mock import patch

from jira_export.models.config import Config
from jira_export.models.project import Project
from jira_export.models.errors import ProjectNotFoundError


def test_load_nonexistent_file(tmp_path):
    config_path = tmp_path / "config.toml"
    config = Config.load(config_path)
    assert config.projects == {}


def test_load_existing_file(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """[projects.alpha]
user = "test@example.com"
domain = "test.atlassian.net"
project = "TEST"
"""
    )
    config = Config.load(config_path)
    assert "alpha" in config.projects
    assert config.projects["alpha"].user == "test@example.com"


def test_save(tmp_path):
    config = Config()
    config.projects["alpha"] = Project(
        user="test@example.com", domain="test.atlassian.net", project="TEST"
    )
    config_path = tmp_path / "config.toml"
    config.save(config_path)
    assert config_path.exists()
    # Load back to verify
    loaded = Config.load(config_path)
    assert "alpha" in loaded.projects


def test_get_project_existing():
    config = Config()
    config.projects["alpha"] = Project(
        user="test@example.com", domain="test.atlassian.net", project="TEST"
    )
    project = config.get_project("alpha")
    assert project.user == "test@example.com"


def test_get_project_not_found():
    config = Config()
    with pytest.raises(ProjectNotFoundError):
        config.get_project("nonexistent")


def test_remove_project():
    config = Config()
    config.projects["alpha"] = Project(
        user="test@example.com", domain="test.atlassian.net", project="TEST"
    )
    with patch("jira_export.models.project.keyring.delete_password"):
        config.remove_project("alpha")
    assert "alpha" not in config.projects


def test_get_and_load_project():
    config = Config()
    config.projects["alpha"] = Project(
        user="test@example.com", domain="test.atlassian.net", project="TEST"
    )
    with patch("jira_export.models.project.keyring.get_password", return_value="secret"):
        result = config.get_and_load_project("alpha")
        assert result.user == "test@example.com"
        assert result.api_key.get_secret_value() == "secret"