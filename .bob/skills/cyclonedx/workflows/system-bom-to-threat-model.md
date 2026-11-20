# Workflow: system BOM to threat-model BOMs

Generate a **threat model** from a CycloneDX 2.0 system BOM: **one threat-model BOM (TM-BOM) per use case**, each linked to the system BOM by BOM-Link. This follows the LF AI & Data Use Cases and Threat Modeling subgroup's method ([README](../../../../subgroups/use-cases-and-threat-models/README.md)): perspective-correct threat statements, NIST SP 800-30 enrichment, CAPEC and CWE mapping, and controls mapped to NIST SP 800-53 and CSA AICM.

The reference output is [examples/tm-bom.code-assistant-1b.json](../examples/tm-bom.code-assistant-1b.json) (with its threat table, [examples/tm-bom.code-assistant-1b.threats.md](../examples/tm-bom.code-assistant-1b.threats.md)), one fully worked threat for the Code Assistant Sub Use Case 1b, linked to [examples/system-bom.code-assistant.json](../examples/system-bom.code-assistant.json). It shows the **shape** of one threat end to end (scenario, attack path, controls, risk, catalogue citation, rationales), not the scale: a real TM-BOM covers every element and sweep item, so the validator's coverage and sweep warnings on this one-threat example are expected.

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
- Confirm with the user which use cases to model and which methodologies to apply. Default to STRIDE for every element and flow, plus MAESTRO categories for AI and agentic elements. Record them in `threats.methodologies` (the 2.0 enum is `STRIDE, LINDDUN, PASTA, MAESTRO, OWASP, TRIKE, VAST, ATFAA, attack-tree`). If you cannot ask, use the defaults and say so in the report.

## Step 2: Create one TM-BOM skeleton per use case

```
python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --use-case usecase:<id> -o <name>.tm-bom.<use-case-id>.json
```

The script refuses to overwrite an existing file; see "Regenerating" below to update one. This writes the system slice, the BOM-Links, metadata properties naming the system BOM and use case, and empty `threats`, `controls` and `risks` sections. Do not hand-write the slice: the script cuts it the same way every time.

## Step 3: Identify threats

Identify threats in three passes: a **structural** pass, a **catalogue sweep**, and a pass for what neither finds. This workflow deliberately names catalogues, not threats: do not start from a list of "usual" threats, because a list steers you toward its items and away from everything else.

**3a. Structural pass (STRIDE).** Apply all six STRIDE categories to:
- every flow in `blueprints[0].flows`, giving most attention to flows whose source and destination are in different zones (they cross a `boundary`);
- every component, actor and blueprint asset in the slice;
- every boundary: what changes in trust across it, and what someone on the less trusted side can reach.

Boundaries in the system BOM may be trust boundaries (`type: "trust"`) or only functional, process or deployment boundaries. Annotate a `trustBoundary` (Step 4) only for boundaries the system BOM types `trust`, or ones you have evidence are trust boundaries; give the evidence in its `description`. If the system BOM draws no trust boundary, do not invent trust levels: apply STRIDE to the crossings anyway, record the missing trust boundaries as an open question in the report, and leave `trustBoundaries` empty. A flow between zones crosses a boundary only at the outermost zones that differ, as the system-BOM workflow defines it.

**3b. Catalogue sweep.** Each element is classified by the tags the system BOM gives it (see [diagram-to-system-bom.md](diagram-to-system-bom.md), "Classify for the threat sweep"). [reference/threat-model-policy.json](../reference/threat-model-policy.json) maps each tag to the catalogues to use. Its `sweep` catalogues are swept **item by item**; its `consult` catalogues are too large for that, and you use them to classify the threats you find.

