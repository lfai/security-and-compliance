# **Assets, Controls, and Threats for Chatbot**  
The tables below detail the assets, controls, and threats shown on the chatbot diagram  
  
****Assets****  

| ID | Asset Name | Description | Located In |
| --- | ------------------------ | ---------------------------------------------------- | ------------------------------------------------------ |
| A01 | AI Engineer Identity | Credentials (e.g., login credentials, access tokens) | Engineer Activities: AI Engineer |
| A02 | Source Documents | Original documents and reference data | Engineer Activities: Database |
| A03 | Vector Embeddings | Numerical representations of knowledge base content | Engineer Activities: Vector Database |
| A04 | Vector Database Metadata | Document metadata and indexing information | Engineer Activities: Vector Database |
| A05 | User Identity | Credentials (e.g., usernames, passwords, tokens) | User Activities: Authn |
| A06 | User Session Tokens | Tokens allowing access | User Activities: Authz |
| A07 | User Query Data | User questions and search requests | User Activities: GenAI App |
| A08 | Retrieved Context | Documents and content retrieved for queries | GenAI App: Retriever |
| A09 | LLM API Keys | API credentials for generative LLM service | Cloud (SaaS)/On-Prem: Generative LLM |
| A10 | LLM Context Data | Prompt context and temporary memory | Cloud (SaaS)/On-Prem: Generative LLM |
| A11 | LLM Output | Generated responses and suggestions | Cloud (SaaS)/On-Prem: Generative LLM |
| A12 | Embedding API Keys | API credentials for embedding model service | Cloud (SaaS)/On-Prem: Embedding Model |
| A13 | Model Weights | Proprietary model parameters  | Cloud (SaaS)/On-Prem: Generative LLM & Embedding Model |
  
  
  
****Controls****  

