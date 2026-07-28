# Use Case: Code Assistant

This document provides concise definitions of the items used in threat modeling diagram.

Diagram (draw.io): ![Diagram](./diagram/ai_code_generator_threat_model_diagram_updated_2026_05_12.drawio.svg)

[Edit this diagram (draw.io XML)](./diagram/ai_code_generator_threat_model_diagram_updated_2026_05_12.drawio)

## Overview

The **Code Assistant** use case describes an AI-powered development assistant that is surfaced to a developer directly inside an Integrated Development Environment (IDE). The assistant is installed as a **model plugin** — a first-class IDE extension that embeds agent capabilities into the editing experience without requiring the developer to switch context to a separate application.

### Local agents (in-IDE runtime)

Once the plugin is installed, a **Code Assistant Agent** runs within the plugin process on the developer's workstation. Before installation it is treated as a static software component (the *Code Assistant Plugin*); once activated inside the IDE it becomes an actor with agency. The Code Assistant Agent handles low-latency tasks such as inline completions, syntax-aware suggestions, and prompt assembly. For more complex, multi-step tasks — autonomous code generation, repository-wide refactoring, test scaffolding — the Code Assistant Agent can delegate to a **Code Assistant Agent (Local Dynamic)**, a locally hosted agent embedded within an agentic framework that has *dynamic* access to tool calling, MCP servers, a retrieval-augmented generation (RAG) pipeline, and a context store. When hardware permits, a locally quantised language model (e.g., an 8 B-parameter model) serves inference entirely on the workstation, keeping code and context within the local trust boundary.

### External connectivity

The plugin and its local agents reach outward through standardised agent protocols — primarily the **Model Context Protocol (MCP)** — to two categories of external endpoint:

1. **Large-model services.** When a task exceeds local model capacity, or when the deployment is configured to delegate the entire agentic framework to a hosted platform, the Code Assistant Agent connects to an **external SaaS agentic platform** via an MCP Gateway. The remote platform hosts a **Remote Code Assistant Agent** — an agent that is opaque to the developer and operates entirely within the External SaaS trust boundary — together with a larger or specialised language model, a remote RAG pipeline, and a remote context store. Results flow back through the MCP Gateway to the local plugin.

2. **Information and tooling services.** Agents can invoke any number of **MCP Servers** that expose capabilities as callable tools: internal enterprise services (code search, ticket systems, internal APIs), external cloud-provider APIs (infrastructure provisioning, container registries, secret managers), and data-retrieval endpoints. Each MCP Server acts as a controlled egress point, enforcing authentication, authorisation, and audit logging before forwarding requests to the underlying service.

### Trust boundaries and deployment variants

Two named boundaries partition the architecture:

- **Internal boundary** — represents **locally networked resources**: the developer's workstation, the IDE, the Code Assistant Plugin and its embedded agent, the local agentic framework, and any MCP servers (e.g., a locally installed Jira MCP Server) that are reachable within the organisation's local network. All components within this boundary are subject to the organisation's own security controls.

- **External boundary** — represents **remotely networked services**: any service that is reached over the public internet or a remote network, including the Agentic SaaS platform (e.g., Claude Code, Cursor), the External Plugin Marketplace, and cloud-provider APIs. Components within this boundary operate under a third-party trust model; the organisation has limited visibility into their internal behaviour and data handling.

The architecture supports two primary deployment variants that share the same plugin surface but differ in where the agentic framework runs:

| Variant | Agentic framework | Model | Data residency |
|---------|------------------|-------|---------------|
| **Sub Use Case 1a** — Local, IDE Agent | Agentic Framework runs locally on the developer's workstation (within the **Internal** boundary) | Local (e.g., small, 8B parameter model) | Stays on-workstation; cloud calls only via explicit MCP |
| **Sub Use Case 1b** — Remote, SaaS Agent | Agentic Framework is hosted on a remote SaaS platform (within the **External** boundary), reached via MCP Gateway | Remote, hosted (e.g., large, 128B parameter model) | Leaves workstation via MCP Gateway to remote SaaS |

In both variants the developer's IDE remains the single point of interaction. Authentication and authorisation services guard every outbound connection, and all agent tool invocations are intended to be logged and auditable regardless of where the agentic framework is hosted.

### CycloneDX 2.0 — `useCase` object

