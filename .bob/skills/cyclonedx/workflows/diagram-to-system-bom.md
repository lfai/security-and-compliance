# Workflow: diagram to system BOM

Turn a system diagram (image, Mermaid or other text diagram) and its supporting Markdown into a **CycloneDX 2.0 system BOM**: the components, actors, trust zones, boundaries, flows, structural relationships and use cases of one system. A threat model is built from this BOM in a separate step ([system-bom-to-threat-model.md](system-bom-to-threat-model.md)), so this workflow records what the system *is* and *does*, not what can go wrong with it.

The reference implementation of this workflow's output is [examples/system-bom.code-assistant.json](../examples/system-bom.code-assistant.json) (the working group's Code Assistant use case). Match its shape and conventions.

## Inputs

| Input | Required | Use |
|---|---|---|
| Diagram image (PNG, JPG, SVG) or text diagram (`.mmd`, PlantUML, draw.io XML) | Yes | Elements, groupings, arrows. |
| Supporting Markdown | Strongly recommended | Element descriptions, use cases, flow purposes, deployment variants. The diagram alone rarely says what each arrow carries or which use case it belongs to. |
| An existing system BOM | No | When updating: keep existing `refId`s stable and bump `version`. |

If the image cannot be read, or only an image is supplied, say what you could not determine and ask for the supporting Markdown rather than guessing.

## Step 1: Inventory the diagram

Before writing JSON, list every element you see, with the evidence for it, in a table the user can check:

| Diagram element | Classified as | refId | Evidence |
|---|---|---|---|

Classify each element using this table:

| Diagram shows | CycloneDX 2.0 element | Where it goes |
|---|---|---|
| A software or hardware box (app, service, plugin, model, store, gateway, MCP server) | `component` with the closest `type` (`application`, `framework`, `library`, `platform`, `service`, `machine-learning-model`, `data`, `container`, `device`, …) | `definitions.components[]`, and referenced from `inventories[].components[]` |
| A person, persona or role | `actor` with an inline `party` (`roles`, plus `persona`, `person` or `organization`) | `blueprints[].actors[]` |
| An autonomous agent that both *is* software and *acts* | Both: a `component` (the software) **and** an `actor` whose `party.system` is `{ "kind": "agent", "ref": "<component refId>", "permissions": [...] }`, plus a `realizes` relationship from the component to the actor | Both places |
| A labelled grouping, trust region, network segment or tenant | `zone` (`type`: `trust`, `network`, `deployment`, `tenant`, …) | `blueprints[].zones[]` |
| Where an arrow crosses from one zone to another | `boundary` with `zones: [zoneA, zoneB]` (at least two) | `blueprints[].boundaries[]` |
| An arrow | `flow` with `source`, `destination`, `type` (`data`, `control`, `message`, `event`, …) | `blueprints[].flows[]` |
| A box drawn inside another box, or inside a zone | `relationship` (see Step 4) | `blueprints[].relationships[]` |
| A named scenario, variant or numbered sequence | `useCase` | `definitions.useCases[]`, referenced from `blueprints[].useCases[]` |
| A data store that is not otherwise a component | `component` of `type: "data"`, or a blueprint `dataStore` if it needs store-specific fields | as above |

Do not invent elements that are not in the diagram or the Markdown. If the diagram implies something (for example an arrow with no label), record it with a `description` that says what is assumed, or add a blueprint `assumptions[]` entry with `validity: "unverified"`.

## Step 2: Assign refIds

- Use a type prefix and kebab-case: `component:local-ide`, `actor:developer`, `party:developer`, `zone:internal`, `boundary:internal-to-external-saas`, `flow:developer-to-ide`, `usecase:code-assistant-1a`, `blueprint:code-assistant`, `inventory:code-assistant`.
- When a flow belongs to only one use-case variant, prefix it with the variant: `flow:1a:plugin-to-codebase`.
- Every `refId` must be unique **in the whole document**. A component and the actor it realizes need different refIds (`component:local-code-asst-agent` and `actor:local-code-asst-agent`).
- `refId` values must not start with `urn:cdx:` (that prefix is reserved for BOM-Links).
- When updating an existing BOM, never rename a `refId`. Threat-model BOMs link to it by refId.

## Step 3: Write the document skeleton

```json
{
  "$schema": "https://cyclonedx.org/schema/2.0/cyclonedx-2.0.schema.json",
  "specFormat": "CycloneDX",
  "specVersion": "2.0",
  "serialNumber": "urn:uuid:<new random UUID v4, lowercase>",
  "version": 1,
  "metadata": { "timestamp": "<UTC now, ISO 8601>" },
  "definitions": { "components": [], "useCases": [] },
  "inventories": [],
  "blueprints": []
}
```

