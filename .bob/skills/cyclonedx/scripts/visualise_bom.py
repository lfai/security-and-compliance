#!/usr/bin/env python3
"""Map where CycloneDX 2.0 elements are declared and where they are referenced.

Writes one self-contained, interactive HTML page with three views:

  Documents  each BOM, the BOM-Links between them, every problem found, and a
             map of which element types reference which, with the system
             slice of each threat-model BOM drawn against the system BOM.
  Elements   every declared element: where it is declared, what it
             references, what references it (in every loaded BOM, including
             through its slice copies), and whether each copy still matches
             the system BOM.
  Schema     every object in the bundled schema: where it sits in a BOM,
             whether it declares a refId, which of its fields are references
             and what they accept, and which element types those fields were
             seen pointing at in the loaded BOMs.

Usage:
  visualise_bom.py bom SYSTEM.json [TM.json ...] [-o MAP.html]
      Map one or more BOMs. Pass the system BOM with its threat-model BOMs
      to see references across them. Default output: bom-map.html.
  visualise_bom.py schema [--observe BOM ...] [-o MAP.html]
      Map the schema only. Reference targets are taken from the --observe
      BOMs (default: the two examples in ../examples/). Default output:
      schema-map.html.

Options:
  --schema PATH   Use a different bundled schema file.
  -o FILE         Output file. An existing file is replaced only if this tool
                  wrote it.

The page needs no network access: it loads no scripts, fonts or styles from
anywhere, and BOM text is shown as text, never as HTML. Standard library only.
"""

import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from validate_bom import (BOMLINK, DEFAULT_SCHEMA, REF_KINDS, SERIAL, SLICE_SECTIONS,  # noqa: E402
                          load_json, objects_by_refid, slice_difference)

TEMPLATE = os.path.join(HERE, "visualise_bom.html")
EXAMPLES = os.path.join(HERE, "..", "examples")
GENERATOR = "cyclonedx skill: visualise_bom.py"
OBJ = re.compile(r"^#/\$defs/([^/]+)/\$defs/([^/]+)$")
ROOT_KEY = "root:bom"
TEXT_LIMIT = 320
JSON_LIMIT = 6000
# Columns of the schema map, system modules first. Others follow alphabetically.
MODULE_ORDER = ("party", "usecase", "component", "definition", "inventories", "blueprint", "data",
                "common", "threat", "weakness", "standard", "requirement", "control", "risk", "annotation")


def short_module(key):
    if key.startswith("cyclonedx-") and key.endswith("-2.0"):
        return key[len("cyclonedx-"):-len("-2.0")]
    return key


def label(parts):
    """Field label: ('useCases', 0, 'flows', 2) or ('useCases', '[]', ...) -> 'useCases[].flows[]'."""
    out = ""
    for p in parts:
        if isinstance(p, int) or p == "[]":
            out += "[]"
        else:
            out += f".{p}" if out else p
    return out


def fmt(path):
    out = ""
    for p in path:
        out += f"[{p}]" if isinstance(p, int) else (f".{p}" if out else p)
    return out or "(root)"


def clip(text, limit=TEXT_LIMIT):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


class Schema:
    """Lookups on the bundled schema shared by the BOM and schema maps."""

    def __init__(self, schema):
        self.root = schema
        self._props = {}

    def resolve(self, ref):
        node = self.root
        for part in ref.lstrip("#/").split("/"):
            node = node[part]
        return node

    def props(self, node, seen=()):
        """Properties of an object definition, including those it takes through allOf."""
        out = dict(node.get("properties", {}))
        for branch in node.get("allOf", []):
            if not isinstance(branch, dict):
                continue
            ref = branch.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/") and ref not in seen:
                out.update(self.props(self.resolve(ref), seen + (ref,)))
            out.update(self.props(branch, seen))
        return out

    def object_key(self, ref):
        """'module:object' for a $ref to an object definition, else None."""
        if ref in self._props:
            return self._props[ref][0]
        m = OBJ.match(ref)
        key = None
        if m:
            node = self.resolve(ref)
            if self.props(node):
                key = f"{short_module(m.group(1))}:{m.group(2)}"
        self._props[ref] = (key,)
        return key

    def declares_refid(self, key):
        if key == ROOT_KEY:
            return False
        module, obj = key.split(":", 1)
        node = self.root["$defs"][f"cyclonedx-{module}-2.0"]["$defs"][obj]
        return "refId" in self.props(node)


