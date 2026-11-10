# Code Assistant

Threat-model use case for an AI code assistant (IDE plugin, local and remote agents, model, RAG, MCP servers).

## Complete CycloneDX 2.0 BOM

**[`code_assistant_bom_2.0.json`](./code_assistant_bom_2.0.json)** is the complete CycloneDX 2.0 BOM for this use case. It contains every object, element and value from all of the fragments in [`definition.md`](./definition.md): all 23 components (declared in `definitions.components` and associated with the Code Assistant system by reference through `inventories`), 3 actors (with their parties), 3 zones, 3 boundaries (without zone-crossing requirements, which are not considered at this time), 23 flows, the structural relationships, and the 3 use cases. The optional blueprint `assets` example in `definition.md` is intentionally not included. It validates against the CycloneDX 2.0 bundled JSON schema ([`cyclonedx-2.0-bundled.schema.json`](../../../../.bob/skills/cyclonedx/schema/2.0/cyclonedx-2.0-bundled.schema.json)). Use this file for tooling, validation, and analysis.

## Documents

| File | Purpose |
|---|---|
| [`code_assistant_bom_2.0.json`](./code_assistant_bom_2.0.json) | The complete, fully described CycloneDX 2.0 BOM (source of truth for tooling). |
| [`definition.md`](./definition.md) | Narrative definitions, the diagram, and the BOM built up in **fragments** with explanations. |
| [`relationship-rationale.md`](./relationship-rationale.md) | Why each relationship type (`aggregates`, `composes`, `contains`) was chosen. |

## How the documents relate (what was simplified)

[`definition.md`](./definition.md) explains the model piece by piece. Its JSON snippets are **fragments**, each showing one part of the BOM (for example only the `actors`, or only the flows for one sub use case). Its closing section, "CycloneDX v2.0 — Code Assistant Threat Model BOM", assembles the pieces into one document but is a **simplified view**: it keeps the structure and mostly the required fields (`refId`, `name`, `type`, `source`, `destination`, and so on) so the overall shape is easy to read, and it leaves out descriptions, permissions, preconditions, postconditions, exceptions, success criteria, notes and other optional detail.

If the two ever differ, [`code_assistant_bom_2.0.json`](./code_assistant_bom_2.0.json) is authoritative.

## Open design questions

Questions about how CycloneDX 2.0 models this use case, for discussion with the CycloneDX designers, are listed at the end of [`definition.md`](./definition.md#outstanding-questions-for-the-cyclonedx-designers).
