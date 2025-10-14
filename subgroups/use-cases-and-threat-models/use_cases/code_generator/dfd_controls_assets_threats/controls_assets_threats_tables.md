# Controls, Assets, and Threats for Code Generator Assistant
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

## Threats

| ID  | Threat (brief)                                                            | STRIDE | Category      | Standards / mappings (OWASP / GenAI / ATLAS) | Likely CWE(s) | Component(s) |
|-----|---------------------------------------------------------------------------|--------|---------------|----------------------------------------------|---------------|--------------|
| T01 | Credential theft / spoofing of developer identity (local device theft, key compromise) | Spoofing | platform      | OWASP A07: Identification & Authentication Failures; MITRE ATLAS: Credential Access | CWE-522, CWE-287 | Workstation: Developer device environment |
| T02 | Local data tampering / ransomware encrypting local workspace (tamper with code) | Tampering | platform      | OWASP A05: Security Misconfiguration; OWASP A08: Software & Data Integrity Failures | CWE-352, CWE-444 | Workstation: Developer device environment |
| T03 | Insider repudiation / misuse: user denies actions or malicious insider modifies code | Repudiation | application  | OWASP A09: Security Logging & Monitoring Failures | CWE-778 | Workstation: Developer device environment |
| T04 | Code tampering in local clone (supply chain/backdoor introduced locally) | Tampering | application   | OWASP A08: Software & Data Integrity Failures; MITRE ATLAS: Supply Chain Compromise | CWE-494, CWE-1104 | Workstation: Local codebase clone |
| T05 | Exposure of local secret/config (leak of tokens in files/IDE) | Information Disclosure | platform | OWASP A02: Cryptographic Failures; OWASP A06: Vulnerable and Outdated Components | CWE-200, CWE-312 | Workstation: Local codebase clone |
| T06 | Malicious plugin/extension code execution (IDE plugin executes arbitrary code) | Elevation of Privilege / Tampering | application | OWASP A05: Security Misconfiguration; MITRE ATLAS: Tool Abuse | CWE-94, CWE-78 | Workstation: IDE |
| T07 | Disclosure via telemetry / IDE context leakage to third parties | Information Disclosure | network | OWASP A02: Cryptographic Failures; OWASP GenAI LLM Top 10: Sensitive Data Exposure | CWE-200, CWE-532 | Workstation: IDE |
| T08 | Prompt injection / model misuse from plugin (malicious input causes model to reveal secrets or misbehave) | Integrity / Spoofing | AI / application | OWASP GenAI LLM Top 10: Prompt Injection; MITRE ATLAS: Adversarial Input | CWE-74, CWE-933 | Workstation: Assistant Plugin |
| T09 | Exfiltration via plugin callbacks (plugin returns data to attacker-controlled endpoint) | Information Disclosure / Denial | network | OWASP A01-A10 (data leakage contexts); MITRE ATLAS: Exfiltration Techniques | CWE-200, CWE-918 | Workstation: Assistant Plugin |
| T10 | Unauthorized agent privilege escalation (agent/tool acting with more privileges than intended) | Elevation of Privilege | platform/application | OWASP A01: Broken Access Control; MITRE ATLAS: Privilege Escalation | CWE-269, CWE-425 | Agent Tools |
| T11 | Tool configuration poisoning / supply chain for agent tools | Tampering | platform | OWASP A08: Software & Data Integrity Failures; MITRE ATLAS: Model/Data Poisoning | CWE-494, CWE-1104 | Agent Tools |
| T12 | API key leakage / credential replay to services (service tokens leaked or reused) | Spoofing / Information Disclosure | network | OWASP A07: Identification & Authentication Failures; MITRE ATLAS: Credential Access | CWE-522, CWE-200 | Service: Service(s) e.g., Jira, GitHub APIs |
| T13 | Broken access control on service resources (excessive permissions, missing RBAC) | Elevation of Privilege / Spoofing | application | OWASP A01: Broken Access Control | CWE-862, CWE-285 | Service: Service(s) e.g., Jira, GitHub APIs |
| T14 | Malicious input leading to backend integrity failures (injection into processing pipeline) | Tampering | application | OWASP A03: Injection; OWASP GenAI LLM Top 10: Malicious Prompt | CWE-89, CWE-79, CWE-74 | Cloud Service: Assistant Backend |
| T15 | Logging/monitoring blindspots enabling repudiation (lack of audit trail) | Repudiation | platform | OWASP A09: Logging & Monitoring Failures | CWE-778, CWE-221 | Cloud Service: Assistant Backend |
| T16 | Prompt injection / jailbreak to LLM leading to unsafe outputs or secret disclosure | Integrity / Information Disclosure | AI | OWASP GenAI LLM Top 10: Prompt Injection / Jailbreak; MITRE ATLAS: Adversarial Input | CWE-74, CWE-94 | Cloud Service: Assistant LLM |
| T17 | Model extraction / theft of model weights or proprietary prompts | Information Disclosure / Tampering | AI / platform | MITRE ATLAS: Model Extraction; OWASP GenAI LLM Top 10: Model Theft | CWE-200, CWE-927 | Cloud Service: Assistant LLM |
| T18 | Data poisoning (training/feedback) undermining model integrity | Tampering | AI | MITRE ATLAS: Data Poisoning; OWASP GenAI LLM Top 10: Data Integrity | CWE-20, CWE-912 | Cloud Service: Assistant LLM |
| T19 | Malicious outputs / hallucinations causing misbehavior or harmful actions (safety) | Information Disclosure / Integrity | AI / application | OWASP GenAI LLM Top 10: Harmful Outputs; MITRE ATLAS: Adversarial Outputs | CWE-20, CWE-703 | Cloud Service: Assistant LLM |
| T20 | Unauthorized model access (compromise of model serving infra) | Elevation of Privilege / Spoofing | platform | MITRE ATLAS: Model Access | CWE-269, CWE-284 | Cloud Service: Assistant LLM |
| T21 | Credential brute force / replay against authn (password spray, stolen tokens) | Spoofing | network/application | OWASP A07: Identification & Authentication Failures | CWE-307, CWE-288 | Authn/Authz: Authn |
| T22 | Broken authorization leading to privilege escalation (improper RBAC checks) | Elevation of Privilege | application | OWASP A01: Broken Access Control | CWE-285, CWE-639 | Authn/Authz: Authz |
