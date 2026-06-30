# Use Case: Code Assistant

This document provides concise definitions of the items used in threat modeling diagram.

Diagram (draw.io): ![Diagram](./diagram/ai_code_generator_threat_model_diagram_updated_2026_05_12.drawio.svg)

[Edit this diagram (draw.io XML)](./diagram/ai_code_generator_threat_model_diagram_updated_2026_05_12.drawio)

### CycloneDX 2.0 — `useCase` object

```json
{
  "bom-ref": "usecase:code-assistant",
  "name": "Code Assistant",
  "description": "A developer uses an AI-powered code assistant—composed of a plugin, one or more agents, a language model, a retrieval-augmented generation (RAG) pipeline, and an agentic framework—to accelerate software development tasks such as code generation, explanation, and review. The assistant may run fully on the developer's workstation (Sub Use Case 1a) or offload its agentic components to an external SaaS platform (Sub Use Case 1b).",
  "actors": [
    { "ref": "actor:developer" },
    { "ref": "actor:code-assistant-agent-static" },
    { "ref": "actor:code-assistant-agent-local-dynamic" },
    { "ref": "actor:code-assistant-agent-remote-dynamic" }
  ],
  "preconditions": [
    "Developer has an IDE installed and a local codebase clone available.",
    "The Code Assistant Plugin is installed and authenticated via the Authentication and Authorization Services.",
    "Required MCP Servers are reachable (internal and/or external)."
  ],
  "postconditions": [
    "Developer receives AI-generated code suggestions, completions, or reviews.",
    "Any tool invocations performed by agents are logged and auditable.",
    "No sensitive code or credentials are unintentionally exfiltrated."
  ],
  "mainFlow": [
    {
      "number": 1,
      "description": "The Developer opens the IDE and initiates an interaction with the Code Assistant Plugin.",
      "actor": { "ref": "actor:developer" }
    },
    {
      "number": 2,
      "description": "The Code Assistant Plugin authenticates the Developer via the Authentication Service and checks permissions via the Authorization Service.",
      "actor": { "ref": "actor:code-assistant-agent-static" }
    },
    {
      "number": 3,
      "description": "The Code Assistant Agent (Static Code) processes the Developer's request, optionally querying the Local Codebase Clone and invoking MCP Servers for tool calls.",
      "actor": { "ref": "actor:code-assistant-agent-static" }
    },
    {
      "number": 4,
      "description": "The static agent forwards complex or multi-step tasks to the Code Assistant Agent (Dynamic Code) running within the Agentic Framework.",
      "actor": { "ref": "actor:code-assistant-agent-static" }
    },
    {
      "number": 5,
      "description": "The Code Assistant Agent (Dynamic Code) orchestrates multi-step workflows, invoking the Code Assistant Model, RAG pipeline, and Context Store as needed.",
      "actor": { "ref": "actor:code-assistant-agent-local-dynamic" }
    },
    {
      "number": 6,
      "description": "The Code Assistant Model generates a response, which is returned through the Agentic Framework to the plugin and presented to the Developer in the IDE.",
      "actor": { "ref": "actor:code-assistant-agent-local-dynamic" }
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
          "description": "The Code Assistant Agent (Static Code) forwards the request to the MCP Gateway on the Agentic SaaS platform.",
          "actor": { "ref": "actor:code-assistant-agent-static" }
        },
        {
          "number": 2,
          "description": "The MCP Gateway routes the request to the MCP Server — Agentic SaaS, which dispatches it to the remote Code Assistant Agent (Dynamic Code).",
          "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
        },
        {
          "number": 3,
          "description": "The remote dynamic agent orchestrates the Remote Code Assistant Model, Remote RAG, and Remote Context Store, then returns the result via the MCP Gateway to the plugin.",
          "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
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
    │   └── Code Assistant Agent (Static Code)
    └── Agentic Framework
        ├── Code Assistant Agent (Dynamic Code)
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
    { "ref": "actor:developer" },
    { "ref": "actor:code-assistant-agent-static" },
    { "ref": "actor:code-assistant-agent-local-dynamic" }
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
      "description": "The Developer submits a coding request through the IDE to the Code Assistant Plugin.",
      "actor": { "ref": "actor:developer" }
    },
    {
      "number": 2,
      "description": "The Code Assistant Plugin authenticates and authorizes the request via the internal Authentication and Authorization Services.",
      "actor": { "ref": "actor:code-assistant-agent-static" }
    },
    {
      "number": 3,
      "description": "The Code Assistant Agent (Static Code) evaluates the request and, for complex tasks, delegates to the local Agentic Framework.",
      "actor": { "ref": "actor:code-assistant-agent-static" }
    },
    {
      "number": 4,
      "description": "The Code Assistant Agent (Dynamic Code) orchestrates the Local Code Assistant Model, invoking Local RAG and Local Context Store to enrich the prompt.",
      "actor": { "ref": "actor:code-assistant-agent-local-dynamic" }
    },
    {
      "number": 5,
      "description": "If external data or service integration is required, the dynamic agent calls the internal Third Party MCP Server or the External Cloud MCP Server.",
      "actor": { "ref": "actor:code-assistant-agent-local-dynamic" }
    },
    {
      "number": 6,
      "description": "The Local Code Assistant Model generates the response, which is returned through the Agentic Framework and plugin to the Developer in the IDE.",
      "actor": { "ref": "actor:code-assistant-agent-local-dynamic" }
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
          "description": "The Code Assistant Agent (Dynamic Code) invokes the MCP Server — Cloud Service.",
          "actor": { "ref": "actor:code-assistant-agent-local-dynamic" }
        },
        {
          "number": 2,
          "description": "The Cloud Service processes the request and returns results through the MCP Server to the dynamic agent.",
          "actor": { "ref": "actor:code-assistant-agent-local-dynamic" }
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
The agentic framework is offloaded to an external SaaS platform, which hosts the dynamic agent, model, RAG, and context store behind an MCP Gateway. The workstation retains the plugin and static agent, with MCP servers connecting to both internal third-party services and external cloud platforms.

```
Internal
├── MCP Server
│   └── Third Party Service (e.g. Jira, GitHub)
├── Authn/Authz
└── Workstation
    ├── IDE
    ├── Local Codebase Clone
    ├── Code Assistant Plugin
    │   └── Code Assistant Agent (Static Code)
    └── Agentic Framework

