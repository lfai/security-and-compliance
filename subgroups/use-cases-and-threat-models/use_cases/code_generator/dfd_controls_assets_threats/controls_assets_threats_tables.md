# Controls, Assets, and Threats for Code Generator Assistant
The tables below detail the controls, assets, and threats shown on the code generator data flow diagram (dfd).

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

### STRIDE Reference

|Type     |  Description | Security Control |
|---------|--------------|------------------|
Spoofing  |	Threat action aimed at accessing and use of another user’s credentials, such as username and password. | Authentication |
Tampering |	Threat action intending to maliciously change or modify persistent data, such as records in a database, and the alteration of data in transit between two computers over an open network, such as the Internet. | Integrity |
Repudiation | 	Threat action aimed at performing prohibited operations in a system that lacks the ability to trace the operations. | Non-Repudiation |
Information disclosure |	Threat action intending to read a file that one was not granted access to, or to read data in transit. | Confidentiality |
Denial of service |	Threat action attempting to deny access to valid users, such as by making a web server temporarily unavailable or unusable. | Availability |
Elevation of privilege |	Threat action intending to gain privileged access to resources in order to gain unauthorized access to information or to compromise a system. | Authorization |

**Source:** [STRIDE Threat List (OWASP)](https://owasp.org/www-community/Threat_Modeling_Process#stride)

### Threat Table

| ID  | Threat (brief)                                                           | Threat Statement                                                                                                   | STRIDE | Category      | Standards / mappings (OWASP / GenAI / ATLAS) | Likely CWE(s) | Component(s) |
|-----|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|--------|---------------|----------------------------------------------|---------------|--------------|
| T01 | Credential theft / spoofing of developer identity                        | Nation state steals credentials on developer device to access source code without authorization                   | Spoofing | platform      | OWASP A07; MITRE ATLAS: Credential Access   | CWE-522, CWE-287 | Workstation: Developer device environment |
| T01 | Credential theft / spoofing of developer identity                        | Disgruntled employee steals local keys to bypass authentication and exfiltrate proprietary code                  | Spoofing | platform      | OWASP A07; MITRE ATLAS: Credential Access   | CWE-522, CWE-287 | Workstation: Developer device environment |
| T02 | Local data tampering / ransomware encrypting local workspace             | Script kiddie encrypts local codebase to disrupt development workflow                                             | Tampering | platform      | OWASP A05, A08                                | CWE-352, CWE-444 | Workstation: Developer device environment |
| T03 | Insider repudiation / misuse                                             | Disgruntled employee modifies code and denies changes to evade accountability                                      | Repudiation | application  | OWASP A09                                     | CWE-778          | Workstation: Developer device environment |
| T04 | Code tampering in local clone                                            | Nation state injects malicious backdoor into local clone to compromise downstream systems                          | Tampering | application   | OWASP A08; MITRE ATLAS: Supply Chain         | CWE-494, CWE-1104 | Workstation: Local codebase clone |
| T05 | Exposure of local secret/config                                          | Accident/mistake accidentally commits API tokens to local repository, exposing secrets                            | Information Disclosure | platform | OWASP A02, A06                               | CWE-200, CWE-312 | Workstation: Local codebase clone |
| T06 | Malicious plugin/extension code execution                                | Nation state installs malicious plugin in IDE to execute arbitrary code                                            | Elevation of Privilege / Tampering | application | OWASP A05; MITRE ATLAS: Tool Abuse          | CWE-94, CWE-78  | Workstation: IDE |
| T07 | Disclosure via telemetry / IDE context leakage                           | Script kiddie captures telemetry from IDE to steal snippets or sensitive data                                      | Information Disclosure | network | OWASP A02; OWASP GenAI LLM Top 10           | CWE-200, CWE-532 | Workstation: IDE |
| T08 | Prompt injection / model misuse from plugin                              | Disgruntled employee injects malicious prompt via plugin to make model reveal secrets                              | Integrity / Spoofing | AI / application | OWASP GenAI LLM Top 10; MITRE ATLAS          | CWE-74, CWE-933 | Workstation: Assistant Plugin |
| T09 | Exfiltration via plugin callbacks                                        | Nation state uses plugin callback to exfiltrate sensitive customer data                                           | Information Disclosure / Denial | network | OWASP A01-A10; MITRE ATLAS: Exfiltration    | CWE-200, CWE-918 | Workstation: Assistant Plugin |
| T10 | Unauthorized agent privilege escalation                                  | Script kiddie escalates privileges of agent tool to bypass intended permissions                                   | Elevation of Privilege | platform/application | OWASP A01; MITRE ATLAS: Privilege Escalation | CWE-269, CWE-425 | Agent Tools |
| T11 | Tool configuration poisoning / supply chain                              | Nation state poisons agent tool configuration to compromise integrity of processing                                | Tampering | platform | OWASP A08; MITRE ATLAS: Model/Data Poisoning | CWE-494, CWE-1104 | Agent Tools |
| T12 | API key leakage / credential replay                                      | Script kiddie steals service API keys to access customer data unauthorized                                        | Spoofing / Information Disclosure | network | OWASP A07; MITRE ATLAS: Credential Access   | CWE-522, CWE-200 | Service: Service(s) e.g., Jira, GitHub APIs |
| T13 | Broken access control on service resources                               | Disgruntled employee bypasses RBAC to modify restricted data                                                      | Elevation of Privilege / Spoofing | application | OWASP A01                                     | CWE-862, CWE-285 | Service: Service(s) e.g., Jira, GitHub APIs |
| T14 | Malicious input leading to backend integrity failures                    | Nation state injects malicious payloads into assistant backend to corrupt processing                                | Tampering | application | OWASP A03; OWASP GenAI LLM Top 10           | CWE-89, CWE-79, CWE-74 | Cloud Service: Assistant Backend |
| T15 | Logging/monitoring blindspots enabling repudiation                       | Disgruntled employee disables logging to hide malicious activity                                                  | Repudiation | platform | OWASP A09                                     | CWE-778, CWE-221 | Cloud Service: Assistant Backend |
| T16 | Prompt injection / jailbreak to LLM                                      | Script kiddie sends malicious prompt to LLM to exfiltrate secrets or generate unsafe outputs                       | Integrity / Information Disclosure | AI | OWASP GenAI LLM Top 10; MITRE ATLAS         | CWE-74, CWE-94  | Cloud Service: Assistant LLM |
| T17 | Model extraction / theft of model weights or proprietary prompts         | Nation state extracts model weights from LLM to replicate or steal intellectual property                            | Information Disclosure / Tampering | AI / platform | MITRE ATLAS; OWASP GenAI LLM Top 10         | CWE-200, CWE-927 | Cloud Service: Assistant LLM |
| T18 | Data poisoning (training/feedback)                                       | Disgruntled employee submits malicious feedback to corrupt model training                                         | Tampering | AI | MITRE ATLAS; OWASP GenAI LLM Top 10         | CWE-20, CWE-912  | Cloud Service: Assistant LLM |
| T19 | Malicious outputs / hallucinations                                       | Script kiddie injects prompts to cause harmful or unsafe model outputs                                            | Information Disclosure / Integrity | AI / application | OWASP GenAI LLM Top 10; MITRE ATLAS         | CWE-20, CWE-703  | Cloud Service: Assistant LLM |
| T20 | Unauthorized model access                                                | Nation state compromises model serving infrastructure to access confidential data                                   | Elevation of Privilege / Spoofing | platform | MITRE ATLAS                                  | CWE-269, CWE-284 | Cloud Service: Assistant LLM |
| T21 | Credential brute force / replay against authn                            | Script kiddie performs password spray on Authn endpoint to access accounts                                         | Spoofing | network/application | OWASP A07                                     | CWE-307, CWE-288 | Authn/Authz: Authn |
| T22 | Broken authorization leading to privilege escalation                     | Disgruntled employee bypasses authorization checks to gain elevated privileges                                     | Elevation of Privilege | application | OWASP A01                                     | CWE-285, CWE-639 | Authn/Authz: Authz |
| T23 | Assistant plugin accesses cloned code not intended for sharing           | Attacker exploits assistant plugin to access and transmit cloned code to backend, violating confidentiality policies                 | Information Disclosure | application | OWASP A02; OWASP GenAI LLM Top 10           | CWE-200, CWE-532 | Workstation: Assistant Plugin |
| T24 | Assistant generates code under restrictive license due to training data contamination | Assistant generates code resembling GPL-licensed code due to training on GPL-licensed datasets, leading to unintentional license violations | Information Disclosure | application | OWASP GenAI LLM Top 10; MITRE ATLAS         | CWE-200, CWE-927 | Workstation: Assistant Plugin |
| T25 | Assistant plugin leaks sensitive information (e.g., API keys) to backend | Assistant plugin inadvertently sends sensitive information like API keys to backend, leading to potential data breaches               | Information Disclosure | application | OWASP A02; OWASP GenAI LLM Top 10           | CWE-200, CWE-532 | Workstation: Assistant Plugin |
| T26 | MCP connection vulnerability allows remote code execution                | Exploitation of MCP connection vulnerability enables remote code execution, compromising system integrity                           | Elevation of Privilege | platform     | OWASP A08; MITRE ATLAS: Command Injection   | CWE-78, CWE-94  | Agent Tools, Service |
| T27 | MCP lacks access controls, enabling unauthorized data access             | Absence of access controls in MCP allows unauthorized entities to access sensitive data, violating confidentiality policies           | Information Disclosure | platform     | OWASP A01; MITRE ATLAS: Access Control      | CWE-284, CWE-285 | Agent Tools, Service |
| T28 | Confused Deputy Attack via MCP Tool Routing                              | Attacker manipulates tool metadata to redirect agent actions, causing unintended operations on behalf of the agent                   | Elevation of Privilege | platform     | OWASP A01: Broken Access Control             | CWE-285, CWE-284 | Agent Tools, Service |
| T29 | Session Hijacking in MCP-enabled Agents                                  | Attacker intercepts or predicts session tokens, gaining unauthorized access to agent sessions                                        | Elevation of Privilege | platform     | OWASP A02: Cryptographic Failures            | CWE-287, CWE-319 | Agent Tools, Service |
| T30 | Token Passthrough Anti-pattern in MCP Communication                      | Improper handling of tokens across agents leads to unauthorized access or escalation of privileges                                    | Elevation of Privilege | platform     | OWASP A01: Broken Access Control             | CWE-285, CWE-284 | Agent Tools, Service |
| T31 | Input/Instruction Boundary Distinction Failure in MCP                    | System fails to distinguish between legitimate instructions and malicious input, enabling injection attacks unique to AI systems    | Tampering | platform     | OWASP A03: Injection                         | CWE-74, CWE-79   | Agent Tools, Service |
| T32 | Missing Integrity/Verification Controls in MCP                           | Lack of mechanisms to ensure data and configuration integrity, enabling tampering and spoofing attacks                               | Tampering | platform     | OWASP A08: Software & Data Integrity Failures | CWE-494, CWE-1104 | Agent Tools, Service |

**References:**
 - [OWASP Top 10 for Web Applications](https://owasp.org/Top10/)
 - [OWASP Top 10 for LLMs](https://genai.owasp.org/llm-top-10/)
 - [MITRE ATLAS](https://atlas.mitre.org/matrices/ATLAS)
 - [Adversa AI MCP Security Top 25 Vulnerabilities](https://adversa.ai/mcp-security-top-25-mcp-vulnerabilities)
