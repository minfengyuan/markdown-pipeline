# Markdown Pipeline Skill

This repository packages a skill plus a minimal MCP server for a fixed Markdown workflow in Codex.

The intended execution path is:

`structured object -> render_markdown -> lint_markdown -> save_markdown`

## Repository Contents

- `skills/markdown-pipeline/SKILL.md`: canonical skill entry
- `tools/markdown-mcp/`: installable Python package and MCP server

## Install

Install has two parts: the MCP server and the skill.

### 1. Install the MCP Server

From `tools/markdown-mcp`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install .
```

For editable local development:

```powershell
pip install -e .
```

### 2. Register the MCP Server in Codex

Add a user-level entry to `~/.codex/config.toml` and point it at the virtual environment interpreter:

```toml
[mcp_servers.markdown_pipeline]
command = "C:/path/to/tools/markdown-mcp/.venv/Scripts/python.exe"
args = ["C:/path/to/tools/markdown-mcp/server.py"]
```

If you prefer the packaged module entrypoint:

```toml
[mcp_servers.markdown_pipeline]
command = "C:/path/to/tools/markdown-mcp/.venv/Scripts/python.exe"
args = ["-m", "markdown_mcp"]
```

### 3. Install the Skill

Copy or sync `skills/markdown-pipeline/` into your Codex user skills directory:

```text
~/.codex/skills/markdown-pipeline/SKILL.md
```

## Usage

Invoke the skill explicitly for Markdown-heavy tasks. The skill will instruct Codex to use this project's `markdown_pipeline` tools instead of writing final Markdown directly.

This is a global tool chain, not an automatic directory rule:

- `markdown_pipeline` is available from any working directory once Codex loads your user-level config.
- `markdown-pipeline` only takes effect when you explicitly mention or invoke the skill.
- The workflow is not meant to rely on `AGENTS.md` or other implicit per-directory triggers.

Example prompt:

```text
Use the markdown-pipeline skill.

Create a technical note about Monorepo + git worktree + git subtree.
First build a structured object.
Then run render_markdown.
Then run lint_markdown.
Save the result to notes/monorepo-worktree-subtree.md.
```

If the task is only to normalize existing Markdown, the skill should use `lint_markdown` and then `save_markdown` when a path is requested.

## Verify Setup

After updating Codex config, verify the MCP server is visible:

```powershell
codex mcp list
```

You should see `markdown_pipeline` in the configured server list.

## What the Skill Enforces

The skill is designed to be invoked explicitly for note, report, tutorial, and documentation tasks. It requires Codex to use this project's `markdown_pipeline` tools to:

1. Build a structured object first.
2. Render Markdown through `render_markdown`.
3. Normalize the output through `lint_markdown`.
4. Save only through `save_markdown` when a path is requested.

## Packaging Notes

`tools/markdown-mcp` now includes a `pyproject.toml`, packaged module entrypoint, and a compatibility `server.py` wrapper. This supports both direct script execution and `pip install` based workflows.

## Formatter Notes

`lint_markdown` is best-effort. It tries external formatters when available and otherwise returns the input unchanged.
