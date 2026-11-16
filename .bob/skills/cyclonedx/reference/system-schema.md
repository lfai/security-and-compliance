<!-- GENERATED from schema/2.0/cyclonedx-2.0-bundled.schema.json. Do not edit by hand; regenerate with:
     python .bob/skills/cyclonedx/scripts/schema_tool.py write-references -->
# CycloneDX 2.0 system schema reference (system BOM)

The modules a **system BOM** uses: `blueprint` (zones, boundaries, actors, flows, relationships), `usecase`, `definitions`, `inventories`/`component`, and `party`. Generated from the bundled schema, so it is exact for this copy of the schema. For any other module, run `python .bob/skills/cyclonedx/scripts/schema_tool.py outline <module>`.

In the Type column, `enum: a, b` means a plain string value, `{role: enum: …}` means an object that wraps the value (for example `{ "role": "developer" }`), and `or custom {name, description}` means a custom object is also accepted.

## Module `blueprint` (cyclonedx-blueprint-2.0)

### `blueprint:blueprints`

A collection of blueprints, each supporting a wide range of analytical activities, from use case documentation and behavioural analysis to comprehensive system-level threat and risk modelling.

Type: array of → blueprint:blueprint

### `blueprint:blueprint`

A versatile, machine-readable model designed to support a wide range of analytical activities, from use case documentation and behavioural analysis to comprehensive system-level threat and risk modelling.

Required: `name`, `modelTypes`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | The name of the blueprint, used to identify this model within the BOM and distinguish it from other blueprints. |
| `description` | string | A detailed explanation of the blueprint, including its scope, the system or subsystem it represents, and any relevant context about the modelling objectives or intended audience. |
| `metadata` | → blueprint:metadata |  |
| `modelTypes` | array of blueprint:modelType — enum: architecture, behavioral, conceptual, data-flow, deployment, logical, network, operational, physical, process — or custom {name, description} | The types of models being represented. |
| `scope` | → blueprint:scope |  |
| `assets` | array of → blueprint:asset | The assets (components, services, data, actors) included in the model. |
| `behaviors` | → behavior:behaviors |  |
| `dataStores` | array of → blueprint:dataStore | Structured description of data stores used in the model. |
| `dataSets` | array of → blueprint:dataSet | Datasets handled by the system, including placements and sensitivity. |
| `zones` | array of → blueprint:zone | Logical, physical, or trust zones that group assets with similar characteristics. |
| `boundaries` | array of → blueprint:boundary | Boundaries between zones. |
| `flows` | array of → blueprint:flow | Data, control, or process flows between assets. |
| `relationships` | array of → blueprint:relationship | Static, structural relationships between elements of the model, complementing the runtime exchanges captured by flows. |
| `actors` | array of → blueprint:actor | Human or system actors involved in the model, distinct from assets. |
| `assumptions` | array of → blueprint:assumption | Assumptions made during the modeling process. |
| `visualizations` | array of → blueprint:visualization | Visual representations of the model. |
| `useCases` | array of object | Use cases analyzed as part of the model, linking actors, goals, and steps to the blueprint's assets, flows, and requirements. |
| `requirements` | array of ref (refId in this document) | References using bom-link or `refId` to the requirements, declared in definitions, that are derived from or related to this model. |
| `externalReferences` | → common:externalReferences |  |
| `properties` | → common:properties |  |

### `blueprint:blueprint.useCases[]`

| Field | Type | Description |
|---|---|---|
| `ref` | ref (refId in this document) | A reference to a use case object defined in definitions. |
| `assets` | array of ref (refId in this document) | References using bom-link or `refId` to the blueprint assets that are involved in or exercised by this use case. |
| `flows` | array of ref (refId in this document) | References using bom-link or `refId` to the blueprint flows that are triggered or traversed during the execution of this use case. |
| `requirements` | array of ref (refId in this document) | References using bom-link or `refId` to the requirements that are implemented, validated, or addressed by this use case. |

### `blueprint:modelType`

The type of model being represented, either a predefined value from the enumeration or a custom name and description for types not covered by the enumeration. Threat, risk, and privacy analyses are represented in their own models, which reference the blueprint, rather than as blueprint model types.

### `blueprint:metadata`

Metadata about the creation, review, and approval of the blueprint.

| Field | Type | Description |
|---|---|---|
| `timestamp` | string | When the blueprint was created or last updated. |
| `authors` | array of → party:partyChoice | The parties that created the blueprint. Each entry is either an inline party object or a reference to a previously declared party. The party's `roles` should include `author`. |
| `reviewer` | → party:partyChoice | The party that reviewed the blueprint. The party's `roles` should include `reviewer`. |
| `reviewDate` | string | When the blueprint was reviewed. |
| `approver` | → party:partyChoice | The party that approved the blueprint. The party's `roles` should include `signatory` or a custom role identifying the approving authority. |
| `approvalDate` | string | When the blueprint was approved. |
| `ordinalVersion` | → common:ordinalVersion |  |
| `frozen` | boolean | Whether the blueprint is frozen and must be versioned before modification. |
| `lifecycles` | → common:lifecycles |  |
| `validityPeriod` | → blueprint:validityPeriod |  |

### `blueprint:validityPeriod`

The period during which the blueprint is considered valid.

| Field | Type | Description |
|---|---|---|
| `start` | string | When the blueprint becomes valid. |
| `end` | string | When the blueprint expires. |
| `reviewFrequency` | string | ISO 8601 duration for review frequency (e.g., P3M for quarterly). |

### `blueprint:scope`

Specifies what is included and excluded from the blueprint model, establishing the boundaries within which the modelling and analysis is performed.

