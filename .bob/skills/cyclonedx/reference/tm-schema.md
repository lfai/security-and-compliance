<!-- GENERATED from schema/2.0/cyclonedx-2.0-bundled.schema.json. Do not edit by hand; regenerate with:
     python .bob/skills/cyclonedx/scripts/schema_tool.py write-references -->
# CycloneDX 2.0 threat-model schema reference (TM-BOM)

The modules a **threat-model BOM** uses: `threat`, `control`, the core of `risk`, `weakness`, and `standard` (for control catalogues such as NIST SP 800-53 and CSA AICM). Generated from the bundled schema, so it is exact for this copy of the schema. For any other module, run `python .bob/skills/cyclonedx/scripts/schema_tool.py outline <module>`.

In the Type column, `enum: a, b` means a plain string value, `{role: enum: …}` means an object that wraps the value (for example `{ "role": "developer" }`), and `or custom {name, description}` means a custom object is also accepted.

## Module `threat` (cyclonedx-threat-2.0)

### `threat:threats`

Threat-modelling content, including the documented threats, the threat scenarios that realize them, the attack patterns and attack trees that describe how they are carried out, and the trust boundaries they cross. Control references throughout this model point at controls that mitigate the referencing element. Where a control is declared in the same document, its appliesTo property may also record the relationship; the reference here is intended primarily for controls defined elsewhere.

| Field | Type | Description |
|---|---|---|
| `threats` | array of → threat:threat | The documented threats. Each describes what can go wrong, independent of any specific actor or occurrence. |
| `threatScenarios` | array of → threat:threatScenario | The threat scenarios, each realizing one or more documented threats in a specific way. |
| `attackPatterns` | array of → threat:attackPattern | A library of attack patterns, typically aligned with CAPEC, that threats and threat scenarios can reference. |
| `attackTrees` | array of → threat:attackTree | Attack trees that decompose attacker goals into sub-goals and techniques. |
| `attackPaths` | array of → threat:attackPath | Attack paths that describe the ordered progression of an attack across elements and trust boundaries, including lateral movement. |
| `abuseCases` | array of → threat:abuseCase | Abuse or misuse cases that describe how the system can be exercised by an adversary. |
| `trustBoundaries` | array of → threat:trustBoundary | The trust boundaries of the system, extending the architectural boundaries defined in a blueprint with trust semantics. |
| `methodologies` | array of threat:methodology — enum: STRIDE, LINDDUN, PASTA, MAESTRO, OWASP, TRIKE, VAST, ATFAA, attack-tree — or custom {name, description} | The threat modeling methodologies applied to produce this threat model, such as STRIDE, LINDDUN, PASTA, or attack trees. |
| `properties` | → common:properties |  |

### `threat:methodology`

A threat modeling methodology applied to produce this threat model. Use the custom option for methodologies not covered by the enumeration.

### `threat:threat`

A documented threat, describing what can go wrong independent of any specific actor or occurrence. A threat can be catalogued on its own; a threat scenario references it to describe a specific realization.