```json
{
  "bom-ref": "usecase:code-assistant",
  "name": "Code Assistant",
  "description": "A developer uses an AI-powered code assistant—composed of a plugin, one or more agents, a language model, a retrieval-augmented generation (RAG) pipeline, and an agentic framework—to accelerate software development tasks such as code generation, explanation, and review. The assistant may run fully on the developer's workstation (Sub Use Case 1a) or offload its agentic components to an external SaaS platform (Sub Use Case 1b).",
  "actors": [
    { "ref": "actor-developer" },
    { "ref": "code-asst-agent-static-data" },
    { "ref": "local-code-asst-agent" },
    { "ref": "remote-code-asst-agent" }
  ],
  "preconditions": [
    "Developer has an IDE installed and a local codebase clone available.",
    "The Code Assistant Plugin has been installed from a trusted, authenticated Plugin Marketplace (e.g., VS Code Marketplace, JetBrains Marketplace) whose publisher identity and plugin integrity are verified before delivery to the IDE.",
    "The installed Code Assistant Plugin is authenticated and authorized via the Authentication and Authorization Services.",
    "The MCP Server — Agentic SaaS (e.g., Claude Code, hosted remotely on the Agentic SaaS platform) is reachable from the developer's workstation.",
    "The locally installed MCP Server (e.g., a Jira MCP Server installed on the developer's workstation) is running and reachable."
  ],
  "postconditions": [
    "Developer receives AI-generated code suggestions, completions, or reviews.",
    "Any tool invocations performed by agents are logged and auditable.",
    "No sensitive code or credentials are unintentionally exfiltrated."
  ],
  "mainFlow": [
    {
      "number": 1,
      "description": "The Developer (actor-developer) obtains the Code Assistant Plugin (code-asst-plugin) from a trusted, authenticated Plugin Marketplace (external-plugin-marketplace) and installs it into the IDE (local-ide).",
      "actor": { "ref": "actor-developer" }
    },
    {
      "number": 2,
      "description": "The Developer opens the IDE (local-ide) and activates the Code Assistant Plugin (code-asst-plugin) to initiate a coding assistance interaction.",
      "actor": { "ref": "actor-developer" }
    },
    {
      "number": 3,
      "description": "The Code Assistant Agent (code-asst-agent-static-data) authenticates the Developer via the Authentication Service (authn-service) and checks permissions via the Authorization Service (authz-service).",
      "actor": { "ref": "code-asst-agent-static-data" }
    },
    {
      "number": 4,
      "description": "The Code Assistant Agent (code-asst-agent-static-data) processes the Developer's request, optionally querying the Local Codebase Clone (data-local-codebase). Where tool calls are needed, it dispatches requests to the locally installed MCP Server (e.g., Jira MCP Server on the workstation) to retrieve context such as tickets or project metadata.",
      "actor": { "ref": "code-asst-agent-static-data" }
    },
    {
      "number": 5,
      "description": "The Code Assistant Agent (code-asst-agent-static-data) forwards complex or multi-step tasks to the Code Assistant Agent (Local Dynamic) (local-code-asst-agent) running within the Agentic Framework (framework-1a).",
      "actor": { "ref": "code-asst-agent-static-data" }
    },
    {
      "number": 6,
      "description": "The Code Assistant Agent (Local Dynamic) (local-code-asst-agent) orchestrates multi-step workflows using the local model (model-local), RAG pipeline (rag-local), and context store (ctx-local). Where remote agentic capabilities are required, requests are routed to the MCP Server — Agentic SaaS (e.g., Claude Code, hosted remotely) via the MCP Gateway (mcp-gateway).",
      "actor": { "ref": "local-code-asst-agent" }
    },
    {
      "number": 7,
      "description": "The model generates a response, which is returned through the Agentic Framework and Code Assistant Plugin (code-asst-plugin) to the Developer (actor-developer) in the IDE (local-ide).",
      "actor": { "ref": "model-local" }
    }
  ],
  "alternativeFlows": [
    {
      "name": "External SaaS Agentic Execution (Sub Use Case 1b)",
      "description": "The Agentic Framework and its components (dynamic agent, model, RAG, context store) are hosted on an external SaaS platform rather than on the developer's workstation.",
      "condition": "The Code Assistant Plugin is configured to delegate agentic workflows to an external Agentic SaaS platform.",
      "steps": [
        {
          "number": 1,
          "description": "The Code Assistant Agent (code-asst-agent-static-data) forwards the request to the MCP Gateway (mcp-gateway) on the Agentic SaaS platform.",
          "actor": { "ref": "code-asst-agent-static-data" }
        },
        {
          "number": 2,
          "description": "The MCP Gateway (mcp-gateway) routes the request to the MCP Server — Agentic SaaS (mcp-agentic-saas), which dispatches it to the Remote Code Assistant Agent (remote-code-asst-agent).",
          "actor": { "ref": "mcp-gateway" }
        },
        {
          "number": 3,
          "description": "The Remote Code Assistant Agent (remote-code-asst-agent) orchestrates the Remote Code Assistant Model (model-remote), Remote RAG (rag-remote), and Remote Context Store (ctx-remote), then returns the result via the MCP Gateway (mcp-gateway) to the Code Assistant Plugin (code-asst-plugin).",
          "actor": { "ref": "remote-code-asst-agent" }
        }
      ]
    }
  ],
  "exceptions": [
    {
      "name": "Authentication Failure",
      "condition": "The Authentication Service rejects the Developer's credentials or token.",
      "description": "The developer cannot authenticate, preventing plugin activation.",
      "handling": "The plugin displays an authentication error; the developer is prompted to re-authenticate or contact an administrator."
    },
    {
      "name": "MCP Server Unreachable",
      "condition": "An internal or external MCP Server is unavailable or returns a connection error.",
      "description": "Tool calls from the agent cannot be completed, potentially stalling multi-step workflows.",
      "handling": "The agent reports the tool failure to the developer and falls back to model-only responses where possible."
    },
    {
      "name": "Prompt Injection Detected",
      "condition": "Malicious content in the codebase, context store, or RAG output attempts to redirect agent behavior.",
      "description": "An injected instruction overrides the developer's intent, potentially causing unauthorized tool invocations or data exfiltration.",
      "handling": "The agentic framework applies input sanitization; suspicious instructions are flagged and execution is halted pending developer review."
    }
  ],
  "successCriteria": [
    "Developer receives accurate, contextually relevant code suggestions or completions.",
    "All agent tool invocations are authorized and within the defined permission scope.",
    "No sensitive data (credentials, proprietary code) is transmitted to unauthorized endpoints.",
    "Audit logs capture all agent actions and external service calls."
  ],
  "notes": [
    "This top-level use case is realized by two sub use cases (1a and 1b) that differ in the deployment location of the Agentic Framework and its hosted components.",
    "Actors encoded as CycloneDX 2.0 `actors` objects; bom-ref values must match entries in the `actors` array."
  ]
}
```

## Sub Use Case 1a:
The developer's workstation hosts the full agentic framework, including the dynamic agent, model, RAG, and context store. The assistant plugin communicates directly with locally running components, with MCP servers bridging internal third-party services and external cloud platforms.

```
Internal
├── MCP Server
│   └── Third Party Service
├── Authn/Authz
└── Workstation
    ├── IDE
    ├── Local Codebase Clone
    ├── Code Assistant Plugin
    │   └── Code Assistant Agent
    └── Agentic Framework
        ├── Code Assistant Agent (Local Dynamic)
        ├── Code Assistant Model (e.g. 8b)
        ├── RAG
        └── Context Store

External Cloud
└── MCP Server
    └── Cloud Service
```

### CycloneDX 2.0 — `useCase` object

