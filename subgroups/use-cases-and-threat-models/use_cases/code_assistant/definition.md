## Use Case: Code Assistant

This README provides concise definitions of key components and concepts used in threat modeling diagram.

Diagram (draw.io): ![Diagram](./diagram/ai_code_generator_threat_model_diagram_updated_2026_05_05.drawio.svg)

[Edit this diagram (draw.io XML)](./diagramm/ai_code_generator_threat_model_diagram_updated_2026_05_05.drawio)

### Code Assistant - Sub Use Case Specification

Note that within the Code Assistant Use Case there are two sub use cases:

A. The Backend for the Code Assistant is locally hosted within the same workstation  
B. The Backend for the Code Assistant is remotely hosted  

### Logical boundries

Used to describe the control zones of an organization relative to the usecases of the org.

- **Internal**  
  Systems, APIs, or infrastructure owned and operated within the organization’s environment—generally more trusted but still pose risks such as misconfigurations, lateral movement, and insider threats.

- **External**  
  Third-party systems or services outside the organization’s control (e.g., SaaS, APIs, cloud providers)—introduce additional risks including supply chain vulnerabilities, data exposure, and limited visibility or control over security practices.

### Actors

Humans or services that take action

- **Developer**  
  The human actor who writes, modifies, and maintains code—considered a potential target (e.g., phishing, credential theft) or source of risk (e.g., introducing vulnerabilities or misconfigurations).

- **Code Assistant Agent**   
    An AI model within the assistant plugin that combines reasoning ("thinking") and tool interaction capabilities (e.g., APIs, code execution) to perform actions. In threat modeling, it is treated as an active actor since these capabilities can be leveraged—intentionally or through manipulation (e.g., prompt injection)—to carry out malicious or unintended actions such as data exfiltration, unsafe operations, or abuse of integrated services.

### Data

Data at rest or data in motion

- **Code Assistant Plugin**  
  A compromised or intentionally malicious AI-powered IDE plugin that appears to assist with coding but performs unauthorized actions—introducing risks such as data exfiltration, credential harvesting, backdoor insertion, or manipulation of code and outputs.  

### Components

Software or services

Common:

- **IDE (Integrated Development Environment)**  
  The software environment (e.g., VS Code, IntelliJ) where code is written and tested—an attack surface due to risks like malicious extensions, insecure settings, or credential exposure.

- **Local codebase clone**  
  A developer’s local copy of a repository—treated as a sensitive asset since it may contain proprietary code, secrets, or configurations that could be exposed if the endpoint is compromised.

- **Authentication (Authn)**  
  The service for verifying the identity of a user or system (e.g., passwords, tokens, MFA)—risks include credential theft, weak authentication mechanisms, and session hijacking.

- **Authorization (Authz)**  
  The service for determining what an authenticated user or system is allowed to access or perform—risks include excessive permissions, privilege escalation, and misconfigured access controls.

- **Services (e.g., Jira)**  
  External systems integrated into workflows (e.g., issue tracking, CI/CD, cloud services)—represent additional attack surfaces where data could be accessed, modified, or leaked if integrations are insecure.

- **External Plugin Marketplace**  
  A third-party platform where developers discover and install IDE plugins or extensions—introduces supply chain risks such as malicious or vulnerable plugins, insufficient vetting, and potential for unauthorized data access or exfiltration.

### Sub Use Case 1a:

- **Code Assistant Agent (local)**  
  The server-side infrastructure that processes requests from the assistant plugin, orchestrates workflows, and communicates with LLMs and external services—an important trust boundary and potential target for data interception or abuse.

- **Code Assistant Model (local)**  
  The core AI model that generates responses or code suggestions—relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, or insecure output generation (component within the Agent).

- **Context Store (local)**  
  A system design where the LLM retrieves external data (e.g., documents, code, APIs) to enhance responses—introduces risks around data exposure, untrusted data sources, and injection attacks via retrieved content.

- **Rag (local)**  
  A modular component that enables Retrieval-Augmented Generation by dynamically fetching relevant local or external data (e.g., files, documentation, APIs) to support the agent’s decision-making and response generation based on the scenario. Within an agentic framework on a workstation, it is invoked contextually to enhance task execution, but introduces risks such as exposure of sensitive local data, ingestion of untrusted content, and propagation of malicious or manipulated inputs into the model’s outputs.

- **MCP server (AWS Service) (Remote)**  
  Third-party extensions supplied by external vendors—introduces supply chain risks, including malicious or vulnerable code, excessive permissions, or data exfiltration.
```
Internal
├── MCP Server
│   └── Service (Jira)
├── Authn/Authz
└── Workstation
    ├── IDE
    ├── Local Codebase Clone
    ├── Code Assistant Plugin
    │   └── Code Assistant Agent (Static Code)
    └── Agentic Framework
        ├── Code Assistant Agent (Dynamic Code)
        ├── Code Assistant Model (e.g. 8b)
        ├── Rag
        └── Context Store

External B
└── MCP Server
    └── Service (AWS)
```

### Sub Use Case 1b:

- **Remote Backend Gateway**
  The service (e.g., proxy, firewall) that receives connections aimed at the remote backend

- **Code Assistant Agent (Dynamic code)(remote)**  
  The server-side infrastructure that processes requests from the assistant plugin, orchestrates workflows, and communicates with LLMs and external services—an important trust boundary and potential target for data interception or abuse.

- **Code Assistant Model (e.g. 30b)(remote)**  
  The core AI model that generates responses or code suggestions—relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, or insecure output generation (component within the Agent).

- **Context Store (remote)**  
  A system design where the LLM retrieves external data (e.g., documents, code, APIs) to enhance responses—introduces risks around data exposure, untrusted data sources, and injection attacks via retrieved content.

- **Rag (local)**  
  A modular component that enables Retrieval-Augmented Generation by dynamically fetching relevant local or external data (e.g., files, documentation, APIs) to support the agent’s decision-making and response generation based on the scenario. Within an agentic framework on a workstation, it is invoked contextually to enhance task execution, but introduces risks such as exposure of sensitive local data, ingestion of untrusted content, and propagation of malicious or manipulated inputs into the model’s outputs.

- **MCP server (Jira Service) (Local)**  
  A user- or organization-built extension that integrates with the assistant to provide additional functionality—poses risks if poorly secured, such as unauthorized data access, insecure APIs, or privilege escalation.

- **MCP server (AWS Service) (remote)**  
  Third-party extensions supplied by external vendors—introduces supply chain risks, including malicious or vulnerable code, excessive permissions, or data exfiltration.

```
Internal
├── MCP Server
│   └── Service (Jira)
├── Authn/Authz
└── Workstation
    ├── IDE
    ├── Local Codebase Clone
    ├── Code Assistant Plugin
    │   └── Code Assistant Agent (Static Code)
    └── Agentic Framework

External A
├── Plugin Marketplace
└── Agentic SaaS
    ├── MCP Gateway
    └── MCP Server (Claude code)
        ├── Code Assistant Agent (Dynamic Code)
        ├── Code Assistant Model (e.g. 30b)
        ├── Rag
        └── Context store

External B
└── MCP Server
    └── Service (AWS)
```