Required: `refId`, `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the threat elsewhere using a `refId` or bom-link. |
| `name` | string | The name of the threat. |
| `description` | string | A description of the threat. |
| `source` | string | The source of the threat, such as a threat intelligence feed, a threat catalogue, or an analysis activity. |
| `origin` | enum: adversarial, accidental, structural, environmental — or custom {name, description} | The nature of the threat source that gives rise to this threat, following the threat source types of [NIST SP 800-30](https://csrc.nist.gov/pubs/sp/800/30/r1/final). Use the custom option for an orig… |
| `categories` | array of object | The methodology-specific categories that this threat falls under. A threat may be categorized under more than one methodology, for example STRIDE and MAESTRO. The methodology is one of the supported … |
| `weaknesses` | → weakness:weaknesses | The weaknesses that this threat exploits. |
| `relatedVulnerabilities` | array of ref (refId in this document) | References using bom-link or `refId` to the vulnerabilities that this threat exploits or that inform it. |
| `attackPatterns` | array of ref (refId in this document) | References using bom-link or `refId` to the attack patterns by which this threat is carried out. |
| `attackTrees` | array of ref (refId in this document) | References using bom-link or `refId` to the attack trees that decompose this threat. |
| `abuseCases` | array of ref (refId in this document) | References using bom-link or `refId` to the abuse cases that illustrate how this threat can be exercised. |
| `killChainPhase` | threat:killChainPhase — enum: reconnaissance, weaponization, delivery, exploitation, installation, command-and-control, actions-on-objectives | The phase of the cyber kill chain at which this threat operates. |
| `behaviors` | array of ref (refId in this document) | References using bom-link or `refId` to the declared behaviors that constitute the intent of this threat, drawn from the behavior taxonomy. |
| `indicators` | → threat:indicators |  |
| `affects` | array of ref (refId in this document) | References using bom-link or `refId` to the assets that this threat can affect. |
| `relatedBusinessObjectives` | array of ref (refId in this document) | References using bom-link or `refId` to the business objectives this threat endangers. |
| `mitigations` | array of ref (refId in this document) | References using bom-link or `refId` to the controls that mitigate this threat. |
| `externalReferences` | → common:externalReferences |  |
| `properties` | → common:properties |  |

### `threat:threat.categories[]`

A threat category. The taxonomy determines the permitted category values.

Required: `taxonomy`, `category`

| Field | Type | Description |
|---|---|---|
| `taxonomy` | enum: STRIDE, LINDDUN, MAESTRO, MITRE-ATTACK | The threat classification taxonomy that the category is drawn from. |
| `category` | string | The category within the taxonomy. The permitted values are determined by the taxonomy. |

- When taxonomy = "STRIDE": `category` enum: spoofing, tampering, repudiation, information-disclosure, denial-of-service, elevation-of-privilege
- When taxonomy = "LINDDUN": `category` enum: linkability, identifiability, non-repudiation, detectability, disclosure-of-information, unawareness, non-compliance
- When taxonomy = "MAESTRO": `category` enum: foundation-models, data-operations, agent-frameworks, deployment-and-infrastructure, evaluation-and-observability, security-and-compliance, agent-ecosystem
- When taxonomy = "MITRE-ATTACK": `category` enum: reconnaissance, resource-development, initial-access, execution, persistence, privilege-escalation, defense-evasion, credential-access, discovery, lateral-movement, collection, command-and-control, exfiltration, impact

### `threat:threatScenario`

A specific realization of a threat, in which an actor seeks to cause harm. The scenario references the threats it realizes, supplies the actor by reference to a party, and carries the scenario-specific traits, such as motivation, intent, access level, and likelihood. The consequence is expressed by the damage scenarios it leads to, and the resulting risk is documented under risks, referencing both.

Required: `refId`, `name`, `threats`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the threat scenario elsewhere using a `refId` or bom-link. |
| `name` | string | The name of the threat scenario. |
| `description` | string | A description of the threat scenario. |
| `event` | string | The event that realizes or triggers the threat in this scenario. |
| `threats` | array of ref (refId in this document) | References using bom-link or `refId` to the threats that this scenario realizes. A scenario realizes one or more threats. |
| `actor` | ref (refId in this document) | Reference using bom-link or `refId` to the party that is the actor in this scenario. Named adversary groups are organizations and abstract attacker classes are personas. |
| `threatProfile` | ref (refId in this document) | Reference using bom-link or `refId` to a reusable threat profile that describes the durable capabilities of the actor. |
| `motivation` | array of enum: financial, political, personal, ideological, espionage, destruction, disruption, reputation, curiosity, competitive, revenge, activism | The motivations of the actor in this scenario. |
| `intent` | enum: accidental, opportunistic, targeted, persistent | The intent of the actor in this scenario. |
| `accessLevel` | enum: none, external, internal, privileged, physical | The level of access the actor is assumed to have in this scenario. |
| `attackVector` | → threat:attackVector |  |
| `exploitability` | → threat:exploitability |  |
| `likelihood` | → risk:likelihood | The likelihood that this scenario is realized, which in attack terms is its feasibility. The consequence is carried by the damage scenarios the scenario leads to, and the paired rating by the risk th… |
| `riskAttributes` | array of risk:riskAttribute — enum: accountability, authentication, authorization, authenticity, availability, compliance, confidentiality, connectivity, control, data-subject-rights, integrity, minimization, non-repudiation, possession, privacy, purpose-limitation, transparency, utility — or custom {name, description} | The security and privacy attributes that this threat would compromise if realized. |
| `affects` | array of ref (refId in this document) | References using bom-link or `refId` to the assets affected in this scenario. |
| `damageScenarios` | array of ref (refId in this document) | References using bom-link or `refId` to the damage scenarios, declared under the risks collection, that this scenario can lead to. |
| `relatedVulnerabilities` | array of ref (refId in this document) | References using bom-link or `refId` to the vulnerabilities exploited in this scenario. |
| `externalReferences` | → common:externalReferences |  |
| `properties` | → common:properties |  |

### `threat:threatProfiles`

Reusable threat profiles, each describing the durable characteristics of an actor that may pose a threat.

Type: array of → threat:threatProfile

### `threat:threatProfile`

A durable, actor-level characterization of the capability to pose a threat, capturing attributes that persist across scenarios. Scenario-specific attributes, such as motivation, intent, and access level, belong on a threat scenario rather than on this profile.

Required: `refId`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference this threat profile elsewhere using a `refId` or bom-link. |
| `name` | string | The name of the threat profile. |
| `description` | string | A description of the threat profile. |
| `sophistication` | enum: none, minimal, intermediate, advanced, expert | The level of technical sophistication an actor characterized by this profile is assumed to possess. |
| `resources` | enum: minimal, limited, moderate, substantial, unlimited | The level of resources an actor characterized by this profile is assumed to have available. |
| `skillSet` | array of string | The specific skills an actor characterized by this profile is assumed to possess. |
| `properties` | → common:properties |  |

### `threat:attackVector`

The conditions under which an attack is possible, following the convention of common vulnerability scoring systems.

| Field | Type | Description |
|---|---|---|
| `type` | enum: network, adjacent, local, physical | The context by which an attack is possible. |
| `complexity` | enum: low, high | The complexity of the attack. |
| `privileges` | enum: none, low, high | The level of privileges required to carry out the attack. |
| `userInteraction` | enum: none, required | Whether the attack requires interaction from a user other than the attacker. |
| `scope` | enum: unchanged, changed | Whether a successful attack affects resources beyond the vulnerable component. |

### `threat:attackPattern`

A description of the common attributes and approach of an attack, typically aligned with CAPEC. Techniques are aligned with MITRE ATT&CK.

Required: `refId`, `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the attack pattern elsewhere using a `refId` or bom-link. |
| `capecId` | integer | The Common Attack Pattern Enumeration and Classification (CAPEC) identifier for this attack pattern. |
| `name` | string | The name of the attack pattern. |
| `description` | string | A description of the attack pattern. |
| `prerequisites` | array of string | The conditions that must hold for the attack to be possible. |
| `techniques` | array of → threat:technique | The techniques used to carry out the attack, typically aligned with MITRE ATT&CK. |
| `mitigations` | array of ref (refId in this document) | References using bom-link or `refId` to the controls that mitigate this attack pattern. |
| `examples` | array of string | Real-world examples of the attack pattern. |