# ------------------------------------------------------------ BOM analysis ---

def walk_bom(doc, schema):
    """Walk a BOM alongside the schema.

    Returns (refs, types):
      refs   list of (path, value, kind, (object_key, field_parts)), kind as in
             validate_bom.find_refs ('local', 'bomlink' or 'misplaced'), plus the
             schema object and field the reference was found in;
      types  path -> schema object keys the value at that path was matched to.
    The (path, value, kind) triples equal validate_bom.find_refs; the tests check it.
    """
    refs, seen = [], set()
    types = collections.defaultdict(list)

    def visit(inst, node, path, ctx, depth=0):
        if depth > 60 or not isinstance(node, dict):
            return
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/"):
            kind = REF_KINDS.get(ref.rsplit("/", 1)[-1])
            if kind and isinstance(inst, str):
                is_link = inst.startswith("urn:cdx:")
                if kind == "local" and is_link:
                    found = "misplaced"
                elif kind == "bomlink" and not is_link:
                    found = None
                else:
                    found = "bomlink" if is_link else "local"
                if found:
                    key = (tuple(path), inst, found)
                    if key not in seen:
                        seen.add(key)
                        refs.append((list(path), inst, found, ctx))
                return
            okey = schema.object_key(ref)
            inner = ctx
            if okey:
                if isinstance(inst, dict) and okey not in types[tuple(path)]:
                    types[tuple(path)].append(okey)
                if ctx[1]:  # a new object; at the same path it is a base the outer object extends
                    inner = (okey, ())
            visit(inst, schema.resolve(ref), path, inner, depth + 1)
        for kw in ("allOf", "oneOf", "anyOf"):
            for branch in node.get(kw, []):
                visit(inst, branch, path, ctx, depth + 1)
        if "then" in node:
            visit(inst, node["then"], path, ctx, depth + 1)
        if isinstance(inst, dict):
            props = node.get("properties", {})
            for k, v in inst.items():
                if k in props:
                    visit(v, props[k], path + [k], (ctx[0], ctx[1] + (k,)), depth + 1)
        elif isinstance(inst, list) and isinstance(node.get("items"), dict):
            for i, v in enumerate(inst):
                visit(v, node["items"], path + [i], (ctx[0], ctx[1] + ("[]",)), depth + 1)

    visit(doc, schema.root, [], (ROOT_KEY, ()))
    return refs, types


def declared(doc):
    """(path, object) for every object with a string refId, in document order."""
    out = []

    def walk(inst, path):
        if isinstance(inst, dict):
            if isinstance(inst.get("refId"), str):
                out.append((tuple(path), inst))
            for k, v in inst.items():
                walk(v, path + [k])
        elif isinstance(inst, list):
            for i, v in enumerate(inst):
                walk(v, path + [i])

    walk(doc, [])
    return out


def at(doc, path):
    node = doc
    for p in path:
        node = node[p]
    return node


def element_type(schema, candidates):
    for key in candidates:
        if schema.declares_refid(key):
            return key
    return candidates[0] if candidates else "unknown:element"


def display_name(obj):
    for key in ("name", "title", "text", "description"):
        if isinstance(obj.get(key), str) and obj[key].strip():
            return clip(obj[key], 90)
    return ""


def raw_json(obj):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    return text if len(text) <= JSON_LIMIT else text[:JSON_LIMIT] + "\n… (truncated)"


def doc_role(doc):
    return "threat-model" if any(doc.get(k) for k in ("threats", "controls", "risks")) else "system"


def use_case_of(doc):
    for prop in (doc.get("metadata") or {}).get("properties", []) or []:
        if isinstance(prop, dict) and prop.get("name") == "lfai:threat-model:use-case":
            return prop.get("value")
    return None