External SaaS
├── Plugin Marketplace
└── Agentic SaaS
    ├── MCP Gateway
    └── MCP Server (e.g. Claude code)
        ├── Code Assistant Agent (Dynamic Code)
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
  "description": "The agentic framework is offloaded to an external SaaS platform, which hosts the dynamic agent, model, RAG pipeline, and context store behind an MCP Gateway. The workstation retains the Code Assistant Plugin and static agent. MCP Servers connect to both internal third-party services and external cloud platforms. The Plugin Marketplace is the source for plugin installation.",
  "actors": [
    { "ref": "actor:developer" },
    { "ref": "actor:code-assistant-agent-static" },
    { "ref": "actor:code-assistant-agent-remote-dynamic" }
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
      "description": "The Developer installs the Code Assistant Plugin from the External Plugin Marketplace and opens it within the IDE.",
      "actor": { "ref": "actor:developer" }
    },
    {
      "number": 2,
      "description": "The Code Assistant Plugin authenticates and authorizes the request via the internal Authentication and Authorization Services.",
      "actor": { "ref": "actor:code-assistant-agent-static" }
    },
    {
      "number": 3,
      "description": "The Code Assistant Agent (Static Code) evaluates the request and forwards complex tasks to the Agentic SaaS platform via the MCP Gateway.",
      "actor": { "ref": "actor:code-assistant-agent-static" }
    },
    {
      "number": 4,
      "description": "The MCP Gateway on the Agentic SaaS platform authenticates the inbound request and routes it to the MCP Server — Agentic SaaS.",
      "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
    },
    {
      "number": 5,
      "description": "The Code Assistant Agent (Dynamic Code) on the SaaS platform orchestrates the Remote Code Assistant Model, Remote RAG, and Remote Context Store.",
      "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
    },
    {
      "number": 6,
      "description": "If external service integration is required, the remote dynamic agent calls the internal Third Party MCP Server or the External Cloud MCP Server.",
      "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
    },
    {
      "number": 7,
      "description": "The Remote Code Assistant Model generates the response, which is returned via the MCP Gateway and plugin to the Developer in the IDE.",
      "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
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
          "description": "The Code Assistant Agent (Dynamic Code) issues a tool call to the internal Third Party MCP Server via the established secure channel.",
          "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
        },
        {
          "number": 2,
          "description": "The Third Party Service processes the request and returns results through the MCP Server to the remote dynamic agent.",
          "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
        }
      ]
    },
    {
      "name": "Cloud Service Tool Call",
      "description": "The remote dynamic agent requires data or actions from an external cloud provider.",
      "condition": "The developer's request or the agent's workflow requires interaction with a cloud service (e.g., AWS, GCP).",
      "steps": [
        {
          "number": 1,
          "description": "The Code Assistant Agent (Dynamic Code) invokes the MCP Server — Cloud Service.",
          "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
        },
        {
          "number": 2,
          "description": "The Cloud Service processes the request and returns results through the MCP Server to the remote dynamic agent.",
          "actor": { "ref": "actor:code-assistant-agent-remote-dynamic" }
        }
      ]
    }
  ],
  "exceptions": [
    {
      "name": "Agentic SaaS Platform Unavailable",
      "condition": "The Agentic SaaS platform or MCP Gateway is unreachable due to an outage or network failure.",
      "description": "The developer cannot complete multi-step agentic tasks; the plugin degrades to static-only responses.",
      "handling": "The Code Assistant Agent (Static Code) notifies the developer of the degraded state and provides best-effort responses without SaaS delegation."
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
| Code Assistant Agent (Static Code)  | Application            | 1a,1b    | Internal       |
| Code Assistant Agent (Dynamic Code) | Application            | 1a       | Internal       |
| Code Assistant Agent (Dynamic Code) | Application            | 1b       | External SaaS  |
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
  "specVersion": "1.7",
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

- **Code Assistant Agent (Static Code)**
  An AI model embedded within the assistant plugin that combines reasoning and tool interaction capabilities (e.g., APIs, code execution) to perform actions directly within the developer environment. In threat modeling it is treated as an active actor, since these capabilities can be leveraged—intentionally or through manipulation such as prompt injection—to carry out malicious or unintended actions including data exfiltration, unsafe operations, or abuse of integrated services.

- **Local Code Assistant Agent (Dynamic Code)**
  A locally hosted AI model within the agentic framework that combines reasoning and tool interaction capabilities to orchestrate multi-step workflows, invoke external services, and coordinate with the broader agent ecosystem. In threat modeling it is treated as an active actor with an expanded blast radius relative to its static counterpart—its autonomous, multi-tool operation makes it susceptible to prompt injection, workflow hijacking, and cascading misuse of integrated systems.

- **Remote Code Assistant Agent (Dynamic Code)**
  A remotely hosted AI model within the agentic framework that combines reasoning and tool interaction capabilities to orchestrate multi-step workflows, invoke external services, and coordinate with the broader agent ecosystem. In threat modeling it is treated as an active actor with an expanded blast radius relative to its static counterpart—its autonomous, multi-tool operation makes it susceptible to prompt injection, workflow hijacking, and cascading misuse of integrated systems.

#### CycloneDX 2.0 Blueprint — `actors` encoding

```json
{
  "actors": [
    {
      "bom-ref": "actor:developer",
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
      "bom-ref": "actor:code-assistant-agent-static",
      "party": {
        "roles": [
          { "role": "agent" }
        ],
        "system": {
          "kind": "agent",
          "permissions": [
            "invoke-ide-apis",
            "read-local-codebase",
            "call-llm-inference-endpoint"
          ]
        }
      },
      "description": "An AI model embedded within the assistant plugin that combines reasoning and tool interaction capabilities (e.g., APIs, code execution) to perform actions directly within the developer environment. Treated as an active actor susceptible to prompt injection and abuse of integrated services."
    },
    {
      "bom-ref": "actor:code-assistant-agent-local-dynamic",
      "party": {
        "roles": [
          { "role": "agent" }
        ],
        "system": {
          "kind": "agent",
          "permissions": [
            "orchestrate-multi-step-workflows",
            "invoke-external-services",
            "coordinate-agent-ecosystem",
            "read-local-codebase"
          ]
        }
      },
      "description": "A locally hosted AI model within the agentic framework that orchestrates multi-step workflows and invokes external services. Treated as an active actor with an expanded blast radius—susceptible to prompt injection, workflow hijacking, and cascading misuse of integrated systems."
    },
    {
      "bom-ref": "actor:code-assistant-agent-remote-dynamic",
      "party": {
        "roles": [
          { "role": "agent" }
        ],
        "system": {
          "kind": "agent",
          "permissions": [
            "orchestrate-multi-step-workflows",
            "invoke-external-services",
            "coordinate-agent-ecosystem"
          ]
        }
      },
      "description": "A remotely hosted AI model within the agentic framework that orchestrates multi-step workflows and invokes external services. Treated as an active actor with an expanded blast radius—susceptible to prompt injection, workflow hijacking, and cascading misuse of integrated systems."
    }
  ]
}
```

### Components

#### Group

Used to describe the control zones of an organization relative to the usecases of the org.

- **Internal**  
  Systems, APIs, or infrastructure owned and operated within the organization’s environment—generally more trusted but still pose risks such as misconfigurations, lateral movement, and insider threats.

- **External SaaS**  
  Third-party managed software platforms that provide application or agentic capabilities (SaaS-style trust boundary) — introduce additional risks including supply chain vulnerabilities, data exposure, and limited visibility or control over security practices.

- **External Cloud**  
  Third-party infrastructure and cloud service providers used as dependencies or execution targets — introduce additional risks including supply chain vulnerabilities, data exposure, and limited visibility or control over security practices.

#### Data

Data at rest or data in motion

- **Code Assistant Plugin**  
  A compromised or intentionally malicious AI-powered IDE plugin that appears to assist with coding but performs unauthorized actions—introducing risks such as data exfiltration, credential harvesting, backdoor insertion, or manipulation of code and outputs.  

- **Local Codebase clone**  
  A developer’s local copy of a repository—treated as a sensitive asset since it may contain proprietary code, secrets, or configurations that could be exposed if the endpoint is compromised.

- **Local Context Store**  
  A locally hosted data store that supplies structured or unstructured content to the model or retrieval pipeline to enrich responses. Risks include unauthorized access to sensitive stored content, poisoning of the data corpus, and data leakage via model outputs.

- **Remote Context Store**  
  A remotely hosted data store that supplies structured or unstructured content to the model or retrieval pipeline to enrich responses. Risks include unauthorized access to sensitive stored content, poisoning of the data corpus, and data leakage via model outputs.

- **RAG data**  
  TBC

#### Application

- **Integrated Development Environment (IDE)**  
  The software environment (e.g., VS Code, IntelliJ) where code is written and tested—an attack surface due to risks like malicious extensions, insecure settings, or credential exposure.

- **Authentication Service**  
  The service for verifying the identity of a user or system (e.g., passwords, tokens, MFA)—risks include credential theft, weak authentication mechanisms, and session hijacking.

- **Authorization Service**  
  The service for determining what an authenticated user or system is allowed to access or perform—risks include excessive permissions, privilege escalation, and misconfigured access controls.

- **Third Party MCP Server**
  An organization-operated MCP server that integrates the assistant with internal third-party services. Poses risks if misconfigured or inadequately secured, including unauthorized data access, insecure API exposure, and privilege escalation through service integrations.

- **Local RAG**  
  A component, hosted locally, that dynamically fetches relevant content from available data sources to augment the model's context and improve response quality. Introduces risks around ingestion of untrusted or manipulated content, exposure of sensitive data through retrieval, and injection of malicious inputs that propagate into model outputs.

- **Remote RAG**  
  A component, hosted remotely, that dynamically fetches relevant content from available data sources to augment the model's context and improve response quality. Introduces risks around ingestion of untrusted or manipulated content, exposure of sensitive data through retrieval, and injection of malicious inputs that propagate into model outputs.
  
- **MCP Server — Cloud Service**  
  A vendor-operated MCP server that integrates the assistant with external cloud platforms and services. Introduces supply chain risks including vulnerable or malicious dependencies, excessive permissions, and potential exfiltration of data passed through the integration.

- **MCP Server — Agentic SaaS**
  The MCP server component hosted within the Agentic SaaS platform, responsible for exposing assistant capabilities and orchestrating downstream agent, model, and retrieval components. A high-value target due to its central role—risks include unauthorized access, data interception, and abuse of its broad orchestration capabilities.

- **MCP Gateway**
  The ingress service (e.g., proxy, API gateway, or firewall) that receives and routes inbound connections to the assistant backend. Acts as a perimeter trust boundary—misconfiguration or compromise can expose backend infrastructure to unauthorized access or traffic manipulation.

#### Platform

- **External Plugin Marketplace**  
  An externally operated third-party platform where developers discover and install IDE plugins or extensions—introduces supply chain risks such as malicious or vulnerable plugins, insufficient vetting, and potential for unauthorized data access or exfiltration.

- **Agentic SaaS**
  An externally operated platform that delivers agentic assistant capabilities as a managed service. Introduces risks related to third-party data handling, limited visibility into model behavior and data flows, dependency on external availability, and reduced control over security posture.

#### Framework

- **Agentic Framework**  
  The orchestration layer that coordinates multi-step, tool-using workflows on behalf of the assistant. Manages execution flow between the model, retrieval systems, and external services—a high-impact trust boundary where prompt injection, tool misuse, or unintended action chains can have significant consequences.

### Machine-Learning-Model

- **Local Code Assistant Model**  
  The core AI model that generates responses or code suggestions. Run locally (e.g., a self-hosted model). Relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, and insecure output generation. This is a component within the Agent.

- **Remote Code Assistant Model**  
  The core AI model that generates responses or code suggestions. Run remotely (e.g., a cloud-hosted model such as a 30B-parameter model). Relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, and insecure output generation. This is a component within the Agent.

## CycloneDX v1.7 — Code Assistant Threat Model BOM

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.7",
  "version": 1,
  "components": [
    {
      "type": "device",
      "bom-ref": "actor-developer",
      "name": "Developer",
      "description": "The human actor who writes, modifies, and maintains code—considered a potential target or source of risk.",
      "properties": [
        { "name": "cdx:category", "value": "actor" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "app-ide",
      "name": "Integrated Development Environment (IDE)",
      "description": "The software environment where code is written and tested.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    },

    {
      "type": "data",
      "bom-ref": "data-plugin",
      "name": "Code Assistant Plugin",
      "description": "AI-powered IDE plugin that may be compromised or malicious.",
      "properties": [
        { "name": "cdx:category", "value": "data" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" },
        { "name": "cdx:parent", "value": "app-ide" }
      ]
    },

    {
      "type": "data",
      "bom-ref": "data-local-codebase",
      "name": "Local Codebase Clone",
      "description": "Local copy of repository containing sensitive code and secrets.",
      "properties": [
        { "name": "cdx:category", "value": "data" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "app-authn",
      "name": "Authentication Service",
      "description": "Service responsible for identity verification.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "app-authz",
      "name": "Authorization Service",
      "description": "Service responsible for access control decisions.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "app-mcp-third-party",
      "name": "Third Party MCP Server",
      "description": "Organization-operated MCP server integrating third-party services.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "app-agent-static",
      "name": "Code Assistant Agent (Static Code)",
      "description": "AI model embedded in plugin performing tool use inside IDE.",
      "properties": [
        { "name": "cdx:category", "value": "actor" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a,1b" },
        { "name": "cdx:parent", "value": "data-plugin" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "app-agent-dynamic-1a",
      "name": "Code Assistant Agent (Dynamic Code)",
      "description": "Agentic model orchestrating multi-step workflows (local deployment).",
      "properties": [
        { "name": "cdx:category", "value": "actor" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a" },
        { "name": "cdx:parent", "value": "framework-1a" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "app-agent-dynamic-1b",
      "name": "Code Assistant Agent (Dynamic Code)",
      "description": "Agentic model orchestrating multi-step workflows (remote SaaS deployment).",
      "properties": [
        { "name": "cdx:category", "value": "actor" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" },
        { "name": "cdx:parent", "value": "framework-1b" }
      ]
    },

    {
      "type": "framework",
      "bom-ref": "framework-1a",
      "name": "Agentic Framework (Internal)",
      "description": "Orchestration layer for multi-step tool execution.",
      "properties": [
        { "name": "cdx:category", "value": "framework" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a" }
      ]
    },

    {
      "type": "framework",
      "bom-ref": "framework-1b",
      "name": "Agentic Framework (External SaaS)",
      "description": "Cloud-hosted orchestration layer coordinating agent workflows.",
      "properties": [
        { "name": "cdx:category", "value": "framework" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" }
      ]
    },

    {
      "type": "machine-learning-model",
      "bom-ref": "model-local",
      "name": "Local Code Assistant Model",
      "description": "Locally hosted AI model generating code suggestions.",
      "properties": [
        { "name": "cdx:category", "value": "machine-learning-model" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a" },
        { "name": "cdx:parent", "value": "framework-1a" }
      ]
    },

    {
      "type": "machine-learning-model",
      "bom-ref": "model-remote",
      "name": "Remote Code Assistant Model",
      "description": "Cloud-hosted AI model generating code suggestions.",
      "properties": [
        { "name": "cdx:category", "value": "machine-learning-model" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" },
        { "name": "cdx:parent", "value": "framework-1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "rag-local",
      "name": "Local RAG",
      "description": "Local retrieval-augmented generation system.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "rag-remote",
      "name": "Remote RAG",
      "description": "Cloud-hosted retrieval-augmented generation system.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" }
      ]
    },

    {
      "type": "data",
      "bom-ref": "ctx-local",
      "name": "Local Context Store",
      "description": "Local data store used for retrieval augmentation.",
      "properties": [
        { "name": "cdx:category", "value": "data" },
        { "name": "cdx:environment", "value": "Internal" },
        { "name": "cdx:usecases", "value": "1a" }
      ]
    },

    {
      "type": "data",
      "bom-ref": "ctx-remote",
      "name": "Remote Context Store",
      "description": "Remote data store used for retrieval augmentation.",
      "properties": [
        { "name": "cdx:category", "value": "data" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "mcp-gateway",
      "name": "MCP Gateway",
      "description": "Ingress gateway routing assistant traffic.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "mcp-agentic-saas",
      "name": "MCP Server — Agentic SaaS",
      "description": "Core SaaS orchestration MCP server.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" }
      ]
    },

    {
      "type": "platform",
      "bom-ref": "external-plugin-marketplace",
      "name": "External Plugin Marketplace",
      "description": "Third-party plugin distribution platform.",
      "properties": [
        { "name": "cdx:category", "value": "platform" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" }
      ]
    },

    {
      "type": "platform",
      "bom-ref": "agentic-saas",
      "name": "Agentic SaaS",
      "description": "Managed agentic assistant platform.",
      "properties": [
        { "name": "cdx:category", "value": "platform" },
        { "name": "cdx:environment", "value": "External SaaS" },
        { "name": "cdx:usecases", "value": "1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "mcp-cloud",
      "name": "MCP Server — Cloud Service",
      "description": "Vendor-operated MCP integration service.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "External Cloud" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    },

    {
      "type": "application",
      "bom-ref": "cloud-service",
      "name": "Cloud Service (AWS/GCP/etc.)",
      "description": "Underlying cloud infrastructure services.",
      "properties": [
        { "name": "cdx:category", "value": "application" },
        { "name": "cdx:environment", "value": "External Cloud" },
        { "name": "cdx:usecases", "value": "1a,1b" }
      ]
    }
  ]
}
```
