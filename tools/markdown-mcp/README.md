# markdown-mcp

`markdown-mcp` is a minimal MCP server that keeps Markdown generation on a narrow, auditable pipeline:

`structured object -> render_markdown -> lint_markdown -> save_markdown`

## Tool Surface

- `render_markdown`
- `lint_markdown`
- `save_markdown`

No helper tools are exposed. The skill is expected to enforce the workflow.

The companion skill in `skills/markdown-pipeline/SKILL.md` should be the place that tells Codex to use these tools for Markdown normalization.

## Package Install

From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install .
```

For editable development installs:

```powershell
pip install -e .
```

## Runtime Entrypoints

You can start the server in either of these ways:

```powershell
python server.py
```

```powershell
python -m markdown_mcp
```

The repository keeps `server.py` as a compatibility wrapper around the packaged module.

## Codex Config

Add a user-level entry to `~/.codex/config.toml` and point it at the virtual environment interpreter:

```toml
[mcp_servers.markdown_pipeline]
command = "C:/path/to/tools/markdown-mcp/.venv/Scripts/python.exe"
args = ["C:/path/to/tools/markdown-mcp/server.py"]
```

If you prefer the module entrypoint, use:

```toml
[mcp_servers.markdown_pipeline]
command = "C:/path/to/tools/markdown-mcp/.venv/Scripts/python.exe"
args = ["-m", "markdown_mcp"]
```

## Formatter Behavior

`lint_markdown` attempts `prettier` and `markdownlint` when they are present on `PATH`. If neither tool is installed, the function returns the content unchanged.
