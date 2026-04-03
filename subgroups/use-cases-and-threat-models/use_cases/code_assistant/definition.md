## Usecase: Code Assistant

This README provides concise definitions of key components and concepts used in threat modeling diagram.

Diagram (draw.io): ![Diagram](security-and-compliance/subgroups/use-cases-and-threat-models/use_cases/code_assistant/diagram/ai_code_generator_threat_model_diagram.drawio.svg)

[Edit this diagram (draw.io XML)](/Users/colingigool/Documents/open_source/security-and-compliance/subgroups/use-cases-and-threat-models/use_cases/code_assistant/diagram/ai_code_generator_threat_model_diagram.drawio.xml)

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

- **(Code Assistant LLM) Model (Thinking & Tooling capability)**   
    An AI model within the assistant plugin that combines reasoning (“thinking”) and tool interaction capabilities (e.g., APIs, code execution) to perform actions. In threat modeling, it is treated as an active actor since these capabilities can be leveraged—intentionally or through manipulation (e.g., prompt injection)—to carry out malicious or unintended actions such as data exfiltration, unsafe operations, or abuse of integrated services.

### Data

Data at rest or data in motion
- **Code Assistant Plugin (Malicious)**  
  A compromised or intentionally malicious AI-powered IDE plugin that appears to assist with coding but performs unauthorized actions—introducing risks such as data exfiltration, credential harvesting, backdoor insertion, or manipulation of code and outputs.

### Components

Software or services

- **IDE (Integrated Development Environment)**  
  The software environment (e.g., VS Code, IntelliJ) where code is written and tested—an attack surface due to risks like malicious extensions, insecure settings, or credential exposure.

- **Local codebase clone**  
  A developer’s local copy of a repository—treated as a sensitive asset since it may contain proprietary code, secrets, or configurations that could be exposed if the endpoint is compromised.
- **Assistant Backend (Agent Runner)**  
  The server-side infrastructure that processes requests from the assistant plugin, orchestrates workflows, and communicates with LLMs and external services—an important trust boundary and potential target for data interception or abuse.

- **(Code assistant LLM) Model (Large Language Model)**  
  The core AI model that generates responses or code suggestions—relevant in threat modeling due to risks like prompt injection, data leakage, model manipulation, or insecure output generation.

- **RAG (Retrieval-Augmented Generation)**  
  A system design where the LLM retrieves external data (e.g., documents, code, APIs) to enhance responses—introduces risks around data exposure, untrusted data sources, and injection attacks via retrieved content.

- **Custom Extension (e.g., MCP server)**  
  A user- or organization-built extension that integrates with the assistant to provide additional functionality—poses risks if poorly secured, such as unauthorized data access, insecure APIs, or privilege escalation.

- **Vendor-provided Extension (e.g., MCP server)**  
  Third-party extensions supplied by external vendors—introduces supply chain risks, including malicious or vulnerable code, excessive permissions, or data exfiltration.

- **Authentication (Authn)**  
  The process of verifying the identity of a user or system (e.g., passwords, tokens, MFA)—risks include credential theft, weak authentication mechanisms, and session hijacking.

- **Authorization (Authz)**  
  The process of determining what an authenticated user or system is allowed to access or perform—risks include excessive permissions, privilege escalation, and misconfigured access controls.

- **Services (e.g., Jira)**  
  External systems integrated into workflows (e.g., issue tracking, CI/CD, cloud services)—represent additional attack surfaces where data could be accessed, modified, or leaked if integrations are insecure.

- **External Plugin Marketplace**  
  A third-party platform where developers discover and install IDE plugins or extensions—introduces supply chain risks such as malicious or vulnerable plugins, insufficient vetting, and potential for unauthorized data access or exfiltration.

- **(Code Assistant LLM) Model (Thinking & Tooling capability)**  
    A core system component of the assistant architecture responsible for processing inputs, generating responses, and orchestrating tool usage. It represents a critical trust boundary where data is interpreted and actions are initiated, introducing risks related to insecure outputs, data leakage, improper tool invocation, and reliance on untrusted inputs.