### `threat:technique`

A specific technique used to carry out an attack, typically aligned with MITRE ATT&CK.

| Field | Type | Description |
|---|---|---|
| `id` | string | The identifier of the technique, such as a MITRE ATT&CK technique identifier. |
| `name` | string | The name of the technique. |
| `tactic` | string | The tactic that the technique supports, such as a MITRE ATT&CK tactic. |
| `procedure` | string | The specific procedure by which the technique is carried out. |

### `threat:attackTree`

A decomposition of an attacker goal into sub-goals and techniques, expressed as a flat collection of nodes. Each node lists its child nodes by reference together with an operator that says how those children combine, so the tree is expressed without nesting. One node is the root, representing the attacker goal.

Required: `refId`, `nodes`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the attack tree elsewhere using a `refId` or bom-link. |
| `name` | string | The name of the attack tree. |
| `description` | string | A description of the attack tree. |
| `root` | ref (refId in this document) | Optional reference using bom-link or `refId` to the root node within nodes, representing the attacker goal. When omitted, the root is the node that no other node lists as a child. |
| `nodes` | array of → threat:attackTreeNode | The nodes of the attack tree. Each node references its child nodes, which are themselves entries in this array, forming the hierarchy without nesting. |

### `threat:attackTreeNode`

A node in an attack tree, representing an attacker goal, sub-goal, or technique. A node references its child nodes and carries an operator that says how those children combine. The hierarchy is expressed by these references rather than by nesting.

Required: `refId`, `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the node elsewhere using a `refId` or bom-link. |
| `name` | string | The goal, sub-goal, or technique that the node represents. |
| `description` | string | A description of the node. |
| `operator` | enum: and, or | Specifies how the nodes listed in 'children' combine to achieve this node. A value of 'and' requires every child node; a value of 'or' requires any single child node. For example, a node whose childr… |
| `children` | array of ref (refId in this document) | References using bom-link or `refId` to the child nodes that decompose this node. Each child node is a separate entry in the same nodes array, so the hierarchy is expressed without nesting. A child n… |
| `attackPattern` | ref (refId in this document) | Reference using bom-link or `refId` to the attack pattern that this node represents. |
| `weakness` | ref (refId in this document) | Reference using bom-link or `refId` to the weakness that this node exploits. |
| `cost` | enum: negligible, low, moderate, high, prohibitive | The relative cost to an attacker of achieving this node. |
| `skill` | enum: none, basic, intermediate, advanced, expert | The skill level required to achieve this node. |
| `detectability` | enum: undetectable, low, moderate, high | How readily an attempt to achieve this node can be detected. |
| `mitigations` | array of ref (refId in this document) | References using bom-link or `refId` to the controls that mitigate this attack tree node. |

### `threat:abuseCase`

A description of how an adversary can misuse the system to achieve a malicious goal. An abuse case is the security counterpart of a use case and reuses its flow structure.

Required: `refId`, `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the abuse case elsewhere using a `refId` or bom-link. |
| `name` | string | The name of the abuse case, typically expressed as a malicious goal. |
| `description` | string | A narrative describing how the system can be misused or abused. |
| `abuser` | ref (refId in this document) | Reference using bom-link or `refId` to the party that abuses the system, typically an attacker persona. |
| `realizes` | array of ref (refId in this document) | References using bom-link or `refId` to the threats that this abuse case realizes. |
| `preconditions` | array of string | The conditions that must hold before the abuse case can begin. |
| `mainFlow` | array of → usecase:step | The ordered steps the abuser follows. |
| `targets` | array of ref (refId in this document) | References using bom-link or `refId` to the assets or flows targeted in this abuse case. |
| `detectionOpportunities` | array of string | The signals, logs, or controls that present an opportunity to detect the abuse. |
| `mitigations` | array of ref (refId in this document) | References using bom-link or `refId` to the controls that mitigate this abuse case. |