def display_path(path):
    try:
        rel = os.path.relpath(path)
    except ValueError:  # another drive on Windows
        return os.path.basename(path)
    return path if rel.startswith("..") and os.path.isabs(path) else rel.replace(os.sep, "/")


def analyse(paths, schema):
    """Build the page data for the BOMs at `paths`."""
    docs, elements, refs, copies, problems = [], [], [], [], []
    loaded = [(p, load_json(p)) for p in paths]
    by_serial = {}
    walked = []

    for i, (path, doc) in enumerate(loaded):
        m = SERIAL.match(str(doc.get("serialNumber", "")))
        serial = m.group(1) if m else None
        if serial:
            if serial in by_serial:
                problems.append({"sev": "error", "doc": i,
                                 "text": f"has the same serialNumber as {display_path(loaded[by_serial[serial]][0])}"})
            else:
                by_serial[serial] = i
        else:
            problems.append({"sev": "info", "doc": i,
                             "text": "has no serialNumber, so no other BOM can BOM-Link to it"})
        docs.append({"i": i, "name": os.path.basename(path), "path": display_path(path), "serial": serial,
                     "version": str(doc.get("version", 1)), "role": doc_role(doc), "useCase": use_case_of(doc)})
        walked.append(walk_bom(doc, schema))

    # Declared elements, keyed "doc|path".
    ids = []  # per doc: refId -> element key (first declaration)
    for i, (path, doc) in enumerate(loaded):
        doc_ids = {}
        types = walked[i][1]
        for p, obj in declared(doc):
            key = f"{i}|{fmt(p)}"
            rid = obj["refId"]
            if rid in doc_ids:
                problems.append({"sev": "error", "doc": i, "el": key,
                                 "text": f"refId '{rid}' is declared more than once (first at {doc_ids[rid].split('|', 1)[1]})"})
            else:
                doc_ids[rid] = key
            elements.append({"k": key, "d": i, "id": rid, "t": element_type(schema, types.get(p, [])),
                             "p": fmt(p), "n": display_name(obj),
                             "x": clip(obj["description"]) if isinstance(obj.get("description"), str) else "",
                             "j": raw_json(obj)})
        ids.append(doc_ids)
    element_paths = [{tuple(_parse(e["p"])) for e in elements if e["d"] == i} for i in range(len(loaded))]

    # References.
    pseudo = {}
    for i, (path, doc) in enumerate(loaded):
        doc_refs = walked[i][0]
        owners = element_paths[i]
        # Group references by the object that holds them, to find relationship-style
        # objects: {"ref": subject, "<kind>": [targets]} with no refId of their own.
        holders = collections.defaultdict(set)
        for p, _v, _k, _c in doc_refs:
            q = p[:-1] if isinstance(p[-1], int) else p
            holders[tuple(q[:-1])].add(q[-1])
        for p, value, kind, (okey, fparts) in doc_refs:
            owner = next((tuple(p[:n]) for n in range(len(p), -1, -1) if tuple(p[:n]) in owners), None)
            if owner is None:
                cut = next((n + 1 for n, x in enumerate(p) if isinstance(x, int)), 1)
                owner = tuple(p[:cut])
                pkey = f"{i}|{fmt(owner)}"
                if pkey not in pseudo:
                    obj = at(doc, owner)
                    obj = obj if isinstance(obj, dict) else {}
                    cands = walked[i][1].get(owner, [])
                    pseudo[pkey] = {"k": pkey, "d": i, "id": None, "t": cands[0] if cands else "unknown:element",
                                    "p": fmt(owner), "n": display_name(obj), "x": "", "j": raw_json(obj)}
            okey_el = f"{i}|{fmt(owner)}"
            q = p[:-1] if isinstance(p[-1], int) else p
            holder, field = tuple(q[:-1]), q[-1]
            source, via, flabel = okey_el, None, label(p[len(owner):])
            fields_here = holders.get(holder, set())
            if holder != owner and "ref" in fields_here and len(fields_here) > 1 and field != "ref":
                subject = at(doc, holder).get("ref")
                if isinstance(subject, str) and subject in ids[i]:
                    source, via, flabel = ids[i][subject], okey_el, field
            rec = {"s": source, "f": flabel, "sf": f"{okey}.{label(fparts)}", "val": value,
                   "kind": kind, "p": fmt(p), "t": None, "st": "ok"}
            if via:
                rec["v"] = via
            if holder != owner and field == "ref" and len(fields_here) > 1:
                rec["role"] = "subject"
            resolve_ref(rec, i, value, kind, ids, by_serial, docs)
            refs.append(rec)
    elements.extend(pseudo.values())

    # Slice copies: elements of a threat-model BOM's system slice against the system BOM.
    for i, (path, doc) in enumerate(loaded):
        sys_i = None
        for r in doc.get("externalReferences", []) or []:
            m = BOMLINK.match(str(r.get("url", ""))) if r.get("type") == "bom" else None
            if m and m.group("serial") in by_serial and by_serial[m.group("serial")] != i:
                sys_i = by_serial[m.group("serial")]
                break
            if m:
                problems.append({"sev": "info", "doc": i, "text": f"links to BOM urn:cdx:{m.group('serial')}, "
                                 "which is not loaded; pass it too to see the references across them"})
        if sys_i is None:
            continue
        docs[i]["system"] = sys_i
        system = loaded[sys_i][1]
        sys_serial = docs[sys_i]["serial"]
        back = [r for r in system.get("externalReferences", []) or []
                if r.get("type") == "threat-model" and BOMLINK.match(str(r.get("url", "")))
                and BOMLINK.match(r["url"]).group("serial") == docs[i]["serial"]]
        if not back:
            problems.append({"sev": "warn", "doc": i, "text": f"{docs[sys_i]['name']} has no threat-model external "
                             "reference to this TM-BOM (slice_use_case.py --link adds one)"})
        elif BOMLINK.match(back[0]["url"]).group("version") != docs[i]["version"]:
            problems.append({"sev": "warn", "doc": i, "text": f"{docs[sys_i]['name']} links to version "
                             f"{BOMLINK.match(back[0]['url']).group('version')} of this TM-BOM, "
                             f"which is now version {docs[i]['version']}"})
        sys_objs = objects_by_refid(system, SLICE_SECTIONS)
        containers = {b.get("refId") for b in doc.get("blueprints", []) if isinstance(b, dict)}
        for rid, (section, obj) in objects_by_refid(doc, SLICE_SECTIONS).items():
            here = ids[i].get(rid)
            if rid not in sys_objs or rid not in ids[sys_i]:
                problems.append({"sev": "error", "doc": i, "el": here,
                                 "text": f"'{rid}' is in the system slice ({section}) but not in {docs[sys_i]['name']}"})
                continue
            diff = None
            if rid not in containers:
                d = slice_difference(obj, sys_objs[rid][1], section, sys_serial)
                if d:
                    where, a, b = d
                    diff = (f"{where or '(object)'}: {clip(json.dumps(a, ensure_ascii=False), 120)} here, "
                            f"{clip(json.dumps(b, ensure_ascii=False), 120)} in the system BOM")
            copies.append({"a": here, "b": ids[sys_i][rid], "drift": diff})
            if diff:
                problems.append({"sev": "error", "doc": i, "el": here,
                                 "text": f"'{rid}' differs from {docs[sys_i]['name']} at {diff}"})

    for r in refs:
        sev = {"dangling": "error", "misplaced": "error", "malformed": "error", "bad-fragment": "error",
               "old-version": "warn", "not-loaded": "info"}.get(r["st"])
        if sev:
            problems.append({"sev": sev, "doc": int(r["s"].split("|", 1)[0]), "el": r["s"],
                             "text": f"{r['p']}: {STATUS_TEXT[r['st']].format(v=r['val'])}"})

    types = {e["t"] for e in elements}
    return {"docs": docs, "elements": elements, "refs": refs, "copies": copies, "problems": problems,
            "types": {t: {"label": t.split(":", 1)[1], "module": t.split(":", 1)[0]} for t in sorted(types)}}


