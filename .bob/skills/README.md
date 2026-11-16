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
- **Threat catalogues:** `cyclonedx/reference/catalogues/` holds ID, title and link for each catalogue the threat-model workflow uses: OWASP Top 10 (web, 2025), OWASP API Security Top 10 (2023), OWASP Top 10 for LLM Applications (2025), OWASP Top 10 for Agentic Applications (2026), OWASP MCP Top 10 (2025, beta), MITRE ATLAS, MITRE ATT&CK Enterprise and CWE. Editions and fetch dates are in `catalogues.json`. Only IDs, titles and links are copied: the OWASP lists are CC BY-SA 4.0, ATLAS is Apache-2.0, and ATT&CK and CWE are used under MITRE's terms, whose notices are kept in each file. To refresh them, run `python .bob/skills/cyclonedx/scripts/fetch_catalogues.py` (needs network access) and review the diff.
- **Threat-model policy:** `cyclonedx/reference/threat-model-policy.json` says which catalogues are swept for which kind of element, and which `lfai:` property names are allowed. It names whole catalogues only. The reasons for the agent and MCP choices are recorded in its `catalogueDecisions`. **Open item:** the OWASP MCP Top 10's licence is CC BY-SA 4.0 in its LICENSE.md but CC BY-NC-SA 4.0 on its project page; this should be raised with its project leads.
- **Examples:** `examples/system-bom.code-assistant.json` is a copy of [`code_assistant_bom_2.0.json`](../../subgroups/use-cases-and-threat-models/use_cases/code_assistant/code_assistant_bom_2.0.json) with a `serialNumber` (needed for BOM-Links) and a back-link to the example TM-BOM. If the source BOM changes, copy it again, keep the same `serialNumber`, and re-run the slice and validation.