### `threat:exploitability`

The degree to which a threat can be exploited in practice.

| Field | Type | Description |
|---|---|---|
| `level` | vulnerability:exploitMaturity — enum: not-defined, unreported, proof-of-concept, functional, active | The maturity of available exploitation capability, using the same scale as vulnerability exploit maturity. |
| `complexity` | enum: trivial, low, medium, high, very-high | The complexity of exploitation. |
| `skillRequired` | enum: none, basic, intermediate, advanced, expert | The skill level required to exploit the threat. |
| `automatable` | boolean | Whether exploitation can be automated. |

### `threat:indicators`

The observable indicators associated with a threat.

| Field | Type | Description |
|---|---|---|
| `compromise` | array of string | The indicators that a compromise has occurred. |
| `attack` | array of string | The indicators that an attack is under way. |
| `signatures` | array of → threat:signature | The detection signatures associated with the threat. |

### `threat:signature`

A detection signature for a threat.

Required: `type`, `value`

| Field | Type | Description |
|---|---|---|
| `type` | enum: yara, snort, regex, hash, behavior | The type of signature. |
| `value` | string | The signature value or pattern. |
| `description` | string | A description of what the signature detects. |
| `confidence` | enum: low, medium, high | The confidence level of a detection by this signature. |

### `threat:trustBoundary`

A security annotation marking an architectural boundary as one across which trust changes. It references a boundary defined in a blueprint, where the zones, type, and crossing requirements already live, and adds only the trust differential and the threats and controls at that boundary.

Required: `refId`, `boundary`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the trust boundary elsewhere using a `refId` or bom-link. |
| `boundary` | ref (refId in this document) | Reference using bom-link or `refId` to the blueprint boundary that this trust boundary annotates. |
| `name` | string | The name of the trust boundary. |
| `description` | string | A description of the trust boundary. |
| `trustLevel` | enum: untrusted, semi-trusted, trusted, highly-trusted | The trust level differential across the boundary. |
| `threatsAtBoundary` | array of ref (refId in this document) | References using bom-link or `refId` to the threats that could exploit this boundary. |
| `controlsAtBoundary` | array of ref (refId in this document) | References using bom-link or `refId` to the controls that mitigate threats at this trust boundary. |
| `properties` | → common:properties |  |

### `threat:killChainPhase`

A phase of the cyber kill chain.

### `threat:attackPathStep`

A single step in an attack path, describing one action in the progression of an attack.

Required: `description`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | A short name for the step. |
| `description` | string | The action the adversary performs in this step. |
| `technique` | → threat:technique | The technique used in this step, typically aligned with MITRE ATT&CK. |
| `attackPattern` | ref (refId in this document) | Reference using bom-link or `refId` to the attack pattern applied in this step. |
| `killChainPhase` | threat:killChainPhase — enum: reconnaissance, weaponization, delivery, exploitation, installation, command-and-control, actions-on-objectives | The phase of the cyber kill chain at which this step operates. |
| `source` | ref (refId in this document) | Reference using bom-link or `refId` to the element or zone from which this step originates. |
| `destination` | ref (refId in this document) | Reference using bom-link or `refId` to the element or zone this step reaches. |
| `boundaryCrossed` | ref (refId in this document) | Reference using bom-link or `refId` to the trust boundary this step crosses. |
| `exploits` | array of ref (refId in this document) | References using bom-link or `refId` to the weaknesses or vulnerabilities this step exploits. |
| `mitigations` | array of ref (refId in this document) | References using bom-link or `refId` to the controls that mitigate this attack path step, by preventing or detecting it. |
| `properties` | → common:properties |  |

### `threat:attackPath`

An ordered sequence of steps that an adversary follows to progress from initial access toward an objective, crossing elements and trust boundaries. An attack path complements an attack tree: the tree decomposes a goal into alternatives, whereas the path expresses the temporal progression of a single attack, including lateral movement.