| ID | Control Name | Description | Located In | Mitigates Threats |
| --- | ------------------------------------ | ------------------------------------------------------------------------- | ---------------------------------------- | ------------------------ |
| C01 | Multi-Factor Authentication (MFA) | Require MFA for AI Engineer accounts | Engineer Activities: AI Engineer | T01 |
| C02 | Privileged Access Monitoring | Monitor and log all privileged user activities for anomalous behaviour | Engineer Activities: AI Engineer | T01, T02 |
| C03 | Role-Based Access Control (RBAC) | Implement least-privilege access to database resources | Engineer Activities: Database | T03, T18 |
| C04 | Data Encryption at Rest | Encrypt all stored documents and sensitive data | Engineer Activities: Database | T06, T19 |
| C05 | Source Validation | Verify authenticity and provenance of all data sources | Engineer Activities: Database | T04, T20 |
| C06 | Input Validation and Sanitisation | Validate and sanitise all inputs before processing | Engineer Activities: Data Processing | T07, T08 |
| C07 | Processing Audit Logs | Maintain detailed logs of all data transformations | Engineer Activities: Data Processing | T10 |
| C08 | Embedding Access Controls | Restrict who can view or export embedding data | Engineer Activities: Vector Database | T11 |
| C09 | Embedding Integrity Verification | Use cryptographic hashes to verify embedding integrity | Engineer Activities: Vector Database | T12, T13 |
| C10 | Vector Database Access Control | Implement fine-grained access controls on vector operations | Engineer Activities: Vector Database | T14, T18 |
| C11 | Query Parameterisation | Use parameterised queries to prevent injection attacks | Engineer Activities: Vector Database | T15 |
| C12 | Rate Limiting on Vector Queries | Limit number of queries per user/session to prevent DoS and exfiltration | Engineer Activities: Vector Database | T16, T17 |
| C13 | User Multi-Factor Authentication | Require MFA for all users | User Activities: User | T21 |
| C14 | Secure Session Management | Use cryptographically secure session tokens with timeout | User Activities: Authn & Authz | T22 |
| C15 | Prompt Injection Detection | Scan queries for known prompt injection and jailbreak patterns | User Activities: Input Guard (Query) | T27, T29 |
| C16 | Input Sanitisation | Remove or escape potentially harmful characters and validate input length | User Activities: Input Guard (Query) | T28 |
| C17 | Embedding Input Validation | Validate queries before embedding generation | User Activities: Input Guard (Embedding) | T30 |
| C18 | Embedding Service Rate Limiting | Limit embedding requests per user/session | User Activities: Input Guard (Embedding) | T31 |
| C19 | Standard Authentication Protocol | Implement OAuth 2.0 / OIDC with token-based authentication | User Activities: Authn & Authz | T22, T23 |
| C20 | Least Privilege Access | Grant minimum necessary permissions with centralised policy enforcement | User Activities: Authn & Authz | T24, T25 |
| C21 | Authentication Audit Logging | Log all authentication and authorisation events | User Activities: Authn & Authz | T26 |
| C22 | PII Detection and Redaction | Scan responses for personal and sensitive information | User Activities: Output Guard | T32, T35 |
| C23 | Content Moderation | Filter harmful, biased, or inappropriate content | User Activities: Output Guard | T33, T34 |
| C24 | API Authentication and Authorisation | Require authentication for all API endpoints | GenAI App: GenAI App | T37 |
| C25 | API Rate Limiting | Limit API calls per user/IP address | GenAI App: GenAI App | T38, T42 |
| C26 | TLS/SSL Encryption | Encrypt all API communications | GenAI App: GenAI App | T39 |
| C27 | Retrieval Validation | Validate retrieved content before use | GenAI App: Retriever | T43, T44 |
| C28 | Context Window Limits | Restrict amount of retrieved information | GenAI App: Retriever | T45 |
| C29 | Query Complexity Limits | Limit computational complexity of searches | GenAI App: Retriever | T47 |
| C30 | LLM Query Rate Limiting | Limit queries to prevent model extraction and DoS | Cloud (SaaS)/On-Prem: Generative LLM | T48, T51 |
| C31 | Response Validation | Verify LLM responses for quality, safety, and hallucinations | Cloud (SaaS)/On-Prem: Generative LLM | T49, T50 |
| C32 | API Key Secrets Management | Store keys in secure vault with regular rotation | Cloud (SaaS)/On-Prem: Generative LLM | T52, T53 |
| C33 | Embedding Service Rate Limiting | Limit embedding generation requests to prevent extraction | Cloud (SaaS)/On-Prem: Embedding Model | T54 |
| C34 | Input Normalisation | Normalise inputs to reduce adversarial effectiveness | Cloud (SaaS)/On-Prem: Embedding Model | T55 |
| C35 | Embedding API Key Secrets Management | Store keys in secure vault with regular rotation | Cloud (SaaS)/On-Prem: Embedding Model | T56, T57 |
| C36 | Comprehensive Logging and Monitoring | Log all system activities with centralised SIEM | All components | All threats (detection) |
| C37 | Encryption in Transit | Use TLS for all inter-component communications | All components | Information Disclosure |
| C38 | Regular Security Assessments | Conduct periodic penetration testing and vulnerability assessments | All components | All threats (prevention) |
  
  
  
**Universal Controls**  

| ID | Control Name | Description | Located In |
| --- | ---------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------- |
| C39 | Logging & Auditing | Maintain detailed logs for all actions and access events, enabling traceability and detection | Scope (all components) |
| C40 | Monitoring & Alerts | Continuous monitoring for abnormal activity, with alerts for potential security incidents | Scope (all components) |
| C41 | Backup & Recovery | Ensure regular backups and tested recovery procedures for all critical assets | Scope (all components) |
| C42 | Access Control / RBAC | Enforce principle of least privilege for all users, services, and components | Scope (all components) |
| C43 | Secure Configuration | Standardise and harden configurations for all components to reduce attack surface | Scope (all components) |
| C44 | Anti-Malware / Endpoint Protection | Deploy malware/endpoint protections for all local devices and service hosts | Scope (all components) |
| C45 | Secret Management | Centralised and secure storage for credentials, API keys, and other sensitive secrets | Scope (all components) |
| C46 | Continuous Security Testing | Automated security scanning (SAST/DAST/IAST) for code, services, and infrastructure | Scope (all components) |
  
  
  
## **Threats**  
  
**STRIDE Reference**  

