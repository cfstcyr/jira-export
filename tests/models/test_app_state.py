import pytest
from pathlib import Path

from jira_export.models.app_state import AppState
from jira_export.models.config import Config


def test_load_config(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """[projects.alpha]
user = "test@example.com"
domain = "test.atlassian.net"
project = "TEST"
"""
    )
    app_state = AppState(config_file=config_file)
    config = app_state.load_config()
    assert isinstance(config, Config)
    assert "alpha" in config.projects
    # Test caching
    config2 = app_state.load_config()
    assert config is config2


def test_load_config_empty(tmp_path):
    config_file = tmp_path / "config.toml"
    app_state = AppState(config_file=config_file)
    config = app_state.load_config()
    assert isinstance(config, Config)
    assert config.projects == {}