Required: `refId`, `name`, `steps`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | A human-readable name for the attack path. |
| `description` | string | A description of the attack path. |
| `objective` | string | The attacker objective that the path works toward, such as exfiltrating data or achieving code execution. |
| `actor` | ref (refId in this document) | Reference using bom-link or `refId` to the adversary that follows this path. |
| `steps` | array of → threat:attackPathStep | The ordered steps of the path, from the initial action to the objective. The order of the array is significant. |
| `realizes` | array of ref (refId in this document) | References using bom-link or `refId` to the threats that this path realizes. |
| `externalReferences` | → common:externalReferences |  |
| `properties` | → common:properties |  |

## Module `control` (cyclonedx-control-2.0)

### `control:controls`

The safeguards and countermeasures that are recommended or in place. Controls may be declared on their own for governance, risk, and compliance use cases, or referenced from threats, trust boundaries, and risk responses.

Type: array of → control:control

### `control:control`

A safeguard or countermeasure that protects systems, data, or operations. A control binds the elements that implement it to the requirements it satisfies, and records its implementation status and assessed effectiveness.

Required: `refId`, `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the control elsewhere using a `refId` or bom-link. |
| `name` | string | The name of the control. |
| `description` | string | A description of the control. |
| `category` | enum: preventive, detective, corrective, compensating, deterrent, recovery — or custom {name, description} | The category of the control. Use the custom option for a category specific to an organization's taxonomy. |
| `status` | control:implementationStatus — enum: recommended, proposed, approved, rejected, planned, in-progress, implemented, verified, decommissioned — or custom {name, description} | The implementation status of the control. |
| `appliesTo` | array of ref (refId in this document) | References using bom-link or `refId` to the elements the control protects, such as components, services, zones, or boundaries. A control without this property applies to the organization or system as… |
| `implementedBy` | array of ref (refId in this document) | References using bom-link or `refId` to the components, services, formulation workflows, or parties that implement the control. |
| `satisfies` | array of ref (refId in this document) | References using bom-link or `refId` to the requirements the control satisfies, including requirements defined within standards. |
| `effectiveness` | → control:effectiveness | The assessed effectiveness of the control. |
| `owner` | → party:partyChoice | The party accountable for the control. May be an inline party object or a reference to a previously declared party. |
| `externalReferences` | → common:externalReferences |  |
| `properties` | → common:properties |  |

### `control:implementationStatus`

The implementation status of a control or response. Use the custom option for a status specific to an organization's process.

### `control:effectiveness`

The measured or assessed effectiveness of a control or response.

| Field | Type | Description |
|---|---|---|
| `percentage` | number | Effectiveness as a decimal from 0 to 1. |
| `rating` | enum: ineffective, marginal, adequate, good, excellent | Effectiveness as a qualitative rating. |

### `risk:risks`

A collection of risks identified through risk analysis, together with the assessments that evaluate them. The model is framework-neutral and can document risk regardless of the risk management framework in use, including [ISO 31000](https://www.iso.org/iso-31000-risk-management.html), [NIST SP 800-30](https://csrc.nist.gov/pubs/sp/800/30/r1/final), the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), [COSO ERM](https://www.coso.org/), [ISO/IEC 27005](https://www.iso.org/standard/80585.html), and OCTAVE. It accommodates qualitative, semi-quantitative,…

| Field | Type | Description |
|---|---|---|
| `risks` | array of → risk:risk | The documented risks identified through risk analysis. |
| `damageScenarios` | array of → risk:damageScenario | The damage scenarios identified through risk analysis. A damage scenario describes an adverse consequence for the subjects it affects, independent of any particular cause, and is rated per impact cat… |
| `assessments` | array of → risk:assessment | Point-in-time risk assessment events, each evaluating one or more of the documented risks. |
| `riskAppetites` | array of → risk:riskAppetite | The risk appetites that apply to this collection. Multiple entries support a document covering more than one party. |
| `properties` | → common:properties |  |

### `risk:risk`

Required: `refId`, `name`, `statement`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | A human-readable name for the risk. |
| `statement` | string | Structured risk statement describing source, event, and impact. |
| `description` | string | Additional narrative about the risk. |
| `domains` | array of → risk:riskDomain | The risk domains this risk affects. |
| `affects` | array of ref (refId in this document) | References using bom-link or `refId` to the subjects this risk concerns. A subject may be a component, service, dataset, or model, or a party such as a person, persona, or organization, including a g… |
| `relatedThreats` | array of ref (refId in this document) | References using bom-link or `refId` to the threats or threat scenarios from a threat model that inform this risk. A reference may point to a discrete threat or to a threat scenario. |
| `relatedDamageScenarios` | array of ref (refId in this document) | References using bom-link or `refId` to the damage scenarios that this risk realizes. A risk typically pairs a threat scenario, which supplies the likelihood, with a damage scenario, which supplies t… |
| `relatedVulnerabilities` | array of ref (refId in this document) | References using bom-link or `refId` to the vulnerabilities that inform this risk. |
| `relatedWeaknesses` | array of ref (refId in this document) | References using bom-link or `refId` to the weaknesses that inform this risk. |
| `relatedBehaviors` | array of ref (refId in this document) | References using bom-link or `refId` to the declared or observed behaviours that inform this risk. Any behaviour can give rise to a risk depending on context and expectation, for example an observed … |
| `relatedRequirements` | array of ref (refId in this document) | References using bom-link or `refId` to the requirements whose absence or non-conformance gives rise to this risk, such as a requirement that is unmet or only partially met. |
| `relatedStandards` | array of ref (refId in this document) | References using bom-link or `refId` to the standards whose non-conformance gives rise to this risk. |
| `relatedClaims` | array of ref (refId in this document) | References using bom-link or `refId` to the conformance claims that give rise to this risk, such as a [CycloneDX Attestations](https://cyclonedx.org/capabilities/attestations/) claim recording that a… |
| `relatedBusinessObjectives` | array of ref (refId in this document) | References using bom-link or `refId` to the business objectives this risk threatens. |
| `inherentRisk` | → risk:rating | The assessed risk before any responses are applied. |
| `residualRisk` | → risk:rating | The assessed risk remaining after responses are applied. |
| `targetRisk` | → risk:rating | The risk level the organization aims to reach for this risk. The overall risk appetite is recorded separately on the risks collection or assessment. |
| `responses` | array of → risk:riskResponse | The responses applied to this risk. |
| `status` | enum: identified, assessed, treated, monitored, retired — or custom {name, description} | The lifecycle status of the risk. The status tracks progress through the risk process; the disposition chosen, such as reduce, share, or accept, is recorded on the responses. Use the custom option fo… |
| `owner` | → party:partyChoice | The party accountable for this risk. May be an inline party object or a reference to a previously declared party. The party's `roles` should include `owner`. |
| `externalReferences` | array of → common:externalReference |  |
| `properties` | → common:properties |  |

### `risk:damageScenario`

An adverse consequence for one or more subjects, described independently of the threat or event that could cause it. A damage scenario carries an impact per category, such as safety, financial, operational, or privacy, so that the same consequence can be paired with several causes. In ISO/SAE 21434 terms, for example, the damage scenario is the harm to a road user, the threat scenario is the cause, and the risk pairs the two.

Required: `refId`, `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | A short name for the damage scenario. |
| `description` | string | A description of the adverse consequence and the circumstances in which it occurs. |
| `affects` | array of ref (refId in this document) | References using bom-link or `refId` to the subjects harmed in this damage scenario, such as the functions, assets, or components involved and the parties harmed, for example a road user or a patient. |
| `impacts` | array of → risk:impact | The impact of the damage scenario, one entry per impact category or group of categories, each with its own level. For example, a single damage scenario may be catastrophic for safety and moderate for… |
| `externalReferences` | → common:externalReferences |  |
| `properties` | → common:properties |  |