STATUS_TEXT = {
    "dangling": "'{v}' does not match any refId in this document",
    "misplaced": "BOM-Link '{v}' is not allowed here; this field takes a refId in this document",
    "malformed": "malformed BOM-Link '{v}'",
    "bad-fragment": "the fragment of '{v}' is not a refId in the linked BOM",
    "old-version": "'{v}' links to an older version of the linked BOM",
    "not-loaded": "'{v}' links to a BOM that is not loaded",
}


def _parse(text):
    """Inverse of fmt for the paths this tool writes."""
    if text == "(root)":
        return []
    out = []
    for name, index in re.findall(r"([^.\[\]]+)|\[(\d+)\]", text):
        out.append(int(index) if index else name)
    return out


def resolve_ref(rec, i, value, kind, ids, by_serial, docs):
    if kind == "misplaced":
        rec["st"] = "misplaced"
        return
    if kind == "local":
        rec["t"] = ids[i].get(value)
        rec["st"] = "ok" if rec["t"] else "dangling"
        return
    m = BOMLINK.match(value)
    if not m:
        rec["st"] = "malformed"
        return
    target = by_serial.get(m.group("serial"))
    if target is None:
        rec["st"] = "not-loaded"
        return
    rec["td"] = target
    frag = m.group("ref")
    if frag:
        rec["t"] = ids[target].get(frag)
        if not rec["t"]:
            rec["st"] = "bad-fragment"
            return
    else:
        rec["st"] = "doc"
    if m.group("version") != docs[target]["version"]:
        rec["st"] = "old-version"


