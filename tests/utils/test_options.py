from types import SimpleNamespace

import pytest
import typer

from jira_export.models.app_state import AppState
from jira_export.utils import options


def _write_config(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[projects.alpha]
user = "alpha@example.com"
domain = "alpha.atlassian.net"
project = "ALPHA"

[projects.bravo]
user = "bravo@example.com"
domain = "bravo.atlassian.net"
project = "BRAVO"
""".strip()
        + "\n",
    )
    return config_path


def test_prompt_project_id_returns_supplied_value(monkeypatch, tmp_path):
    config_path = _write_config(tmp_path)
    ctx: typer.Context = SimpleNamespace(obj=AppState(config_file=config_path))  # type: ignore

    def fail_select(*_args, **_kwargs):
        raise AssertionError(
            "questionary.select should not be invoked when project_id is provided"
        )

    monkeypatch.setattr(options.questionary, "select", fail_select)

    assert options.prompt_project_id("alpha", ctx) == "alpha"


def test_prompt_project_id_selects_from_config(monkeypatch, tmp_path):
    config_path = _write_config(tmp_path)
    ctx: typer.Context = SimpleNamespace(obj=AppState(config_file=config_path))  # type: ignore
    captured = {}

    class DummyPrompt:
        def __init__(self, value: str):
            self._value = value

        def ask(self) -> str:
            return self._value

    def fake_select(message: str, choices: list[str], **_kwargs):
        captured["message"] = message
        captured["choices"] = choices
        return DummyPrompt("bravo")

    monkeypatch.setattr(options.questionary, "select", fake_select)

    assert options.prompt_project_id(None, ctx) == "bravo"
    assert captured["message"] == "Select a project"
    assert captured["choices"] == ["alpha", "bravo"]


def test_prompt_project_id_raises_when_no_projects(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text("")
    ctx: typer.Context = SimpleNamespace(obj=AppState(config_file=config_path))  # type: ignore

    with pytest.raises(typer.BadParameter):
        options.prompt_project_id(None, ctx)


def test_prompt_project_id_aborts_on_cancel(monkeypatch, tmp_path):
    config_path = _write_config(tmp_path)
    ctx: typer.Context = SimpleNamespace(obj=AppState(config_file=config_path))  # type: ignore

    class DummyPrompt:
        def ask(self) -> None:
            return None

    monkeypatch.setattr(
        options.questionary,
        "select",
        lambda *_args, **_kwargs: DummyPrompt(),
    )

    with pytest.raises(typer.Abort):
        options.prompt_project_id(None, ctx)
