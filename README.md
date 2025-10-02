# jira-export

Lightweight CLI for exporting Jira issues to TOML or JSON using reusable project
profiles.

## Requirements
- Python 3.13 or newer.
- [`uv`](https://docs.astral.sh/uv/) installed and on your `PATH`.
- Access to an Atlassian Cloud Jira project and a personal API token.
- A working system keyring (macOS Keychain, Windows Credential Manager, or a
  Secret Service backend on Linux) to store your Jira token securely.

## Installation
Install the latest published build directly from GitHub:

```bash
uv tool install git+https://github.com/cfstcyr/jira-export
```

This exposes the `jira-export` executable on your `PATH`. Verify the install
with:

```bash
jira-export --help
```

## First Run
1. [Create a Jira API token](https://id.atlassian.com/manage-profile/security/api-tokens)
   for the account that has access to the project you want to export.
2. Add a project profile to the CLI; the command will prompt for the details and
   store the API token in your system keyring:

   ```bash
   jira-export projects add
   ```

   Supply:
   - `project_id`: Friendly name you will reference later (e.g. `product`).
   - `user`: Jira username or email.
   - `domain`: Jira domain such as `example.atlassian.net`.
   - `project`: Jira project key, e.g. `PROD`.
   - `api_key`: The API token you generated.

3. List saved projects any time with:

   ```bash
   jira-export projects list
   ```

## Configuration Reference
By default configuration lives next to your operating system's config folder
under the `jira-export` application directory:

| Platform | Config file path |
| --- | --- |
| macOS | `~/Library/Application Support/jira-export/config.toml` |
| Linux | `~/.config/jira-export/config.toml` |
| Windows | `%APPDATA%\\jira-export\\config.toml` |

Use `--config-file` to point the CLI at an alternate configuration, e.g.:

```bash
jira-export --config-file ./jira-config.toml projects list
```

The config file keeps non-secret project metadata. API tokens are stored only in
your keyring.

## Export Issues
Run the exporter with a saved `project_id`. Results are printed to `stdout`, so
pipe or redirect as needed. If you omit `--project-id`, the CLI prompts you to
select from the configured projects.

```bash
jira-export export --project-id product > product.toml
```

Key options:
- `--jql`: Add extra JQL filters, e.g.
  `jira-export export -p product --jql "status = \"In Progress\""`.
- `--format`: Choose `toml` (default) or `json`.
- `--verbose`: Show detailed logs, including Jira API pagination progress.

The command reports progress while fetching issues and exits with a non-zero
status if the project profile cannot be found.

## Working With The Output
- TOML output contains a single `issues` array. Each issue includes the fields
  sent by the Jira API, flattened for easy consumption.
- Switch to JSON when integrating with other tooling:

  ```bash
  jira-export export -p product --format json | jq '.issues | length'
  ```

## Troubleshooting
- **Missing project profile:** Run `jira-export projects list` to confirm the
  `project_id`. Re-add it with `jira-export projects add` if necessary.
- **Keyring errors on Linux:** Install a Secret Service backend such as
  `gnome-keyring` or `KWallet`, then rerun the add command.
- **Multiple configs:** Always pass `--config-file` when scripting to avoid
  relying on machine-specific defaults.

For full help on any command, append `--help`, e.g. `jira-export export --help`.