- `specFormat` (not `bomFormat`) and `specVersion: "2.0"` are the only required top-level fields. The 2.0 schema rejects `bomFormat`, `bom-ref`, `components` or `services` at the top level.
- Always set `serialNumber`. Threat-model BOMs link back to it, and a BOM without one cannot be linked to. To generate a UUID, run `python -c "import uuid; print(uuid.uuid4())"`.
- Declare each component once, in `definitions.components`. Add the system as the inventory `subject`, and reference every member from `inventories[0].components` as `{ "ref": "<refId>" }`.

## Step 4: Fill the blueprint

One blueprint per system: `refId`, `name`, `description`, and `modelTypes` (`["logical"]` for an architecture diagram, `["data-flow"]` for a DFD).

**Zones and boundaries.** Make one zone for each trust region. Make one boundary for each pair of zones that a flow crosses, and only where a flow crosses. Leave `crossingRequirements` out unless the source states the controls; do not invent them.

**Actors.** Use an inline `party` with `roles` (for example `[{ "role": "developer" }]`) and exactly one of `persona`, `person`, `organization` or `system`. For a human role, use a `persona` with `archetype` and `scope`. For an agent, use `system` with `kind: "agent"`, `ref` and `permissions`.

**Flows.** Each flow needs `refId`, `name`, `source`, `destination` and `type`, and its `source` and `destination` must be refIds of components or actors in this document. Add `description` saying what is carried and why, and add `sequence` (integer order), `synchronous` and `encrypted` when the source says so. If the diagram does not say whether a flow is encrypted, leave `encrypted` out; do not default it to `true` or `false`.

**Relationships.** Each entry has a `ref` (the subject) and **exactly one** kind. Pick the kind as follows:

| Kind | Use for | Code Assistant example |
|---|---|---|
| `aggregates` | Zone → its top-level members (the parts exist independently) | `zone:internal` aggregates the IDE, plugin, auth services |
| `composes` | Framework or platform → runtime parts that cannot exist without it | `component:internal-agentic-framework` composes the local agent, model, RAG and context store |
| `contains` | A component embedded in another | `component:code-asst-plugin` contains `component:code-asst-agent` |
| `realizes` | A component → the actor it becomes when active | `component:local-code-asst-agent` realizes `actor:local-code-asst-agent` |
| `dependsOn` | Runtime or build dependency (prefer `flows` for runtime calls) | |

Put each component in exactly one zone, either directly or through its parent. [relationship-rationale.md](../../../../subgroups/use-cases-and-threat-models/use_cases/code_assistant/relationship-rationale.md) records the working group's reasoning.

**Use cases.** Declare the content in `definitions.useCases[]`: `refId`, `name`, `description`, `preconditions`, `postconditions`, `exceptions`, `successCriteria`, `notes`, and `actors` when known. Then have the blueprint list the flows each use case traverses:

```json
"useCases": [ { "ref": "usecase:code-assistant-1a", "flows": ["flow:developer-to-ide", "..."] } ]
```

When the system has deployment variants (for example local vs SaaS), make one use case per variant and an umbrella use case whose flows are the union. The threat-model workflow generates one TM-BOM per variant.

Optionally, add `visualizations[]` to the blueprint pointing at the source diagram: `{ "name": "...", "type": { "type": "data-flow" }, "url": "<relative path or URL>" }`.

## Step 5: Validate and fix

Run the validator and fix every error before showing the result:

```
python .bob/skills/cyclonedx/scripts/validate_bom.py <system-bom>.json
```

The validator checks the schema, refId uniqueness and that every reference resolves. It needs the `jsonschema` package; if that is missing, run with `--no-schema` and tell the user that schema validation did not run. For a field you are unsure about, look it up with `python .bob/skills/cyclonedx/scripts/schema_tool.py outline blueprint:flow` (or any `module:object`) rather than reading the 1 MB bundled schema.

## Step 6: Report

Tell the user:
1. The file you wrote, its `serialNumber` and `version`.
2. Counts: components, actors, zones, boundaries, flows, relationships, use cases.
3. The inventory table from Step 1, with anything inferred or assumed marked.
4. Open questions where the diagram was ambiguous (unlabelled arrows, elements with no zone, flows not assigned to a use case).
5. The validator result.
