# AI assistant skills

Skills for AI coding assistants used by the working group. Each skill is a directory holding a `SKILL.md` (instructions, with `name` and `description` frontmatter) and any supporting files.

| Skill | What it does |
|---|---|
| [`cyclonedx`](cyclonedx/SKILL.md) | CycloneDX 2.0 (and 1.7) BOM expert. Turns a system diagram and supporting Markdown into a **system BOM**, generates one **threat-model BOM per use case** from a system BOM, and validates BOMs and the links between them. |
| [`purl`](purl/SKILL.md) | Package URL (ECMA-427) authoring and normalization, used for component identity in BOMs. |

## Using them

**New to this? Start with [cyclonedx/GETTING-STARTED.md](cyclonedx/GETTING-STARTED.md)**: setup, the two steps, how to check the result, and troubleshooting.


- **IBM Bob** loads skills from `.bob/skills/<name>/SKILL.md` in the workspace, so open the repository in Bob and the skills are available in the next task (`/cyclonedx`, or ask in plain language).
- **Claude Code** loads [`.claude/skills/claude-cyclonedx/SKILL.md`](../../.claude/skills/claude-cyclonedx/SKILL.md), a thin entry point that points at the shared files here. Keep the shared content in `.bob/skills/` and edit the Claude entry point only for Claude-specific instructions.

A skill name must match its directory name and be lowercase kebab-case. Bob skips a skill with an invalid name silently.

## Requirements

The `cyclonedx` scripts need Python 3.9 or later. Schema validation also needs `jsonschema` and `rfc3339-validator` (both MIT). Install them into a virtual environment, as [GETTING-STARTED.md](cyclonedx/GETTING-STARTED.md#1-set-up-once) shows for macOS, Linux and Windows. Installing into the system Python is refused on many Linux distributions.

```
pip install -r .bob/skills/cyclonedx/scripts/requirements.txt
```

## Maintaining the CycloneDX skill

- **Tests:** `pip install -r .bob/skills/cyclonedx/scripts/requirements-dev.txt`, then `python -m pytest .bob/skills/cyclonedx/scripts/tests -q`. They cover the examples, the slicer (reference closure, `--update`), the validator's error cases, and that the generated references are current.
- **Schema updates:** replace `cyclonedx/schema/2.0/cyclonedx-2.0-bundled.schema.json` with the new bundle from the CycloneDX specification repository, then run `python .bob/skills/cyclonedx/scripts/schema_tool.py write-references` and the tests.
- **Threat catalogues:** `cyclonedx/reference/catalogues/` holds ID, title and link for each catalogue the threat-model workflow uses: OWASP Top 10 (web, 2025), OWASP API Security Top 10 (2023), OWASP Top 10 for LLM Applications (2025), OWASP Top 10 for Agentic Applications (2026), MITRE ATLAS, MITRE ATT&CK Enterprise and CWE. Editions and fetch dates are in `catalogues.json`. Only IDs, titles and links are copied: the OWASP lists are CC BY-SA 4.0, ATLAS is Apache-2.0, and ATT&CK and CWE are used under MITRE's terms, whose notices are kept in each file. To refresh them, run `python .bob/skills/cyclonedx/scripts/fetch_catalogues.py` (needs network access) and review the diff.
- **Threat-model policy:** `cyclonedx/reference/threat-model-policy.json` says which catalogues are swept for which kind of element, and which `lfai:` property names are allowed. It names whole catalogues only. The reasons for the catalogue choices are recorded in its `catalogueDecisions`.
- **Decision needed: MCP and tool servers.** The proposed catalogue, the OWASP MCP Top 10 (2025, beta), is **not included**: its repository licence file says CC BY-SA 4.0, but its project page says CC BY-NC-SA 4.0 (non-commercial). Until its project leads confirm which applies, tool servers are checked with STRIDE and the use-case review only, and the validator warns for each one. To add it once the licence is confirmed: add `owasp-mcp-top10` to the `tool-server` sweep in the policy and run `python .bob/skills/cyclonedx/scripts/fetch_catalogues.py --only owasp-mcp-top10`.
- **For review: lifecycle scope.** `lifecycleScope` in the policy removes five OWASP LLM items from training-only use cases. It is the one place the policy names catalogue items, and it is proposed, not agreed.
- **Examples:** `examples/system-bom.code-assistant.json` is a copy of [`code_assistant_bom_2.0.json`](../../subgroups/use-cases-and-threat-models/use_cases/code_assistant/code_assistant_bom_2.0.json) with a `serialNumber` (needed for BOM-Links) and a back-link to the example TM-BOM. If the source BOM changes, copy it again, keep the same `serialNumber`, and re-run the slice and validation.
