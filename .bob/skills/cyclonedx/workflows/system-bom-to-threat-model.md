# Workflow: system BOM to threat-model BOMs

Generate a **threat model** from a CycloneDX 2.0 system BOM: **one threat-model BOM (TM-BOM) per use case**, each linked to the system BOM by BOM-Link. This follows the LF AI & Data Use Cases and Threat Modeling subgroup's method ([README](../../../../subgroups/use-cases-and-threat-models/README.md)): perspective-correct threat statements, NIST SP 800-30 enrichment, CAPEC and CWE mapping, and controls mapped to NIST SP 800-53 and CSA AICM.

The reference output is [examples/tm-bom.code-assistant-1b.json](../examples/tm-bom.code-assistant-1b.json), one fully worked threat for the Code Assistant Sub Use Case 1b, linked to [examples/system-bom.code-assistant.json](../examples/system-bom.code-assistant.json).

## How the two documents link

CycloneDX 2.0 has two kinds of reference, and they are not interchangeable:

| Reference | Format | Allowed in |
|---|---|---|
| In-document | the target's `refId`, for example `component:local-ide` | every `affects`, `mitigations`, `appliesTo`, `source`, `boundary`, `threats`, … field in the threat, risk and control modules |
| BOM-Link | `urn:cdx:<serial-uuid>/<version>` (a document) or `urn:cdx:<serial-uuid>/<version>#<refId>` (an element) | `externalReferences[].url`, component references, weakness references, and a few others. **Not** in threat, risk or control reference fields; the schema rejects `urn:cdx:` there. |

A TM-BOM therefore carries a **system slice**: copies of the system BOM's components, actors, zones, boundaries, flows and relationships that the use case exercises, **under the same refIds**. Threats reference those refIds locally, and the links back are:

1. Top level: `externalReferences: [{ "type": "bom", "url": "urn:cdx:<system-serial>/<system-version>" }]`.
2. Each sliced component: `externalReferences: [{ "type": "bom", "url": "urn:cdx:<system-serial>/<system-version>#<component refId>" }]`.
3. Optionally, in the other direction, the system BOM gets `externalReferences: [{ "type": "threat-model", "url": "urn:cdx:<tm-serial>/<tm-version>" }]`.

The same refId means the same element in both documents. Never rename or re-describe a sliced element in the TM-BOM; change the system BOM and regenerate the slice instead.

## Step 1: Check the system BOM and list its use cases

```
python .bob/skills/cyclonedx/scripts/validate_bom.py <system>.json
python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --list
```

- If the system BOM has errors, stop and fix them, or ask the user to.
- If it has no `serialNumber`, it cannot be linked to. Ask the user before running `python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --assign-serial`, which edits the system BOM in place.
- `--list` flags umbrella use cases, whose flows are exactly the union of other use cases. Make TM-BOMs for the specific use cases, not the umbrella, unless the user asks for it.
- Confirm with the user which use cases to model and which methodologies to apply. Default to STRIDE per element and flow, MAESTRO for agentic and AI components, and MITRE ATLAS techniques where relevant; the 2.0 `methodologies` enum is `STRIDE, LINDDUN, PASTA, MAESTRO, OWASP, TRIKE, VAST, ATFAA, attack-tree`.

## Step 2: Create one TM-BOM skeleton per use case

```
python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --use-case usecase:<id> -o <name>.tm-bom.<use-case-id>.json
```

The script refuses to overwrite an existing file; see "Regenerating" below to update one. This writes the system slice, the BOM-Links, metadata properties naming the system BOM and use case, and empty `threats`, `controls` and `risks` sections. Do not hand-write the slice: the script cuts it the same way every time.

## Step 3: Identify threats

Work through the slice systematically. Do not stop at the obvious threats.

1. **Each flow** in `blueprints[0].flows`, and above all every flow whose source and destination are in different zones (it crosses a `boundary`). Apply STRIDE to the flow and to both endpoints.
2. **Each component and actor**, by type: `machine-learning-model` (prompt injection, model poisoning, output handling), agents and `framework` (excessive agency, tool misuse, goal hijacking: MAESTRO `agent-frameworks`), `data` (disclosure, poisoning: `data-operations`), marketplaces and plugins (supply chain: `agent-ecosystem`), MCP servers and gateways (authorization, confused deputy).
3. **Each boundary**: what changes in trust across it, and what an attacker on the less trusted side can reach.
4. **The use case's `exceptions`**, which often name threats already (for example "Prompt Injection Detected", "Malicious Plugin from Marketplace"). Every exception that describes an attack should map to a threat.
5. Cross-check against the OWASP Top 10 for LLM Applications ([OWASP_TOP_10_LLM.md](../../../../subgroups/use-cases-and-threat-models/OWASP_TOP_10_LLM.md)).

