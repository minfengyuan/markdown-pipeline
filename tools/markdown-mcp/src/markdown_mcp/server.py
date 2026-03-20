from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - fallback for local imports without dependency
    class FastMCP:  # type: ignore[override]
        def __init__(self, name: str) -> None:
            self.name = name

        def tool(self, func=None, **_kwargs):
            def decorator(fn):
                return fn

            if func is None:
                return decorator
            return decorator(func)

        def run(self) -> None:
            raise RuntimeError("fastmcp is not installed. Install the package dependencies first.")


mcp = FastMCP("markdown_pipeline")


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _quote_yaml_string(value: Any) -> str:
    return json.dumps(_normalize_text(value), ensure_ascii=False)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _render_frontmatter(data: dict[str, Any]) -> list[str]:
    title = _normalize_text(data.get("title"))
    note_type = _normalize_text(data.get("note_type"))
    status = _normalize_text(data.get("status"))
    tags = _as_list(data.get("tags"))

    if not (title or note_type or status or tags):
        return []

    lines: list[str] = ["---"]
    if title:
        lines.append(f"title: {_quote_yaml_string(title)}")
    if note_type:
        lines.append(f"note_type: {_quote_yaml_string(note_type)}")
    if status:
        lines.append(f"status: {_quote_yaml_string(status)}")
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {_quote_yaml_string(tag)}")
    lines.append("---")
    lines.append("")
    return lines


def _render_paragraphs(values: Any) -> list[str]:
    lines: list[str] = []
    for value in _as_list(values):
        text = _normalize_text(value)
        if text:
            lines.append(text)
            lines.append("")
    return lines


def _render_bullets(values: Any) -> list[str]:
    lines: list[str] = []
    for value in _as_list(values):
        text = _normalize_text(value)
        if text:
            lines.append(f"- {text}")
    if lines:
        lines.append("")
    return lines


def _render_numbered(values: Any) -> list[str]:
    lines: list[str] = []
    for index, value in enumerate(_as_list(values), start=1):
        text = _normalize_text(value)
        if text:
            lines.append(f"{index}. {text}")
    if lines:
        lines.append("")
    return lines


def _render_code_block(block: dict[str, Any]) -> list[str]:
    title = _normalize_text(block.get("title"))
    lang = _normalize_text(block.get("lang"))
    content = str(block.get("content") or "").rstrip()

    lines: list[str] = []
    if title:
        lines.extend([f"### {title}", ""])
    lines.extend([f"```{lang}", content, "```", ""])
    return lines


def _render_sections(sections: Any) -> list[str]:
    lines: list[str] = []
    for section in _as_list(sections):
        if not isinstance(section, dict):
            continue
        heading = _normalize_text(section.get("heading") or section.get("title") or "Section")
        lines.extend([f"## {heading}", ""])

        summary = _normalize_text(section.get("summary"))
        if summary:
            lines.extend([summary, ""])

        lines.extend(_render_paragraphs(section.get("body")))
        lines.extend(_render_bullets(section.get("items")))
        lines.extend(_render_numbered(section.get("numbered")))

        for block in _as_list(section.get("code_blocks")):
            if isinstance(block, dict):
                lines.extend(_render_code_block(block))

    return lines


def _render_global_code_blocks(code_blocks: Any) -> list[str]:
    lines: list[str] = []
    code_block_list = [block for block in _as_list(code_blocks) if isinstance(block, dict)]
    if not code_block_list:
        return lines

    lines.extend(["## Example Code", ""])
    for block in code_block_list:
        lines.extend(_render_code_block(block))
    return lines


def render_markdown_impl(data: dict[str, Any]) -> str:
    if not isinstance(data, dict):
        raise TypeError("render_markdown expects a JSON object")

    lines: list[str] = []
    lines.extend(_render_frontmatter(data))

    title = _normalize_text(data.get("title") or "Untitled")
    lines.extend([f"# {title}", ""])

    summary = _normalize_text(data.get("summary"))
    if summary:
        lines.extend([f"> {summary}", ""])

    lines.extend(_render_paragraphs(data.get("intro")))
    lines.extend(_render_sections(data.get("sections")))
    lines.extend(_render_global_code_blocks(data.get("code_blocks")))

    return "\n".join(lines).rstrip() + "\n"


def _run_formatter(command: list[str], markdown_path: Path) -> None:
    executable = shutil.which(command[0])
    if executable is None:
        return

    full_command = [executable, *command[1:], str(markdown_path)]
    subprocess.run(full_command, check=False, capture_output=True, text=True)


def _create_lint_workdir() -> Path:
    root = Path(__file__).resolve().parents[2] / ".lint-tmp"
    root.mkdir(parents=True, exist_ok=True)

    workdir = root / f"run-{uuid.uuid4().hex}"
    workdir.mkdir(parents=False, exist_ok=False)
    return workdir


def lint_markdown_impl(content: str) -> str:
    workdir = _create_lint_workdir()
    try:
        markdown_path = workdir / "document.md"
        markdown_path.write_text(content, encoding="utf-8")

        _run_formatter(["prettier", "--write"], markdown_path)
        _run_formatter(["markdownlint", "--fix"], markdown_path)

        return markdown_path.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        root = Path(__file__).resolve().parents[2] / ".lint-tmp"
        if root.exists() and not any(root.iterdir()):
            root.rmdir()


def save_markdown_impl(path: str, content: str) -> dict[str, Any]:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return {
        "ok": True,
        "path": str(out_path.resolve()),
        "bytes": out_path.stat().st_size,
    }


@mcp.tool()
def render_markdown(data: dict[str, Any]) -> str:
    """Render structured JSON into normalized Markdown."""

    return render_markdown_impl(data)


@mcp.tool()
def lint_markdown(content: str) -> str:
    """Normalize Markdown with external formatters when available."""

    return lint_markdown_impl(content)


@mcp.tool()
def save_markdown(path: str, content: str) -> dict[str, Any]:
    """Save Markdown content to disk."""

    return save_markdown_impl(path, content)


def main() -> None:
    mcp.run()