# --------------------------------------------------------- schema analysis ---

def schema_objects(schema):
    """Every object definition: fields, reference fields and contained objects."""
    objects = {}
    defs = [(ROOT_KEY, schema.root, "CycloneDX BOM", schema.root.get("description", ""))]
    for mkey, mod in schema.root["$defs"].items():
        for oname, node in mod.get("$defs", {}).items():
            if isinstance(node, dict) and schema.props(node):
                defs.append((f"{short_module(mkey)}:{oname}", node, node.get("title", ""), node.get("description", "")))

    for key, node, title, desc in defs:
        fields, contains = {}, {}

        def walk(n, fpath, fdesc, seen, top=False):
            if not isinstance(n, dict):
                return
            d = n.get("description") or fdesc
            ref = n.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/"):
                kind = REF_KINDS.get(ref.rsplit("/", 1)[-1])
                if kind:
                    f = fields.setdefault(label(fpath), {"f": label(fpath), "kinds": set(), "desc": clip(d or "", 400)})
                    f["kinds"].add(kind)
                    return
                okey = schema.object_key(ref)
                if okey and fpath and not top:
                    contains.setdefault(label(fpath), set()).add(okey)
                elif ref not in seen:
                    walk(schema.resolve(ref), fpath, d, seen | {ref}, top)
            for kw in ("allOf", "oneOf", "anyOf"):
                for b in n.get(kw, []):
                    walk(b, fpath, d, seen, top)
            for kw in ("then", "else"):
                walk(n.get(kw), fpath, d, seen, top)
            for k, v in n.get("properties", {}).items():
                walk(v, fpath + [k], v.get("description") if isinstance(v, dict) else None, seen)
            if isinstance(n.get("items"), dict):
                walk(n["items"], fpath + ["[]"], d, seen)

        walk(node, [], None, frozenset(), top=True)
        objects[key] = {
            "k": key, "m": key.split(":", 1)[0], "o": key.split(":", 1)[1], "title": title,
            "desc": clip(desc or "", 600), "refId": schema.declares_refid(key),
            "fields": [{"f": f["f"], "accepts": accepts(f["kinds"]), "desc": f["desc"]}
                       for f in sorted(fields.values(), key=lambda x: x["f"])],
            "contains": [{"f": f, "t": sorted(ts)} for f, ts in sorted(contains.items())],
        }

    # Where each object sits in a BOM. Collect paths from the root, then show at
    # most three: lists of the object first (where it is declared, such as
    # definitions.components[]), then the shortest.
    found = collections.defaultdict(list)
    queue = collections.deque([(ROOT_KEY, "")])
    while queue:
        key, where = queue.popleft()
        if where.count(".") > 8:
            continue
        for c in objects.get(key, {}).get("contains", []):
            nxt = f"{where}.{c['f']}" if where else c["f"]
            for t in c["t"]:
                if t != ROOT_KEY and len(found[t]) < 12 and nxt not in found[t]:
                    found[t].append(nxt)
                    queue.append((t, nxt))
    for key, obj in objects.items():
        paths = sorted(found.get(key, []), key=lambda p: (not p.endswith("[]"), p.count(".") + p.count("[]"), p))
        obj["at"] = paths[:3]
    return objects


