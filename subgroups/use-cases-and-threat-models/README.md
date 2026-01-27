# Security and Compliance Work Group

## Use Cases and Threat Modeling Subgroup

> [!IMPORTANT]
> - The Use Cases and Threat Modeling** subgroup meets weekly on Tuesdays @12pm US Eastern, 16:00 GMT.  Please use the calendar link below and click the "Need an invite?" link:
>     - [LF AI & Data calendar entry]( https://zoom-lfx.platform.linuxfoundation.org/meeting/93191199454?password=83a7bf08-2b26-44bc-aefd-8ad68b29c733)
>   - Slack: [#security-use-cases-and-threat-modeling](https://lfaifoundation.slack.com/archives/C09DHAQ399P)
>   - Meeting Agendas/Notes: [Google Doc](https://docs.google.com/document/d/1GzbzYeuvrXQIr9Uj6TiVXTrmnLPngOY7vuxc-CjOnas/edit?usp=drive_link)

### Leadership

##### Chairs:
  - Matt Colman (IBM)
    - mtcolman@uk.ibm.com
    - Slack: @Matt Colman
  - Petra Vukmirovoc ([Numan](https://www.numan.com/))
    - Slack: @petra vukmirovic

### Mission

To produce interoperable AI security and compliance standards through its lifecycle-wide use cases that with corresponding controls and risk mitigation measures informed by a library of real world threat models, make them directly consumable by automated security, compliance, and governance workflows.

### Goals

1. Identify and publish at least 3 pilot use cases + threat models in OWASP Threat Model Library
2. Align on the use case - threat model (threats, controls, risks) - standard workflow

### Current Work

As of 27th Jan 2026 we have threat modelled the use case "AI Assistant Code Generator" (based on using a code-generating AI assistant as a plugin in IDE).

The threat Model lives here: https://docs.google.com/spreadsheets/d/1SaB_a9iaSDTNvnyFJznMuBHIXmkDP1fcHX2ltcyJeUs/edit?usp=sharing (please request access if needed)

### WIP - Layer Stack for Threat Modelling

| Layer     | Description    | Example Components    | Key Assets    | Example Threats    |
| --------- | -------------- | --------------------- | ------------- | ------------------ |
| **AI**  | All ML/AI-specific components, pipelines, and data flows | Models, training data, prompt chains, inference APIs  | Model integrity, data confidentiality  | Data poisoning, model inversion, prompt injection |
| **Application**  | Business logic, user interfaces, API endpoints  | Web apps, APIs, microservices, UI code  | Business data, user sessions   | Logic abuse, injection, broken access control   |
| **Software (Runtime & Platform)**  | The software stack *under* the application layer, providing execution and dependencies | Programming languages, libraries, dependencies, runtimes, containers, SDKs | Code integrity, dependency trust, runtime stability | Supply-chain compromise, vulnerable dependency, malicious library, insecure deserialization |
| **Operating System & Firmware**   | Host OS, hypervisor, kernel, and firmware layers  | OS (Linux/Windows), BIOS/UEFI, hypervisors   | System integrity, kernel security   | Privilege escalation, rootkits, firmware tampering   |
| **Data**  | Data storage, flow, and lifecycle   | Databases, object stores, ETL pipelines | Data confidentiality, integrity, availability | Unauthorized access, exfiltration, corruption   |
| **Network**  | Connectivity and communication  | Routers, firewalls, VPCs, load balancers | Traffic confidentiality and availability | DDoS, MITM, routing manipulation    |
| **Infrastructure (Physical & Cloud)** | Compute, storage, virtualization, and hosting | Servers, VMs, cloud accounts, physical datacenters   | Service continuity, platform resilience | Misconfiguration, insider threat, resource exhaustion  |
