"""Threat-model checks used by validate_bom.py.

These go beyond structure: they check that identifiers are real, that
property names follow the policy, that the threat model covers its slice,
and that every catalogue item mapped to an element type has a decision.

Inputs live in the skill and the repository:
  reference/threat-model-policy.json   element type -> catalogues, allowed lfai: properties
  reference/catalogues/*.csv           ID + title per catalogue (fetch_catalogues.py)
  subgroups/use-cases-and-threat-models/reference_files/*.csv   CAPEC, NIST 800-53, AICM, NIST 800-30

Standard library only.
"""

import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tm_rules  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(SKILL, "..", "..", ".."))
POLICY = os.path.join(SKILL, "reference", "threat-model-policy.json")
CATALOGUE_DIR = os.path.join(SKILL, "reference", "catalogues")
WG_REFS = os.path.join(REPO, "subgroups", "use-cases-and-threat-models", "reference_files")


def _norm(text):
    """Compare titles loosely: the source CSVs have mojibake dashes and embedded newlines."""
    text = (text or "").replace("�", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _read_csv(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


class References:
    """Identifier lookups, loaded once. Missing files simply leave a lookup empty."""

    def __init__(self):
        self.policy = {}
        if os.path.exists(POLICY):
            with open(POLICY, encoding="utf-8") as f:
                self.policy = json.load(f)
        self.catalogues = {}   # key -> {id: title}, current items only
        self.deprecated = {}   # key -> {id: title}
        index = os.path.join(CATALOGUE_DIR, "catalogues.json")
        self.catalogue_meta = {}
        if os.path.exists(index):
            with open(index, encoding="utf-8") as f:
                self.catalogue_meta = json.load(f).get("catalogues", {})
            for key, meta in self.catalogue_meta.items():
                path = os.path.join(CATALOGUE_DIR, meta["file"])
                if os.path.exists(path):
                    rows = _read_csv(path)
                    self.catalogues[key] = {r["id"]: r["title"] for r in rows if r.get("group") != "deprecated"}
                    self.deprecated[key] = {r["id"]: r["title"] for r in rows if r.get("group") == "deprecated"}
        self.capec = self._wg("mitre_capec.csv", lambda r: (r["id"], r["name"]))
        self.nist53 = self._wg("NIST_SP-800-53_rev5_catalog_load.csv", lambda r: (r["identifier"], r["name"]))
        self.aicm = self._wg("aicm_controls.csv", lambda r: (r["control_id"].strip(), r["control_title"]))
        self.nist30 = {}
        for name in ("nist_800_30_threat_sources.csv", "nist_800_30_threat_events.csv",
                     "nist_800_30_adverse_impacts.csv"):
            self.nist30.update(self._wg(name, lambda r: (r["id"], r["subcategory"])))

    @staticmethod
    def _wg(name, pick):
        path = os.path.join(WG_REFS, name)
        if not os.path.exists(path):
            return {}
        out = {}
        for r in _read_csv(path):
            try:
                k, v = pick(r)
            except (KeyError, AttributeError):
                continue
            if k:
                out[k] = v
        return out


def _threat_items(doc):
    t = doc.get("threats") or {}
    return t.get("threats") or [], t.get("threatScenarios") or [], t.get("attackPaths") or []


def _props(obj):
    return [(p.get("name", ""), p.get("value", "")) for p in obj.get("properties") or [] if isinstance(p, dict)]


def _all_property_holders(inst):
    if isinstance(inst, dict):
        if isinstance(inst.get("properties"), list):
            yield inst
        for v in inst.values():
            yield from _all_property_holders(v)
    elif isinstance(inst, list):
        for v in inst:
            yield from _all_property_holders(v)


# ----------------------------------------------------------------- checks ---

def check_ids(doc, refs, report):
    """CAPEC, CWE, ATT&CK/ATLAS, NIST 800-53, AICM and NIST 800-30 identifiers must exist."""
    threats = doc.get("threats") or {}
    for i, ap in enumerate(threats.get("attackPatterns") or []):
        cid = ap.get("capecId")
        if cid is not None and refs.capec and str(cid) not in refs.capec:
            report.error(f"threats.attackPatterns[{i}]: CAPEC-{cid} is not in reference_files/mitre_capec.csv")
        elif cid is not None and refs.capec and ap.get("name") and _norm(ap["name"]) != _norm(refs.capec[str(cid)]):
            report.warn(f"threats.attackPatterns[{i}]: CAPEC-{cid} is named '{ap['name']}' here but "
                        f"'{refs.capec[str(cid)]}' in the reference file")

    cwe, cwe_old = refs.catalogues.get("cwe", {}), refs.deprecated.get("cwe", {})
    for w in (doc.get("definitions") or {}).get("weaknesses") or []:
        for ident in w.get("identifiers") or []:
            value = ident.get("value")
            if ident.get("scheme") != "cwe" or not cwe or value in cwe:
                continue
            if value in cwe_old:
                report.error(f"weakness '{w.get('refId')}': {value} is deprecated in CWE "
                             f"('{cwe_old[value]}'); use the CWE that replaces it")
            else:
                report.error(f"weakness '{w.get('refId')}': {value} is not in the CWE catalogue")

    techniques = {**refs.catalogues.get("mitre-attack-enterprise", {}), **refs.catalogues.get("mitre-atlas", {})}

    def check_technique(where, tid):
        if techniques and tid and tid not in techniques:
            report.error(f"{where}: technique {tid} is not in MITRE ATT&CK Enterprise or ATLAS")

    _, _, paths = _threat_items(doc)
    for pi, path in enumerate(paths):
        for si, step in enumerate(path.get("steps") or []):
            check_technique(f"threats.attackPaths[{pi}].steps[{si}]", (step.get("technique") or {}).get("id"))
    for ap in threats.get("attackPatterns") or []:
        for t in ap.get("techniques") or []:
            check_technique(f"attack pattern '{ap.get('refId')}'", t.get("id"))

    for s in (doc.get("definitions") or {}).get("standards") or []:
        name = (s.get("name") or "") + " " + (s.get("refId") or "")
        table, label = (refs.nist53, "NIST SP 800-53") if "800-53" in name else \
                       (refs.aicm, "CSA AICM") if re.search(r"aicm|ai controls matrix", name, re.I) else (None, None)
        if not table:
            continue
        for r in s.get("requirements") or []:
            ident = r.get("identifier")
            if ident not in table:
                report.error(f"standard '{s.get('refId')}': {label} {ident} is not in the reference file")
            elif r.get("title") and _norm(r["title"]) != _norm(table[ident]):
                report.warn(f"standard '{s.get('refId')}': {ident} is titled '{r['title']}' here but "
                            f"'{' '.join(table[ident].split())}' in the reference file")

    for holder in _all_property_holders(doc):
        for name, value in _props(holder):
            if name.startswith("lfai:nist-800-30:") and refs.nist30:
                ident = (value or "").split(" ", 1)[0]
                if ident not in refs.nist30:
                    report.error(f"property {name}: '{ident}' is not a NIST SP 800-30 id in reference_files")
            elif name == "lfai:technique":
                check_technique(f"property {name}", value)
            elif name == "lfai:catalogue-item":
                key, _, item = (value or "").partition(":")
                if key not in refs.catalogues:
                    report.error(f"property {name}: unknown catalogue '{key}'")
                elif item not in refs.catalogues[key]:
                    report.error(f"property {name}: '{item}' is not an item of {key}")

    tm_rules.check_nist30_text(_all_property_holders(doc), refs.nist30, _norm, report)

    def tactic_ids(key):
        path = os.path.join(CATALOGUE_DIR, (refs.catalogue_meta.get(key) or {}).get("file", ""))
        return [r["id"] for r in _read_csv(path) if r.get("group") == "tactic"] if os.path.isfile(path) else []
    tm_rules.check_tactics(doc, tactic_ids("mitre-attack-enterprise"), tactic_ids("mitre-atlas"), report)


def check_properties(doc, refs, report):
    """Only the lfai: names in the policy are allowed, so runs do not invent their own."""
    allowed = set((refs.policy.get("properties") or {}).keys())
    if not allowed:
        return
    seen = set()
    for holder in _all_property_holders(doc):
        for name, _ in _props(holder):
            if name.startswith("lfai:") and name not in allowed and name not in seen:
                seen.add(name)
                report.error(f"property '{name}' is not in reference/threat-model-policy.json; use one of: "
                             + ", ".join(sorted(allowed)))


def _not_applicable(doc, refs):
    """Parse not-applicable annotations.

    Text format: 'not-applicable <key>:<item>[, <key>:<item>...]: <reason>'.
    Returns (set of (subject, key, item), list of (index, key, item, reason), malformed list).
    """
    prefix = ((refs.policy.get("notApplicable") or {}).get("annotationPrefix") or "not-applicable") + " "
    found, records, bad = set(), [], []
    key_re = re.compile(r"[a-z0-9-]+")
    for i, a in enumerate(doc.get("annotations") or []):
        text = a.get("text") or ""
        if not text.startswith(prefix):
            continue
        # Item IDs contain ':' but no spaces, so the first ': ' ends the item list.
        header, sep, reason = text[len(prefix):].partition(": ")
        refs_in = [r.strip() for r in header.split(",")]
        parsed = [r.partition(":") for r in refs_in]
        if not sep or not reason.strip() or not all(
                key_re.fullmatch(k) and item and " " not in item for k, _, item in parsed):
            bad.append((i, text))
            continue
        for key, _, item in parsed:
            records.append((i, key, item, reason))
            for subject in a.get("subjects") or []:
                found.add((subject, key, item))
    return found, records, bad


def classify(doc, policy):
    """{element refId: (set of classification tags, how they were found)} for components and assets.

    An agent actor is the same element as the component that realizes it, so it is
    not swept separately; an agent actor with no realizing component is swept as an agent.
    """
    cls = policy.get("classification") or {}
    vocab = set((cls.get("tags") or {}).keys())
    fallback = cls.get("fallbackByType") or {}
    bp = (doc.get("blueprints") or [{}])[0]
    canon = tm_rules.element_groups(doc)
    out = {}
    for item in ((doc.get("definitions") or {}).get("components") or []) + (bp.get("assets") or []):
        if "refId" not in item:
            continue
        tags = {t for t in item.get("tags") or [] if t in vocab}
        if tags:
            out[item["refId"]] = (tags, "tags")
        elif item.get("type") in fallback:
            out[item["refId"]] = (set(fallback[item["type"]]), "type")
    for actor in bp.get("actors") or []:
        party = actor.get("party") or {}
        is_agent = isinstance(party, dict) and (party.get("system") or {}).get("kind") in ("agent", "bot", "automation")
        if is_agent and canon.get(actor["refId"]) not in out:
            out.setdefault(actor["refId"], ({"agent"}, "actor"))
    return out


def _lifecycle(doc):
    """The use case's lifecycle stage, from the slice's use case (`lfai:lifecycle` property), or None."""
    for uc in (doc.get("definitions") or {}).get("useCases") or []:
        for name, value in _props(uc):
            if name == "lfai:lifecycle":
                return value
    return None


def _sweep_targets(doc, policy):
    """[(element refId, sweep rule)] for every element each sweep applies to."""
    rules = {r["tag"]: r for r in policy.get("sweeps") or []}
    out = []
    for rid, (tags, _) in classify(doc, policy).items():
        for tag in sorted(tags):
            if tag in rules:
                out.append((rid, rules[tag]))
    return out


def _items_for(key, items, lifecycle, policy):
    """Catalogue items to sweep for this lifecycle stage, and those skipped by the policy."""
    skip = set(((policy.get("lifecycleScope") or {}).get(key) or {}).get(lifecycle or "", []))
    return [i for i in items if i not in skip], sorted(skip & set(items))


def check_coverage(doc, refs, report, strict=False):
    """Every sliced element has a threat or a not-applicable record; every control mitigates something."""
    warn = report.error if strict else report.warn
    threats, scenarios, _ = _threat_items(doc)
    if not threats:
        return None  # not a threat model
    bp = (doc.get("blueprints") or [{}])[0]
    canon = tm_rules.element_groups(doc)
    na, na_records, bad = _not_applicable(doc, refs)
    fmt = (refs.policy.get("notApplicable") or {}).get("format", "not-applicable <key>:<id>: <reason>")
    for i, text in bad:
        report.error(f"annotations[{i}]: not-applicable text must be '{fmt}', got '{text[:80]}'")
    tm_rules.check_reasons(na_records, refs.policy, report)
    reviewed = tm_rules.reviewed_records(doc, refs.policy, report)

    affected = set()
    for t in threats + scenarios:
        affected.update(t.get("affects") or [])
    for p in (doc.get("threats") or {}).get("attackPaths") or []:
        for s in p.get("steps") or []:
            affected.update(x for x in (s.get("source"), s.get("destination"), s.get("boundaryCrossed")) if x)
    # A component and the actor it realizes are one element: covering either covers both.
    covered = affected | {canon[a] for a in affected if a in canon} | {a for a, c in canon.items() if c in affected}
    na_subjects = {s for s, _, _ in na}
    na_subjects |= {canon[s] for s in na_subjects if s in canon} | {a for a, c in canon.items() if c in na_subjects}
    elements = [("component", c["refId"]) for c in (doc.get("definitions") or {}).get("components") or []]
    for key, label in (("actors", "actor"), ("flows", "flow"), ("boundaries", "boundary"), ("assets", "asset")):
        elements += [(label, x["refId"]) for x in bp.get(key) or [] if "refId" in x]
    uncovered = [f"{kind} {rid}" for kind, rid in elements if rid not in covered and rid not in na_subjects]
    for item in uncovered:
        warn(f"coverage: {item} is not in any threat's affects and has no not-applicable annotation")

    controls = {c.get("refId") for c in doc.get("controls") or []}
    mitigating = set()
    for t in threats:
        mitigating.update(t.get("mitigations") or [])
    for p in (doc.get("threats") or {}).get("attackPaths") or []:
        for s in p.get("steps") or []:
            mitigating.update(s.get("mitigations") or [])
    for tb in (doc.get("threats") or {}).get("trustBoundaries") or []:
        mitigating.update(tb.get("controlsAtBoundary") or [])
    for r in (doc.get("risks") or {}).get("risks") or []:
        for resp in r.get("responses") or []:
            mitigating.update(resp.get("controls") or [])
    for c in sorted(controls - mitigating - {None}):
        warn(f"coverage: control {c} mitigates no threat")
    accepted = set()
    for r in (doc.get("risks") or {}).get("risks") or []:
        if any(resp.get("strategy") == "accept" for resp in r.get("responses") or []):
            accepted.update(r.get("relatedThreats") or [])
    for t in threats:
        if not t.get("mitigations") and t.get("refId") not in accepted:
            warn(f"coverage: threat {t.get('refId')} has no mitigations and no accepted risk")
        if not t.get("affects"):
            warn(f"coverage: threat {t.get('refId')} affects nothing")
    if not (doc.get("threats") or {}).get("methodologies"):
        warn("coverage: threats.methodologies is empty; record the methodologies applied")
    unreviewed = tm_rules.check_reviews(doc, refs.policy, reviewed, warn)

    # Catalogue sweep completeness, with a component and its actor counted as one element.
    cited = {}
    for t in threats:
        for name, value in _props(t):
            if name == "lfai:catalogue-item":
                for subject in t.get("affects") or []:
                    for target in {subject, canon.get(subject, subject)}:
                        cited.setdefault(target, set()).add(value)
    na_canon = {(canon.get(s, s), k, i) for s, k, i in na} | na
    tm_rules.check_contradictions(na, cited, canon, report)

    lifecycle = _lifecycle(doc)
    sweep_rows, pending, done, swept_by_element, scoped_out = [], set(), set(), {}, {}
    for rid, rule in _sweep_targets(doc, refs.policy):
        if rule.get("pending") and not rule.get("sweep"):
            pending.add((rule["tag"], rid))
        for key in rule.get("sweep") or []:
            swept_by_element.setdefault(rid, set()).add(key)
            if (rid, key) in done:  # two tags can share a catalogue
                continue
            done.add((rid, key))
            items = refs.catalogues.get(key)
            if items is None:
                warn(f"sweep: catalogue '{key}' has no reference file; run scripts/fetch_catalogues.py")
                continue
            in_scope, skipped = _items_for(key, items, lifecycle, refs.policy)
            if skipped:
                scoped_out[key] = skipped
            missing = [i for i in in_scope if f"{key}:{i}" not in cited.get(rid, set())
                       and (rid, key, i) not in na_canon]
            sweep_rows.append((rid, key, len(in_scope), len(in_scope) - len(missing)))
            if missing:
                warn(f"sweep: {rid} ({key}) has no decision for {len(missing)} of {len(in_scope)} items: "
                     + ", ".join(missing))
    tm_rules.check_citation_scope(threats, swept_by_element, canon, report)
    for tag, rid in sorted(pending):
        report.warn(f"sweep: no catalogue chosen yet for '{tag}' elements ({rid}); see threat-model-policy.json")
    by_type = sorted(rid for rid, (_, how) in classify(doc, refs.policy).items() if how == "type")
    if by_type:
        report.warn("sweep: classified by component type because the system BOM gives no classification tag "
                    f"(check these are right, and tag them in the system BOM): {', '.join(by_type)}")

    return {
        "lifecycle": lifecycle,
        "elements": len(elements), "uncovered": uncovered,
        "controls": len(controls), "unmappedControls": sorted(controls - mitigating - {None}),
        "threats": len(threats), "unreviewed": unreviewed,
        "sweep": [{"element": r, "catalogue": k, "items": n, "decided": d} for r, k, n, d in sweep_rows],
        "outOfScopeForLifecycle": scoped_out,
        "pendingCatalogues": sorted(f"{e}:{r}" for e, r in pending),
    }
