# Threat Model Layer Stack

We are considering whether utilising a recognised model for categorising the layer in which the threat applies would benefit the threat modelling approach and allow easier identification of where the control is required.

## WIP - Layer Stack for Threat Modelling

| Layer     | Description    | Example Components    | Key Assets    | Example Threats    |
| --------- | -------------- | --------------------- | ------------- | ------------------ |
| **AI**  | All ML/AI-specific components, pipelines, and data flows | Models, training data, prompt chains, inference APIs  | Model integrity, data confidentiality  | Data poisoning, model inversion, prompt injection |
| **Application**  | Business logic, user interfaces, API endpoints  | Web apps, APIs, microservices, UI code  | Business data, user sessions   | Logic abuse, injection, broken access control   |
| **Software (Runtime & Platform)**  | The software stack *under* the application layer, providing execution and dependencies | Programming languages, libraries, dependencies, runtimes, containers, SDKs | Code integrity, dependency trust, runtime stability | Supply-chain compromise, vulnerable dependency, malicious library, insecure deserialization |
| **Operating System & Firmware**   | Host OS, hypervisor, kernel, and firmware layers  | OS (Linux/Windows), BIOS/UEFI, hypervisors   | System integrity, kernel security   | Privilege escalation, rootkits, firmware tampering   |
| **Data**  | Data storage, flow, and lifecycle   | Databases, object stores, ETL pipelines | Data confidentiality, integrity, availability | Unauthorized access, exfiltration, corruption   |
| **Network**  | Connectivity and communication  | Routers, firewalls, VPCs, load balancers | Traffic confidentiality and availability | DDoS, MITM, routing manipulation    |
| **Infrastructure (Physical & Cloud)** | Compute, storage, virtualization, and hosting | Servers, VMs, cloud accounts, physical datacenters   | Service continuity, platform resilience | Misconfiguration, insider threat, resource exhaustion  |
