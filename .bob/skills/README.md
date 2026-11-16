# AI assistant skills

Skills for AI coding assistants used by the working group. Each skill is a directory holding a `SKILL.md` (instructions, with `name` and `description` frontmatter) and any supporting files.

| Skill | What it does |
|---|---|
| [`cyclonedx`](cyclonedx/SKILL.md) | CycloneDX 2.0 (and 1.7) BOM expert. Turns a system diagram and supporting Markdown into a **system BOM**, generates one **threat-model BOM per use case** from a system BOM, and validates BOMs and the links between them. |
| [`purl`](purl/SKILL.md) | Package URL (ECMA-427) authoring and normalization, used for component identity in BOMs. |

## Using them

- **IBM Bob** loads skills from `.bob/skills/<name>/SKILL.md` in the workspace, so open the repository in Bob and the skills are available in the next task (`/cyclonedx`, or ask in plain language).
- **Claude Code** loads [`.claude/skills/claude-cyclonedx/SKILL.md`](../../.claude/skills/claude-cyclonedx/SKILL.md), a thin entry point that points at the shared files here. Keep the shared content in `.bob/skills/` and edit the Claude entry point only for Claude-specific instructions.

A skill name must match its directory name and be lowercase kebab-case. Bob skips a skill with an invalid name silently.

## Requirements

The `cyclonedx` scripts need Python 3.9 or later. Schema validation also needs `jsonschema` and `rfc3339-validator` (both MIT):

```
pip install -r .bob/skills/cyclonedx/scripts/requirements.txt
```

## Maintaining the CycloneDX skill

- **Tests:** `pip install -r .bob/skills/cyclonedx/scripts/requirements-dev.txt`, then `python -m pytest .bob/skills/cyclonedx/scripts/tests -q`. They cover the examples, the slicer (reference closure, `--update`), the validator's error cases, and that the generated references are current.
- **Schema updates:** replace `cyclonedx/schema/2.0/cyclonedx-2.0-bundled.schema.json` with the new bundle from the CycloneDX specification repository, then run `python .bob/skills/cyclonedx/scripts/schema_tool.py write-references` and the tests.
- **Examples:** `examples/system-bom.code-assistant.json` is a copy of [`code_assistant_bom_2.0.json`](../../subgroups/use-cases-and-threat-models/use_cases/code_assistant/code_assistant_bom_2.0.json) with a `serialNumber` (needed for BOM-Links) and a back-link to the example TM-BOM. If the source BOM changes, copy it again, keep the same `serialNumber`, and re-run the slice and validation.
