---
name: markdown-pipeline
description: Use this skill for note, report, tutorial, and documentation tasks that should be normalized through this project's markdown_pipeline MCP tools.
---

# Markdown Pipeline

Use this skill when the task creates, rewrites, or normalizes Markdown content for notes, reports, tutorials, or documentation.

## Required Tooling

Use the MCP tools provided by this project through the `markdown_pipeline` server:

- `render_markdown`
- `lint_markdown`
- `save_markdown`

Do not bypass these tools unless the user explicitly asks to skip the pipeline.

## Authoring Workflow

For new Markdown content:

1. Build a structured object first.
2. Pass that object to `render_markdown`.
3. Pass the rendered result to `lint_markdown`.
4. If the user asked for a file, write it with `save_markdown`.

Do not write final Markdown directly before the tool flow runs.

## Normalization Workflow

For existing Markdown that only needs cleanup or normalization:

1. Keep the Markdown body as the source of truth.
2. Run `lint_markdown` to normalize formatting.
3. If the user asked for a file, write it with `save_markdown`.

## Structured Object Contract

Prefer this shape for authoring tasks:

```json
{
  "title": "Short title",
  "summary": "One-line summary",
  "tags": ["tag1", "tag2"],
  "note_type": "technical_note",
  "status": "draft",
  "intro": ["Optional intro paragraph."],
  "sections": [
    {
      "heading": "Section title",
      "summary": "Optional section summary",
      "body": ["Paragraph one.", "Paragraph two."],
      "items": ["Bullet one", "Bullet two"],
      "numbered": ["First", "Second"],
      "code_blocks": [
        {
          "title": "Example",
          "lang": "bash",
          "content": "echo hello"
        }
      ]
    }
  ],
  "code_blocks": [
    {
      "title": "Global example",
      "lang": "json",
      "content": "{\"ok\": true}"
    }
  ]
}
```

## Output Rules

- Exactly one H1 for authored documents.
- Use H2 for major sections.
- Use H3 only when it adds real structure.
- Use fenced code blocks with language tags.
- Keep bullet styles consistent.
- Do not add commentary outside the Markdown body.