```json
{
  "bom-ref": "usecase:code-assistant-1a",
  "name": "Code Assistant — Sub Use Case 1a (Local Agentic Framework)",
  "description": "The developer's workstation hosts the full agentic framework, including the dynamic agent, model, RAG pipeline, and context store. The assistant plugin communicates directly with locally running components. MCP Servers bridge internal third-party services and external cloud platforms.",
  "actors": [
    { "ref": "actor-developer" },
    { "ref": "code-asst-agent-static-data" },
    { "ref": "local-code-asst-agent" }
  ],
  "preconditions": [
    "The developer's workstation has sufficient resources to run the local Code Assistant Model (e.g., an 8B-parameter model).",
    "The Agentic Framework, RAG pipeline, and Context Store are installed and running locally.",
    "The Code Assistant Plugin is installed in the IDE and authenticated.",
    "Internal MCP Server and relevant Third Party Services are reachable.",
    "External Cloud MCP Server is reachable if cloud service integrations are required."
  ],
  "postconditions": [
    "Developer receives AI-generated code suggestions produced by the locally hosted model.",
    "All data—including codebase content and context—remains within the internal network boundary unless explicitly forwarded via MCP to an external cloud service.",
    "Agent tool invocations are logged locally."
  ],
  "mainFlow": [
    {
      "number": 1,
      "description": "The Developer (actor-developer) submits a coding request through the IDE (local-ide) to the Code Assistant Plugin (code-asst-plugin).",
      "actor": { "ref": "actor-developer" }
    },
    {
      "number": 2,
      "description": "The Code Assistant Agent (code-asst-agent-static-data) authenticates and authorizes the request via the Authentication Service (authn-service) and Authorization Service (authz-service).",
      "actor": { "ref": "code-asst-agent-static-data" }
    },
    {
      "number": 3,
      "description": "The Code Assistant Agent (code-asst-agent-static-data) evaluates the request and, for complex tasks, delegates to the Code Assistant Agent (Local Dynamic) (local-code-asst-agent) within the local Agentic Framework (framework-1a).",
      "actor": { "ref": "code-asst-agent-static-data" }
    },
    {
      "number": 4,
      "description": "The Code Assistant Agent (Local Dynamic) (local-code-asst-agent) orchestrates the Local Code Assistant Model (model-local), invoking Local RAG (rag-local) and Local Context Store (ctx-local) to enrich the prompt.",
      "actor": { "ref": "local-code-asst-agent" }
    },
    {
      "number": 5,
      "description": "If external data or service integration is required, the Code Assistant Agent (Local Dynamic) (local-code-asst-agent) calls the Third Party MCP Server (local-mcp-server-third-party) or the MCP Server — Cloud Service (mcp-cloud).",
      "actor": { "ref": "local-code-asst-agent" }
    },
    {
      "number": 6,
      "description": "The Local Code Assistant Model (model-local) generates the response, which is returned through the Agentic Framework (framework-1a) and Code Assistant Plugin (code-asst-plugin) to the Developer (actor-developer) in the IDE (local-ide).",
      "actor": { "ref": "model-local" }
    }
  ],
  "alternativeFlows": [
    {
      "name": "Cloud Service Tool Call",
      "description": "The dynamic agent requires data or actions from an external cloud provider.",
      "condition": "The developer's request or the agent's workflow requires interaction with a cloud service (e.g., AWS, GCP).",
      "steps": [
        {
          "number": 1,
          "description": "The Code Assistant Agent (Local Dynamic) (local-code-asst-agent) invokes the MCP Server — Cloud Service (mcp-cloud).",
          "actor": { "ref": "local-code-asst-agent" }
        },
        {
          "number": 2,
          "description": "The Cloud Service (cloud-service) processes the request and returns results through the MCP Server — Cloud Service (mcp-cloud) to the Code Assistant Agent (Local Dynamic) (local-code-asst-agent).",
          "actor": { "ref": "cloud-service" }
        }
      ]
    }
  ],
  "exceptions": [
    {
      "name": "Insufficient Local Resources",
      "condition": "The workstation does not have enough CPU/GPU/RAM to run the local model.",
      "description": "Model inference fails or produces degraded responses due to resource constraints.",
      "handling": "The framework reports an error to the developer; the developer may reduce model size or free system resources."
    },
    {
      "name": "Context Store Poisoning",
      "condition": "Malicious or manipulated content is present in the Local Context Store.",
      "description": "Poisoned retrieval data is injected into the model prompt, potentially altering agent behavior.",
      "handling": "The RAG pipeline applies content validation; suspicious documents are flagged and excluded from context assembly."
    }
  ],
  "successCriteria": [
    "Code suggestions are generated entirely within the internal trust boundary.",
    "No developer code or credentials are transmitted to unapproved external endpoints.",
    "Agent tool calls are restricted to permitted MCP Servers.",
    "Local model inference completes within an acceptable latency threshold."
  ],
  "notes": [
    "This sub use case is characterized by a fully local agentic stack — the dynamic agent, model, RAG, and context store all run on the developer's workstation.",
    "MCP Servers act as the sole egress path to third-party and cloud services."
  ]
}
```

## Sub Use Case 1b:
The agentic framework is offloaded to an external SaaS platform, which hosts the dynamic agent, model, RAG, and context store behind an MCP Gateway. The workstation retains the plugin and local agent, with MCP servers connecting to both internal third-party services and external cloud platforms.

```
Internal
├── MCP Server
│   └── Third Party Service (e.g. Jira, GitHub)
├── Authn/Authz
└── Workstation
    ├── IDE
    ├── Local Codebase Clone
    ├── Code Assistant Plugin
    │   └── Code Assistant Agent
    └── Agentic Framework (stub — agentic execution delegated to External SaaS)

External SaaS
├── Plugin Marketplace
└── Agentic SaaS
    ├── MCP Gateway
    └── MCP Server (e.g. Claude Code)
        ├── Remote Code Assistant Agent
        ├── Code Assistant Model (e.g. 30b)
        ├── RAG
        └── Context store

External Cloud
└── MCP Server
    └── Cloud Service (e.g. AWS, GCP)
```

### CycloneDX 2.0 — `useCase` object

