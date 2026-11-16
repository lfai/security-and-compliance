---
name: claude-cyclonedx
description: Use when the user wants to create, convert, validate or explain an OWASP CycloneDX BOM, and in particular to turn a system diagram (image or Mermaid) and supporting Markdown into a CycloneDX 2.0 system BOM, or to generate threat-model BOMs (one TM-BOM per use case) from a system BOM for LF AI & Data threat modelling. Also covers CycloneDX 1.7 SBOM and AI/ML-BOM questions.
---

# CycloneDX 2.0 BOMs and threat models

This is the Claude Code entry point for the repository's CycloneDX skill. The workflows, scripts, schema and examples live in **`.bob/skills/cyclonedx/`** and are shared with the IBM Bob version of the skill, so both assistants follow the same procedure and produce the same output. Read files from there; do not copy them here.

It covers the two **AI Skill: CycloneDX 2.0** steps of the working group's pipeline:

```
diagram + .md ──▶ [1] system BOM (JSON) ──▶ [2] TM-BOM per use case (JSON)
                                    ▲                 │
                                    └── BOM-Links ────┘
```

## Choose the workflow

| The user wants to… | Read and follow |
|---|---|
| Turn a diagram, image or description of a system into a system BOM | `.bob/skills/cyclonedx/workflows/diagram-to-system-bom.md` |
| Generate a threat model (TM-BOMs) from a system BOM | `.bob/skills/cyclonedx/workflows/system-bom-to-threat-model.md` |
| Validate a CycloneDX 2.0 BOM, or check its links | run `python .bob/skills/cyclonedx/scripts/validate_bom.py <bom>.json [--system <system>.json]` and explain the result |
| Ask what a 2.0 field or object means | run `python .bob/skills/cyclonedx/scripts/schema_tool.py outline <module>[:<object>]` |
| Work with CycloneDX 1.7 | `.bob/skills/cyclonedx/reference/v1.7-quick-reference.md` |

Read the workflow file in full before starting, and follow its steps in order. Paths in the workflows are relative to the repository root, and so are the paths in this file.

## Rules for every CycloneDX 2.0 document

1. **Top level:** `specFormat: "CycloneDX"` and `specVersion: "2.0"` are required. `bomFormat` is a **1.7** field and the 2.0 schema rejects it. Always set `serialNumber` (`urn:uuid:<lowercase uuid4>`), `version` and `metadata.timestamp`.
2. **Identifiers:** every referable element has a `refId`, unique across the whole document. `bom-ref` is 1.7 only. A refId must not start with `urn:cdx:`.
3. **Components** are declared once, in `definitions.components[]`, and included in a system through `inventories[].components[{ "ref": … }]`. There is no top-level `components` or `services` array in 2.0.
4. **Architecture** goes in `blueprints[]`: zones, boundaries, actors, flows, structural relationships, and use-case-to-flow mappings.
5. **Threat models** go in `threats`, `controls` and `risks`. Their reference fields take in-document refIds only. A link to another BOM is a BOM-Link (`urn:cdx:<serial>/<version>#<refId>`) and is allowed only in `externalReferences` and component, weakness and party references. The threat-model workflow explains how a TM-BOM carries a slice of the system BOM so that its references resolve.
6. **Properties:** names under `cdx:` must come from the registered [CycloneDX property taxonomy](https://github.com/CycloneDX/cyclonedx-property-taxonomy); the AI/ML namespace is copied in `.bob/skills/cyclonedx/cyclonedx-property-taxonomy/ai-ml.md`. Working-group properties use the `lfai:` prefix. Never invent `cdx:` names.
7. **Component identity:** to give a component a Package URL, use `identifiers: [{ "party": "<party refId>", "identities": [{ "scheme": "purl", "value": "pkg:…" }] }]`. For purl syntax, read `.bob/skills/purl/SKILL.md`.
8. **No speculation:** confirm fields and enum values from the schema, and CAPEC, NIST and AICM IDs from the reference files in `subgroups/use-cases-and-threat-models/reference_files/`. CWE and ATT&CK/ATLAS IDs have no file in the repository: check them at the MITRE sites when you can, and otherwise mark them as unverified. Never present an unconfirmed ID as checked, and do not guess.
9. **Validate before you present:** run `validate_bom.py` and fix every error. If `jsonschema` is not installed (`pip install -r .bob/skills/cyclonedx/scripts/requirements.txt`), run with `--no-schema` and tell the user that schema validation did not run.

## Do not read the bundled schema whole

`.bob/skills/cyclonedx/schema/2.0/cyclonedx-2.0-bundled.schema.json` is about 1 MB: 34 modular schemas bundled together. Do not open it with Read. Use these instead:

- `.bob/skills/cyclonedx/reference/system-schema.md` is the generated field reference for the system modules (`blueprint`, `usecase`, `definitions`, `inventories`, `component`, `party`).
- `.bob/skills/cyclonedx/reference/tm-schema.md` is the generated field reference for the threat-model modules (`threat`, `control`, `risk`, `weakness`, `standard`).
- `python .bob/skills/cyclonedx/scripts/schema_tool.py modules` lists all 34 modules, `outline <module>:<object>` prints one object's fields and enums, and `extract <module>:<object> -o <file>` writes a standalone schema for one module.
- Use Grep on the reference files when you need one enum value or field.

## Working in Claude Code

- **Images:** read the diagram image with the Read tool; it renders PNG and JPG. If it is a Mermaid or other text diagram, read the source instead.
- **Scripts:** run them with Bash from the repository root. They need Python 3.9 or later; `validate_bom.py` also needs `jsonschema`.
- **Questions:** ask the user with AskUserQuestion when a step says to ask, for example before `--assign-serial` or `--link`, which edit a system BOM in place, or to confirm which use cases and methodologies to model.
- **Large outputs:** a TM-BOM can be long. Build it with the slice script, then add the threats, controls and risks with Edit, or with a short Python script for many entries. Do not retype the system slice by hand.
- **Examples:** `.bob/skills/cyclonedx/examples/` holds the Code Assistant system BOM and a worked, linked TM-BOM for Sub Use Case 1b. Match their shape.
- Never present a BOM that has not been through `validate_bom.py`, and report its result.
