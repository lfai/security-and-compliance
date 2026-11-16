#!/usr/bin/env python3
"""Create a threat-model BOM (TM-BOM) skeleton for one use case of a system BOM.

A CycloneDX 2.0 threat model references assets, flows and boundaries by
`refId`, and those references must resolve inside the same document. A TM-BOM
therefore carries a *system slice*: copies of the system BOM elements that the
use case exercises, under the same `refId`s, plus BOM-Links back to the system
BOM. This tool builds that slice deterministically so every TM-BOM is cut the
same way.

Usage:
  slice_use_case.py SYSTEM.json --list
      List the use cases in the system BOM and the flows each one traverses.
  slice_use_case.py SYSTEM.json --assign-serial
      Add a serialNumber (urn:uuid) to the system BOM, in place, if it has
      none. A system BOM needs one before other BOMs can BOM-Link to it.
  slice_use_case.py SYSTEM.json --use-case usecase:x [-o TM.json]
      Write a TM-BOM skeleton for that use case: the system slice, the links
      back to the system BOM, and empty `threats`, `controls` and `risks`.
      Refuses to overwrite an existing file.
  slice_use_case.py SYSTEM.json --use-case usecase:x -o TM.json --update
      Re-slice an existing TM-BOM after the system BOM changed: keeps its
      serialNumber, bumps its version, and carries over its threats, controls,
      risks, weaknesses, standards and attacker parties.
  slice_use_case.py SYSTEM.json --link TM.json
      Add (or refresh) a `threat-model` external reference in the system BOM,
      in place, pointing at the TM-BOM's serialNumber and version.

What the slice contains, for use case U of blueprint B:
  - flows:          the flows B lists for U
  - endpoints:      every source and destination of those flows
  - actors:         actors that are endpoints, plus the actors U names
  - components:     components that are endpoints, components that realize a
                    sliced actor (party.system.ref), and the structural parents
                    of sliced components (relationships), repeated to a fixpoint
  - zones:          zones that aggregate or contain a sliced component
  - boundaries:     boundaries whose zones are all sliced zones
  - relationships:  kept when the subject is sliced, targets filtered to the slice
  - assets, dataStores, dataSets, assumptions: kept when they touch the slice
  - then every element any copied element references (parties in
    identifiers, zone parents, actor/asset/data-store zones, nested component
    references), repeated until nothing new is added
The output is checked for unresolved references before it is written.
Standard library only.
"""

import argparse
import copy
import datetime
import json
import os
import re
import sys
import uuid

SERIAL = re.compile(r"^urn:uuid:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")
STRUCTURAL = ("aggregates", "composes", "contains")
REL_KINDS = ("aggregates", "associates", "composes", "contains", "dependsOn",
             "generalizes", "realizes", "serves")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")


def serial_uuid(doc):
    m = SERIAL.match(doc.get("serialNumber", ""))
    return m.group(1) if m else None


def bomlink(doc, ref=None):
    link = f"urn:cdx:{serial_uuid(doc)}/{doc.get('version', 1)}"
    return f"{link}#{ref}" if ref else link


def use_case_index(system):
    """[(blueprint, blueprint_use_case_entry, definition_or_None)]"""
    defs = {u.get("refId"): u for u in system.get("definitions", {}).get("useCases", [])}
    out = []
    for bp in system.get("blueprints", []):
        for entry in bp.get("useCases", []):
            out.append((bp, entry, defs.get(entry.get("ref"))))
    return out


def cmd_list(system):
    rows = use_case_index(system)
    if not rows:
        print("No blueprint use cases found (blueprints[].useCases[].ref).")
        return
    flow_sets = {e.get("ref"): set(e.get("flows", [])) for _, e, _ in rows}
    for bp, entry, definition in rows:
        ref = entry.get("ref")
        name = (definition or {}).get("name", "(no definition in definitions.useCases)")
        flows = flow_sets[ref]
        others = [r for r in flow_sets if r != ref and flow_sets[r] and flow_sets[r] < flows]
        umbrella = ""
        if len(others) >= 2 and set().union(*(flow_sets[o] for o in others)) == flows:
            umbrella = f"  [umbrella: its flows are exactly the union of {', '.join(others)}]"
        print(f"{ref}  —  {name}")
        print(f"    blueprint: {bp.get('refId', bp.get('name'))}, flows: {len(flows)}{umbrella}")