```json
{
  "bom-ref": "usecase:code-assistant-1b",
  "name": "Code Assistant — Sub Use Case 1b (External SaaS Agentic Framework)",
  "description": "The agentic framework is offloaded to an external SaaS platform, which hosts the dynamic agent, model, RAG pipeline, and context store behind an MCP Gateway. The workstation retains the Code Assistant Plugin and local agent. MCP Servers connect to both internal third-party services and external cloud platforms. The Plugin Marketplace is the source for plugin installation.",
  "actors": [
    { "ref": "actor-developer" },
    { "ref": "code-asst-agent-static-data" },
    { "ref": "remote-code-asst-agent" }
  ],
  "preconditions": [
    "The Code Assistant Plugin is installed from the External Plugin Marketplace and is authenticated.",
    "The Agentic SaaS platform is accessible and the developer's account is provisioned.",
    "The MCP Gateway on the Agentic SaaS platform is reachable from the developer's workstation.",
    "Internal MCP Server and relevant Third Party Services (e.g., Jira, GitHub) are reachable.",
    "External Cloud MCP Server is reachable if cloud service integrations are required."
  ],
  "postconditions": [
    "Developer receives AI-generated code suggestions produced by the remotely hosted model.",
    "Developer code and context submitted to the SaaS platform are governed by the platform's data handling and retention policies.",
    "Agent tool invocations on the SaaS side are logged by the platform."
  ],
  "mainFlow": [
    {
      "number": 1,
      "description": "The Developer (actor-developer) installs the Code Assistant Plugin (code-asst-plugin) from the External Plugin Marketplace (external-plugin-marketplace) and opens it within the IDE (local-ide).",
      "actor": { "ref": "actor-developer" }
    },
    {
      "number": 2,
      "description": "The Code Assistant Agent (code-asst-agent-static-data) authenticates and authorizes the request via the Authentication Service (authn-service) and Authorization Service (authz-service).",
      "actor": { "ref": "code-asst-agent-static-data" }
    },
    {
      "number": 3,
      "description": "The Code Assistant Agent (code-asst-agent-static-data) evaluates the request and forwards complex tasks to the Agentic SaaS platform (agentic-saas) via the MCP Gateway (mcp-gateway).",
      "actor": { "ref": "code-asst-agent-static-data" }
    },
    {
      "number": 4,
      "description": "The MCP Gateway (mcp-gateway) authenticates the inbound request and routes it to the MCP Server — Agentic SaaS (mcp-agentic-saas).",
      "actor": { "ref": "mcp-gateway" }
    },
    {
      "number": 5,
      "description": "The Remote Code Assistant Agent (remote-code-asst-agent) on the Agentic SaaS platform (agentic-saas) orchestrates the Remote Code Assistant Model (model-remote), Remote RAG (rag-remote), and Remote Context Store (ctx-remote).",
      "actor": { "ref": "remote-code-asst-agent" }
    },
    {
      "number": 6,
      "description": "If external service integration is required, the Remote Code Assistant Agent (remote-code-asst-agent) calls the Third Party MCP Server (local-mcp-server-third-party) or the MCP Server — Cloud Service (mcp-cloud).",
      "actor": { "ref": "remote-code-asst-agent" }
    },
    {
      "number": 7,
      "description": "The Remote Code Assistant Model (model-remote) generates the response, which is returned via the MCP Gateway (mcp-gateway) and Code Assistant Plugin (code-asst-plugin) to the Developer (actor-developer) in the IDE (local-ide).",
      "actor": { "ref": "model-remote" }
    }
  ],
  "alternativeFlows": [
    {
      "name": "Internal Third-Party Service Integration",
      "description": "The remote dynamic agent requires data from an internal third-party service (e.g., Jira, GitHub).",
      "condition": "The agent's workflow includes a tool call targeting an internally operated Third Party MCP Server.",
      "steps": [
        {
          "number": 1,
          "description": "The Remote Code Assistant Agent (remote-code-asst-agent) issues a tool call to the internal Third Party MCP Server (local-mcp-server-third-party) via the established secure channel.",
          "actor": { "ref": "remote-code-asst-agent" }
        },
        {
          "number": 2,
          "description": "The Third Party MCP Server (local-mcp-server-third-party) processes the request against the third-party service and returns results to the Remote Code Assistant Agent (remote-code-asst-agent).",
          "actor": { "ref": "local-mcp-server-third-party" }
        }
      ]
    },
    {
      "name": "Cloud Service Tool Call",
      "description": "The Remote Code Assistant Agent requires data or actions from an external cloud provider.",
      "condition": "The developer's request or the agent's workflow requires interaction with a cloud service (e.g., AWS, GCP).",
      "steps": [
        {
          "number": 1,
          "description": "The Remote Code Assistant Agent (remote-code-asst-agent) invokes the MCP Server — Cloud Service (mcp-cloud).",
          "actor": { "ref": "remote-code-asst-agent" }
        },
        {
          "number": 2,
          "description": "The Cloud Service (cloud-service) processes the request and returns results through the MCP Server — Cloud Service (mcp-cloud) to the Remote Code Assistant Agent (remote-code-asst-agent).",
          "actor": { "ref": "cloud-service" }
        }
      ]
    }
  ],
  "exceptions": [
    {
      "name": "Agentic SaaS Platform Unavailable",
      "condition": "The Agentic SaaS platform or MCP Gateway is unreachable due to an outage or network failure.",
      "description": "The developer cannot complete multi-step agentic tasks; the plugin degrades to static-only responses.",
      "handling": "The Code Assistant Agent (code-asst-agent-static-data) notifies the developer of the degraded state and provides best-effort responses without SaaS delegation."
    },
    {
      "name": "Malicious Plugin from Marketplace",
      "condition": "A plugin installed from the External Plugin Marketplace contains malicious code.",
      "description": "The plugin exfiltrates developer credentials, codebase content, or manipulates agent outputs.",
      "handling": "The Authentication and Authorization Services should enforce least-privilege; organizations should vet plugins prior to installation and monitor plugin network activity."
    },
    {
      "name": "Data Exfiltration via SaaS",
      "condition": "Code or context submitted to the Agentic SaaS platform is accessed or retained in violation of data handling agreements.",
      "description": "Sensitive proprietary code or secrets are exposed to the SaaS provider or third parties.",
      "handling": "Organizations should review SaaS data retention policies, apply code redaction where possible, and avoid submitting secrets or regulated data to external platforms."
    },
    {
      "name": "Prompt Injection via Remote Context Store",
      "condition": "Malicious content ingested into the Remote Context Store or Remote RAG pipeline redirects the remote agent's behavior.",
      "description": "An injected instruction overrides the developer's intent, potentially causing unauthorized tool invocations or data exfiltration from the SaaS platform.",
      "handling": "The SaaS platform and agentic framework apply input sanitization; suspicious instructions are flagged and execution is halted pending developer review."
    }
  ],
  "successCriteria": [
    "Developer receives accurate code suggestions from the remote model within acceptable latency.",
    "All data transmitted to the Agentic SaaS platform is governed by agreed data handling policies.",
    "Agent tool calls are restricted to permitted internal and external MCP Servers.",
    "Plugin integrity is verified prior to installation and during runtime."
  ],
  "notes": [
    "This sub use case introduces a third-party trust boundary at the Agentic SaaS platform, which hosts the most capable (e.g., 30B-parameter) model.",
    "The External Plugin Marketplace is a supply chain risk vector — plugins should be vetted and sourced from trusted publishers.",
    "MCP Gateway acts as the sole ingress point to the SaaS agentic stack and is a high-value target."
  ]
}
```

## Canonical Diagram Entity Mapping

| Canonical Name                      | Taxonomy Group         | Usecases | Group          |
| ----------------------------------- | ---------------------- | -------- | -------------- |
| Developer                           | Actor                  | 1a,1b    | Internal       |
| Code Assistant Plugin               | Data                   | 1a,1b    | Internal       |
| Local Codebase Clone                | Data                   | 1a,1b    | Internal       |
| IDE                                 | Application            | 1a,1b    | Internal       |
| Authentication Service              | Application            | 1a,1b    | Internal       |
| Authorization Service               | Application            | 1a,1b    | Internal       |
| Third Party MCP Server              | Application            | 1a,1b    | Internal       |
| MCP Server — Third Party Service    | Application            | 1a,1b    | Internal       |
| Code Assistant Agent          | Application            | 1a,1b    | Internal       |
| Code Assistant Agent (Local Dynamic) | Application       | 1a       | Internal       |
| Remote Code Assistant Agent  | Application           | 1b       | External SaaS  |
| Agentic Framework                   | Framework              | 1a       | Internal       |
| Agentic Framework                   | Framework              | 1b       | External SaaS  |
| Local Code Assistant Model          | Machine-Learning-Model | 1a       | Internal       |
| Remote Code Assistant Model         | Machine-Learning-Model | 1b       | External SaaS  |
| Local RAG                           | Application            | 1a       | Internal       |
| Remote RAG                          | Application            | 1b       | External SaaS  |
| Local Context Store                 | Data                   | 1a       | Internal       |
| Remote Context Store                | Data                   | 1b       | External SaaS  |
| MCP Gateway                         | Application            | 1b       | External SaaS  |
| MCP Server — Agentic SaaS           | Application            | 1b       | External SaaS  |
| External Plugin Marketplace         | Platform               | 1b       | External SaaS  |
| Agentic SaaS                        | Platform               | 1b       | External SaaS  |
| MCP Server — Cloud Service          | Application            | 1a,1b    | External Cloud |
| Cloud Service (AWS/GCP/etc.)        | Application            | 1a,1b    | External Cloud |

