# Workflow: diagram to system BOM

Turn a system diagram (image, Mermaid or other text diagram) and its supporting Markdown into a **CycloneDX 2.0 system BOM**: the components, actors, trust zones, boundaries, flows, structural relationships and use cases of one system. A threat model is built from this BOM in a separate step ([system-bom-to-threat-model.md](system-bom-to-threat-model.md)), so this workflow records what the system *is* and *does*, not what can go wrong with it.

The reference implementation of this workflow's output is [examples/system-bom.code-assistant.json](../examples/system-bom.code-assistant.json) (the working group's Code Assistant use case). Match its shape and conventions.

## Inputs

| Input | Required | Use |
|---|---|---|
| Diagram image (PNG, JPG, SVG) or text diagram (`.mmd`, PlantUML, draw.io XML) | Yes | Elements, groupings, arrows. |
| Supporting Markdown | Strongly recommended | Element descriptions, use cases, flow purposes, deployment variants. The diagram alone rarely says what each arrow carries or which use case it belongs to. |
| An existing system BOM | No | When updating: keep existing `refId`s stable and bump `version`. |

If the diagram cannot be read, say so and stop. If only a diagram is supplied (an image or a text diagram such as Mermaid, with no supporting Markdown), ask for the supporting Markdown; if you cannot ask, carry on, and record every inference as an assumption, as Step 1 describes.

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
| A data asset held by a component (credentials, tokens, API keys, model weights, documents), usually listed in the notes, not drawn | blueprint `asset` with `type: "data"`, `name`, `description` and `zone`, plus a `contains` relationship from the component that holds it (or `associates` from an actor) | `blueprints[].assets[]`, `blueprints[].relationships[]` |

Do not invent elements that are not in the diagram or the Markdown.

**Ambiguity.** Diagrams are often ambiguous. Do not stop at each ambiguity. Make the most plausible reading, record it as a blueprint `assumptions[]` entry with `validity: "unverified"` (and `relatedAssets` naming the elements involved), and list it in the report as an open question. Common cases:
- **Same label, different shapes.** Two shapes with the same label are separate elements, unless the notes say they are one. Give each a refId that says what it does (for example `component:input-guard-llm` and `component:input-guard-embedding`).
- **A grouping with the same name as a box inside it.** Treat the grouping as that component's boundary (a `contains` relationship), not as a zone.
- **Unlabelled or unnumbered arrows.** Model them as flows with a `description` saying what is assumed. Give `sequence` only to arrows the diagram numbers; arrows sharing a number get the same `sequence`.
- **Roles with no matching archetype.** Choose the closest persona `archetype` (for example `developer` for an AI engineer) and put the exact role in `roles`, as a custom role when it is not in the role list: `{ "name": "clinician", "description": "..." }`.
- **Process steps, swimlanes and decisions.** Flowchart activity boxes ("Upload note", "Save to EHR") are not components or flows: they are steps of a use case. Put them in that use case's `mainFlow` as `{ "number", "description", "actor" }`, and branches (decision diamonds) in `alternativeFlows`; a branch the diagram does not draw (for example only a "Yes" edge) is an assumption. A swimlane that holds only steps is the use case, not a zone. An arrow from a step to a component ("Uses") becomes a flow from the actor performing the step to that component, recorded as an assumption.
- **Duplicate arrows.** Two arrows between the same pair, one labelled and one not, are one flow unless the notes say otherwise.
- **Documentation labels.** Labels such as "Model Card" or "Dataset Card" on a box say that documentation exists; they are not elements. Record them as an assumption, or as an `externalReferences` entry of type `model-card` or `documentation` when a link is given.
- **Human or software.** When a box's name suggests a person in the loop ("Human Oversight Agent"), model what the diagram draws and record the question as an assumption.

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

One blueprint per system: `refId`, `name`, `description`, and `modelTypes` (`["logical"]` for an architecture diagram, `["data-flow"]` for a DFD, both when it is both).

**Zones and boundaries.** Make one zone for each grouping the diagram draws: `type: "trust"` for trust regions (organisation, cloud provider, SaaS), and the closest other type (`functional`, `network`, `deployment`, …) for groupings inside one. When a grouping sits inside another, set the inner zone's `parent`. If the diagram draws no trust region (only process lanes or functional layers), do not invent one: model the groupings with those types, and record an assumption that no trust boundary is drawn, as an open question for the report. Make one boundary for each pair of zones that a flow crosses, and only where a flow crosses, naming the **outermost** zones that differ: a flow from a sub-zone of the organisation to a cloud provider crosses the organisation ↔ cloud boundary. Leave `crossingRequirements` out unless the source states the controls; do not invent them.

**Actors.** Set each actor's `zone` to the zone it works in. Use an inline `party` with `roles` (for example `[{ "role": "developer" }]`) and exactly one of `persona`, `person`, `organization` or `system`. For a human role, use a `persona` with `archetype` and `scope`. For an agent, use `system` with `kind: "agent"`, `ref` and `permissions`. Take permissions only from the diagram and notes (what the agent's arrows and description show it doing), as short kebab-case verbs such as `read-local-codebase`; record inferred ones as an assumption.

