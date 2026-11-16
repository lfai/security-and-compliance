---
name: cyclonedx
description: Use when the user wants to create, convert, validate or explain an OWASP CycloneDX BOM, and in particular to turn a system diagram (image or Mermaid) and supporting Markdown into a CycloneDX 2.0 system BOM, or to generate threat-model BOMs (one TM-BOM per use case) from a system BOM for LF AI & Data threat modelling. Also covers CycloneDX 1.7 SBOM and AI/ML-BOM questions.
---

# CycloneDX 2.0 BOMs and threat models

This skill makes Bob an expert on the OWASP CycloneDX standard: CycloneDX 2.0 (in final drafting, and used for all LF AI & Data threat-modelling work) and CycloneDX 1.7 (ECMA-424). It covers the two **AI Skill: CycloneDX 2.0** steps of the working group's pipeline:

```
diagram + .md ──▶ [1] system BOM (JSON) ──▶ [2] TM-BOM per use case (JSON)
                                    ▲                 │
                                    └── BOM-Links ────┘
```

All paths below are relative to the repository root. The skill directory is `.bob/skills/cyclonedx/`.

## Choose the workflow

| The user wants to… | Read and follow |
|---|---|
| Turn a diagram, image or description of a system into a system BOM | [workflows/diagram-to-system-bom.md](workflows/diagram-to-system-bom.md) |
| Generate a threat model (TM-BOMs) from a system BOM | [workflows/system-bom-to-threat-model.md](workflows/system-bom-to-threat-model.md) |
| Validate a CycloneDX 2.0 BOM, or check its links | run `python .bob/skills/cyclonedx/scripts/validate_bom.py <bom>.json [--system <system>.json]` and explain the result |
| Ask what a 2.0 field or object means | run `python .bob/skills/cyclonedx/scripts/schema_tool.py outline <module>[:<object>]` |
| Work with CycloneDX 1.7 | [reference/v1.7-quick-reference.md](reference/v1.7-quick-reference.md) |

Read the workflow file with `read_file` before starting. Each workflow is the procedure to follow, step by step.

## Rules for every CycloneDX 2.0 document

1. **Top level:** `specFormat: "CycloneDX"` and `specVersion: "2.0"` are required. `bomFormat` is a **1.7** field and the 2.0 schema rejects it. Always set `serialNumber` (`urn:uuid:<lowercase uuid4>`), `version` and `metadata.timestamp`.
2. **Identifiers:** every referable element has a `refId`, unique across the whole document. `bom-ref` is 1.7 only. A refId must not start with `urn:cdx:`.
3. **Components** are declared once, in `definitions.components[]`, and included in a system through `inventories[].components[{ "ref": … }]`. There is no top-level `components` or `services` array in 2.0.
4. **Architecture** goes in `blueprints[]`: zones, boundaries, actors, flows, structural relationships, and use-case-to-flow mappings.
5. **Threat models** go in `threats`, `controls` and `risks`. Their reference fields take in-document refIds only. A link to another BOM is a BOM-Link (`urn:cdx:<serial>/<version>#<refId>`) and is allowed only in `externalReferences` and component, weakness and party references. The threat-model workflow explains how a TM-BOM carries a slice of the system BOM so that its references resolve.
6. **Properties:** names under `cdx:` must come from the registered [CycloneDX property taxonomy](https://github.com/CycloneDX/cyclonedx-property-taxonomy); the AI/ML namespace is copied in [cyclonedx-property-taxonomy/ai-ml.md](cyclonedx-property-taxonomy/ai-ml.md). Working-group properties use the `lfai:` prefix. Never invent `cdx:` names.
7. **Component identity:** to give a component a Package URL, use `identifiers: [{ "party": "<party refId>", "identities": [{ "scheme": "purl", "value": "pkg:…" }] }]`. Follow the [purl skill](../purl/SKILL.md) for purl syntax.
8. **No speculation:** confirm fields and enum values from the schema, and CAPEC, NIST and AICM IDs from the reference files in `subgroups/use-cases-and-threat-models/reference_files/`. CWE and ATT&CK/ATLAS IDs have no file in the repository: check them at the MITRE sites when you can, and otherwise mark them as unverified. Never present an unconfirmed ID as checked, and do not guess.
9. **Validate before you present:** run `validate_bom.py` and fix every error. If `jsonschema` is not installed (`pip install -r .bob/skills/cyclonedx/scripts/requirements.txt`), run with `--no-schema` and tell the user that schema validation did not run.

## Do not read the bundled schema whole

[schema/2.0/cyclonedx-2.0-bundled.schema.json](schema/2.0/cyclonedx-2.0-bundled.schema.json) is about 1 MB: 34 modular schemas bundled together, copied from the CycloneDX specification repository. Instead of reading it:

- [reference/system-schema.md](reference/system-schema.md) is the generated field reference for the system modules (`blueprint`, `usecase`, `definitions`, `inventories`, `component`, `party`).
- [reference/tm-schema.md](reference/tm-schema.md) is the generated field reference for the threat-model modules (`threat`, `control`, `risk`, `weakness`, `standard`).
- `python .bob/skills/cyclonedx/scripts/schema_tool.py modules` lists all 34 modules, `outline <module>:<object>` prints one object's fields and enums, and `extract <module>:<object> -o <file>` writes a standalone schema for one module (for example `threat:threats`).

## Files in this skill

| Path | Purpose |
|---|---|
| `workflows/` | The two step-by-step workflows. |
| `scripts/validate_bom.py` | Schema validation, refId uniqueness, dangling references, BOM-Link checks between a TM-BOM and its system BOM. |
| `scripts/slice_use_case.py` | Lists use cases, cuts the system slice for one use case into a TM-BOM skeleton, adds serial numbers and back-links. |
| `scripts/schema_tool.py` | Module-by-module navigation and extraction of the bundled schema. |
| `reference/` | Generated system and TM schema references, and the 1.7 quick reference. |
| `examples/` | The Code Assistant system BOM and a worked, linked TM-BOM for Sub Use Case 1b. Both validate. |
| `schema/2.0/` | The bundled CycloneDX 2.0 schema. |

The scripts need Python 3.9 or later. `validate_bom.py` also needs `jsonschema`, listed in `scripts/requirements.txt`; the other scripts use the standard library only.

## Reminders

- Ask questions with `ask_followup_question`, and ask before editing a system BOM in place (`--assign-serial`, `--link`).
- Run scripts with `execute_command` from the repository root.
- Never present a BOM that has not been through `validate_bom.py`, and report its result.