## Diagram Content
The following taxonomy is aligned to available component types as present in [CycloneDX 1.7/2.0+](https://cyclonedx.org/docs/1.7/json/#metadata_tools_oneOf_i0_components_items_type). An example is shown below:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "2.0",
  "version": 1,
  "components": [
    {
      "bom-ref": "authn-service",
      "type": "application",
      "name": "Authentication Service"
    }
  ]
}
```

**Note:** Parties/Roles to cover the Threat Modelling concept of Actors will be available from CycloneDX 2.0.

### Parties/Roles (Actors)

Humans or services that take action

- **Developer**
  The human actor who writes, modifies, and maintains code—considered a potential target (e.g., phishing, credential theft) or source of risk (e.g., introducing vulnerabilities or misconfigurations).

  Example: A backend engineer, a DevOps engineer, a security engineer, a contractor with repo access.

- **Code Assistant Agent**
  The agent delivered as part of the Code Assistant Plugin. Before installation the plugin is a static software component; once activated inside the IDE the embedded agent becomes an actor with agency over the developer environment. It handles low-latency tasks such as inline completions and prompt assembly, and can invoke local MCP servers for context retrieval. In threat modeling it is treated as an active actor, since its capabilities can be leveraged—intentionally or through manipulation such as prompt injection—to carry out malicious or unintended actions including data exfiltration, unsafe operations, or abuse of integrated services.

  Example: GitHub Copilot (in-IDE agent), Amazon Q Developer (in-IDE agent)

- **Code Assistant Agent (Local Dynamic)**
  A locally hosted agent embedded within the agentic framework on the developer's workstation. It has *dynamic* capabilities: full access to tool calling, MCP servers, a RAG pipeline, and a context store. It orchestrates multi-step, tool-using workflows on behalf of the developer while keeping all data within the internal trust boundary. In threat modeling it is treated as an active actor with an expanded blast radius—its autonomous, multi-tool operation makes it susceptible to prompt injection, workflow hijacking, and cascading misuse of integrated services accessible via MCP.

  Example: Continue with Ollama, Aider with a locally hosted model, OpenHands with a local LLM

- **Remote Code Assistant Agent**
  An agent hosted entirely within the External SaaS trust boundary, opaque to the developer beyond its API surface. It orchestrates multi-step workflows using a large, remotely hosted model and may have access to additional tools, skills, and service connectors that are not individually enumerated in this use case. In threat modeling it is treated as an active actor with a broad blast radius—its external hosting introduces risks around data exfiltration, third-party data handling, prompt injection via remote context, and limited developer visibility into its internal operations.

  Example: Claude Code (Anthropic), Cursor Agent, Devin (Cognition AI)

#### CycloneDX 2.0 Blueprint — `actors` encoding

```json
{
  "actors": [
    {
      "bom-ref": "actor-developer",
      "party": {
        "roles": [
          { "role": "developer" }
        ],
        "persona": {
          "archetype": "developer",
          "scope": "internal",
          "description": "Human actor who writes, modifies, and maintains code—considered a potential target (e.g., phishing, credential theft) or source of risk (e.g., introducing vulnerabilities or misconfigurations)."
        }
      },
      "description": "The human developer who interacts with the code assistant within the IDE."
    },
    {
      "bom-ref": "code-asst-agent-static-data",
      "party": {
        "roles": [
          { "role": "agent" }
        ],
        "system": {
          "kind": "agent",
          "permissions": [
            "invoke-ide-apis",
            "read-local-codebase",
            "call-llm-inference-endpoint",
            "invoke-local-mcp-servers"
          ]
        }
      },
      "description": "The agent embedded within the Code Assistant Plugin. Operates as a static component prior to installation; once activated in the IDE it becomes an actor with agency over the developer environment. Handles low-latency tasks and local MCP tool calls. Susceptible to prompt injection and abuse of integrated services."
    },
    {
      "bom-ref": "local-code-asst-agent",
      "party": {
        "roles": [
          { "role": "agent" }
        ],
        "system": {
          "kind": "agent",
          "permissions": [
            "orchestrate-multi-step-workflows",
            "invoke-mcp-servers",
            "invoke-local-rag-pipeline",
            "read-write-local-context-store",
            "read-local-codebase"
          ]
        }
      },
      "description": "A locally hosted agent embedded within the agentic framework on the developer's workstation. Has dynamic access to tool calling, MCP servers, a local RAG pipeline, and a local context store. Orchestrates multi-step workflows while keeping data within the internal trust boundary. Susceptible to prompt injection, workflow hijacking, and cascading misuse of MCP-accessible services."
    },
    {
      "bom-ref": "remote-code-asst-agent",
      "party": {
        "roles": [
          { "role": "agent" }
        ],
        "system": {
          "kind": "agent",
          "permissions": [
            "orchestrate-multi-step-workflows",
            "invoke-external-services",
            "invoke-remote-mcp-servers"
          ]
        }
      },
      "description": "An agent hosted entirely within the External SaaS trust boundary, opaque to the developer beyond its API surface. Orchestrates multi-step workflows using a large remote model and may access additional tools, skills, and connectors not enumerated in this use case. Susceptible to prompt injection via remote context, third-party data handling risks, and limited developer visibility into its internal operations."
    }
  ]
}
```

### Components

#### Group

Used to describe the control zones of an organization relative to the usecases of the org.

- **Internal**
  The **local network boundary**. Contains systems, APIs, or infrastructure that are locally reachable within the organisation's own network—the developer's workstation, on-premises services, and locally installed MCP servers. Components here are governed by the organisation's own security controls and are generally more trusted, but still pose risks such as misconfigurations, lateral movement, and insider threats.

  Example: Developer workstation, self-hosted GitLab, locally installed Jira MCP Server, on-prem Jenkins CI

- **External SaaS**
  The **remote network boundary** for managed SaaS services. Contains third-party software platforms that are accessed over the public internet or a remote network and provide application or agentic capabilities—including the Agentic SaaS platform that hosts the Remote Code Assistant Agent. Components here operate under a third-party trust model and introduce additional risks including supply chain vulnerabilities, data exposure, and limited visibility or control over security practices.

  Example: Claude Code (Anthropic), Cursor, GitHub Copilot Workspace, Slack

- **External Cloud**
  The **remote network boundary** for cloud infrastructure providers. Contains third-party infrastructure and cloud service providers used as execution targets or data stores, accessed remotely via MCP Servers. Introduce additional risks including supply chain vulnerabilities, data exposure, and limited visibility or control over security practices.

  Example: AWS, Google Cloud Platform (GCP), Microsoft Azure

#### Data

Data at rest or data in motion

- **Code Assistant Plugin**
  A compromised or intentionally malicious AI-powered IDE plugin that appears to assist with coding but performs unauthorized actions—introducing risks such as data exfiltration, credential harvesting, backdoor insertion, or manipulation of code and outputs.

  Example: Malicious fake ESLint extension, trojanized Prettier plugin

- **Local Codebase clone**
  A developer’s local copy of a repository—treated as a sensitive asset since it may contain proprietary code, secrets, or configurations that could be exposed if the endpoint is compromised.

  Example: local monorepo checkout

- **Local Context Store**
  A locally hosted data store that supplies structured or unstructured content to the model or retrieval pipeline to enrich responses. Risks include unauthorized access to sensitive stored content, poisoning of the data corpus, and data leakage via model outputs.

  Example: Local Chroma DB, local FAISS index

- **Remote Context Store**
  A remotely hosted data store that supplies structured or unstructured content to the model or retrieval pipeline to enrich responses. Risks include unauthorized access to sensitive stored content, poisoning of the data corpus, and data leakage via model outputs.

  Example: Pinecone, Weaviate

- **RAG data**
  TBC

#### Application

- **Integrated Development Environment (IDE)**
  The software environment where code is written and tested—an attack surface due to risks like malicious extensions, insecure settings, or credential exposure.

   Example: VS Code, JetBrains IntelliJ IDEA, Google Antigravity IDE

- **Authentication Service**
  The service for verifying the identity of a user or system—risks include credential theft, weak authentication mechanisms, and session hijacking.

  Example: Okta, Microsoft Entra ID, AWS Cognito

- **Authorization Service**
  The service for determining what an authenticated user or system is allowed to access or perform—risks include excessive permissions, privilege escalation, and misconfigured access controls.

  Example: Open Policy Agent (OPA), AWS IAM, HashiCorp Boundary

- **Third Party MCP Server**
  An organization-operated MCP server that integrates the assistant with internal third-party services. Poses risks if misconfigured or inadequately secured, including unauthorized data access, insecure API exposure, and privilege escalation through service integrations.

  Example: Internal MCP server bridging Jira, Confluence

- **Code Assistant Agent** *(as a component — prior to activation as an actor)*
  Before the Code Assistant Plugin is installed and activated, the embedded agent is modelled as a static application component. Once activated inside the IDE it transitions to an actor (`code-asst-agent-static-data`). As a component it is subject to supply chain risks: a compromised plugin binary may carry a malicious agent payload.

- **Code Assistant Agent (Local Dynamic)** *(as a component)*
  The locally hosted dynamic agent component embedded within the agentic framework. Modelled as an application component within the framework boundary. Subject to the same supply chain and configuration risks as other locally deployed software, with the additional risk of tool-call misuse and prompt injection once operating as an actor.

- **Remote Code Assistant Agent** *(as a component)*
  The agent component hosted within the External SaaS platform. From the developer's perspective it is an opaque, remotely operated component. Its internal implementation, tool access, and data flows are not fully visible or controlled by the developer's organisation.

- **Local RAG**
  A component, hosted locally, that dynamically fetches relevant content from available data sources to augment the model's context and improve response quality. Introduces risks around ingestion of untrusted or manipulated content, exposure of sensitive data through retrieval, and injection of malicious inputs that propagate into model outputs.

  Example: Local LangChain + Chroma, LlamaIndex + FAISS

- **Remote RAG**
  A component, hosted remotely, that dynamically fetches relevant content from available data sources to augment the model's context and improve response quality. Introduces risks around ingestion of untrusted or manipulated content, exposure of sensitive data through retrieval, and injection of malicious inputs that propagate into model outputs.

  Example: Hosted LangChain + Pinecone, Haystack + Weaviate

- **MCP Server — Cloud Service**
  A vendor-operated MCP server that integrates the assistant with external cloud platforms and services. Introduces supply chain risks including vulnerable or malicious dependencies, excessive permissions, and potential exfiltration of data passed through the integration.

  Example: AWS S3 MCP integration, Google Drive MCP connector

- **MCP Server — Agentic SaaS**
  The MCP server component hosted within the Agentic SaaS platform, responsible for exposing assistant capabilities and orchestrating downstream agent, model, and retrieval components. A high-value target due to its central role—risks include unauthorized access, data interception, and abuse of its broad orchestration capabilities.

  Example: Cursor cloud MCP layer, GitHub Copilot Workspace MCP backend

- **MCP Gateway**
  The ingress service (e.g., proxy, API gateway, or firewall) that receives and routes inbound connections to the assistant backend. Acts as a perimeter trust boundary—misconfiguration or compromise can expose backend infrastructure to unauthorized access or traffic manipulation.

  Example: AWS API Gateway, Nginx reverse proxy, Cloudflare Tunnel

#### Platform

- **External Plugin Marketplace**
  An externally operated third-party platform where developers discover and install IDE plugins or extensions—introduces supply chain risks such as malicious or vulnerable plugins, insufficient vetting, and potential for unauthorized data access or exfiltration.

  Example: VS Code Marketplace, JetBrains Marketplace, Chrome Web Store

- **Agentic SaaS**
  An externally operated platform that delivers agentic assistant capabilities as a managed service. Introduces risks related to third-party data handling, limited visibility into model behavior and data flows, dependency on external availability, and reduced control over security posture.

  Example: Cursor, GitHub Copilot Workspace

#### Framework

- **Agentic Framework**
  The orchestration layer that coordinates multi-step, tool-using workflows on behalf of the assistant. Manages execution flow between the model, retrieval systems, and external services—a high-impact trust boundary where prompt injection, tool misuse, or unintended action chains can have significant consequences.

  Example: LangChain, CrewAI, Anthropic Agents SDK,

### Machine-Learning-Model

- **Local Code Assistant Model**
  The core AI model that generates responses or code suggestions. Run locally (e.g., a self-hosted model). Relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, and insecure output generation. This is a component within the Agent.

  Example: Ollama + CodeLlama 13B, self-hosted Mistral 7B

- **Remote Code Assistant Model**
  The core AI model that generates responses or code suggestions. Run remotely (e.g., a cloud-hosted model such as a 30B-parameter model). Relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, and insecure output generation. This is a component within the Agent.

  Example: Claude Sonnet (Anthropic API), GPT-4o (Azure OpenAI), Llama 3 70B (Amazon Bedrock)

## CycloneDX v2.0 — Code Assistant Threat Model BOM

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "2.0",
  "version": 1,
  "components": [
    {
      "type": "device",
      "bom-ref": "actor-developer",
      "name": "Developer",
      "description": "The human actor who writes, modifies, and maintains code—considered a potential target (e.g., phishing, credential theft) or source of risk (e.g., introducing vulnerabilities or misconfigurations).",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "local-ide",
      "name": "Integrated Development Environment (IDE)",
      "description": "The software environment where code is written and tested—an attack surface due to risks like malicious extensions, insecure settings, or credential exposure.",
      "properties": [
      ]
    },

    {
      "type": "data",
      "bom-ref": "code-asst-plugin",
      "name": "Code Assistant Plugin",
      "description": "A compromised or intentionally malicious AI-powered IDE plugin that appears to assist with coding but performs unauthorized actions—introducing risks such as data exfiltration, credential harvesting, backdoor insertion, or manipulation of code and outputs.",
      "properties": [
      ]
    },

    {
      "type": "data",
      "bom-ref": "data-local-codebase",
      "name": "Local Codebase Clone",
      "description": "A developer's local copy of a repository—treated as a sensitive asset since it may contain proprietary code, secrets, or configurations that could be exposed if the endpoint is compromised.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "authn-service",
      "name": "Authentication Service",
      "description": "The service for verifying the identity of a user or system—risks include credential theft, weak authentication mechanisms, and session hijacking.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "authz-service",
      "name": "Authorization Service",
      "description": "The service for determining what an authenticated user or system is allowed to access or perform—risks include excessive permissions, privilege escalation, and misconfigured access controls.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "local-mcp-server-third-party",
      "name": "Third Party MCP Server",
      "description": "An organization-operated MCP server that integrates the assistant with internal third-party services. Poses risks if misconfigured or inadequately secured, including unauthorized data access, insecure API exposure, and privilege escalation through service integrations.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "code-asst-agent-static-data",
      "name": "Code Assistant Agent",
      "description": "The agent embedded within the Code Assistant Plugin and running inside the IDE on the developer's workstation. Modelled as a static component prior to plugin activation; once activated it becomes an actor with agency. Handles low-latency tasks such as inline completions and prompt assembly, and invokes local MCP servers for context retrieval. Subject to prompt injection, supply chain compromise via the plugin delivery path, and abuse of IDE-accessible APIs.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "local-code-asst-agent",
      "name": "Code Assistant Agent (Local Dynamic)",
      "description": "A locally hosted agent embedded within the agentic framework on the developer's workstation. Has dynamic access to tool calling, MCP servers, a local RAG pipeline, and a local context store. Orchestrates multi-step, tool-using workflows on behalf of the developer while keeping all data within the internal trust boundary. Susceptible to prompt injection, workflow hijacking, and cascading misuse of MCP-accessible services.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "remote-code-asst-agent",
      "name": "Remote Code Assistant Agent",
      "description": "An agent hosted entirely within the External SaaS trust boundary, opaque to the developer beyond its API surface. Orchestrates multi-step workflows using a large, remotely hosted model and may have access to additional tools, skills, and service connectors that are not individually enumerated in this use case. Susceptible to prompt injection via remote context, third-party data handling risks, and limited developer visibility into its internal operations.",
      "properties": [
      ]
    },

    {
      "type": "framework",
      "bom-ref": "framework-1a",
      "name": "Agentic Framework (Internal)",
      "description": "The orchestration layer that coordinates multi-step, tool-using workflows on behalf of the assistant. Manages execution flow between the model, retrieval systems, and external services—a high-impact trust boundary where prompt injection, tool misuse, or unintended action chains can have significant consequences.",
      "properties": [
      ]
    },

    {
      "type": "framework",
      "bom-ref": "framework-1b",
      "name": "Agentic Framework (External SaaS)",
      "description": "The orchestration layer that coordinates multi-step, tool-using workflows on behalf of the assistant. Manages execution flow between the model, retrieval systems, and external services—a high-impact trust boundary where prompt injection, tool misuse, or unintended action chains can have significant consequences.",
      "properties": [
      ]
    },

    {
      "type": "machine-learning-model",
      "bom-ref": "model-local",
      "name": "Local Code Assistant Model",
      "description": "The core AI model that generates responses or code suggestions, run locally (e.g., a self-hosted model). Relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, and insecure output generation. This is a component within the Agent.",
      "properties": [
      ]
    },

    {
      "type": "machine-learning-model",
      "bom-ref": "model-remote",
      "name": "Remote Code Assistant Model",
      "description": "The core AI model that generates responses or code suggestions, run remotely (e.g., a cloud-hosted model such as a 30B-parameter model). Relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, and insecure output generation. This is a component within the Agent.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "rag-local",
      "name": "Local RAG",
      "description": "A component, hosted locally, that dynamically fetches relevant content from available data sources to augment the model's context and improve response quality. Introduces risks around ingestion of untrusted or manipulated content, exposure of sensitive data through retrieval, and injection of malicious inputs that propagate into model outputs.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "rag-remote",
      "name": "Remote RAG",
      "description": "A component, hosted remotely, that dynamically fetches relevant content from available data sources to augment the model's context and improve response quality. Introduces risks around ingestion of untrusted or manipulated content, exposure of sensitive data through retrieval, and injection of malicious inputs that propagate into model outputs.",
      "properties": [
      ]
    },

    {
      "type": "data",
      "bom-ref": "ctx-local",
      "name": "Local Context Store",
      "description": "A locally hosted data store that supplies structured or unstructured content to the model or retrieval pipeline to enrich responses. Risks include unauthorized access to sensitive stored content, poisoning of the data corpus, and data leakage via model outputs.",
      "properties": [
      ]
    },

    {
      "type": "data",
      "bom-ref": "ctx-remote",
      "name": "Remote Context Store",
      "description": "A remotely hosted data store that supplies structured or unstructured content to the model or retrieval pipeline to enrich responses. Risks include unauthorized access to sensitive stored content, poisoning of the data corpus, and data leakage via model outputs.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "mcp-gateway",
      "name": "MCP Gateway",
      "description": "The ingress service (e.g., proxy, API gateway, or firewall) that receives and routes inbound connections to the assistant backend. Acts as a perimeter trust boundary—misconfiguration or compromise can expose backend infrastructure to unauthorized access or traffic manipulation.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "mcp-agentic-saas",
      "name": "MCP Server — Agentic SaaS",
      "description": "The MCP server component hosted within the Agentic SaaS platform, responsible for exposing assistant capabilities and orchestrating downstream agent, model, and retrieval components. A high-value target due to its central role—risks include unauthorized access, data interception, and abuse of its broad orchestration capabilities.",
      "properties": [
      ]
    },

    {
      "type": "platform",
      "bom-ref": "external-plugin-marketplace",
      "name": "External Plugin Marketplace",
      "description": "An externally operated third-party platform where developers discover and install IDE plugins or extensions—introduces supply chain risks such as malicious or vulnerable plugins, insufficient vetting, and potential for unauthorized data access or exfiltration.",
      "properties": [
      ]
    },

    {
      "type": "platform",
      "bom-ref": "agentic-saas",
      "name": "Agentic SaaS",
      "description": "An externally operated platform that delivers agentic assistant capabilities as a managed service. Introduces risks related to third-party data handling, limited visibility into model behavior and data flows, dependency on external availability, and reduced control over security posture.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "mcp-cloud",
      "name": "MCP Server — Cloud Service",
      "description": "A vendor-operated MCP server that integrates the assistant with external cloud platforms and services. Introduces supply chain risks including vulnerable or malicious dependencies, excessive permissions, and potential exfiltration of data passed through the integration.",
      "properties": [
      ]
    },

    {
      "type": "application",
      "bom-ref": "cloud-service",
      "name": "Cloud Service (AWS/GCP/etc.)",
      "description": "Third-party infrastructure and cloud service providers used as dependencies or execution targets—introduce additional risks including supply chain vulnerabilities, data exposure, and limited visibility or control over security practices.",
      "properties": [
      ]
    }
  ],
  "flows": [
    {
      "bom-ref": "flow-developer-to-ide",
      "name": "Developer submits coding request",
      "description": "The Developer initiates a coding assistance interaction by submitting a request through the IDE.",
      "source": "actor-developer",
      "destination": "local-ide",
      "type": "control",
      "synchronous": true,
      "sequence": 1
    },
    {
      "bom-ref": "flow-ide-to-plugin",
      "name": "IDE activates plugin",
      "description": "The IDE routes the developer's request to the Code Assistant Plugin.",
      "source": "local-ide",
      "destination": "code-asst-plugin",
      "type": "control",
      "synchronous": true,
      "sequence": 2
    },
    {
      "bom-ref": "flow-plugin-to-authn",
      "name": "Plugin authenticates developer",
      "description": "The Code Assistant Agent sends credentials to the Authentication Service to verify developer identity.",
      "source": "code-asst-agent-static-data",
      "destination": "authn-service",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 3
    },
    {
      "bom-ref": "flow-plugin-to-authz",
      "name": "Plugin checks developer permissions",
      "description": "The Code Assistant Agent queries the Authorization Service to verify developer permissions.",
      "source": "code-asst-agent-static-data",
      "destination": "authz-service",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 4
    },
    {
      "bom-ref": "flow-plugin-to-codebase",
      "name": "Local agent queries codebase",
      "description": "The Code Assistant Agent reads from the Local Codebase Clone to assemble context for the request.",
      "source": "code-asst-agent-static-data",
      "destination": "data-local-codebase",
      "type": "data",
      "synchronous": true,
      "sequence": 5
    },
    {
      "bom-ref": "flow-plugin-to-mcp-third-party",
      "name": "Local agent calls internal MCP Server",
      "description": "The Code Assistant Agent dispatches a tool call to the internally operated Third Party MCP Server (e.g., Jira MCP Server) to retrieve context such as tickets or project metadata.",
      "source": "code-asst-agent-static-data",
      "destination": "local-mcp-server-third-party",
      "type": "control",
      "synchronous": true,
      "sequence": 6
    },
    {
      "bom-ref": "flow-plugin-to-framework-1a",
      "name": "Local agent delegates to local agentic framework",
      "description": "The Code Assistant Agent forwards complex or multi-step tasks to the Code Assistant Agent (Local Dynamic) within the local Agentic Framework. Applies to Sub Use Case 1a only.",
      "source": "code-asst-agent-static-data",
      "destination": "framework-1a",
      "type": "control",
      "synchronous": true,
      "sequence": 7
    },
    {
      "bom-ref": "flow-dynamic-1a-to-model-local",
      "name": "Local dynamic agent invokes local model",
      "description": "The Code Assistant Agent (Local Dynamic) sends the enriched prompt to the Local Code Assistant Model for inference.",
      "source": "local-code-asst-agent",
      "destination": "model-local",
      "type": "data",
      "synchronous": true,
      "sequence": 8
    },
    {
      "bom-ref": "flow-dynamic-1a-to-rag-local",
      "name": "Local dynamic agent queries local RAG",
      "description": "The Code Assistant Agent (Local Dynamic) retrieves augmented context from the Local RAG pipeline.",
      "source": "local-code-asst-agent",
      "destination": "rag-local",
      "type": "data",
      "synchronous": true,
      "sequence": 9
    },
    {
      "bom-ref": "flow-dynamic-1a-to-ctx-local",
      "name": "Local dynamic agent reads local context store",
      "description": "The Code Assistant Agent (Local Dynamic) fetches structured context from the Local Context Store.",
      "source": "local-code-asst-agent",
      "destination": "ctx-local",
      "type": "data",
      "synchronous": true,
      "sequence": 10
    },
    {
      "bom-ref": "flow-dynamic-1a-to-mcp-cloud",
      "name": "Local dynamic agent calls cloud MCP Server",
      "description": "The Code Assistant Agent (Local Dynamic) invokes the MCP Server — Cloud Service to interact with an external cloud provider (e.g., AWS, GCP). Applies to Sub Use Case 1a only.",
      "source": "local-code-asst-agent",
      "destination": "mcp-cloud",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 11
    },
    {
      "bom-ref": "flow-mcp-cloud-to-cloud-service",
      "name": "Cloud MCP Server calls cloud service",
      "description": "The MCP Server — Cloud Service forwards the tool call to the target Cloud Service (e.g., AWS, GCP) and returns results.",
      "source": "mcp-cloud",
      "destination": "cloud-service",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 12
    },
    {
      "bom-ref": "flow-model-local-to-developer",
      "name": "Local model returns response to developer",
      "description": "The Local Code Assistant Model response travels back through the Agentic Framework and Code Assistant Plugin to the Developer in the IDE.",
      "source": "model-local",
      "destination": "actor-developer",
      "type": "data",
      "synchronous": true,
      "sequence": 13
    },
    {
      "bom-ref": "flow-plugin-to-mcp-gateway",
      "name": "Local agent forwards request to MCP Gateway",
      "description": "The Code Assistant Agent sends complex tasks to the MCP Gateway on the Agentic SaaS platform for remote execution. Applies to Sub Use Case 1b only.",
      "source": "code-asst-agent-static-data",
      "destination": "mcp-gateway",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 14
    },
    {
      "bom-ref": "flow-mcp-gateway-to-mcp-agentic-saas",
      "name": "MCP Gateway routes request to SaaS MCP Server",
      "description": "The MCP Gateway authenticates the inbound request and routes it to the MCP Server — Agentic SaaS.",
      "source": "mcp-gateway",
      "destination": "mcp-agentic-saas",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 15
    },
    {
      "bom-ref": "flow-mcp-agentic-saas-to-dynamic-1b",
      "name": "SaaS MCP Server dispatches to remote dynamic agent",
      "description": "The MCP Server — Agentic SaaS dispatches the request to the Remote Code Assistant Agent within the Agentic SaaS platform.",
      "source": "mcp-agentic-saas",
      "destination": "remote-code-asst-agent",
      "type": "control",
      "synchronous": true,
      "sequence": 16
    },
    {
      "bom-ref": "flow-dynamic-1b-to-model-remote",
      "name": "Remote dynamic agent invokes remote model",
      "description": "The Remote Code Assistant Agent sends the enriched prompt to the Remote Code Assistant Model for inference.",
      "source": "remote-code-asst-agent",
      "destination": "model-remote",
      "type": "data",
      "synchronous": true,
      "sequence": 17
    },
    {
      "bom-ref": "flow-dynamic-1b-to-rag-remote",
      "name": "Remote dynamic agent queries remote RAG",
      "description": "The Remote Code Assistant Agent retrieves augmented context from the Remote RAG pipeline.",
      "source": "remote-code-asst-agent",
      "destination": "rag-remote",
      "type": "data",
      "synchronous": true,
      "sequence": 18
    },
    {
      "bom-ref": "flow-dynamic-1b-to-ctx-remote",
      "name": "Remote dynamic agent reads remote context store",
      "description": "The Remote Code Assistant Agent fetches structured context from the Remote Context Store.",
      "source": "remote-code-asst-agent",
      "destination": "ctx-remote",
      "type": "data",
      "synchronous": true,
      "sequence": 19
    },
    {
      "bom-ref": "flow-dynamic-1b-to-mcp-third-party",
      "name": "Remote dynamic agent calls internal MCP Server",
      "description": "The Remote Code Assistant Agent issues a tool call to the internal Third Party MCP Server (e.g., Jira, GitHub) via a secure channel. Applies to Sub Use Case 1b only.",
      "source": "remote-code-asst-agent",
      "destination": "local-mcp-server-third-party",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 20
    },
    {
      "bom-ref": "flow-dynamic-1b-to-mcp-cloud",
      "name": "Remote dynamic agent calls cloud MCP Server",
      "description": "The Remote Code Assistant Agent invokes the MCP Server — Cloud Service to interact with an external cloud provider (e.g., AWS, GCP). Applies to Sub Use Case 1b only.",
      "source": "remote-code-asst-agent",
      "destination": "mcp-cloud",
      "type": "control",
      "synchronous": true,
      "encrypted": true,
      "sequence": 21
    },
    {
      "bom-ref": "flow-model-remote-to-developer",
      "name": "Remote model returns response to developer",
      "description": "The Remote Code Assistant Model response travels back through the MCP Gateway and Code Assistant Plugin to the Developer in the IDE.",
      "source": "model-remote",
      "destination": "actor-developer",
      "type": "data",
      "synchronous": true,
      "sequence": 22
    },
    {
      "bom-ref": "flow-marketplace-to-plugin",
      "name": "Plugin Marketplace delivers plugin to IDE",
      "description": "The External Plugin Marketplace delivers the Code Assistant Plugin to the developer's IDE during installation. Applies to Sub Use Case 1b only.",
      "source": "external-plugin-marketplace",
      "destination": "code-asst-plugin",
      "type": "data",
      "synchronous": false,
      "sequence": 0
    }
  ]
}
```