| Tag | Sweep, item by item | Consult |
|---|---|---|
| `web-app` | OWASP Top 10 (web applications) | CWE |
| `api` | OWASP API Security Top 10 | CWE |
| `ai-model`, `ai-data`, `ai-pipeline` | OWASP Top 10 for LLM Applications | MITRE ATLAS |
| `agent` | OWASP Top 10 for Agentic Applications | MITRE ATLAS |
| `tool-server` | OWASP MCP Top 10 (beta edition) | MITRE ATT&CK |

**One element, not two.** An agent appears as a component and as the actor it `realizes`. They are one element: sweep and annotate the component, and a threat or annotation on either counts for both.

**Lifecycle scope.** A use case may carry a property `lfai:lifecycle` of `training` or `inference` (set in the system BOM). The policy's `lifecycleScope` lists catalogue items that cannot apply in a stage, with the reason; they are not swept there and need no annotation. The coverage report lists them, so the scoping stays visible.

**Overlapping items.** Some items of two swept catalogues cover the same ground. Write one threat and cite both items on it; do not write two threats for the same thing.

The policy file is the source of truth if this table and it ever differ. The item lists, with pinned editions, are in [reference/catalogues/](../reference/catalogues/); read the CSV for each catalogue you sweep.

For **every element and every item** of each sweep catalogue that applies to it, record a decision:
- **It applies:** write a threat (Step 4) whose `affects` includes the element, and cite the item with a property `{ "name": "lfai:catalogue-item", "value": "<catalogue key>:<item id>" }`, for example `owasp-top10-web:A01:2025`. One threat may cite several items.
- **It does not apply:** add an annotation saying why. Its `subjects` are the element refIds it covers, and its `text` follows the format in the policy file: `not-applicable <catalogue key>:<item id>[, <catalogue key>:<item id>...]: <reason>`. Several items can share one annotation when one reason covers them. Give a real reason specific to the element, not "not relevant".

```json
"annotations": [
  {
    "subjects": ["component:local-ide"],
    "annotator": { "component": { "type": "application", "name": "cyclonedx skill" } },
    "timestamp": "2026-01-01T00:00:00Z",
    "text": "not-applicable owasp-top10-web:A07:2025: the IDE has no login of its own; the developer authenticates at the Authentication Service"
  }
]
```

If a tag ever has no sweep catalogue, rely on 3a and 3c for those elements, and list them in the report. If the system BOM gives an element no tag, the validator falls back to classifying it by component type and warns you; check the fallback is right, and say in the report which elements were classified that way.

**3c. Beyond the catalogues.** Catalogues miss what is specific to this system. Trace each use case end to end and ask what an attacker, an insider, a failing component or a careless user could do at each step that neither pass found. Include:
- what happens when a security component (guard, filter, authorization service) fails or times out;
- data that keeps its sensitivity, or loses its access controls, as it moves between components;
- the use case's `exceptions`, `preconditions` and blueprint `assumptions`: every one that describes something going wrong, or that might not hold, should lead to a threat or to a recorded reason why not. If the use case has none, say so in the report.

Record the review of every blueprint assumption and every use case in the slice as an annotation whose `subjects` include it and whose `text` is `reviewed <refId>: <outcome>`, where the outcome names the threats it led to or says why it led to none (for example `reviewed assumption:patient-data: led to threat:phi-channel-interception`). The validator warns about any assumption or use case without one.

Threats from 3c cite no catalogue item, which is expected.

**Threats shared with other use cases.** Each TM-BOM must stand on its own, so a threat on an element or flow that appears in several use cases is written in each TM-BOM where it applies. Write it once per TM-BOM, and mention in its `description` when the same threat is modelled in another use case's TM-BOM.

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
| `attackPath` (for multi-step threats) | `threats.attackPaths[]` | `refId`, `name`, `steps[]` | each step has a `description`, `source`/`destination` (sliced refIds), `boundaryCrossed`, `technique` (`{id, name, tactic}`, where `tactic` is a tactic **ID**: `TA0001` for ATT&CK or `AML.TA0005` for ATLAS; from ATT&CK or ATLAS), `attackPattern`, `exploits`, `mitigations` |
| `trustBoundary` (annotation) | `threats.trustBoundaries[]` | `refId`, `boundary` | `trustLevel`, `threatsAtBoundary[]`, `controlsAtBoundary[]` |