def cmd_assign_serial(path, system):
    if serial_uuid(system):
        print(f"{path} already has serialNumber {system['serialNumber']}")
        return
    if "serialNumber" in system:
        sys.exit(f"{path} has an invalid serialNumber '{system['serialNumber']}'. Fix it by hand (urn:uuid:<lowercase uuid>).")
    new = {}
    for k, v in system.items():
        new[k] = v
        if k == "specVersion":
            new["serialNumber"] = f"urn:uuid:{uuid.uuid4()}"
    if "serialNumber" not in new:
        new = {"serialNumber": f"urn:uuid:{uuid.uuid4()}", **new}
    new.setdefault("version", 1)
    save(path, new)
    print(f"Added serialNumber {new['serialNumber']} to {path}")


def by_refid(items):
    return {i["refId"]: i for i in items if isinstance(i, dict) and "refId" in i}


def rel_targets(rel, kinds=REL_KINDS):
    out = []
    for k in kinds:
        out.extend(rel.get(k, []))
    if "custom" in rel and kinds is REL_KINDS:
        for c in rel["custom"]:
            out.extend(c.get("targets", []))
    return out


REF_KEYS = {"ref", "parent", "zone", "componentRef", "partyRef", "party"}


def local_refs(obj, elements):
    """refIds of known elements that obj references, at any depth.

    Without the schema this is a heuristic: a string under a reference-like key
    ("ref", "parent", "zone", "componentRef", "partyRef", "party") that names a
    known element. The self-check after slicing catches anything it misses.
    """
    found = set()

    def walk(node, key=None):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("refId", "externalReferences"):
                    continue
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)
        elif isinstance(node, str) and key in REF_KEYS and node in elements:
            found.add(node)

    walk(obj)
    return found