### `risk:rating`

A methodology-neutral assessment of risk along likelihood and impact, with an overall score. The same shape expresses inherent, residual, and target risk so reductions can be compared. A rating can be qualitative (a `level`), semi-quantitative (a numeric `score` on a bounded scale), or quantitative (for example a probable monetary loss under [FAIR](https://www.fairinstitute.org/)). For a catalogue of assessment techniques, see [IEC 31010](https://www.iso.org/standard/72140.html).

| Field | Type | Description |
|---|---|---|
| `likelihood` | → risk:likelihood |  |
| `impacts` | array of → risk:impact | The impacts of the risk in this rating. A rating may carry more than one impact, for example a harm and a benefit for the same affected group, each with its own polarity and categories. |
| `score` | → risk:riskScore |  |
| `detectability` | object | The ease or likelihood of detecting the event before or as it is realized, used as a third axis by methodologies such as [FMEA](https://asq.org/quality-resources/fmea), whose risk priority number mul… |
| `controllability` | object | The ability of the people involved to avoid the harm once the event occurs, used as a third axis by functional safety methodologies such as the hazard analysis and risk assessment of [ISO 26262](http… |
| `confidence` | number | Confidence in this rating, expressed as a decimal from 0 to 1, where 1 is full confidence. Supports quantitative methods that reason over uncertainty. |
| `rationale` | string | The justification for this rating, including the method and the evidence considered. |

### `risk:likelihood`

Required: `level`

| Field | Type | Description |
|---|---|---|
| `level` | enum: very-low, low, medium, high, very-high, certain | The qualitative likelihood level representing the overall assessed probability of the risk or scenario being realized. |
| `score` | number | Numeric likelihood score on the scale defined by the methodology. |
| `probability` | number | Probability as a decimal from 0 to 1. |
| `frequency` | number | The expected number of events within the timeframe, for frequency-based methods such as the [FAIR](https://www.fairinstitute.org/) loss event frequency. Unlike a probability, a frequency may exceed 1. |
| `timeframe` | string | The period over which the probability or frequency is assessed, expressed as an [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) duration, for example P1Y for one year. |
| `range` | → risk:estimateRange | A range for the probability or frequency, supporting quantitative methods that reason over distributions. |
| `factors` | array of → risk:likelihoodFactor | The factors considered when determining the likelihood level. |
| `rationale` | string | The justification for the likelihood rating. |

### `risk:impact`

Required: `level`

| Field | Type | Description |
|---|---|---|
| `level` | enum: negligible, low, moderate, major, catastrophic | The qualitative impact severity level. |
| `polarity` | enum: harm, benefit | Whether the impact represents a harm or a benefit. Benefits support modeling opportunities and positive risk. |
| `score` | number | Numeric impact score on the scale defined by the methodology. |
| `categories` | array of risk:impactCategory — enum: financial, reputation, regulatory, safety, privacy, operational, strategic, discrimination, fairness, human-rights, environmental, societal, psychological, physical, health — or custom {name, description} | The categories of impact, including harms relevant to AI and societal risk. |
| `factors` | array of → risk:impactFactor | The factors considered when determining the impact, allowing methodologies that derive impact from multiple weighted dimensions to record the breakdown. |
| `range` | → risk:estimateRange | A range for the impact score, supporting quantitative methods that reason over distributions. |
| `riskAttributes` | array of risk:riskAttribute — enum: accountability, authentication, authorization, authenticity, availability, compliance, confidentiality, connectivity, control, data-subject-rights, integrity, minimization, non-repudiation, possession, privacy, purpose-limitation, transparency, utility — or custom {name, description} | The risk attributes affected. |
| `quantification` | → risk:impactQuantification |  |
| `description` | string | A description of the potential impact. |
| `methodology` | risk:riskMethodology — enum: dread, fair, fmea, nist-sp-800-30, octave, owasp-risk-rating, qualitative-matrix — or custom {name, description} | The methodology used to derive this impact rating, where the impact is rated on its own, for example on a damage scenario before any risk is scored. |

### `risk:riskResponse`

An action taken to modify a risk, pairing the chosen strategy with the controls that implement it. Covers the full set of dispositions, from avoiding or reducing a risk to accepting it or, for a positive risk, pursuing it.

Required: `refId`, `strategy`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference this response elsewhere using a `refId` or bom-link. |
| `strategy` | enum: avoid, reduce, share, accept, exploit, enhance | The disposition chosen for the risk. |
| `description` | string | A description of the response. |
| `controls` | array of ref (refId in this document) | References using bom-link or `refId` to the controls that implement this response. Where a control is declared in the same document, its appliesTo property may also record the relationship. |
| `status` | control:implementationStatus — enum: recommended, proposed, approved, rejected, planned, in-progress, implemented, verified, decommissioned — or custom {name, description} | The implementation status of the response. |
| `effectiveness` | → control:effectiveness |  |
| `cost` | enum: trivial, low, medium, high, extreme | Cost |
| `priority` | risk:priority — enum: none, low, medium, high, critical |  |
| `owner` | → party:partyChoice | The party accountable for this response. May be an inline party object or a reference to a previously declared party. |
| `targetDate` | string | The date by which this response is targeted to be implemented. |
| `addresses` | array of ref (refId in this document) | References using bom-link or `refId` to the items this response addresses, such as a threat, vulnerability, weakness, or another risk. |
| `externalReferences` | array of → common:externalReference |  |
| `properties` | → common:properties |  |

### `risk:riskAttribute`

A security or privacy attribute representing a potential impact area when a risk is realized. Use the custom option for attributes specific to an organization's risk taxonomy.

### `weakness:weakness`

A source of risk: a flaw, hazard, bias, or other predisposing condition of a subject or its context that, under certain circumstances, can contribute to a vulnerability, to a threat being realized, or to an adverse or beneficial outcome. A weakness records the condition itself. It may be identified in an external registry, classified by external taxonomies, or named, and at least a name or an identifier shall be provided. What the condition leads to, how likely that is, who or what is affected, and the consequences are not recorded on the weakness. They are expressed by the vulnerability, thr…

At least one of: {name} | {identifiers}

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An optional identifier which can be used to reference the weakness elsewhere using a `refId` or bom-link. |
| `kind` | enum: flaw, hazard, bias, predisposing-condition — or custom {name, description} | The kind of source this weakness is. The kind separates a flaw in the subject, an intrinsic hazard, a systematic bias, and a circumstantial predisposing condition, so that weaknesses of one kind can … |
| `name` | string | A short name for the weakness. A name is required when no identifier is given, and is recommended beside an identifier whose registry is not freely readable. |
| `description` | string | A description of the weakness: the condition itself, where it arises in the subject or its context, and the evidence for it. Likelihood, affected parties, and consequences belong to the vulnerability… |
| `identifiers` | array of → weakness:weaknessIdentifier | Identifiers of this weakness in external registries that assign a stable identifier to each entry, such as a CWE identifier. A weakness may carry identifiers from several registries when they describ… |
| `categories` | array of → weakness:weaknessCategory | Classifications of this weakness in taxonomies that name categories without assigning identifiers to entries, such as the NIST SP 1270 categories of bias. Categories complement identifiers; a weaknes… |

### `weakness:weaknessReference`

A reference to a weakness declared elsewhere, such as in the definitions registry, in another position of the same document, or in another document via BOM-Link. A reference includes the referenced weakness exactly as declared: every position that references the same weakness includes an identical weakness.

Required: `ref`

| Field | Type | Description |
|---|---|---|
| `ref` | ref (refId in this document) \| BOM-Link element (urn:cdx:...#ref) | Reference using bom-link or `refId` to the weakness. |

### `weakness:weaknessIdentifier`

An identifier of a weakness in an external registry, given by the scheme of the registry and the value the registry assigns.

Required: `scheme`, `value`

| Field | Type | Description |
|---|---|---|
| `scheme` | enum: cwe, imdrf-aet, hfacs, sot, ghs, iso-6520, iso-iec-24772 — or custom {name, description, url} | The registry that assigns the identifier. |
| `schemeVersion` | string | The version or edition of the registry that issued the identifier, for example 4.20 for CWE or 8.0 for HFACS. |
| `value` | string | The identifier value as issued by the registry, for example CWE-502. |

### `standard:standard`

A standard may consist of regulations, industry or organizational-specific standards, maturity models, best practices, or any other requirements which can be evaluated against or attested to.

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the object elsewhere in the document. Every `refId` shall be unique within the document. |
| `name` | string | The name of the standard. This will often be a shortened, single name of the standard. |
| `version` | string | The version of the standard. |
| `description` | string | The description of the standard. |
| `owner` | string | The owner of the standard, often the entity responsible for its release. |
| `requirements` | → standard:requirements |  |
| `levels` | → standard:levels |  |
| `externalReferences` | → common:externalReferences |  |
| `signatures` | → common:signatures |  |

### `standard:requirement`

Requirement

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the object elsewhere in the document. Every `refId` shall be unique within the document. |
| `identifier` | string | The unique identifier used in the standard to identify a specific requirement. This should match what is in the standard and should not be the requirements `refId`. |
| `title` | string | The title of the requirement. |
| `text` | string | The textual content of the requirement. |
| `descriptions` | array of string | The supplemental text that provides additional guidance or context to the requirement, but is not directly part of the requirement. |
| `openCre` | array of string | The Common Requirements Enumeration (CRE) identifier(s). CRE is a structured and standardized framework for uniting security standards and guidelines. CRE links each section of a resource to a shared… |
| `parent` | ref (refId in this document) | The `refId` to a parent requirement. This establishes a hierarchy of requirements. Top-level requirements shall not define a parent. Only child requirements should define parents. |
| `properties` | → common:properties |  |
| `externalReferences` | → common:externalReferences |  |

### `common:externalReference`

External references provide a way to document systems, sites, and information that may be relevant but are not included with the BOM. They may also establish specific relationships within or external to the BOM.

Required: `url`, `type`

| Field | Type | Description |
|---|---|---|
| `url` | string \| ref (refId or BOM-Link) | The URI (URL or URN) to the external reference. External references are URIs and therefore can accept any URL scheme including https ([RFC-7230](https://www.ietf.org/rfc/rfc7230.txt)), mailto ([RFC-2… |
| `comment` | string | A comment describing the external reference |
| `type` | enum: vcs, issue-tracker, website, advisories, bom, mailing-list, social, chat, documentation, support, source-distribution, distribution, distribution-intake, license, build-meta, build-system, release-notes, security-contact, model-card, log, configuration, evidence, formulation, attestation, threat-model, adversary-model, risk-assessment, hazard-analysis, safety-case, vulnerability-assertion, exploitability-statement, pentest-report, static-analysis-report, dynamic-analysis-report, runtime-analysis-report, test-report, incident-report, component-analysis-report, maturity-report, certification-report, codified-infrastructure, quality-metrics, poam, perspective, electronic-signature, digital-signature, rfc-9116, patent, patent-family, patent-assertion, citation, swid-tag, gs1-digital-link, other | Specifies the type of external reference. |
| `hashes` | array of → common:hash | The hashes of the external reference (if applicable). |
| `properties` | → common:properties |  |