**NIST SP 800-30 enrichment.** The 2.0 `threat` has no 800-30 fields beyond `origin`, so record the specific entries as properties, using the IDs from the reference files in `subgroups/use-cases-and-threat-models/reference_files/`:

```json
"properties": [
  { "name": "lfai:nist-800-30:threat-source", "value": "TS-ADV-01 Adversarial - Individual - Outsider" },
  { "name": "lfai:nist-800-30:threat-event", "value": "TE-20 Deliver/insert/install malicious capabilities - Insert tampered critical components into systems" },
  { "name": "lfai:nist-800-30:adverse-impact", "value": "AI-AST-06 HARM TO ASSETS - Loss of intellectual property" }
]
```

**Properties.** The `lfai:` prefix marks working-group properties. Use only the names listed in [reference/threat-model-policy.json](../reference/threat-model-policy.json) under `properties`, with the value formats given there. The validator rejects any other `lfai:` name. If you need something the list lacks, record it in the report as a proposal rather than inventing a name. Never put these under `cdx:`, which is reserved for registered CycloneDX taxonomy names.

**`threat.source`.** Say where the threat came from in this model: `"structural pass (STRIDE)"`, `"catalogue sweep"`, or `"use case and assumption review"`.

**Threats outside STRIDE.** Some threats fit no STRIDE category, for example an AI model's misinformation. Give them their MAESTRO category, and say in the report which threats have no STRIDE category.

**Scenario actors.** `threatScenario.actor` is the party who causes the harm. For an adversary, declare an attacker party in `definitions.parties`. For a mistake by someone in the diagram, reference that actor's party. For a failure with no one behind it (`origin: "structural"` or `"environmental"`), leave `actor` out. The threat statement still centres on the diagram's actors, as described in Step 3.

**CAPEC and CWE.** Follow [capec_prompt.txt](../../../../subgroups/use-cases-and-threat-models/prompts_for_threat_modelling/capec_prompt.txt): CAPEC describes attacker behaviour (`attackPatterns`), CWE describes the system weakness (`weaknesses`), and the two are never mixed. Prefer the most specific entry and never invent IDs. Check each ID against its source:

| Identifier | Check against |
|---|---|
| CAPEC | `subgroups/use-cases-and-threat-models/reference_files/mitre_capec.csv` |
| NIST SP 800-30 | `subgroups/use-cases-and-threat-models/reference_files/nist_800_30_*.csv` |
| CWE | `.bob/skills/cyclonedx/reference/catalogues/cwe.csv` (deprecated entries are marked; do not use them) |
| MITRE ATT&CK techniques | `.bob/skills/cyclonedx/reference/catalogues/mitre-attack-enterprise.csv` |
| MITRE ATLAS techniques | `.bob/skills/cyclonedx/reference/catalogues/mitre-atlas.csv` |

Search these files with grep rather than reading them whole. The validator checks every one of these IDs, and an ID that is not in its file is an error. CAPEC has no pattern for most AI-specific threats (prompt injection, data and model poisoning, hallucination). For those, leave `attackPatterns` empty and give ATLAS techniques instead; that is expected, not a gap. Give each CAPEC and CWE its one-line justification, as `capec_prompt.txt` asks, in a `lfai:capec-rationale` or `lfai:cwe-rationale` property on the threat. Give ATT&CK and ATLAS technique IDs on attack path steps (`technique.id`), or as `lfai:technique` properties on the threat. ATLAS tactics have no place in `threat.categories`, which only accepts MITRE-ATTACK tactics, so record ATLAS by technique.

## Step 5: Map controls