def accepts(kinds):
    if "either" in kinds or {"local", "bomlink"} <= kinds:
        return "either"
    return "bomlink" if kinds == {"bomlink"} else "local"


def schema_data(schema, bom_data, observed_from):
    objects = schema_objects(schema)
    types = {e["k"]: e["t"] for e in bom_data["elements"]}
    observed = collections.defaultdict(collections.Counter)
    for r in bom_data["refs"]:
        if r["t"]:
            observed[r["sf"]][types[r["t"]]] += 1
    order = {m: n for n, m in enumerate(MODULE_ORDER)}
    modules = sorted({o["m"] for o in objects.values() if o["m"] != "root"}, key=lambda m: (order.get(m, 99), m))
    common = schema.root["$defs"].get("cyclonedx-common-2.0", {}).get("$defs", {})
    return {
        "objects": objects,
        "modules": ["root"] + modules,
        "observed": {sf: dict(c.most_common()) for sf, c in sorted(observed.items())},
        "observedFrom": observed_from,
        "refKinds": {name: {"accepts": kind, "desc": clip(common.get(name, {}).get("description", ""), 400)}
                     for name, kind in REF_KINDS.items()},
    }


# ------------------------------------------------------------------ output ---

def render(data):
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    # Keep BOM text from closing the script element or opening a comment.
    blob = blob.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    blob = blob.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    marker = "/*__DATA__*/null"
    if marker not in page:
        sys.exit(f"{TEMPLATE} has no data marker")
    return page.replace(marker, blob, 1)


def write(path, text):
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(2000)
        if f'content="{GENERATOR}"' not in head:
            sys.exit(f"{path} exists and was not written by this tool; choose another -o")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--schema", default=DEFAULT_SCHEMA, help="bundled CycloneDX 2.0 schema")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bom", help="map one or more BOMs and the schema")
    b.add_argument("boms", nargs="+", help="system BOM and threat-model BOMs")
    b.add_argument("-o", "--output", default="bom-map.html")
    s = sub.add_parser("schema", help="map the schema only")
    s.add_argument("--observe", nargs="+", metavar="BOM",
                   default=[os.path.join(EXAMPLES, "system-bom.code-assistant.json"),
                            os.path.join(EXAMPLES, "tm-bom.code-assistant-1b.json")],
                   help="BOMs to take observed reference targets from (default: the examples)")
    s.add_argument("-o", "--output", default="schema-map.html")
    args = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    schema = Schema(load_json(args.schema))
    paths = args.boms if args.cmd == "bom" else args.observe
    for path in paths:
        doc = load_json(path)
        if doc.get("specFormat") != "CycloneDX" or str(doc.get("specVersion")) != "2.0":
            sys.exit(f"{path}: this tool maps CycloneDX 2.0 (specFormat 'CycloneDX', specVersion '2.0')")
    bom = analyse(paths, schema)
    data = {"mode": args.cmd, "generator": GENERATOR,
            "schema": schema_data(schema, bom, [os.path.basename(x) for x in paths])}
    if args.cmd == "bom":
        data.update(bom)
    write(args.output, render(data))

    print(f"Wrote {args.output}")
    if args.cmd == "bom":
        sev = collections.Counter(x["sev"] for x in bom["problems"])
        print(f"  documents: {len(bom['docs'])}, elements: {sum(1 for e in bom['elements'] if e['id'])}, "
              f"references: {len(bom['refs'])}, slice copies: {len(bom['copies'])}")
        print(f"  problems: {sev['error']} error(s), {sev['warn']} warning(s), {sev['info']} note(s)")
    print("  Open it in a browser; it needs no network access.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
