# CycloneDX Blueprint Relationship Rationale

This document records the reasoning behind the relationship types chosen to encode the structural containment graphs in [`definition.md`](./definition.md). The three types used are drawn directly from the `relationship` object defined in [`cyclonedx-blueprint-2.0.schema.json`](../../../../.bob/skills/cyclonedx/schema/2.0/model/cyclonedx-blueprint-2.0.schema.json).

---

## Relationship types

### `aggregates`

> *"The subject is the whole in a whole-part relationship in which each part may exist independently of the whole."*

Used for **boundaries → their top-level members**.

A boundary (`boundary:internal`, `boundary:external-saas`, `boundary:external-cloud`) is a trust or network grouping label. The assets it contains — workstation components, MCP servers, authentication services — exist as deployable artefacts in their own right and would still be meaningful system entities even if the boundary classification were removed or renamed. This loose coupling matches the `aggregates` semantic.

### `composes`

> *"The subject is the whole in a whole-part relationship in which each part cannot exist without the whole."*

Used for **frameworks and platform services → their runtime sub-components**.

An Agentic Framework (`component:internal-agentic-framework`, `component:external-saas-agentic-framework`) only makes sense as a unified runtime; the local dynamic agent, local model, RAG pipeline, and context store are instantiated and lifecycle-managed as a single cohesive unit. Removing the framework removes all of them. The same applies to `component:agentic-saas` composing its MCP Gateway and MCP Server, and `component:mcp-agentic-saas` composing the remote agent, remote model, remote RAG, and remote context store.

### `contains`

> *"The subject contains or nests each target."*

Used for **components that structurally wrap or directly embed another component**.

- `component:code-asst-plugin` contains `component:code-asst-agent` — the agent is embedded within the plugin process and exposed as an internal capability, not an independently deployed service.
- `component:mcp-cloud` contains `component:cloud-service` — the MCP Server is the sole access point that proxies and fronts the cloud service; the nesting is an architectural encapsulation rather than a lifecycle dependency.

---

## Sub Use Case 1a — relationship graph

| Subject | Relationship | Targets |
|---|---|---|
| `boundary:internal` | `aggregates` | `component:mcp-server-third-party`, `component:authn-service`, `component:authz-service`, `component:local-ide`, `component:data-local-codebase`, `component:code-asst-plugin`, `component:internal-agentic-framework` |
| `component:code-asst-plugin` | `contains` | `component:code-asst-agent` |
| `component:internal-agentic-framework` | `composes` | `actor:local-code-asst-agent`, `component:code-assistant-model-local`, `component:rag-local`, `component:context-store-local` |
| `boundary:external-cloud` | `aggregates` | `component:mcp-cloud` |
| `component:mcp-cloud` | `contains` | `component:cloud-service` |

---

## Sub Use Case 1b — relationship graph

| Subject | Relationship | Targets |
|---|---|---|
| `boundary:internal` | `aggregates` | `component:mcp-server-third-party`, `component:authn-service`, `component:authz-service`, `component:local-ide`, `component:data-local-codebase`, `component:code-asst-plugin`, `component:external-saas-agentic-framework` |
| `component:code-asst-plugin` | `contains` | `component:code-asst-agent` |
| `boundary:external-saas` | `aggregates` | `component:external-plugin-marketplace`, `component:agentic-saas` |
| `component:agentic-saas` | `composes` | `component:mcp-gateway`, `component:mcp-agentic-saas` |
| `component:mcp-agentic-saas` | `composes` | `actor:remote-code-asst-agent`, `component:code-assistant-model-remote`, `component:rag-remote`, `component:context-store-remote` |
| `boundary:external-cloud` | `aggregates` | `component:mcp-cloud` |
| `component:mcp-cloud` | `contains` | `component:cloud-service` |

---

## Key distinctions

| Question | Answer |
|---|---|
| Why not `aggregates` for framework sub-components? | The model, RAG, and context store are instantiated and torn down with the framework — they have no independent existence at runtime. `composes` captures this lifecycle dependency. |
| Why not `composes` for boundary members? | Boundaries are logical groupings for security and trust analysis. Their member components could be redeployed, renamed, or regrouped without ceasing to exist as system entities. `aggregates` preserves that independence. |
| Why not `composes` for plugin → agent? | The agent is embedded within the plugin but is also referenced independently by flows and use cases (e.g. `flow:1a:agent-authenticates`). `contains` correctly models the nesting without asserting that the agent's existence is entirely contingent on the plugin. |
| Why not `dependsOn` for any of these? | `dependsOn` captures runtime or build-time dependency (A needs B to function), not structural containment. All relationships here model *where things live in the architecture*, not *what they call at runtime* — that is the role of `flows`. |
