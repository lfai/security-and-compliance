#!/usr/bin/env python3
"""Validate a CycloneDX 2.0 BOM, and optionally its links to a system BOM.

Checks, in order:
  1. JSON Schema validation against the bundled CycloneDX 2.0 schema
     (needs the `jsonschema` package; see --no-schema).
  2. Every `refId` is unique in the document. JSON Schema cannot check this.
  3. Every in-document reference (a field typed as a refId reference in the
     schema) points at a `refId` declared in the same document.
  4. Every BOM-Link (urn:cdx:<serial>/<version>[#<refId>]) is well formed.
     With --system, links to the system BOM must match its serialNumber and
     version, and each #<refId> fragment must exist in the system BOM.
     With --linked, links to those documents are checked the same way.
  5. With --system (threat-model BOMs): the document links to the system BOM
     from its top-level externalReferences, and every element copied into its
     system slice (blueprints, definitions.components, definitions.useCases)
     is identical to the system BOM element with the same refId, ignoring the
     back-links the slicer adds.
  6. Checks that also run with --no-schema: no CycloneDX 1.7 keys (bomFormat,
     bom-ref, top-level components or services), exactly one kind per
     relationship, and no BOM-Link in a field that takes only a refId.

Usage:
  validate_bom.py BOM.json
  validate_bom.py TM-BOM.json --system SYSTEM-BOM.json
  validate_bom.py SYSTEM-BOM.json --linked TM-BOM-1.json --linked TM-BOM-2.json

Exit code 0 when there are no errors (warnings allowed), 1 on errors,
2 when the tool cannot run.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCHEMA = os.path.join(HERE, "..", "schema", "2.0", "cyclonedx-2.0-bundled.schema.json")

BOMLINK = re.compile(
    r"^urn:cdx:(?P<serial>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
    r"/(?P<version>[1-9][0-9]*)(?:#(?P<ref>.+))?$"
)
SERIAL = re.compile(r"^urn:uuid:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")

# Schema definitions whose instances are references, and what they accept.
REF_KINDS = {
    "refLinkType": "local",           # refId in this document
    "elementLink": "either",          # refId or BOM-Link element
    "bomLinkElementType": "bomlink",  # BOM-Link element only
    "bomLinkDocumentType": "bomlink",
    "bomLink": "bomlink",
}
SLICE_SECTIONS = ("blueprints", "definitions.components", "definitions.useCases")
# Fields slice_use_case.py filters down to the slice's members (or drops), so a
# sliced copy may hold an ordered subset of the system BOM's list.
TRIMMED_LISTS = ("relatedAssets", "actors", "requirements", "businessObjectives")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"Cannot read {path}: {exc}")


def fmt(path):
    out = ""
    for p in path:
        out += f"[{p}]" if isinstance(p, int) else (f".{p}" if out else p)
    return out or "(root)"


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


# ---------------------------------------------------------------- schema ---

def schema_validate(doc, schema, report):
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError:
        return False
    # The bundle keeps a few relative $refs (SPDX ids, crypto and behaviour
    # taxonomies). Stub them as permissive schemas so validation can run
    # offline; the values they govern are not checked.
    base = schema.get("$id", "https://cyclonedx.org/schema/2.0/").rsplit("/", 2)[0] + "/"
    stub = {"$schema": "https://json-schema.org/draft/2020-12/schema"}
    registry = Registry().with_resources(
        (base + name, Resource.from_contents({**stub, "$id": base + name}))
        for name in ("spdx.schema.json", "cryptography-defs.schema.json", "behavior-taxonomy.schema.json")
    )
    validator = Draft202012Validator(schema, registry=registry,
                                     format_checker=Draft202012Validator.FORMAT_CHECKER)
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        msg = err.message if len(err.message) < 400 else err.message[:400] + "…"
        best = err
        if err.context:  # oneOf/anyOf: show the closest branch failure too
            best = min(err.context, key=lambda e: (-len(e.absolute_path), len(e.message)))
            if best is not err:
                msg += f"  [closest branch: {fmt(list(best.absolute_path))}: {best.message[:200]}]"
        report.error(f"schema: {fmt(list(err.absolute_path))}: {msg}")
    return True


# ----------------------------------------------------- reference discovery ---

def find_refs(doc, schema):
    """Walk the document alongside the schema and return the reference values.

    Returns (refs, ids): refs is a list of (path, value, kind); ids maps each
    declared refId to the list of paths declaring it.
    """
    refs, seen, ids = [], set(), {}

    def resolve(ref):
        node = schema
        for part in ref.lstrip("#/").split("/"):
            node = node[part]
        return node

    def visit(inst, node, path, depth=0):
        if depth > 60 or not isinstance(node, dict):
            return
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/"):
            kind = REF_KINDS.get(ref.rsplit("/", 1)[-1])
            if kind and isinstance(inst, str):
                is_link = inst.startswith("urn:cdx:")
                if kind == "local" and is_link:
                    found = "misplaced"   # a BOM-Link where only a refId is allowed
                elif kind == "bomlink" and not is_link:
                    found = None          # another branch (refLinkType) records it
                else:
                    found = "bomlink" if is_link else "local"
                if found:
                    key = (tuple(path), inst, found)
                    if key not in seen:
                        seen.add(key)
                        refs.append((list(path), inst, found))
                return
            visit(inst, resolve(ref), path, depth + 1)
        for kw in ("allOf", "oneOf", "anyOf"):
            for branch in node.get(kw, []):
                visit(inst, branch, path, depth + 1)
        if "then" in node:
            visit(inst, node["then"], path, depth + 1)
        if isinstance(inst, dict):
            props = node.get("properties", {})
            for k, v in inst.items():
                if k in props:
                    visit(v, props[k], path + [k], depth + 1)
        elif isinstance(inst, list) and isinstance(node.get("items"), dict):
            for i, v in enumerate(inst):
                visit(v, node["items"], path + [i], depth + 1)

    def collect_ids(inst, path):
        if isinstance(inst, dict):
            if isinstance(inst.get("refId"), str):
                ids.setdefault(inst["refId"], []).append(path)
            for k, v in inst.items():
                collect_ids(v, path + [k])
        elif isinstance(inst, list):
            for i, v in enumerate(inst):
                collect_ids(v, path + [i])

    visit(doc, schema, [])
    collect_ids(doc, [])
    return refs, ids


def objects_by_refid(doc, sections):
    """Map refId -> (section, object) for objects under the given sections."""
    found = {}

    def walk(inst, section):
        if isinstance(inst, dict):
            if isinstance(inst.get("refId"), str):
                found.setdefault(inst["refId"], (section, inst))
            for v in inst.values():
                walk(v, section)
        elif isinstance(inst, list):
            for v in inst:
                walk(v, section)

    for section in sections:
        node = doc
        for part in section.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if node is not None:
            walk(node, section)
    return found


def _paths_with_key(inst, key, path=None):
    path = path or []
    if isinstance(inst, dict):
        if key in inst:
            yield path + [key]
        for k, v in inst.items():
            yield from _paths_with_key(v, key, path + [k])
    elif isinstance(inst, list):
        for i, v in enumerate(inst):
            yield from _paths_with_key(v, key, path + [i])


def _comparable(obj, sys_serial):
    """A copy of an element without the back-links the slicer adds."""
    obj = json.loads(json.dumps(obj))
    if sys_serial and isinstance(obj.get("externalReferences"), list):
        prefix = f"urn:cdx:{sys_serial}/"
        obj["externalReferences"] = [r for r in obj["externalReferences"]
                                     if not (r.get("type") == "bom" and str(r.get("url", "")).startswith(prefix))]
        if not obj["externalReferences"]:
            del obj["externalReferences"]
    return obj


def _first_difference(a, b, path=""):
    """(path, a_value, b_value) of the first difference, or None. Lists compare in order."""
    if type(a) is not type(b):
        return path.lstrip("."), a, b
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f"{path}.{k}".lstrip("."), a.get(k, "(missing)"), b.get(k, "(missing)")
            d = _first_difference(a[k], b[k], f"{path}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return path.lstrip(".") + " (length)", len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            d = _first_difference(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else (path.lstrip("."), a, b)


# ------------------------------------------------------------------ main ---

def check(doc, schema, report, system=None, system_path=None, linked=()):
    refs, ids = find_refs(doc, schema)
    targets = {}  # serial uuid -> (path, version, refIds)
    for lpath, ldoc in linked:
        m = SERIAL.match(ldoc.get("serialNumber", ""))
        if m:
            targets[m.group(1)] = (lpath, str(ldoc.get("version", 1)), find_refs(ldoc, schema)[1])
        else:
            report.error(f"linked document {lpath} has no valid serialNumber")

    for rid, paths in ids.items():
        if len(paths) > 1:
            report.error(f"refId '{rid}' is declared {len(paths)} times: " + ", ".join(fmt(p) for p in paths))

    serial = doc.get("serialNumber")
    if not serial:
        report.warn("no serialNumber: other BOMs cannot BOM-Link to this document until one is added")

    sys_serial = sys_version = None
    sys_ids = {}
    if system is not None:
        m = SERIAL.match(system.get("serialNumber", ""))
        if not m:
            report.error(f"system BOM {system_path} has no valid serialNumber, so it cannot be linked to. "
                         "Add one (urn:uuid:<uuid4>) and bump its version.")
        else:
            sys_serial, sys_version = m.group(1), str(system.get("version", 1))
        _, sys_ids = find_refs(system, schema)
        if sys_serial:
            targets[sys_serial] = (system_path, sys_version, sys_ids)

    # Mistakes JSON Schema would also catch, repeated so --no-schema catches them.
    for key in ("bomFormat", "components", "services"):
        if key in doc:
            report.error(f"top-level '{key}' is CycloneDX 1.7; in 2.0 use "
                         + ("specFormat" if key == "bomFormat" else "definitions.components + inventories"))
    for path in _paths_with_key(doc, "bom-ref"):
        report.error(f"{fmt(path)}: 'bom-ref' is CycloneDX 1.7; use 'refId' in 2.0")
    kinds = ("aggregates", "associates", "composes", "contains", "dependsOn",
             "generalizes", "realizes", "serves", "custom")
    for bi, bp in enumerate(doc.get("blueprints", []) or []):
        for ri, rel in enumerate(bp.get("relationships", []) or []):
            present = [k for k in kinds if k in rel]
            if len(present) != 1:
                report.error(f"blueprints[{bi}].relationships[{ri}]: needs exactly one relationship kind, has "
                             + (", ".join(present) or "none"))

    local, links, unchecked = 0, 0, {}
    for path, value, kind in refs:
        if kind == "misplaced":
            report.error(f"{fmt(path)}: BOM-Link '{value}' is not allowed here; this field takes a refId in this "
                         "document. Copy the element into the document (see the system slice) and reference its refId.")
            continue
        if kind == "local":
            local += 1
            if value not in ids:
                report.error(f"{fmt(path)}: reference '{value}' does not match any refId in this document")
            continue
        links += 1
        m = BOMLINK.match(value)
        if not m:
            report.error(f"{fmt(path)}: malformed BOM-Link '{value}' (expected urn:cdx:<uuid>/<version>[#<refId>])")
            continue
        if m.group("serial") in targets:
            tpath, tversion, tids = targets[m.group("serial")]
            if m.group("version") != tversion:
                report.warn(f"{fmt(path)}: links to version {m.group('version')} of {os.path.basename(tpath)}, "
                            f"which is now version {tversion}")
            frag = m.group("ref")
            if frag and frag not in tids:
                report.error(f"{fmt(path)}: BOM-Link fragment '#{frag}' is not a refId in {os.path.basename(tpath)}")
        elif serial and SERIAL.match(serial) and m.group("serial") == SERIAL.match(serial).group(1):
            frag = m.group("ref")
            if frag and frag not in ids:
                report.error(f"{fmt(path)}: self BOM-Link fragment '#{frag}' is not a refId in this document")
        else:
            unchecked.setdefault(m.group("serial"), []).append(fmt(path))
    for other, paths in unchecked.items():
        report.warn(f"{len(paths)} BOM-Link(s) to document {other} not checked (first: {paths[0]}); "
                    "pass that document with --system or --linked to check them")

    if system is not None and sys_serial:
        top = [r.get("url", "") for r in doc.get("externalReferences", []) if r.get("type") == "bom"]
        if not any(BOMLINK.match(u) and BOMLINK.match(u).group("serial") == sys_serial for u in top):
            report.error("no top-level externalReferences entry of type 'bom' links to the system BOM "
                         f"(expected url 'urn:cdx:{sys_serial}/{sys_version}')")
        sys_objs = objects_by_refid(system, SLICE_SECTIONS)
        slice_containers = {b.get("refId") for b in doc.get("blueprints", []) if isinstance(b, dict)}
        for rid, (section, obj) in objects_by_refid(doc, SLICE_SECTIONS).items():
            if rid not in sys_objs:
                report.error(f"{section}: '{rid}' is in this document's system slice but not in the system BOM")
                continue
            sys_section, sys_obj = sys_objs[rid]
            if sys_section != section:
                report.error(f"'{rid}' is under {section} here but under {sys_section} in the system BOM")
                continue
            if rid in slice_containers:
                continue  # the slice blueprint itself; its members are compared one by one
            here_obj, there_obj = _comparable(obj, sys_serial), _comparable(sys_obj, sys_serial)
            # Reference lists the slicer trims to the slice: allowed to be an ordered subset.
            for key in TRIMMED_LISTS:
                a, b = here_obj.get(key), there_obj.get(key)
                if isinstance(a, list) and isinstance(b, list) and [x for x in b if x in a] == a:
                    here_obj[key] = there_obj[key] = None
            diff = _first_difference(here_obj, there_obj)
            if diff is not None:
                where, here, there = diff
                report.error(f"{section}: '{rid}' differs from the system BOM at {where or '(object)'}: "
                             f"{json.dumps(here, ensure_ascii=False)[:120]} here, "
                             f"{json.dumps(there, ensure_ascii=False)[:120]} in the system BOM. "
                             "Change the system BOM and re-slice instead of editing the copy.")

    return {"refIds": len(ids), "local_refs": local, "bom_links": links}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("bom", help="the BOM to validate")
    p.add_argument("--system", help="the system BOM a threat-model BOM links to")
    p.add_argument("--linked", action="append", default=[], metavar="BOM",
                   help="another BOM this document links to (repeatable); checks its BOM-Links")
    p.add_argument("--schema", default=DEFAULT_SCHEMA, help="bundled CycloneDX 2.0 schema")
    p.add_argument("--no-schema", action="store_true", help="skip JSON Schema validation (structure checks only)")
    p.add_argument("--strict", action="store_true",
                   help="treat threat-model coverage and catalogue-sweep gaps as errors, not warnings")
    p.add_argument("--report-json", metavar="FILE",
                   help="write the threat-model coverage report as JSON (for the workflow's final report)")
    args = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    schema = load_json(args.schema)
    doc = load_json(args.bom)
    system = load_json(args.system) if args.system else None
    report = Report()

    if doc.get("specFormat") != "CycloneDX" or str(doc.get("specVersion")) != "2.0":
        report.error("this tool validates CycloneDX 2.0: expected specFormat 'CycloneDX' and specVersion '2.0'")

    schema_ran = False
    if not args.no_schema:
        schema_ran = schema_validate(doc, schema, report)
        if not schema_ran:
            print("jsonschema is not installed, so schema validation could not run.\n"
                  "Install it (pip install jsonschema) or rerun with --no-schema for the structure checks only.",
                  file=sys.stderr)
            return 2
    linked = [(path, load_json(path)) for path in args.linked]
    stats = check(doc, schema, report, system, args.system, linked)

    sys.path.insert(0, HERE)
    import tm_checks
    refs = tm_checks.References()
    tm_checks.check_properties(doc, refs, report)
    tm_checks.check_ids(doc, refs, report)
    coverage = tm_checks.check_coverage(doc, refs, report, strict=args.strict)
    if args.report_json and coverage is not None:
        with open(args.report_json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(coverage, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(f"{args.bom}")
    if not schema_ran:
        state = "SKIPPED (--no-schema): enums, required fields and formats were not checked"
    elif any(e.startswith("schema:") for e in report.errors):
        state = "FAILED"
    else:
        state = "passed (SPDX licence ids and the crypto and behaviour taxonomies are not checked offline)"
    print(f"  schema validation: {state}")
    print(f"  refIds: {stats['refIds']}, in-document references: {stats['local_refs']}, BOM-Links: {stats['bom_links']}")
    if args.system:
        print(f"  linked system BOM: {args.system}")
    for path in args.linked:
        print(f"  linked BOM: {path}")
    if coverage is not None:
        swept = sum(r["decided"] for r in coverage["sweep"])
        total = sum(r["items"] for r in coverage["sweep"])
        print(f"  threat model: {coverage['threats']} threats; "
              f"{coverage['elements'] - len(coverage['uncovered'])}/{coverage['elements']} elements covered; "
              f"{coverage['controls'] - len(coverage['unmappedControls'])}/{coverage['controls']} controls mapped; "
              f"catalogue sweep {swept}/{total} item decisions")
    for e in report.errors:
        print(f"  ERROR   {e}")
    for w in report.warnings:
        print(f"  WARNING {w}")
    print(f"  result: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