def build_slice(system, use_case_ref):
    rows = [r for r in use_case_index(system) if r[1].get("ref") == use_case_ref]
    if not rows:
        sys.exit(f"Use case '{use_case_ref}' is not referenced by any blueprint. Run with --list.")
    bp, entry, definition = rows[0]
    if definition is None:
        sys.exit(f"Use case '{use_case_ref}' has no entry in definitions.useCases.")

    flows_all = by_refid(bp.get("flows", []))
    actors_all = by_refid(bp.get("actors", []))
    zones_all = by_refid(bp.get("zones", []))
    comps_all = by_refid(system.get("definitions", {}).get("components", []))
    parties_all = by_refid(system.get("definitions", {}).get("parties", []))
    stores_all = by_refid(bp.get("dataStores", []))
    rels = bp.get("relationships", [])

    missing = [f for f in entry.get("flows", []) if f not in flows_all]
    if missing:
        sys.exit(f"Use case lists flows that the blueprint does not declare: {', '.join(missing)}")
    flows = [flows_all[f] for f in entry.get("flows", [])]

    members = set()
    for f in flows:
        members.update([f["source"], f["destination"]])
    members.update(definition.get("actors", []))

    # Components realizing sliced actors, and actors realized by sliced components.
    def close_over_actors():
        changed = False
        for aref, actor in actors_all.items():
            party = actor.get("party", {})
            sysref = party.get("system", {}).get("ref") if isinstance(party, dict) else None
            if aref in members and sysref and sysref not in members:
                members.add(sysref)
                changed = True
        for rel in rels:
            if rel.get("ref") in members:
                for t in rel.get("realizes", []):
                    if t in actors_all and t not in members:
                        members.add(t)
                        changed = True
        return changed

    # Structural parents (and zones) of sliced elements, to a fixpoint.
    def close_over_parents():
        changed = False
        for rel in rels:
            subject = rel.get("ref")
            if subject in members:
                continue
            if any(t in members for t in rel_targets(rel, STRUCTURAL)):
                if subject in comps_all or subject in zones_all:
                    members.add(subject)
                    changed = True
        return changed

    while close_over_actors() | close_over_parents():
        pass

    # Blueprint assets that represent a sliced component or party, or that a sliced
    # component or actor holds (`contains`, `composes`, `aggregates`, `associates`).
    # Data assets such as credentials, API keys and model weights are modelled this
    # way, and threats need them as `affects` targets.
    assets_all = by_refid(bp.get("assets", []))
    for aref, asset in assets_all.items():
        if asset.get("componentRef") in members or asset.get("partyRef") in members:
            members.add(aref)
    holds = ("contains", "composes", "aggregates", "associates")
    for rel in rels:
        if rel.get("ref") in members and rel.get("ref") not in zones_all:
            for t in rel_targets(rel, holds):
                if t in assets_all:
                    members.add(t)
    # Zones that sliced actors, assets and data stores sit in.
    for table in (actors_all, assets_all, stores_all):
        for r, obj in table.items():
            if r in members and obj.get("zone") in zones_all:
                members.add(obj["zone"])

    # Close over every in-document reference inside the elements being copied,
    # so the slice never points at something it does not contain.
    elements = {**comps_all, **actors_all, **zones_all, **stores_all, **assets_all, **parties_all}
    while True:
        added = set()
        for r in list(members):
            for target in local_refs(elements.get(r), elements):
                if target not in members:
                    added.add(target)
        if not added:
            break
        members |= added
        while close_over_actors() | close_over_parents():
            pass

    zones = [z for r, z in zones_all.items() if r in members]
    zone_refs = {z["refId"] for z in zones}
    boundaries = [b for b in bp.get("boundaries", []) if b.get("zones") and set(b["zones"]) <= zone_refs]
    for b in boundaries:
        members.add(b["refId"])

    sliced_rels = []
    for rel in rels:
        if rel.get("ref") not in members:
            continue
        new = {"ref": rel["ref"]}
        for k in REL_KINDS:
            kept = [t for t in rel.get(k, []) if t in members]
            if kept:
                new[k] = kept
        if "custom" in rel:
            custom = []
            for c in rel["custom"]:
                kept = [t for t in c.get("targets", []) if t in members]
                if kept:
                    custom.append({**c, "targets": kept})
            if custom:
                new["custom"] = custom
        kinds = [k for k in new if k != "ref"]
        # The schema allows exactly one relationship kind per entry.
        for k in kinds:
            sliced_rels.append({"ref": rel["ref"], k: new[k]})

    actors = [copy.deepcopy(a) for r, a in actors_all.items() if r in members]
    comps = [copy.deepcopy(c) for r, c in comps_all.items() if r in members]

    parties = [copy.deepcopy(p) for r, p in parties_all.items() if r in members]
    assets = [copy.deepcopy(a) for r, a in assets_all.items() if r in members]
    stores = [copy.deepcopy(s) for r, s in stores_all.items() if r in members]
    data_sets = [copy.deepcopy(d) for d in bp.get("dataSets", []) if d.get("refId") in members]
    # Assumptions are kept when general, or when they touch the slice; their links are trimmed to it.
    # Assumptions are kept when general, or when they touch the slice (an element or a
    # flow of it); their links are trimmed to the slice. Report the ones left out.
    in_slice = members | {f["refId"] for f in flows}
    assumptions, left_out = [], []
    for a in bp.get("assumptions", []):
        related = a.get("relatedAssets")
        if related and not any(x in in_slice for x in related):
            left_out.append(a.get("refId") or a.get("description", "")[:40])
            continue
        a = copy.deepcopy(a)
        if related:
            a["relatedAssets"] = [x for x in related if x in in_slice]
        assumptions.append(a)
    if left_out:
        print(f"Assumptions not in this slice (they relate to nothing in it): {', '.join(left_out)}", file=sys.stderr)

    definition = copy.deepcopy(definition)
    # Use case links to requirements and business objectives are not part of the slice.
    dropped = [k for k in ("requirements", "businessObjectives") if definition.pop(k, None)]
    if dropped:
        print(f"Note: removed {', '.join(dropped)} from the sliced use case; the TM-BOM does not carry them.",
              file=sys.stderr)
    if "actors" in definition:
        definition["actors"] = [x for x in definition["actors"] if x in members]

    # Unknown endpoints: flows may target elements this tool does not slice.
    known = set(actors_all) | set(comps_all) | set(zones_all) | set(stores_all) | {a.get("refId") for a in bp.get("assets", [])}
    unknown = sorted(m for m in members if m not in known and m not in {b["refId"] for b in boundaries})
    if unknown:
        print("Warning: these sliced references are not components, actors, zones, data stores or assets "
              "and were not copied: " + ", ".join(unknown), file=sys.stderr)

    blueprint = {
        "refId": bp.get("refId", "blueprint:system"),
        "name": bp.get("name", "System"),
        "description": f"Slice of {bp.get('name', 'the system blueprint')} for {definition.get('name', use_case_ref)}, "
                       "copied from the linked system BOM. Every element keeps its system BOM refId.",
        "modelTypes": copy.deepcopy(bp.get("modelTypes", ["logical"])),
    }
    for key, value in (("assets", assets), ("dataStores", stores), ("dataSets", data_sets),
                       ("zones", [copy.deepcopy(z) for z in zones]),
                       ("boundaries", [copy.deepcopy(b) for b in boundaries]),
                       ("actors", actors), ("flows", [copy.deepcopy(f) for f in flows]),
                       ("relationships", sliced_rels), ("assumptions", assumptions)):
        if value:
            blueprint[key] = value
    bp_uc = {"ref": use_case_ref, "flows": list(entry.get("flows", []))}
    if entry.get("assets"):
        bp_uc["assets"] = [a for a in entry["assets"] if a in members]
    blueprint["useCases"] = [bp_uc]
    return blueprint, comps, parties, definition