| Type | Description | Security Control |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Spoofing | Threat action aimed at accessing and use of another user’s credentials, such as username and password. | Authentication |
| Tampering | Threat action intending to maliciously change or modify persistent data, such as records in a database, and the alteration of data in transit between two computers over an open network, such as the Internet. | Integrity |
| Repudiation | Threat action aimed at performing prohibited operations in a system that lacks the ability to trace the operations. | Non-Repudiation |
| Information disclosure | Threat action intending to read a file that one was not granted access to, or to read data in transit. | Confidentiality |
| Denial of service | Threat action attempting to deny access to valid users, such as by making a web server temporarily unavailable or unusable. | Availability |
| Elevation of privilege | Threat action intending to gain privileged access to resources in order to gain unauthorized access to information or to compromise a system. | Authorization |
  
  
**Source:** [STRIDE Threat List (OWASP)](https://owasp.org/www-community/Threat_Modeling_Process#stride)  
  
  
  
**Engineer Activities - Threats**  

| ID | Threat (brief) | Description | STRIDE | Category | Standards / mappings (OWASP / GenAI / ATLAS) | Likely CWE(s) | Component(s) | IBM AI Risk Atlas Mapping |
| --- | ---------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------- | ----------- | ------------------------------------------------------------------------------------- | ---------------- | ----------------- | ------------------------- |
| T01 | Credential theft | Attacker steals AI Engineer login credentials to access data preparation systems | Spoofing | Platform | OWASP A07: Identification and Authentication Failures | CWE-522, CWE-287 | (AI Engineer) |  |
| T02 | Malicious insider | AI Engineer intentionally abuses privileges to poison data or steal information | Tampering, Information Disclosure | Application | OWASP A04: Insecure Design | CWE-506, CWE-200 | (AI Engineer) | Intellectual Property |
| T03 | Unauthorised access | Attacker bypasses access controls to access source documents | Information Disclosure | Platform | OWASP A01: Broken Access Control | CWE-284, CWE-285 | (Database) | Intellectual Property |
| T04 | Data tampering  | Attacker modifies source documents to inject malicious or false content | Tampering | Application | OWASP A08: Software and Data Integrity Failures; OWASP LLM03: Training Data Poisoning | CWE-494, CWE-565 | (Database) |  |
| T05 | Denial of a Service | Attacker disrupts database availability preventing data operations | Denial of Service | Platform | OWASP A04: Insecure Design | CWE-400, CWE-770 | (Database) |  |
| T06 | Sensitive data exposure  | Database contains unprotected sensitive or proprietary information | Information Disclosure | Platform | OWASP A02: Cryptographic Failures; OWASP LLM06: Sensitive Information Disclosure | CWE-311, CWE-312 | (Database) | Intellectual Property |
| T07 | Code Injection | Attacker injects malicious code through crafted documents or inputs | Tampering, Elevation of Privilege | Application | OWASP A03: Injection | CWE-94, CWE-502 | (Data Processing) |  |
| T08 | Data poisoning | Attacker manipulates data during processing to corrupt embeddings | Tampering | AI | OWASP LLM03: Training Data Poisoning; MITRE ATLAS: Data Poisoning | CWE-20, CWE-912 | (Data Processing) |  |
| T09 | Pipeline failiure | Data processing component crashes or fails disrupting operations | Denial of Service | Application | OWASP A04: Insecure Design | CWE-754, CWE-703 | (Data Processing) |  |
| T10 | Insufficient logging | Lack of audit trails prevents detection of malicious activities | Repudiation | Platform | OWASP A09: Security Logging and Monitoring Failures | CWE-778, CWE-117 | (Data Processing) |  |
| T11 | Reconstructing embedded data | An attacker tries to figure out what the original documents were by analysing the embeddings | Information Disclosure | AI | OWASP LLM06: Sensitive Information Disclosure; MITRE ATLAS: Model Inversion | CWE-200, CWE-327 | (Embeddings) | Intellectual Property |
| T12 | Embedding manipulation  | An attacker creates fake embeddings that trick the system into returning wrong documents | Tampering | AI | MITRE ATLAS: Adversarial Examples | CWE-20, CWE-345 | (Embeddings) |  |
| T13 | Undetected embedding modification  | An attacker changes the embeddings and the system does not notice | Tampering | Application | OWASP A08: Software and Data Integrity Failures | CWE-353, CWE-354 | (Embeddings) |  |
| T14 | Unauthorised access | Attacker bypasses authorisation to access vector database | Elevation of Privilege | Platform | OWASP A01: Broken Access Control | CWE-285, CWE-862 | (Vector Database) |  |
| T15 | Injection attacks | Attacker exploits input validation to inject malicious queries | Tampering | Application | OWASP A03: Injection | CWE-89, CWE-943 | (Vector Database) |  |
| T16 | Stolen data from vector database | An attacker copies/downloads lots of embeddings to steal  | Information Disclosure | Application | OWASP A01: Broken Access Control | CWE-200, CWE-359 | (Vector Database) | Intellectual Property |
| T17 | Denial of a service | Attacker overwhelms database making it unresponsive | Denial of Service | Platform | OWASP A04: Insecure Design | CWE-400, CWE-770 | (Vector Database) |  |
| T18 | Insufficient access controls | Weak authorisation allows unauthorised database operations | Elevation of Privilege | Platform | OWASP A01: Broken Access Control | CWE-269, CWE-863 | (Vector Database) |  |
| T19 | Lack of encryption | Embeddings stored without encryption expose knowledge base | Information Disclosure | Platform | OWASP A02: Cryptographic Failures | CWE-311, CWE-326 | (Vector Database) | Intellectual Property |
| T20 | Unvalidated data source | System ingests untrusted documents without proper validation | Tampering | Application | OWASP A08: Software and Data Integrity Failures | CWE-345, CWE-494 | (Vector Database) |  |
  
  
  
**User Activities - Threats**  

| ID | Threat (brief) | Description | STRIDE | Category | Standards / mappings (OWASP / GenAI / ATLAS) | Likely CWE(s) | Component(s) | IBM AI Risk Atlas Mapping |
| --- | ----------------------------------- | --------------------------------------------------------------------------------------- | --------------------------------- | ----------- | ------------------------------------------------------------- | ---------------- | ------------------------- | ------------------------- |
| T21 | User credential theft | Attacker steals a user's login details to access the application | Spoofing | Platform | OWASP A07: Identification and Authentication Failures | CWE-522, CWE-287 | (User) |  |
| T22 | Session hijacking | Attacker intercepts an active user session to impersonate them | Spoofing | Network | OWASP A07: Identification and Authentication Failures | CWE-384, CWE-523 | (User), (Authn & Authz) |  |
| T23 | Authentication bypass | Attacker finds a way to access the system without logging in properly | Spoofing | Application | OWASP A07: Identification and Authentication Failures | CWE-287, CWE-306 | (Authn & Authz) |  |
| T24 | Authorisation bypass | Attacker accesses resources they shouldn't have permission to use | Elevation of Privilege | Application | OWASP A01: Broken Access Control | CWE-285, CWE-862 | (Authn & Authz) |  |
| T25 | Privilege escalation | User gains higher level permissions than they should have | Elevation of Privilege | Application | OWASP A01: Broken Access Control | CWE-269, CWE-639 | (Authn & Authz) |  |
| T26 | Insufficient authentication logging | System doesn't keep proper records of who logged in and when | Repudiation | Platform | OWASP A09: Security Logging and Monitoring Failures | CWE-778, CWE-778 | (Authn & Authz) |  |
| T27 | Prompt injection attack | Attacker crafts clever questions to trick the AI into doing unintended things | Tampering, Information Disclosure | AI | OWASP LLM01: Prompt Injection; MITRE ATLAS: Adversarial Input | CWE-74, CWE-94 | (Input Guard - Query) |  |
| T28 | Input validation bypass | Attacker finds a way around the checks that validate user questions | Tampering | Application | OWASP A03: Injection | CWE-20, CWE-116 | (Input Guard - Query) |  |
| T29 | Jailbreak attack | Attacker uses techniques to make the AI ignore its safety rules | Integrity | AI | OWASP LLM01: Prompt Injection | CWE-74, CWE-863 | (Input Guard - Query) |  |
| T30 | Adversarial query for embedding | Attacker creates specially designed questions to manipulate what information gets found | Tampering | AI | MITRE ATLAS: Adversarial Examples | CWE-20, CWE-345 | (Input Guard - Embedding) |  |
| T31 | Embedding service abuse | Attacker sends too many requests overwhelming the embedding system | Denial of Service | Application | OWASP A04: Insecure Design | CWE-400, CWE-770 | (Input Guard - Embedding) |  |
| T32 | PII leakage in responses | AI responses accidentally include personal or sensitive information | Information Disclosure | AI | OWASP LLM06: Sensitive Information Disclosure | CWE-200, CWE-359 | (Output Guard) |  |
| T33 | Output guard bypass | Attacker finds a way to receive unfiltered responses from the AI | Tampering | Application | OWASP A04: Insecure Design | CWE-863, CWE-284 | (Output Guard) |  |
| T34 | Harmful content generation | AI generates inappropriate, biased, or dangerous content that passes filters | Integrity | AI | OWASP LLM09: Misinformation | CWE-703, CWE-670 | (Output Guard) |  |
| T35 | Insufficient output filtering | Filters don't catch all types of sensitive or harmful content in responses | Information Disclosure | Application | OWASP LLM06: Sensitive Information Disclosure | CWE-200, CWE-116 | (Output Guard) |  |
  
  
  
**GenAI App - Threats**  

| ID | Threat (brief) | Description | STRIDE | Category | Standards / mappings (OWASP / GenAI / ATLAS) | Likely CWE(s) | Component(s) | IBM AI Risk Atlas Mapping |
| --- | --------------------------------- | ------------------------------------------------------------------------------ | ---------------------- | ----------- | ----------------------------------------------- | ---------------- | ------------ | ------------------------- |
| T36 | Application logic tampering | Attacker modifies the application's code or settings to change how it works | Tampering | Application | OWASP A08: Software and Data Integrity Failures | CWE-494, CWE-829 | (Gen AI App) |  |
| T37 | API abuse | Attacker exploits the application's interfaces to perform unauthorised actions | Elevation of Privilege | Application | OWASP API1: Broken Object Level Authorization | CWE-285, CWE-639 | (Gen AI App) |  |
| T38 | Application denial of service | Attacker overloads the application making it unavailable to legitimate users | Denial of Service | Application | OWASP LLM04: Model Denial of Service | CWE-400, CWE-770 | (Gen AI App) |  |
| T39 | Insecure API communication | Data sent between systems isn't properly protected, allowing interception | Information Disclosure | Network | OWASP A02: Cryptographic Failures | CWE-319, CWE-311 | (Gen AI App) |  |
| T40 | Application logic errors | Software bugs or design flaws cause incorrect or insecure behaviour | Tampering | Application | OWASP A04: Insecure Design | CWE-754, CWE-691 | (Gen AI App) |  |
| T41 | Cross-site scripting in responses | Application fails to clean AI responses, allowing malicious scripts to run | Tampering | Application | OWASP A03: Injection | CWE-79, CWE-80 | (Gen AI App) |  |
| T42 | Insufficient rate limiting | System allows too many requests, enabling resource exhaustion attacks | Denial of Service | Application | OWASP API4: Lack of Resources & Rate Limiting | CWE-770, CWE-400 | (Gen AI App) |  |
| T43 | Retriever manipulation | Attacker influences what documents the system finds and uses | Tampering | Application | OWASP LLM01: Prompt Injection | CWE-829, CWE-706 | (Retriever) |  |
| T44 | Context injection via retrieval | Corrupted database causes harmful content to be retrieved and used | Tampering | AI | OWASP LLM01: Prompt Injection | CWE-74, CWE-506 | (Retriever) |  |
| T45 | Excessive context retrieval | System retrieves more sensitive information than necessary for the AI | Information Disclosure | Application | OWASP API3: Excessive Data Exposure | CWE-200, CWE-359 | (Retriever) |  |
| T46 | Retrieval ranking manipulation | Attacker biases the search results to prioritise specific documents | Tampering | AI | MITRE ATLAS: Adversarial Examples | CWE-20, CWE-345 | (Retriever) |  |
| T47 | Retriever denial of service | Attacker overloads the retrieval system with complex searches | Denial of Service | Application | OWASP LLM04: Model Denial of Service | CWE-400, CWE-770 | (Retriever) |  |
  
  
  
**Cloud (SaaS)/On-Prem - Generative LLM - Threats**  

| ID | Threat (brief) | Description | STRIDE | Category | Standards / mappings (OWASP / GenAI / ATLAS) | Likely CWE(s) | Component(s) | IBM AI Risk Atlas Mapping |
| --- | ----------------------------- | ---------------------------------------------------------------------------------- | ---------------------- | ----------- | ------------------------------------------------------- | ---------------- | ---------------- | ------------------------- |
| T48 | Model extraction / theft | Attacker steals the generative LLM by repeatedly querying it | Information Disclosure | AI | OWASP LLM10: Model Theft; MITRE ATLAS: Model Extraction | CWE-200, CWE-327 | (Generative LLM) | Intellectual Property |
| T49 | Prompt injection to LLM | Attacker bypasses safety checks to send harmful instructions to the generative LLM | Tampering | AI | OWASP LLM01: Prompt Injection | CWE-74, CWE-94 | (Generative LLM) |  |
| T50 | Model hallucination | Generative LLM generates false information but presents it as true | Integrity | AI | OWASP LLM09: Misinformation | CWE-703, CWE-670 | (Generative LLM) |  |
| T51 | LLM service denial of service | Attacker sends complex requests that exhaust the generative LLM's resources | Denial of Service | Application | OWASP LLM04: Model Denial of Service | CWE-400, CWE-770 | (Generative LLM) |  |
| T52 | Third-party provider breach | External generative LLM service provider is compromised, exposing data | Information Disclosure | Platform | OWASP A08: Software and Data Integrity Failures | CWE-923, CWE-201 | (Generative LLM) |  |
| T53 | API key exposure | Generative LLM service credentials are leaked, allowing unauthorised use | Spoofing | Platform | OWASP A02: Cryptographic Failures | CWE-522, CWE-798 | (Generative LLM) |  |
  
  
  
**Cloud (SaaS)/On-Prem - Embedding Model -Threats**  

| ID | Threat (brief) | Description | STRIDE | Category | Standards / mappings (OWASP / GenAI / ATLAS) | Likely CWE(s) | Component(s) | IBM AI Risk Atlas Mapping |
| --- | --------------------------- | ----------------------------------------------------------------------------- | ---------------------- | -------- | ------------------------------------------------------- | ---------------- | ----------------- | ------------------------- |
| T54 | Model extraction | Attacker steals the embedding model by repeatedly querying it | Information Disclosure | AI | OWASP LLM10: Model Theft; MITRE ATLAS: Model Extraction | CWE-200, CWE-327 | (Embedding Model) | Intellectual Property |
| T55 | Model manipulation | Attacker influences the embedding model to create biased data representations | Tampering | AI | MITRE ATLAS: Adversarial Examples | CWE-20, CWE-345 | (Embedding Model) |  |
| T56 | Third-party provider breach | External embedding service provider is compromised, exposing data | Information Disclosure | Platform | OWASP A08: Software and Data Integrity Failures | CWE-923, CWE-201 | (Embedding Model) |  |
| T57 | API key exposure | Embedding service credentials are leaked, allowing unauthorised use | Spoofing | Platform | OWASP A02: Cryptographic Failures | CWE-522, CWE-798 | (Embedding Model) |  |
  
  
  
**References:**  
- [OWASP Top 10 for Web Applications](https://owasp.org/Top10/)  
- [OWASP Top 10 for LLMs](https://genai.owasp.org/llm-top-10/)  
- [MITRE ATLAS](https://atlas.mitre.org/matrices/ATLAS)  
- [CWE List](https://cwe.mitre.org/data/)  
- [IBM AI Risk Atlas](https://www.ibm.com/docs/en/watsonx/saas?topic=ai-risk-atlas)  
- [Adversa AI MCP Security Top 25 Vulnerabilities](https://adversa.ai/mcp-security-top-25-mcp-vulnerabilities)  
