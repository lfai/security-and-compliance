"""Consistency rules for threat-model BOMs, used by tm_checks.py.

Each rule reports through the shared Report object. They check what the
coverage counts cannot: that decisions do not contradict each other, that
citations match the sweep, that reasons are real, and that free-text values
match the identifiers they carry. Standard library only.
"""

import re


def element_groups(doc):
    """{refId: canonical refId}: a component and the actor it realizes are one element.

    The canonical id is the component's. Elements not in any pair map to themselves.
    """
    bp = (doc.get("blueprints") or [{}])[0]
    canon = {}
    for rel in bp.get("relationships") or []:
        for actor in rel.get("realizes") or []:
            canon[actor] = rel.get("ref")
    for actor in bp.get("actors") or []:
        party = actor.get("party") or {}
        sysref = (party.get("system") or {}).get("ref") if isinstance(party, dict) else None
        if sysref:
            canon.setdefault(actor["refId"], sysref)
    for asset in bp.get("assets") or []:
        if asset.get("componentRef") and asset.get("refId"):
            canon.setdefault(asset["refId"], asset["componentRef"])
    return canon


def check_reasons(na_records, policy, report):
    """Not-applicable reasons must say something specific about the element."""
    rules = (policy.get("notApplicable") or {})
    min_words = int(rules.get("minReasonWords", 6))
    banned = [b.lower() for b in rules.get("bannedReasons", [])]
    for index, key, item, reason in na_records:
        text = reason.strip().lower().rstrip(".")
        if text in banned or len(text.split()) < min_words:
            report.error(f"annotations[{index}]: the reason for {key}:{item} is too thin ('{reason.strip()}'); "
                         f"say why it does not apply to this element, in at least {min_words} words")


def check_contradictions(na_set, cited, canon, report):
    """An item cannot be both cited by a threat and marked not applicable for the same element."""
    for (subject, key, item) in sorted(na_set):
        for target in {subject, canon.get(subject, subject)}:
            if f"{key}:{item}" in cited.get(target, set()):
                report.error(f"{subject}: {key}:{item} is marked not applicable but a threat that affects it "
                             "cites it; remove one of the two")
                break


def check_citation_scope(threats, swept_by_element, canon, report):
    """A cited sweep item must belong to a catalogue swept for at least one element the threat affects."""
    for t in threats:
        affected = set(t.get("affects") or [])
        affected |= {canon.get(a, a) for a in affected}
        allowed = set()
        for a in affected:
            allowed |= swept_by_element.get(a, set())
        for name, value in [(p.get("name"), p.get("value", "")) for p in t.get("properties") or []]:
            if name != "lfai:catalogue-item":
                continue
            key = value.split(":", 1)[0]
            if allowed and key not in allowed:
                report.warn(f"threat {t.get('refId')}: cites {value}, but {key} is not swept for any element "
                            f"it affects (swept: {', '.join(sorted(allowed))}); check the element's tags")


def check_nist30_text(holders, nist30, norm, report):
    """A NIST 800-30 property's text must match the entry its ID names."""
    for holder in holders:
        for p in holder.get("properties") or []:
            name, value = p.get("name", ""), p.get("value", "") or ""
            if not name.startswith("lfai:nist-800-30:"):
                continue
            ident, _, text = value.partition(" ")
            expected = nist30.get(ident)
            if expected and text and norm(expected) not in norm(text):
                report.warn(f"property {name}: '{ident}' is '{expected}' in the reference file, "
                            f"but the value says '{text}'")


TACTIC_FORMATS = (re.compile(r"^TA\d{4}$"), re.compile(r"^AML\.TA\d{4}$"))


def check_tactics(doc, attack_tactics, atlas_tactics, report):
    """technique.tactic must be a tactic ID (TA0001 or AML.TA0005) from ATT&CK or ATLAS."""
    known = set(attack_tactics) | set(atlas_tactics)
    places = []
    for pi, path in enumerate((doc.get("threats") or {}).get("attackPaths") or []):
        for si, step in enumerate(path.get("steps") or []):
            places.append((f"threats.attackPaths[{pi}].steps[{si}].technique", step.get("technique") or {}))
    for ai, ap in enumerate((doc.get("threats") or {}).get("attackPatterns") or []):
        for ti, tech in enumerate(ap.get("techniques") or []):
            places.append((f"threats.attackPatterns[{ai}].techniques[{ti}]", tech))
    for where, tech in places:
        tactic = tech.get("tactic")
        if not tactic:
            continue
        if not any(f.match(tactic) for f in TACTIC_FORMATS):
            report.error(f"{where}.tactic: '{tactic}' must be a tactic ID such as TA0001 (ATT&CK) or "
                         "AML.TA0005 (ATLAS), not a name")
        elif known and tactic not in known:
            report.error(f"{where}.tactic: {tactic} is not an ATT&CK or ATLAS tactic")


def reviewed_records(doc, policy, report):
    """Parse 'reviewed <refId>: <outcome>' annotations; return the set of reviewed refIds."""
    prefix = ((policy.get("review") or {}).get("annotationPrefix") or "reviewed") + " "
    found = set()
    for i, a in enumerate(doc.get("annotations") or []):
        text = a.get("text") or ""
        if not text.startswith(prefix):
            continue
        m = re.match(re.escape(prefix) + r"(\S+?):\s+(\S.*)", text)
        if not m:
            report.error(f"annotations[{i}]: review text must be '{prefix}<refId>: <outcome>', got '{text[:80]}'")
            continue
        found.add(m.group(1))
    return found


def check_reviews(doc, policy, reviewed, warn):
    """Every assumption and use case in the slice is reviewed (step 3c)."""
    bp = (doc.get("blueprints") or [{}])[0]
    todo = [a.get("refId") for a in bp.get("assumptions") or [] if a.get("refId")]
    todo += [u.get("refId") for u in (doc.get("definitions") or {}).get("useCases") or [] if u.get("refId")]
    missing = [r for r in todo if r not in reviewed]
    for r in missing:
        warn(f"review: {r} has no 'reviewed {r}: <outcome>' annotation (workflow step 3c)")
    return missing
