# Controls and Assets for Code Generator Assistant
The tables below detail the controls and assets shown on the code generator data flow diagram (dfd).

## Controls

| ID    | Control Name                     | Description                                                 | Located In                                       |
|-------|----------------------------------|-------------------------------------------------------------|--------------------------------------------------|
| C01   | Device Hardening                 | Secure developer workstation configuration                  | Workstation: Developer environment               |
| C02   | Endpoint EDR / AV                | Local runtime monitoring and malware protection             | Workstation: Developer environment               |
| C03   | TLS Encryption                   | Enforces encryption in transit for all communications       | Workstation, Agent Tools, Service, Cloud Service |
| C04   | Multi-Factor Authentication      | Strong authentication to access system resources            | Authn                                            |
| C05   | Access Logging                   | Audit trail for authentication and authorization events     | Authz                                            |
| C06   | Local Secrets Vault              | Secure storage for API keys and credentials                 | Workstation: Local codebase clone                |
| C07   | IDE Sandboxing                   | Restricts plugin access to code and environment             | Workstation: IDE                                 |
| C08   | Code Signing Validation          | Ensures downloaded plugins / dependencies are trusted       | Workstation: Assistant Plugin                    |
| C09   | Agent Tool Permissions           | Defines what agent tools can access or modify               | Agent Tools                                      |
| C10   | Network Policy Enforcement       | Limits agent tools’ outbound network requests               | Agent Tools                                      |
| C11   | Service API Tokens               | Scoped service credentials for integrations                 | Service                                          |
| C12   | Data Access Control              | Least-privilege access for service data                     | Service                                          |
| C13   | Input Sanitization               | Filters malicious requests at backend                       | Cloud Service: Assistant Backend                 |
| C14   | Request Rate Limiting            | Prevents abuse or prompt injection flooding                 | Cloud Service: Assistant Backend                 |
| C15   | Logging & Monitoring             | Monitors backend activity                                   | Cloud Service: Assistant LLM                     |
| C16   | Output Filtering                 | Controls what generated content can be returned             | Cloud Service: Assistant LLM                     |
| C17   | Role-Based Access Control (RBAC  | Limits access per user role                                 | Cloud Service: Assistant LLM                     |
| C18   | Data-at-Rest Encryption          | All stored data is encrypted using strong cryptography      | Workstation: Developer environment, Local codebase clone, IDE, Assistant Plugin; Agent Tools; Service; Cloud Service: Assistant Backend & LLM |

### Universal Controls

| ID    | Control Name                       | Description                                                                 | Located In                                 |
|-------|------------------------------------|-----------------------------------------------------------------------------|--------------------------------------------|
| C19   | Logging & Auditing                 | Maintain detailed logs for all actions and access events, enabling traceability and detection | Scope (all components)   |
| C20   | Monitoring & Alerts                | Continuous monitoring for abnormal activity, with alerts for potential security incidents | Scope (all components)       |
| C21   | Backup & Recovery                  | Ensure regular backups and tested recovery procedures for all critical assets | Scope (all components)                   |
| C22   | Access Control / RBAC              | Enforce principle of least privilege for all users, services, and components | Scope (all components)                    |
| C23   | Secure Configuration               | Standardize and harden configurations for all components to reduce attack surface | Scope (all components)               |
| C24   | Anti-Malware / Endpoint Protection | Deploy malware/endpoint protections for all local devices and service hosts | Scope (all components)                     |
| C25   | Secret Management                  | Centralized and secure storage for credentials, API keys, and other sensitive secrets | Scope (all components)           |
| C26   | Continuous Security Testing        | Automated security scanning (SAST/DAST/IAST) for code, services, and infrastructure | Scope (all components)             |

## Assets

| ID    | Asset Name                  | Description                                   | Located In                         |
|-------|-----------------------------|-----------------------------------------------|------------------------------------|
| A01   | Developer Identity          | Credentials (e.g., SSH keys, tokens)          | Workstation: Developer environment |
| A02   | Personal Workspace Data     | Local temp files and environment              | Workstation: Developer environment |
| A03   | Authn Service Config        | Authentication settings and secrets           | Authn                              |
| A04   | User Session Tokens         | Tokens allowing access                        | Authz                              |
| A05   | Local Codebase Clone        | Developer working copy                        | Workstation: Local codebase clone  |
| A06   | IDE Context Data            | In-memory project metadata                    | Workstation: IDE                   |
| A07   | Assistant Plugin Data       | User commands, snippets, suggestions          | Workstation: Assistant Plugin      |
| A08   | Agent Tool Configs          | Tool/extension configuration and credentials  | Agent Tools                        |
| A09   | Tool Execution Results      | Local execution results and metadata          | Agent Tools                        |
| A10   | Service Data / Projects     | Stored project or ticket information          | Service                            |
| A11   | Service Logs / Metadata     | Activity or audit information                 | Service                            |
| A12   | Assistant Backend Data      | Backend request context or session info       | Cloud Service: Assistant Backend   |
| A13   | LLM Model Data              | Prompt context, temporary memory              | Cloud Service: Assistant LLM       |
| A14   | LLM Output / Suggestions    | Generated suggestions or responses            | Cloud Service: Assistant LLM       |