Follow [control_prompt.txt](../../../../subgroups/use-cases-and-threat-models/prompts_for_threat_modelling/control_prompt.txt) and [csa_aicm_prompt.txt](../../../../subgroups/use-cases-and-threat-models/prompts_for_threat_modelling/csa_aicm_prompt.txt):

1. Declare each control catalogue once, as a `standard` in `definitions.standards[]`, with only the `requirements[]` you use: `{ refId, identifier, title }` (for example `req:nist-800-53:cm-14`, `CM-14`, `Signed Components`). Check identifiers and titles against `reference_files/NIST_SP-800-53_rev5_catalog_load.csv` and `reference_files/aicm_controls.csv`; the validator checks them too. Those files have two quirks: some NIST titles contain a garbled character where a dash should be, and some AICM titles contain line breaks. Write the title with a plain hyphen and on one line. AICM IDs have the form `AIS-08`, with no `.X` suffix, whatever `csa_aicm_prompt.txt` says.
2. Write each control as a system-specific safeguard in `controls[]`, with `refId`, `name`, `description`, `category` (`preventive`, `detective`, `corrective`, …), `status` (`recommended` unless the source says it is in place), `appliesTo` (sliced refIds), and `satisfies` (the requirement refIds, both NIST and AICM).
3. Tier 1 (direct mitigations) are usually `preventive` and Tier 2 (supporting controls) are usually `detective`, `corrective` or `compensating`. To keep the tier explicitly, add `{ "name": "lfai:control-tier", "value": "1" }`.
4. Link threats to controls through `threat.mitigations`, and boundaries to controls through `trustBoundary.controlsAtBoundary`.
5. `control_prompt.txt` asks which CAPEC and CWE each control mitigates. Record them on the control as properties `{ "name": "lfai:mitigates", "value": "CAPEC-185" }` (one per ID).
6. `csa_aicm_prompt.txt` treats each AICM control as a child of a NIST SP 800-53 control. `satisfies` is a flat list, so record each pairing on the control as `{ "name": "lfai:aicm-parent", "value": "req:csa-aicm:ais-13 < req:nist-800-53:sc-7" }`.

## Step 6: Risks (optional, recommended)

For each threat scenario, add a `damageScenario` (`refId`, `name`, `affects`, `impacts: [{ level, categories, riskAttributes }]`) and a `risk` (`refId`, `name`, `statement` in the form source, event, impact; `relatedThreats`, `relatedDamageScenarios`, `inherentRisk`, `responses: [{ refId, strategy, controls }]`, `status: "identified"`). Several scenarios with the same consequence can share one damage scenario, and several closely related scenarios can share one risk (list them all in `relatedThreats`); one risk per scenario is not required.

At design stage, ratings are judgements, not measurements. Give an `inherentRisk` rating only with a `rationale` that says what it rests on (for example "the flow crosses into a third-party zone with no stated authentication"). If you have no basis for a rating, leave `inherentRisk` out, and say in the report which risks are unrated.

## Step 7: Validate, link back, report

Validate first, then write the threat table (Step 8): the table is only as correct as the TM-BOM it is written from.

```
python .bob/skills/cyclonedx/scripts/validate_bom.py <tm-bom>.json --system <system>.json --report-json <tm-bom>.coverage.json
```

It checks, as **errors**:
- the schema (including formats such as `date-time`), local references, BOM-Links, and that every sliced element is identical to its system BOM counterpart (apart from the back-links the slicer adds and the lists it trims or removes);
- that every CAPEC, CWE, ATT&CK, ATLAS, NIST 800-53, AICM and NIST 800-30 ID exists in its reference file, including IDs in `lfai:mitigates` and the rationale properties, and that NIST 800-30 IDs are of the right kind;
- that catalogue citations and not-applicable annotations name a real catalogue item;
- that every `lfai:` property name is in the policy file, with a valid value where the policy defines one (`lfai:control-tier`, `lfai:lifecycle`, `lfai:aicm-parent`);
- that not-applicable annotations follow the format, give a real reason, and do not contradict a threat that cites the same item;
- that `technique.tactic` is a tactic ID, and that review annotations follow the format.