Required: `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | Name of the scope. |
| `description` | string | Description of what is included and excluded from the model. |
| `boundaries` | array of string | Explicit boundaries of the model. |
| `includedComponents` | array of ref (refId in this document) | References using bom-link or `refId` to components explicitly included. |
| `excludedComponents` | array of ref (refId in this document) | References using bom-link or `refId` to components explicitly excluded. |
| `properties` | → common:properties |  |

### `blueprint:inScope`

Whether this element is within the scope of the model.

### `blueprint:asset`

A component, service, data store, actor, or other element included in the blueprint model. An actor asset references a party, since a party such as a person, persona, system, or organization may itself be an asset, including a person in the intelligence sense of a human source.

Exactly one of: {refId, componentRef} | {refId, partyRef} | {refId, type, name}

| Field | Type | Description |
|---|---|---|
| `refId` | refId | Unique identifier for the asset. |
| `componentRef` | ref (refId in this document) | Reference using bom-link or `refId` to the component this asset represents. |
| `partyRef` | ref (refId in this document) | Reference using bom-link or `refId` to the party this asset represents, such as a person, persona, system, or organization. Used when the asset is an actor. |
| `type` | enum: actor, agent, api, broker, cache, component, container, data, data-store, device, endpoint, function, gateway, infrastructure, interface, model, module, network, process, queue, resource, service, stream, subsystem, system, tool — or custom {name, description} | The kind of asset. Use the custom option for kinds not covered by the enumeration. |
| `name` | string | Name of the asset. |
| `description` | string | Description of the asset's role and purpose. |
| `inScope` | → blueprint:inScope |  |
| `zone` | ref (refId in this document) | Reference using bom-link or `refId` to the zone containing this asset. |
| `classification` | → blueprint:assetClassification |  |
| `tags` | → common:tags |  |
| `responsibilities` | array of string | Responsibilities or functions of this asset. |
| `interfaces` | array of → blueprint:interface | Interfaces exposed by this asset. |
| `useCases` | array of ref (refId in this document) | References using bom-link or `refId` to use case objects that describe how actors interact with this asset, including the specific goals, sequences of steps, alternative and exception flows, and any … |
| `authentication` | array of blueprint:authenticationType — enum: api-key, basic, bearer, biometric, certificate, digest, eap, fido2, form, hmac, jwt, kerberos, ldap, magic-link, mtls, none, ntlm, oauth1, oauth2, oidc, pin, psk, push, radius, saml, scram, session-cookie, ssh, totp — or custom {name, description} | Authentication methods supported/required. |
| `authorization` | array of blueprint:authorizationType — enum: abac, acl, capability, dac, mac, none, pbac, radac, rbac, rebac — or custom {name, description} | Authorization models supported/required. |
| `ownership` | → blueprint:ownership |  |
| `properties` | → common:properties |  |
| `externalReferences` | → common:externalReferences |  |

### `blueprint:dataStore`

A persistent storage system used within the modelled system to hold, retrieve, or manage data.

Required: `refId`, `name`, `type`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | Name of the data store. |
| `description` | string | Purpose and contents of the store. |
| `inScope` | → blueprint:inScope |  |
| `type` | enum: block, blockchain, cache, column-family, data-lake, data-warehouse, document, event-log, file, graph, hierarchical, in-memory, key-value, ledger, message-queue, multi-model, object, registry, relational, search, spatial, time-series, vector — or custom {name, description} | The type of data store. Use the custom option for technologies not covered by the enumeration. |
| `vendor` | string | The vendor or publisher of the data store product. |
| `product` | string | The name of the data store product. |
| `version` | string | The version of the data store product. |
| `environment` | string | Deployment environment (prod, test, etc.). |
| `zone` | ref (refId in this document) | Reference using bom-link or `refId` to the zone where the asset resides. |
| `location` | string | Physical or logical hosting location. |
| `technologies` | array of string | Supporting technologies or services. |
| `dataSets` | array of ref (refId in this document) | References using bom-link or `refId` to data sets stored here. |
| `authorization` | array of blueprint:authorizationType — enum: abac, acl, capability, dac, mac, none, pbac, radac, rbac, rebac — or custom {name, description} | Authorization models supported/required. |
| `properties` | → common:properties |  |

### `blueprint:dataSet`

A logical collection of related data managed within the modelled system, including its classification, ownership, and storage placements.

Required: `refId`, `name`, `description`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | Name of the dataset. |
| `description` | string | What information is contained and why it exists. |
| `dataProfiles` | array of → data:dataProfileChoice | Data profiles that govern the dataset. Each entry is either an inline profile object or a reference using bom-link or `refId` to a previously declared profile, typically declared in the definitions. |
| `dataObjects` | array of → data:dataObjectChoice | The specific data objects stored in the dataset. Each object names a payload and may reference one of the dataset's data profiles for its governing policy. |
| `recordCount` | integer | Approximate number of records. |
| `inScope` | → blueprint:inScope |  |
| `owners` | array of → party:partyChoice | Parties that own the dataset. Each entry is either an inline party object or a reference to a previously declared party. The party's `roles` should include `owner`. |
| `authorization` | array of blueprint:authorizationType — enum: abac, acl, capability, dac, mac, none, pbac, radac, rbac, rebac — or custom {name, description} | Authorization models supported/required. |
| `placements` | array of object | Where the dataset resides. |
| `properties` | → common:properties |  |

### `blueprint:dataSet.placements[]`

Describes where a dataset physically or logically resides and the storage characteristics at that location.

Required: `dataStore`

| Field | Type | Description |
|---|---|---|
| `dataStore` | ref (refId in this document) | Reference using bom-link or `refId` to the store holding this dataset. |
| `encrypted` | boolean | Whether the dataset is encrypted at this location. |
| `retention` | string | Retention policy for this placement. |
| `replicated` | boolean | Indicates if this placement is a replica. |

### `blueprint:interface`

Required: `name`, `type`

| Field | Type | Description |
|---|---|---|
| `name` | string | Name of the interface. |
| `type` | enum: rest, graphql, grpc, soap, messaging, file, database, cli, gui, api, event, stream — or custom {name, description} | The type of interface. Use the custom option for types not covered by the enumeration. |
| `description` | string | Description of the interface. |
| `specification` | string | Link or reference to interface specification. |
| `protocol` | string | Communication protocol used. |
| `dataFormat` | string | Data format (e.g., JSON, XML, Protocol Buffers). |
| `authentication` | array of blueprint:authenticationType — enum: api-key, basic, bearer, biometric, certificate, digest, eap, fido2, form, hmac, jwt, kerberos, ldap, magic-link, mtls, none, ntlm, oauth1, oauth2, oidc, pin, psk, push, radius, saml, scram, session-cookie, ssh, totp — or custom {name, description} |  |
| `operations` | array of string | Operations or methods exposed. |

### `blueprint:zone`

A grouping of assets that share a common characteristic, security posture, or administrative control, so they can be reasoned about as a unit. A zone may be logical, physical, network, trust, or another kind, may nest within a parent zone, and is connected to or separated from other zones by boundaries.

Required: `refId`, `name`, `type`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | Name of the zone. |
| `description` | string | Description of the zone's characteristics. |
| `type` | enum: availability, compliance, data, deployment, functional, geographic, logical, network, organizational, physical, process, tenant, trust — or custom {name, description} | The type of zone. Use the custom option for types not covered by the enumeration. |
| `parent` | ref (refId in this document) | Reference using bom-link or `refId` to the parent zone if this is a sub-zone. |
| `characteristics` | array of string | Key characteristics of this zone. |
| `constraints` | array of string | Constraints or limitations of this zone. |
| `inScope` | → blueprint:inScope |  |
| `properties` | → common:properties |  |

### `blueprint:boundary`

An edge that separates or connects two or more zones, marking a point where security controls, policies, or trust levels change. The controls expected when data or actors cross it are captured in crossingRequirements, and the threat model's trust boundary extends a boundary with trust semantics.

Required: `refId`, `zones`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | Name of the boundary. |
| `type` | enum: data, functional, network, organizational, physical, process, trust — or custom {name, description} | The type of boundary. Use the custom option for types not covered by the enumeration. |
| `zones` | array of ref (refId in this document) | References using bom-link or `refId` to the zones this boundary connects or separates. |
| `crossingRequirements` | → blueprint:crossingRequirements |  |
| `sessionManagement` | → blueprint:sessionManagement |  |
| `inScope` | → blueprint:inScope |  |
| `properties` | → common:properties |  |

### `blueprint:crossingRequirements`

The security controls, policies, and constraints applied when data or actors cross a boundary between zones, such as the authentication and authorization enforced, the protocols permitted, and the validation, logging, and monitoring performed at the crossing.

| Field | Type | Description |
|---|---|---|
| `authentication` | array of blueprint:authenticationType — enum: api-key, basic, bearer, biometric, certificate, digest, eap, fido2, form, hmac, jwt, kerberos, ldap, magic-link, mtls, none, ntlm, oauth1, oauth2, oidc, pin, psk, push, radius, saml, scram, session-cookie, ssh, totp — or custom {name, description} | Authentication required to cross this boundary. |
| `authorization` | array of blueprint:authorizationType — enum: abac, acl, capability, dac, mac, none, pbac, radac, rbac, rebac — or custom {name, description} | Authorization models enforced at this boundary. |
| `dataValidation` | boolean | Whether data is validated when crossing this boundary. |
| `dataTransformation` | boolean | Whether data is transformed when crossing this boundary. |
| `logging` | boolean | Whether crossings are logged. |
| `monitoring` | boolean | Whether crossings are monitored. |
| `rateLimit` | string | Rate limiting policy. |
| `protocols` | array of string | Allowed protocols for crossing. |

### `blueprint:sessionManagement`

The lifecycle of the authenticated session established at this boundary, covering session timeouts, access and refresh token validity, and logout behaviour. These properties characterize the session that results from authenticating, independently of the authentication method used.

| Field | Type | Description |
|---|---|---|
| `accessTokenExpires` | boolean | Whether access tokens issued for this boundary expire. |
| `accessTokenTtl` | integer | Validity period of an access token, in seconds. |
| `refreshToken` | boolean | Whether refresh tokens are issued for this boundary. |
| `refreshTokenExpires` | boolean | Whether refresh tokens expire. |
| `refreshTokenTtl` | integer | Validity period of a refresh token, in seconds. |
| `idleTimeout` | integer | Period of inactivity after which the session ends, in seconds. |
| `absoluteTimeout` | integer | Period after session creation after which the session ends regardless of activity, in seconds. |
| `userLogout` | boolean | Whether a user can explicitly end the session. |
| `systemLogout` | boolean | Whether the system can end the session without user action. |

### `blueprint:relationship`

A typed structural relationship from one element to one or more others, complementing the runtime exchanges captured by flows. The subject is `ref`, and the kind of relationship is expressed as a single typed property whose value lists the targets, mirroring the dependency graph for readability.

Required: `ref`

Exactly one of: {aggregates} | {associates} | {composes} | {contains} | {dependsOn} | {generalizes} | {realizes} | {serves} | {custom}

| Field | Type | Description |
|---|---|---|
| `ref` | ref (refId in this document) | Reference using bom-link or `refId` to the subject element of the relationship. |
| `aggregates` | → blueprint:relationshipTargets | The subject is the whole in a whole-part relationship in which each target part may exist independently of the whole. |
| `associates` | → blueprint:relationshipTargets | The subject has a general association with each target. |
| `composes` | → blueprint:relationshipTargets | The subject is the whole in a whole-part relationship in which each target part cannot exist without the whole. |
| `contains` | → blueprint:relationshipTargets | The subject contains or nests each target. |
| `dependsOn` | → blueprint:relationshipTargets | The subject depends on each target. |
| `generalizes` | → blueprint:relationshipTargets | The subject is a generalisation of each target, as in inheritance. |
| `realizes` | → blueprint:relationshipTargets | The subject realises or implements each target. |
| `serves` | → blueprint:relationshipTargets | The subject provides a service to each target. |
| `custom` | array of object | Relationships whose kind is not covered by the predefined properties. Each entry names the kind and lists its targets. |

### `blueprint:relationship.custom[]`

Custom Relationship

Required: `type`, `targets`

| Field | Type | Description |
|---|---|---|
| `type` | string | The name of the custom relationship kind. |
| `targets` | → blueprint:relationshipTargets | The targets of the custom relationship. |
| `description` | string | A description of the custom relationship kind. |

### `blueprint:relationshipTargets`

References using bom-link or `refId` to the target elements of a relationship.

Type: array of ref (refId in this document)

### `blueprint:flow`

Represents a data, control, or process flow between two assets, capturing the direction, type, protocols, and security controls that govern the exchange.

Required: `refId`, `name`, `source`, `destination`, `type`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | Name or description of the flow. |
| `description` | string | Detailed description of what flows and why. |
| `inScope` | → blueprint:inScope |  |
| `type` | enum: control, data, energy, event, financial, message, physical, process, signal — or custom {name, description} | The type of flow. Use the custom option for types not covered by the enumeration. |
| `source` | ref (refId in this document) | Reference using bom-link or `refId` to the source of the flow. The source may be either an asset (such as a component, service, data store, or other element in the blueprint) or an actor that origina… |
| `destination` | ref (refId in this document) | Reference using bom-link or `refId` to the destination of the flow. The destination may be either an asset (such as a component, service, data store, or other element in the blueprint) or an actor th… |
| `bidirectional` | boolean | Whether flow occurs in both directions. |
| `synchronous` | boolean | Whether the flow is synchronous or asynchronous. |
| `encrypted` | boolean | Whether the data carried by this flow is encrypted in transit. |
| `volume` | string | Expected volume or frequency of flow. |
| `timing` | string | Timing characteristics (real-time, batch, scheduled). |
| `protocols` | array of string | Communication protocols used by this flow. |
| `dataProfiles` | array of → data:dataProfileChoice | Data profiles that govern the data carried by this flow. A flow may carry data governed by multiple profiles, for example a payment submission carrying both payment card data and customer personally … |
| `dataObjects` | array of → data:dataObjectChoice | The specific data objects carried by this flow. Each object names a payload and may reference one of the flow's data profiles for its governing policy. |
| `authentication` | array of blueprint:authenticationType — enum: api-key, basic, bearer, biometric, certificate, digest, eap, fido2, form, hmac, jwt, kerberos, ldap, magic-link, mtls, none, ntlm, oauth1, oauth2, oidc, pin, psk, push, radius, saml, scram, session-cookie, ssh, totp — or custom {name, description} | Authentication required for this flow. |
| `authorization` | array of blueprint:authorizationType — enum: abac, acl, capability, dac, mac, none, pbac, radac, rbac, rebac — or custom {name, description} | Authorization models enforced on this flow. |
| `sequence` | integer | Ordering hint so flows can be assembled into sequence diagrams. |
| `properties` | → common:properties |  |

### `blueprint:actor`

An actor is a contextual binding between a party and the modelled system. The party identifies who or what is acting (an organisation, person, system, or persona). The actor layer adds properties that are meaningful only within the blueprint, such as the permissions the actor holds in this system and the trust zone in which the actor operates. Identity, roles, archetype, and inter-party relations such as delegation are carried by the wrapped party and shall not be duplicated on the actor.

Required: `refId`, `party`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | Unique identifier for this actor binding. References to actors from other parts of the blueprint, such as use cases or flows, use this identifier. |
| `party` | → party:partyChoice | The party that this actor binds to the modelled system. May be an inline party object declaring identity and roles in place, or a bom-link or `refId` to a party declared elsewhere in the document. |
| `description` | string | A narrative describing this actor's role within the modelled system, distinct from the party's identity-level description. Use to record context-specific framing such as why this actor is in scope or… |
| `inScope` | → blueprint:inScope |  |
| `permissions` | array of string | The permissions, capabilities, or duties this actor holds within the modelled system. Distinct from any innate party-level capabilities; these are scoped to the blueprint. |
| `zone` | ref (refId in this document) | Reference using bom-link or `refId` to the trust zone in which the actor operates. |
| `properties` | → common:properties |  |

### `blueprint:assumption`

A stated belief or condition accepted as true for the purposes of the model, which may impact the validity of the analysis if proven false.

Required: `description`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `description` | string | A clear statement of the assumption being made, including the believed condition, the reasoning or evidence behind it, and any constraints or scope under which it applies. |
| `topic` | enum: availability, business, compliance, operational, performance, security, technical — or custom {name, description} | The topic of the assumption. Use the custom option for topics not covered by the enumeration. |
| `relatedAssets` | array of ref (refId in this document) | References using bom-link or `refId` to the assets that are directly affected by or dependent on this assumption, enabling impact analysis when the assumption's validity changes. |
| `validity` | enum: invalid, unknown, unverified, verified | The current validation state of the assumption, tracked over time to ensure that modelling decisions built on this assumption remain sound. |
| `impact` | string | A narrative describing the consequences to the model, its assets, or the broader system if this assumption proves false, including the severity and scope of affected components. |
| `owner` | → party:partyChoice | The party responsible for tracking, validating, and maintaining this assumption over the lifecycle of the model. May be an inline party object or a reference to a previously declared party. The party… |
| `validationMethod` | string | The approach, test, or evidence that can be used to confirm or disprove this assumption, such as a review, audit, penetration test, or empirical measurement. |
| `validationDate` | string | The date and time when the assumption was last validated or reviewed, used to track staleness and trigger re-evaluation. |

### `blueprint:visualization`

A visual representation of the model or a subset of its elements, capturing the diagram type, its content, and the elements depicted.

Required: `name`, `type`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | Name or title of the visualization. |
| `description` | string | Description of what the visualization shows. |
| `type` | blueprint:visualizationType — {type: enum: activity, architecture, attack-tree, block, class, code, communication, component, container, context, data-flow, deployment, entity, flowchart, matrix, mind-map, network, process, sequence, state, timing, use-case} — or custom {name, description} |  |
| `attachment` | → common:attachment |  |
| `url` | string | URL to the diagram if stored externally. |
| `level` | enum: detailed, high, medium, overview | Level of detail in the visualization. |
| `elements` | array of ref (refId in this document) | References using bom-link or `refId` to elements shown in this visualization. |
| `interactive` | boolean | Whether the visualization is interactive. |
| `layers` | array of string | Layers or views available in the visualization. |
| `properties` | → common:properties |  |

### `blueprint:visualizationType`

The type of diagram or visual representation.

### `blueprint:assetClassification`

| Field | Type | Description |
|---|---|---|
| `criticality` | risk:criticality — enum: minimal, low, moderate, high, critical |  |
| `safetyIntegrityLevels` | array of → blueprint:safetyIntegrityLevel | The safety integrity classifications of this asset in the context of the blueprint. An asset may carry classifications from more than one scheme, for example where an element classified under IEC 615… |
| `riskAttributes` | array of risk:riskAttribute — enum: accountability, authentication, authorization, authenticity, availability, compliance, confidentiality, connectivity, control, data-subject-rights, integrity, minimization, non-repudiation, possession, privacy, purpose-limitation, transparency, utility — or custom {name, description} | The security and privacy attributes of this asset that are worth protecting, such as integrity or availability, whose compromise leads to damage. Corresponds to the cybersecurity properties of an ass… |
| `classification` | data:dataClassification — enum: confidential, internal, public, restricted, classified — or custom {name, description} |  |
| `categories` | array of string | Business or technical categories. |
| `tags` | array of string | Tags for classification and search. |

### `blueprint:safetyIntegrityLevel`

A safety integrity classification drawn from a functional safety scheme, such as an Automotive Safety Integrity Level, a Safety Integrity Level, a Design Assurance Level, or a software safety class. The classification describes the safety significance of the context; a level that an authority has attested the subject achieved is recorded as a certification.

Required: `scheme`, `level`

| Field | Type | Description |
|---|---|---|
| `scheme` | enum: ISO-26262, IEC-61508, DO-178C, IEC-62304, EN-50128 — or custom {name, description} | The functional safety scheme from which the level is drawn. Use the custom option for schemes not covered by the enumeration. |
| `level` | string | The level within the scheme, using the designation the scheme defines. Lowercase kebab-case tokens are recommended so that levels compare reliably across documents. |

### `blueprint:ownership`

Parties responsible for the asset. Each entry is either an inline party object or a reference to a previously declared party. The party's `roles` carry the relationship (`owner`, `steward`, `custodian`, `end-user`, or a custom role). Multiple parties may share the same role; preference among them is expressed via `role.order`.

Type: array of → party:partyChoice

### `blueprint:authenticationType`

The authentication method or protocol used to verify identity, either a predefined value from the enumeration or a custom object describing a method not covered by the enumeration.

### `blueprint:authorizationType`

The authorization model used to determine and enforce access permissions, either a predefined value from the enumeration or a custom object describing a model not covered by the enumeration.

### `usecase:useCases`

A collection of use cases that describe how actors interact with the system to achieve specific goals.

Type: array of → usecase:useCase

### `usecase:useCase`

A structured description of how one or more actors interact with the system to achieve a specific goal, including the primary flow, alternative paths, and exception scenarios.

Required: `refId`, `name`

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `name` | string | The name or title of the use case, typically expressed as a verb phrase that captures the goal from the actor's perspective (e.g., 'Place Order', 'Reset Password'). |
| `description` | string | A detailed narrative of the use case, including the actor's goal, the scope of the interaction, and any relevant business rules or constraints that govern its execution. |
| `actors` | array of ref (refId in this document) | References using bom-link or `refId` to the actors that participate in this use case, representing anyone or anything that initiates or interacts with the described flow. |
| `preconditions` | array of string | Conditions that must hold true before the use case can begin execution, such as required system state, authenticated sessions, available resources, or prior completed use cases. |
| `postconditions` | array of string | Conditions that will be true after the use case completes successfully, describing the expected system state, data changes, notifications sent, or side effects produced. |
| `mainFlow` | array of → usecase:step | The primary sequence of steps representing the most common or expected path through the use case, from the triggering action to the successful outcome. |
| `alternativeFlows` | array of → usecase:flow | Variant paths that branch from the main flow under specific conditions, representing valid but less common ways to achieve the use case goal or a modified outcome. |
| `exceptions` | array of → usecase:exception | Error or failure scenarios that may interrupt the main or alternative flows, including the triggering condition and how the system responds to recover or terminate gracefully. |
| `successCriteria` | array of string | Measurable or observable criteria that determine whether the use case has been completed successfully, used for validation, acceptance testing, and stakeholder sign-off. |
| `requirements` | array of ref (refId in this document) | References using bom-link or `refId` to the requirements that are implemented, validated, or addressed by this use case. |
| `businessObjectives` | array of ref (refId in this document) | References using bom-link or `refId` to the business objectives this use case supports. |
| `notes` | array of string | Supplementary information, clarifications, open questions, or implementation guidance that provides additional context beyond the formal use case structure. |
| `properties` | → common:properties |  |

### `usecase:step`

A single discrete action within a use case flow, performed by a specific actor, that advances the interaction toward the use case goal.

Required: `number`, `description`

| Field | Type | Description |
|---|---|---|
| `number` | integer | The sequence number indicating the ordinal position of this step within its flow, starting at 1. |
| `description` | string | A clear, action-oriented statement describing what the actor does in this step and the expected system response, written in the form 'The [actor] [action]'. |
| `actor` | ref (refId in this document) | Reference using bom-link or `refId` to the actor who initiates or performs this step, which may be a human user, an external system, or the system under design. |

### `usecase:flow`

An alternative sequence of steps that branches from the main flow under a specific condition, representing a valid variant path through the use case.

Required: `name`, `condition`

| Field | Type | Description |
|---|---|---|
| `name` | string | A short, descriptive name identifying this alternative flow (e.g., 'Payment Declined', 'Guest Checkout'). |
| `description` | string | A narrative explaining the purpose and context of this alternative flow, including how it differs from the main flow and under what circumstances it applies. |
| `condition` | string | The specific condition, decision point, or triggering event that causes execution to diverge from the main flow into this alternative path. |
| `steps` | array of → usecase:step | The ordered sequence of steps that comprise this alternative flow, following the same structure as main flow steps. |

### `usecase:exception`

An error or failure scenario that may interrupt the normal execution of a use case, including the condition that triggers it and how the system responds.

Required: `name`, `condition`

| Field | Type | Description |
|---|---|---|
| `name` | string | A short, descriptive name identifying this exception scenario (e.g., 'Session Timeout', 'Insufficient Funds', 'Service Unavailable'). |
| `description` | string | A narrative describing the nature of this exception, its potential causes, and its impact on the use case and the actors involved. |
| `condition` | string | The specific error condition, system state, or external event that triggers this exception during the execution of the use case. |
| `handling` | string | The recovery strategy or response the system takes when this exception occurs, such as retrying the operation, rolling back changes, notifying the user, or escalating to support. |

### `definition:definitions`

A collection of reusable objects that may be referenced from elsewhere in the document or provided for interchange. The canonical form of each object is independent of any assertion, so every reference to it denotes an identical object.

| Field | Type | Description |
|---|---|---|
| `components` | array of → component:component | Reusable component declarations. Each entry is a concrete component that may be referenced from any position that accepts a component reference. Declaring a component here does not by itself include … |
| `parties` | array of → party:party | Reusable party declarations. Each entry is a concrete party that may be referenced by its `refId` from any position that accepts a party. Declaring a party here does not by itself associate the party… |
| `licenses` | array of license:licenseDeclaration — {acknowledgement: enum: declared, concluded, expression, expressionDetails, refId, licensing, properties} — or custom {license} | Reusable license declarations. Each entry is a concrete license or license expression that may be referenced by its `refId` from any position that accepts a license reference. Declaring a license her… |
| `profiles` | → profile:profiles |  |
| `releaseNotes` | array of → release-notes:releaseNotes | Reusable release notes declarations. Each entry may be referenced by its `refId` from the components whose release it describes. |
| `certifications` | → certification:certifications | Reusable certification declarations. Each entry may be referenced by its `refId` from the subjects it applies to. |
| `weaknesses` | array of → weakness:weakness | Reusable weakness declarations. Each entry may be referenced by its `refId` from the vulnerabilities and threats it gives rise to. |
| `graphics` | array of → common:graphic | Reusable graphics. Each entry may be referenced by its `refId` from any record that accepts graphics, such as a performance metric or an energy consumption. |
| `dataObjects` | array of → data:dataObject | Reusable data object declarations. Each entry may be referenced by its `refId` from the flows that carry it and the data sets that store it. |
| `detectionRules` | array of → evidence:detectionRule | Reusable detection rule declarations. Each entry may be referenced by its `refId` from every analysis method whose result the rule produced. |
| `patches` | array of → common:patch | Reusable patch declarations. Each entry may be referenced by its `refId` from the pedigree of every component to which the patch applies. |
| `standards` | → standard:standards |  |
| `patents` | → patent:patents |  |
| `useCases` | → usecase:useCases |  |
| `requirements` | → requirement:requirements |  |
| `businessObjectives` | → business-objective:businessObjectives |  |

### `component:inventory`

The declared inventory of one subject: the entries included in the subject. The completeness of the list is asserted through compositions.

Required: `subject`, `components`

| Field | Type | Description |
|---|---|---|
| `refId` | refId | An identifier which can be used to reference the inventory elsewhere in the document. Every `refId` shall be unique within the document. |
| `subject` | → component:component \| → component:componentReference | The subject whose inventory this statement declares. Either a concrete component or a reference using bom-link or `refId` to a component declared elsewhere, such as in the definitions. |
| `components` | → component:components | The entries included in the subject. Entries may be concrete components, references to components declared elsewhere, or component-choice wrappers. |
| `properties` | → common:properties |  |
| `signatures` | → common:signatures | Enveloped signatures over the inventory statement. A signature binds reference entries by their identifiers; the content of a referenced component is covered by the hashes or signatures on the refere… |

### `component:component`

Component

Required: `type`, `name`

| Field | Type | Description |
|---|---|---|
| `type` | enum: application, framework, library, container, platform, operating-system, device, device-driver, firmware, file, machine-learning-model, data, cryptographic-asset, material, service | Specifies the type of component. For software components, classify as application if no more specific appropriate classification is available or cannot be determined for the component. |
| `mediaType` | → common:mediaType |  |
| `refId` | refId | An identifier which can be used to reference the component elsewhere in the document. Every `refId` shall be unique within the document. Value should not start with the BOM-Link intro 'urn:cdx:' to a… |
| `parties` | → party:parties |  |
| `origins` | array of → common:origin | The geographic origins of the component, each expressed as a distribution across one or more countries or subdivisions. Multiple origins are allowed, each calculated on a different basis. |
| `group` | string | The grouping name or identifier. This will often be a shortened, single name of the company or project that produced the component, or the source package or domain name. Whitespace and special charac… |
| `name` | string | The name of the component. This will often be a shortened, single name of the component. Examples: commons-lang3 and jquery |
| `version` | → component:version | The component version. The version should ideally comply with semantic versioning but is not enforced. Must be used exclusively, either 'version' or 'versionRange', but not both. |
| `versionRange` | → component:versionRange | For an external component, this specifies the accepted version range. The value must adhere to the Package URL Version Range syntax (vers), as defined at <https://github.com/package-url/vers-spec May… |
| `isExternal` | boolean | Determine whether this component is external. An external component is one that is not part of an assembly, but is expected to be provided by the environment, regardless of the component's `.scope`. … |
| `description` | string | Specifies a description for the component |
| `scope` | enum: required, optional, excluded | Specifies the scope of the component. If scope is not specified, 'required' scope SHOULD be assumed by the consumer of the BOM. |
| `hashes` | array of → common:hash | The hashes of the component. |
| `measurements` | → component:measurements | Component Measurements |
| `licenses` | → license:licenseChoice | Component License(s) |
| `copyright` | → component:copyrightText |  |
| `patentAssertions` | → patent:patentAssertions | Component Patent(s) |
| `requirementAssertions` | → requirement:requirementAssertions | Component Requirement(s) |
| `useCaseAssertions` | → usecase:useCaseAssertions | Component Use Case(s) |
| `identifiers` | → component:identifiers |  |
| `pedigree` | object | Component pedigree is a way to document complex supply chain scenarios where components are created, distributed, modified, redistributed, combined with other components, etc. Pedigree supports viewi… |
| `components` | array of → component:componentEntry | A list of entries included in the parent component, including software, hardware, and services. Entries may be concrete components, references to components declared elsewhere, or component-choice wr… |
| `evidence` | → component:componentEvidence | Provides the ability to document evidence collected through various forms of extraction or analysis. |
| `releaseNotes` | → release-notes:releaseNotes \| → release-notes:releaseNotesReference | The release notes for the component. Either inline release notes or a reference using bom-link or `refId` to release notes defined elsewhere, such as in the definitions. |
| `modelProperties` | → ai-ml:modelProperties | Intrinsic technical characteristics of a machine learning model. This object SHOULD be specified for any component of type `machine-learning-model` and shall not be specified for other component type… |
| `data` | array of → component:componentData | This object SHOULD be specified for any component of type `data` and must not be specified for other component types. |
| `cryptoProperties` | → cryptography:cryptoProperties | Cryptographic Properties |
| `agility` | → component:agility |  |
| `classification` | → physical:classification | Hierarchical classification of the item, with optional taxonomy codes from external standards. This object may only be specified for components of type `device` or `material` and shall not be specifi… |
| `boardLocation` | → physical:boardLocation | Placement of the item on a printed circuit board, panel, or assembly. This object may only be specified for components of type `device` and shall not be specified for other component types. |
| `deviceType` | physical:deviceType — enum: smd, pth, dip, sip, qfn, qfp, bga, csp, sot, to, wlcsp, module, die, discrete — or custom {name, description} | Package or mounting style of the physical item, expressed as a predefined device type or a custom device type. This object may only be specified for components of type `device` and shall not be speci… |
| `leadTime` | → physical:leadTime | Supplier lead time for procuring the item. This object may only be specified for components of type `device` or `material` and shall not be specified for other component types. |
| `materialForm` | physical:materialForm — enum: powder, ingot, billet, bar, rod, wire, sheet, foil, plate, tube, pellet, flake, sponge, liquid, gas — or custom {name, description} | Physical form in which the material is supplied, expressed as a predefined material form or a custom material form. This object may only be specified for components of type `material` and shall not b… |
| `quantity` | → physical:quantity | The quantity of the item in the context in which it is declared, such as the number of identical parts within the enclosing assembly or the amount of material in the described lot. This object may on… |
| `certifications` | array of → certification:certification \| → certification:certificationReference | Certifications held by or applicable to the component. Each entry is either an inline certification or a reference using bom-link or `refId` to a certification defined elsewhere, such as in the defin… |
| `endpoints` | array of string | The endpoint URIs of the service. Multiple endpoints are allowed. May only be used for components of type `service`. |
| `dataProfiles` | array of → data:dataProfileChoice | The data handled by the service, characterized by data profiles. Each entry is either an inline profile object or a reference using bom-link or `refId` to a previously declared profile, typically dec… |
| `tags` | → common:tags | Tags |
| `properties` | → common:properties |  |
| `externalReferences` | → common:externalReferences |  |
| `signatures` | → common:signatures |  |

### `component:componentReference`

A reference to a component declared elsewhere, such as in the definitions registry, in another position of the same document, or in another document via BOM-Link. A reference includes the referenced component exactly as declared: every position that references the same component includes an identical component. Where the inclusion context differs, such as a different scope or quantity, declare the component inline instead.

Required: `ref`

| Field | Type | Description |
|---|---|---|
| `ref` | ref (refId in this document) \| BOM-Link element (urn:cdx:...#ref) | Reference using bom-link or `refId` to the component. |

### `party:party`

Identifies an organization, individual, system, or abstract archetype that participates in supplying, producing, attesting, operating, owning, regulating, or otherwise relating to the subject. Each party plays one or more named roles. Roles may carry preference order (`role.order`) to express primary, alternate, and secondary rankings among parties sharing the same role. Exactly one identity sub-shape (`organization`, `person`, `system`, or `persona`) shall be present. Optional sub-objects layer inter-party relationships and standard extension data.

Required: `roles`

Exactly one of: {organization} | {person} | {system} | {persona}

| Field | Type | Description |
|---|---|---|
| `refId` | refId |  |
| `roles` | array of party:role — {role: enum: agent, assembler, asserter, attacker, auditor, author, broker, carrier, certificate-authority, committer, competitor, consignee, consignor, contributor, customer, custodian, customs-broker, data-controller, data-processor, data-recipient, data-subject, delegate, developer, distributor, end-user, engineer, exporter, freight-forwarder, holder, importer, insider-threat, inspector, insurer, integrator, issuer, key-escrow-agent, legal-contact, licensee, licensor, maintainer, manufacturer, operator, owner, packager, partner, principal, provider, publisher, purchaser, quality-control, regulator, relying-party, repackager, researcher, reviewer, security-contact, signatory, steward, subject, supplier, support-contact, third-party-logistics, timestamp-authority, validation-authority, verifier, warehouse-operator, order} — or custom {name, description, order} | One or more roles the party fulfils. Each role may carry an `order` indicating preference among parties sharing the same role (for example, primary versus alternate supplier). |
| `organization` | → party:organization | Identity attributes valid when the party is an organization, company, government body, or other collective. |
| `person` | → party:person | Identity attributes valid when the party is an individual person. |
| `system` | → party:system | Identity attributes valid when the party is a software system, hardware system, service account, automation, or autonomous agent. |
| `persona` | → party:persona | Identity attributes valid when the party is an abstract archetype rather than a specific named instance. |
| `relations` | → party:partyRelations | Links from this party to other parties. |
| `tags` | → common:tags |  |
| `properties` | → common:properties |  |
| `externalReferences` | → common:externalReferences |  |

### `party:partyReference`

A reference to a party declared elsewhere, such as in the definitions registry, in another position of the same document, or in another document via BOM-Link. A reference includes the referenced party exactly as declared: every position that references the same party includes an identical party. Where the party context differs, such as a different role, declare the party inline instead.

Required: `ref`

| Field | Type | Description |
|---|---|---|
| `ref` | ref (refId in this document) \| BOM-Link element (urn:cdx:...#ref) | Reference using bom-link or `refId` to the party. |

### `party:persona`

Identity attributes for a party that is an abstract archetype rather than a specific named instance. Use for generic users, generic suppliers, or hypothesized attackers when a specific party is intentionally not named. When the specific instance is known (for example a tracked APT group), use `organization` instead.

| Field | Type | Description |
|---|---|---|
| `label` | string | A short, human-readable label for the persona, used to tell personas apart and to refer to them in documentation, diagrams, and tooling. The label is a display handle and does not assert the identity… |
| `description` | string | Free-text description of the persona instance. Use to refine the archetype with details relevant to the threat model, such as the persona's assumed context, history, or behavioral pattern. |
| `archetype` | enum: end-user, power-user, administrator, developer, operator, internal, external, anonymous, guest, customer, partner, supplier, vendor, contractor, third-party, auditor, researcher, regulator, law-enforcement, attacker, insider-threat, hacktivist, nation-state, organized-crime, competitor, public — or custom {name, description} | The persona archetype. May be a predefined archetype from the CycloneDX persona-archetype taxonomy expressed as a plain string, or a custom archetype expressed as an object with `name` and optional `… |
| `scope` | enum: internal, external, mixed | Scope |
| `permissions` | array of string | Capabilities the persona is assumed to hold. |
| `assumedPosture` | string | Assumed security posture of the persona in this context. |

### `party:system`

Identity attributes for a party that is a software system, hardware system, service account, automation, or autonomous agent.

| Field | Type | Description |
|---|---|---|
| `label` | string | A short, human-readable label for the system, used to refer to it in documentation, diagrams, and tooling. Where `ref` is present, the referenced object remains the authoritative source of identity. |
| `kind` | enum: software-system, hardware-system, service-account, machine-identity, automation, agent, bot, oracle, smart-contract, device, robot — or custom {name, description} | The kind of system the party represents. May be a predefined kind from the CycloneDX system-kind taxonomy expressed as a plain string, or a custom kind expressed as an object with `name` and optional… |
| `ref` | ref (refId in this document) | Reference to any object carrying a `refId` that represents this system. The referenced object provides the underlying identity (component, service, blueprint asset, or other object type). Use to asso… |
| `identifiers` | array of → party:identifier | Machine identifiers for the system, such as service principal, workload identity, certificate subject, or device serial. |
| `permissions` | array of string | Capabilities or duties the system possesses. |

### `party:role`

A role that a party fulfils. May be a predefined role from the CycloneDX role taxonomy or a custom role definition. The optional `order` property ranks parties that share the same role, supporting use cases such as primary versus alternate suppliers in hardware manufacturing supply chains.