**Flows.** Each flow needs `refId`, `name`, `source`, `destination` and `type`, and its `source` and `destination` must be refIds of components or actors in this document. Add `description` saying what is carried and why, and add `sequence` (integer order), `synchronous` and `encrypted` when the source says so. If the diagram does not say whether a flow is encrypted, leave `encrypted` out; do not default it to `true` or `false`.

**Relationships.** Each entry has a `ref` (the subject) and **exactly one** kind. Pick the kind as follows:

| Kind | Use for | Code Assistant example |
|---|---|---|
| `aggregates` | Zone → its top-level members (the parts exist independently) | `zone:internal` aggregates the IDE, plugin, auth services |
| `composes` | Framework or platform → runtime parts that cannot exist without it | `component:internal-agentic-framework` composes the local agent, model, RAG and context store |
| `contains` | A component embedded in another | `component:code-asst-plugin` contains `component:code-asst-agent` |
| `realizes` | A component → the actor it becomes when active | `component:local-code-asst-agent` realizes `actor:local-code-asst-agent` |
| `dependsOn` | Runtime or build dependency (prefer `flows` for runtime calls) | |

Put each component in exactly one zone, either directly or through its parent. In short: `aggregates` when the parts would still exist without the whole, `composes` when they would not, `contains` for nesting without that lifecycle claim, and `flows` (not `dependsOn`) for what calls what at runtime.

**Use cases.** Declare the content in `definitions.useCases[]`: `refId`, `name`, `description`, `preconditions`, `postconditions`, `mainFlow` and `alternativeFlows` (the steps, when the diagram or notes give them), `exceptions`, `successCriteria`, `notes`, and `actors` when known. Then have the blueprint list the flows each use case traverses:

```json
"useCases": [ { "ref": "usecase:code-assistant-1a", "flows": ["flow:developer-to-ide", "..."] } ]
```

**Lifecycle.** AI systems often mix training-time flows (dataset to model, feedback to training data) with runtime flows (the system in use). Put them in separate use cases, and mark each use case with a property `{ "name": "lfai:lifecycle", "value": "training" }` or `"inference"`. The threat-model workflow uses it to skip catalogue items that cannot apply in that stage. If a model component is both trained and served, it is the same component in both use cases; record in an assumption which of its training flows the diagram omits.

Split use cases where the flows differ: by deployment variant when the variants have different flows (for example local vs SaaS), or by activity when the diagram has separate activities (for example ingestion vs query). A variant that changes no flow (for example "SaaS or on-prem" for the same component) is not a separate use case; record it as an assumption. When there are several use cases, add an umbrella use case whose flows are their union. The threat-model workflow generates one TM-BOM per specific use case.

Optionally, add `visualizations[]` to the blueprint pointing at the source diagram: `{ "name": "...", "type": { "type": "data-flow" }, "url": "<path relative to the BOM file, or a URL>" }`.

**Model and dataset details.** For a `machine-learning-model` component, fill `modelProperties` with what the source states (for example `tasks`); for a `data` component that is a dataset, add `data: [{ "type": "dataset" }]`. Leave out what the source does not say rather than guessing, and record any inferred value as an assumption. Use `type: "data"` only for data, not for software such as a plugin.

**Classify for the threat sweep.** Give every component (and every blueprint asset that is itself a system part, such as an API) one or more classification tags in its `tags` array. The threat-model workflow uses them to choose which threat catalogues to sweep for that element. The tags and their meanings are in [reference/threat-model-policy.json](../reference/threat-model-policy.json) under `classification`: `web-app`, `api`, `ai-model`, `ai-data`, `ai-pipeline`, `agent`, `tool-server`, and `none` for an element in no sweep. Classify by what the element *does*, from the diagram and notes. Examples: a retriever is `ai-pipeline`, a vector database is `ai-data`, a guardrail is `ai-pipeline`, a hosted LLM is `ai-model`, and a web front end that calls it is `web-app`. If you are unsure, record the choice as an assumption.

## Step 5: Validate and fix

Run the validator and fix every error before showing the result:

```
python .bob/skills/cyclonedx/scripts/validate_bom.py <system-bom>.json
```

The validator checks the schema, refId uniqueness and that every reference resolves. It does not check that each component is in exactly one zone, or that boundaries match the flows that cross zones; check those yourself. It needs the `jsonschema` package; if that is missing, run with `--no-schema` and tell the user that schema validation did not run. For a field you are unsure about, look it up with `python .bob/skills/cyclonedx/scripts/schema_tool.py outline blueprint:flow` (or any `module:object`) rather than reading the 1 MB bundled schema.

## Step 6: Report

Tell the user:
1. The file you wrote, its `serialNumber` and `version`.
2. Counts: components, blueprint assets (0 is expected when there are no notes listing data assets), actors, zones, boundaries, flows, relationships, use cases.
3. The inventory table from Step 1, with anything inferred or assumed marked, and each component's classification tags.
4. Open questions: every assumption you recorded, as a question the user can answer (unlabelled arrows, elements with no zone, flows not assigned to a use case, uncertain classifications).
5. The validator result.