**Write each threat statement in the working group's format and perspective**:

- Structure: *Actor A does B to C, which results in D to E*: who, action, technical component, the reason, the resource.
- Perspective: put the actors **in the diagram** at the centre. Write *"Developer uses an unofficial marketplace and unknowingly installs a malicious version of the official plugin into the IDE. This results in code being sent to an external, attacker-controlled backend."*, not *"External attacker publishes a malicious plugin…"*.

Put the statement in both `threat.description` and `threatScenario.description`.

## Step 4: Encode each threat

For each threat, add these to the TM-BOM:

| Object | Section | Required | Fill in |
|---|---|---|---|
| `threat` | `threats.threats[]` | `refId`, `name` | `description` (the statement), `origin` (NIST 800-30 source type: `adversarial`, `accidental`, `structural`, `environmental`), `categories[]` (`{taxonomy, category}`: STRIDE, MAESTRO, LINDDUN or MITRE-ATTACK, with category values from the schema), `affects[]` (sliced refIds), `attackPatterns[]`, `weaknesses[]`, `killChainPhase`, `mitigations[]` (control refIds) |
| `threatScenario` | `threats.threatScenarios[]` | `refId`, `name`, `threats[]` | `actor` (a party refId), `motivation[]`, `intent`, `accessLevel`, `attackVector`, `likelihood.level` + `rationale`, `riskAttributes[]`, `affects[]`, `damageScenarios[]` |
| attacker `party` | `definitions.parties[]` | `roles` + one of `persona`/`organization`/`person` | `roles: [{ "role": "attacker" }]`, `persona.archetype` (`attacker`, `insider-threat`, `nation-state`, `organized-crime`, …). This belongs in the TM-BOM, not in the system BOM. |
| `attackPattern` | `threats.attackPatterns[]` | `refId`, `name` | `capecId` (integer), `description` |
| `weakness` | `definitions.weaknesses[]` | `name` or `identifiers` | `refId`, `kind: "flaw"`, `identifiers: [{ "scheme": "cwe", "value": "CWE-494" }]`. Threats reference them as `{ "ref": "weakness:..." }`. |
| `attackPath` (for multi-step threats) | `threats.attackPaths[]` | `refId`, `name`, `steps[]` | each step has a `description`, `source`/`destination` (sliced refIds), `boundaryCrossed`, `technique` (`{id, name, tactic}` from ATT&CK or ATLAS), `attackPattern`, `exploits`, `mitigations` |
| `trustBoundary` (annotation) | `threats.trustBoundaries[]` | `refId`, `boundary` | `trustLevel`, `threatsAtBoundary[]`, `controlsAtBoundary[]` |

**NIST SP 800-30 enrichment.** The 2.0 `threat` has no 800-30 fields beyond `origin`, so record the specific entries as properties, using the IDs from the reference files in `subgroups/use-cases-and-threat-models/reference_files/`:

```json
"properties": [
  { "name": "lfai:nist-800-30:threat-source", "value": "TS-ADV-01 Adversarial - Individual - Outsider" },
  { "name": "lfai:nist-800-30:threat-event", "value": "TE-20 Deliver/insert/install malicious capabilities - Insert tampered critical components into systems" },
  { "name": "lfai:nist-800-30:adverse-impact", "value": "AI-AST-06 HARM TO ASSETS - Loss of intellectual property" },
  { "name": "lfai:owasp-llm-top-10", "value": "LLM03:2025 Supply Chain" }
]
```

The `lfai:` prefix marks these as working-group properties. Never put them under `cdx:`, which is reserved for registered CycloneDX taxonomy names.

**CAPEC and CWE.** Follow [capec_prompt.txt](../../../../subgroups/use-cases-and-threat-models/prompts_for_threat_modelling/capec_prompt.txt): CAPEC describes attacker behaviour (`attackPatterns`), CWE describes the system weakness (`weaknesses`), and the two are never mixed. Prefer the most specific entry and never invent IDs. Check each ID against its source:

| Identifier | Check against |
|---|---|
| CAPEC | `reference_files/mitre_capec.csv` (in the repository) |
| NIST SP 800-30 | `reference_files/nist_800_30_*.csv` |
| CWE | not in the repository. Use the MITRE CWE list (https://cwe.mitre.org/) if you can fetch it; otherwise use only CWEs you are certain of, and mark each one as unverified in the report |
| MITRE ATT&CK / ATLAS techniques | not in the repository. Use https://attack.mitre.org/ or https://atlas.mitre.org/ if you can fetch them; otherwise mark each one as unverified in the report |

If you cannot confirm an ID, either leave it out, or keep it and list it as unverified; never present it as checked.

## Step 5: Map controls

Follow [control_prompt.txt](../../../../subgroups/use-cases-and-threat-models/prompts_for_threat_modelling/control_prompt.txt) and [csa_aicm_prompt.txt](../../../../subgroups/use-cases-and-threat-models/prompts_for_threat_modelling/csa_aicm_prompt.txt):

1. Declare each control catalogue once, as a `standard` in `definitions.standards[]`, with only the `requirements[]` you use: `{ refId, identifier, title }` (for example `req:nist-800-53:cm-14`, `CM-14`, `Signed Components`). Check identifiers and titles against `reference_files/NIST_SP-800-53_rev5_catalog_load.csv` and `reference_files/aicm_controls.csv`.
2. Write each control as a system-specific safeguard in `controls[]`, with `refId`, `name`, `description`, `category` (`preventive`, `detective`, `corrective`, …), `status` (`recommended` unless the source says it is in place), `appliesTo` (sliced refIds), and `satisfies` (the requirement refIds, both NIST and AICM).
3. Tier 1 (direct mitigations) are usually `preventive` and Tier 2 (supporting controls) are usually `detective`, `corrective` or `compensating`. To keep the tier explicitly, add `{ "name": "lfai:control-tier", "value": "1" }`.
4. Link threats to controls through `threat.mitigations`, and boundaries to controls through `trustBoundary.controlsAtBoundary`.

## Step 6: Risks (optional, recommended)

For each threat scenario, add a `damageScenario` (`refId`, `name`, `affects`, `impacts: [{ level, categories, riskAttributes }]`) and a `risk` (`refId`, `name`, `statement` in the form source, event, impact; `relatedThreats`, `relatedDamageScenarios`, `inherentRisk`, `responses: [{ refId, strategy, controls }]`, `status: "identified"`). Rate likelihood and impact only when there is evidence for it, and give a `rationale`.

## Step 7: Validate, link back, report

```
python .bob/skills/cyclonedx/scripts/validate_bom.py <tm-bom>.json --system <system>.json
```

This checks the schema (including formats such as `date-time`), that every local reference resolves, that every sliced element is identical to its system BOM counterpart (apart from the back-links the slicer adds and lists it trims to the slice), and that every BOM-Link fragment resolves in the system BOM. It cannot check SPDX licence IDs or the crypto and behaviour taxonomies offline. Fix every error. Remove `threats`, `controls` or `risks` arrays that you left empty.

If the user wants links in both directions, run `python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --link <tm-bom>.json` for each TM-BOM. It edits the system BOM in place, so ask first. Then validate the system BOM with `--linked <tm-bom>.json`.

Report, for each TM-BOM: the file, its serialNumber, the use case it covers, the number of threats per STRIDE and MAESTRO category, the elements and flows with **no** threat (coverage gaps), the controls with no threat mapped, the CAPEC, CWE and control IDs you could not confirm, and the validator result.

## Regenerating after the system BOM changes

When the system BOM changes, bump its `version`, then re-slice each existing TM-BOM in place:

```
python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --use-case usecase:<id> -o <tm-bom>.json --update
```

`--update` keeps the TM-BOM's `serialNumber`, bumps its `version`, and carries over its threats, controls, risks, weaknesses, standards and attacker parties. It reports flows that were added or removed, so you can review threats on removed flows; it refuses to write if a threat now references an element that is no longer in the slice. If the system BOM links back to the TM-BOM, rerun `--link` to refresh the version, then validate. A BOM-Link to an older version is reported as a warning, so you can find stale TM-BOMs.