It checks, as **warnings** (errors with `--strict`):
- a threat-model BOM with no threats;
- coverage: every component, actor, flow, boundary and asset is in some threat's `affects` or has a not-applicable annotation; every control mitigates a threat; every threat has mitigations or an accepted risk; `methodologies` is not empty;
- the catalogue sweep: every item of every sweep catalogue has a decision for every element it applies to;
- every assumption and use case has a review annotation;
- citations of a catalogue that is not swept for any element the threat affects, and NIST 800-30 text that does not match its ID;
- elements whose tag has no chosen catalogue, and elements classified by component type because they have no tag.

It cannot check SPDX licence IDs or the crypto and behaviour taxonomies offline, and it cannot judge whether a not-applicable reason is sound; that needs human review. Fix every error, and every warning you can. Remove `threats`, `controls` or `risks` arrays that you left empty.

If the user wants links in both directions, run `python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --link <tm-bom>.json` for each TM-BOM. It edits the system BOM in place, so ask first. Then validate the system BOM with `--linked <tm-bom>.json`.

Report, for each TM-BOM, using the validator's output and `--report-json` file rather than counting by hand:
- the file, its serialNumber, and the use case it covers;
- the number of threats per STRIDE and MAESTRO category, and the threats with no STRIDE category;
- coverage: the elements and flows with no threat, and the controls with no threat;
- the catalogue sweep: items decided per element and catalogue, how many items were marked not applicable, elements with no chosen catalogue, and elements classified by component type;
- risks left unrated, and any defaults you chose because you could not ask the user;
- the validator result, with any warnings you could not resolve.

## Step 8: Write the threat table

Once a TM-BOM validates with no errors, write its threat table, a Markdown page for people to read and review:

```
python .bob/skills/cyclonedx/scripts/tm_to_markdown.py <tm-bom>.json
```

This writes `<tm-bom>.threats.md` next to the TM-BOM (the `.json` suffix replaced by `.threats.md`; use `-o` to choose another path). The page has three tables:

- **Threats:** one row per threat, in the shape of the working group's [Code Assistant threat table](../../../../subgroups/use-cases-and-threat-models/use_cases/code_assistant/threats/code_assistant_threats.md): the threat statement, STRIDE and MAESTRO categories, where it is located (affected elements by zone), the actor, the NIST SP 800-30 impact, source and event, catalogue items, MITRE ATT&CK and ATLAS techniques, whether it is AI specific, CAPEC and CWE with their rationales, the mitigating controls, and the risk rating.
- **Controls:** one row per control, with its category, tier, status, the elements it applies to, the NIST SP 800-53 and CSA AICM requirements it satisfies, and the threats it mitigates.
- **Catalogue items decided not applicable:** every not-applicable annotation, with its elements and reason, so reviewers can check the reasons the validator cannot judge.

The page is generated from the TM-BOM and says so in its first line. Never edit it by hand: change the TM-BOM and run the script again. The script replaces an existing file only if it wrote it. Give the user the path of each page in the report.

## Regenerating after the system BOM changes

When the system BOM changes, bump its `version`, then re-slice each existing TM-BOM in place:

```
python .bob/skills/cyclonedx/scripts/slice_use_case.py <system>.json --use-case usecase:<id> -o <tm-bom>.json --update
```

`--update` keeps the TM-BOM's `serialNumber`, bumps its `version`, and carries over its threats, controls, risks, weaknesses, standards and attacker parties. It reports flows that were added or removed, so you can review threats on removed flows; it refuses to write if a threat now references an element that is no longer in the slice. If the system BOM links back to the TM-BOM, rerun `--link` to refresh the version, then validate. A BOM-Link to an older version is reported as a warning, so you can find stale TM-BOMs. Then rerun `tm_to_markdown.py` (Step 8) so the threat table matches.
