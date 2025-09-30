# Repository Guidelines

## Project Structure & Module Organization
The Typer CLI lives in `src/jira_export/app.py`, where commands are registered on the shared `app`. The console entry point (`src/jira_export/__main__.py`) should stay a thin wrapper that calls `app()`. Add reusable sync logic in additional modules inside `src/jira_export/` and import them into `app.py`; keep command implementations small and delegate to service functions. Unit tests should mirror the package layout under `tests/`, e.g., `tests/test_app.py` targeting CLI wiring and `tests/services/` for helpers.

## Build, Test, and Development Commands
Run `uv sync` after modifying dependencies to install the locked environment. Use `uv run jira-export sync` (or simply `uv run jira-export`) to execute the default sync command. `uv run python -m jira_export --help` surfaces Typer's auto-generated help during development. Once `pytest` is added to dev dependencies, execute `uv run pytest` for the full suite; add `-k <pattern>` when focusing on specific cases.

## Coding Style & Naming Conventions
Target Python 3.13 features and stay PEP 8 compliant with 4-space indentation and 88-character lines. Modules should be lowercase with underscores, functions and variables snake_case, and Typer command functions named `sync_*` to mirror CLI verbs. Prefer explicit type hints on public functions to make Typer's help text clearer. Adopt docstrings for new modules describing the Jira data they touch. Before committing, run a formatter (`uvx ruff format` or `uvx black`) and a static check such as `uvx ruff check src tests`.

## Testing Guidelines
Write tests with `pytest` and Typer's `CliRunner`. Place unit tests in `tests/` with filenames `test_<module>.py`. Use fixtures in `tests/conftest.py` to manage Jira API doubles. Aim for at least 85% coverage on new modules and include integration-style CLI tests that assert exit codes and output.

## Commit & Pull Request Guidelines
Use Conventional Commit prefixes (`feat:`, `fix:`, `chore:`) written in the imperative mood. Reference the related Jira issue ID in either the subject or body. Pull requests should summarize the behavior change, outline manual or automated test evidence, and call out any configuration updates or secrets required for reviewers. Attach CLI transcripts or screenshots when UI-facing output changes.

## Security & Configuration Tips
Never commit Jira credentials or tokens; load them via environment variables or `.env` files ignored by git. Document expected variables in a `README` or `.env.example` update and scrub debug output before sharing logs.