def unresolved_refs(doc):
    """In-document references in doc that resolve to nothing, using the validator's schema walk."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import validate_bom  # same directory; standard library only for this function
    with open(validate_bom.DEFAULT_SCHEMA, encoding="utf-8") as f:
        schema = json.load(f)
    refs, ids = validate_bom.find_refs(doc, schema)
    return [(validate_bom.fmt(p), v) for p, v, kind in refs if kind == "local" and v not in ids]


# Sections of an existing TM-BOM that --update carries over (the threat-model content).
TM_CONTENT = ("threats", "controls", "risks", "vulnerabilities", "annotations")
TM_DEFINITIONS = ("weaknesses", "standards", "requirements", "businessObjectives")


def cmd_slice(system, use_case_ref, out_path, system_path, update=False):
    if not serial_uuid(system):
        sys.exit(f"{system_path} has no serialNumber, so a TM-BOM cannot BOM-Link to it. "
                 "Run with --assign-serial first (it edits the system BOM in place).")
    previous = None
    if out_path and os.path.exists(out_path):
        if not update:
            sys.exit(f"{out_path} already exists. Use --update to re-slice it in place (keeps its serialNumber, "
                     "bumps its version and carries over its threats, controls and risks), or choose another -o.")
        previous = load(out_path)
    blueprint, comps, parties, definition = build_slice(system, use_case_ref)
    for c in comps:
        refs = c.setdefault("externalReferences", [])
        link = bomlink(system, c["refId"])
        if not any(r.get("url") == link for r in refs):
            refs.append({"type": "bom", "url": link, "comment": "This component as declared in the system BOM."})

    uc_name = definition.get("name", use_case_ref)
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    definitions = {"components": comps}
    if parties:
        definitions["parties"] = parties
    definitions["useCases"] = [definition]
    tm = {
        "$schema": system.get("$schema", "https://cyclonedx.org/schema/2.0/cyclonedx-2.0.schema.json"),
        "specFormat": "CycloneDX",
        "specVersion": "2.0",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "tools": {"components": [{"type": "application", "name": "cyclonedx skill: slice_use_case.py"}]},
            "properties": [
                {"name": "lfai:threat-model:system-bom", "value": bomlink(system)},
                {"name": "lfai:threat-model:use-case", "value": use_case_ref},
            ],
        },
        "externalReferences": [{
            "type": "bom",
            "url": bomlink(system),
            "comment": f"System BOM this threat model was generated from. Elements in definitions and blueprints "
                       f"are a slice of it for the use case '{uc_name}' and keep its refIds.",
        }],
        "definitions": definitions,
        "blueprints": [blueprint],
        "threats": {"methodologies": [], "threats": [], "threatScenarios": []},
        "controls": [],
        "risks": {"risks": [], "damageScenarios": []},
    }

    if previous is not None:
        tm["serialNumber"] = previous.get("serialNumber", tm["serialNumber"])
        tm["version"] = int(previous.get("version", 1)) + 1
        for key in TM_CONTENT:
            if key in previous:
                tm[key] = previous[key]
        prev_defs = previous.get("definitions", {})
        for key in TM_DEFINITIONS:
            if key in prev_defs:
                definitions[key] = prev_defs[key]
        # Parties the threat model added (attackers) are kept; system parties come from the new slice.
        system_parties = {p.get("refId") for p in system.get("definitions", {}).get("parties", [])}
        sliced = {p.get("refId") for p in definitions.get("parties", [])}
        extra = [p for p in prev_defs.get("parties", [])
                 if p.get("refId") not in system_parties and p.get("refId") not in sliced]
        if extra:
            definitions["parties"] = definitions.get("parties", []) + extra
        # Threat-model annotations on the blueprint (none today) would be lost; say what changed instead.
        old_members = {x.get("refId") for x in (previous.get("blueprints") or [{}])[0].get("flows", [])}
        new_members = {x.get("refId") for x in blueprint.get("flows", [])}
        if old_members != new_members:
            print(f"Flows added: {sorted(new_members - old_members) or 'none'}; "
                  f"removed: {sorted(old_members - new_members) or 'none'}. Review threats on removed flows.",
                  file=sys.stderr)

    missing = unresolved_refs(tm)
    if missing:
        print("The slice has references it cannot resolve. This is a bug in the slicer or an invalid system BOM "
              "(run validate_bom.py on it):", file=sys.stderr)
        for where, value in missing:
            print(f"  {where}: '{value}'", file=sys.stderr)
        if previous is not None:
            print("  (Some may be threat-model references to elements no longer in the slice.)", file=sys.stderr)
        sys.exit(1)

    text = json.dumps(tm, indent=2, ensure_ascii=False) + "\n"
    if out_path:
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        counts = {k: len(blueprint.get(k, [])) for k in ("assets", "zones", "boundaries", "actors", "flows", "relationships")}
        print(f"Wrote {out_path}: {len(comps)} components, " + ", ".join(f"{v} {k}" for k, v in counts.items()),
              file=sys.stderr)
        sys_bp = next((b for b in system.get("blueprints", []) if b.get("refId") == blueprint["refId"]), {})
        kept = {a.get("refId") for a in blueprint.get("assets", [])}
        dropped = [a.get("refId") for a in sys_bp.get("assets", []) if a.get("refId") not in kept]
        if dropped:
            print(f"Not in this slice ({len(dropped)} blueprint assets not held by a sliced element): "
                  + ", ".join(dropped), file=sys.stderr)
        if previous is None:
            print("Empty threats/controls/risks sections are placeholders; remove any you do not fill "
                  "(empty arrays are valid but add noise).", file=sys.stderr)
        else:
            print(f"Updated in place: serialNumber kept, version {tm['version']}. If the system BOM links to this "
                  "TM-BOM, rerun --link to refresh the version.", file=sys.stderr)
    else:
        sys.stdout.write(text)


def cmd_link(system_path, system, tm_path):
    tm = load(tm_path)
    if not serial_uuid(tm):
        sys.exit(f"{tm_path} has no valid serialNumber to link to.")
    use_case = next((p.get("value") for p in tm.get("metadata", {}).get("properties", [])
                     if p.get("name") == "lfai:threat-model:use-case"), None)
    refs = system.setdefault("externalReferences", [])
    prefix = f"urn:cdx:{serial_uuid(tm)}/"
    refs[:] = [r for r in refs if not (r.get("type") == "threat-model" and str(r.get("url", "")).startswith(prefix))]
    entry = {"type": "threat-model", "url": bomlink(tm),
             "comment": f"Threat model BOM ({os.path.basename(tm_path)})" + (f" for {use_case}" if use_case else "") + "."}
    refs.append(entry)
    save(system_path, system)
    print(f"Linked {system_path} -> {entry['url']}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("system", help="the system BOM (CycloneDX 2.0 JSON)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="list the use cases")
    g.add_argument("--assign-serial", action="store_true", help="add a serialNumber to the system BOM in place")
    g.add_argument("--use-case", metavar="REFID", help="write a TM-BOM skeleton for this use case")
    g.add_argument("--link", metavar="TM_BOM", help="add a threat-model link to the system BOM in place")
    p.add_argument("-o", "--output", help="output file for --use-case (default: stdout)")
    p.add_argument("--update", action="store_true",
                   help="with --use-case -o EXISTING: re-slice in place, keeping serialNumber and threat content")
    args = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    system = load(args.system)
    if system.get("specVersion") != "2.0":
        sys.exit("The system BOM must be CycloneDX 2.0 (specVersion '2.0').")
    if args.list:
        cmd_list(system)
    elif args.assign_serial:
        cmd_assign_serial(args.system, system)
    elif args.use_case:
        cmd_slice(system, args.use_case, args.output, args.system, args.update)
    else:
        cmd_link(args.system, system, args.link)


if __name__ == "__main__":
    main()
