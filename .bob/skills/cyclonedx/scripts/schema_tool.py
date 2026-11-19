#!/usr/bin/env python3
"""Navigate the bundled CycloneDX 2.0 JSON schema one module at a time.

The bundled schema (schema/2.0/cyclonedx-2.0-bundled.schema.json) is about
1 MB.  Agents should not read it whole.  This tool prints the part they need.

Usage:
  schema_tool.py modules
      List every module in the bundle and the objects it defines.
  schema_tool.py outline <module>[:<object>] [...]
      Print the fields, required fields, enumerations and descriptions of a
      module (all its objects) or of one object, as Markdown.
      Examples:  outline threat            outline blueprint:flow
  schema_tool.py write-references [--check]
      Regenerate reference/system-schema.md and reference/tm-schema.md from
      the bundled schema (or, with --check, fail if they are out of date).
  schema_tool.py extract <module>:<object> [-o FILE]
      Write a standalone JSON schema whose root is that object, carrying only
      the definitions it needs.  Use it to validate a fragment such as a
      `threats` block on its own.
      Example:  extract threat:threats -o threats.schema.json

Options:
  --schema PATH   Use a different bundled schema file.

Module names drop the "cyclonedx-" prefix and "-2.0" suffix, so
"cyclonedx-blueprint-2.0" is "blueprint".  Standard library only.
"""

import argparse
import copy
import json
import os
import sys

DEFAULT_SCHEMA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "schema", "2.0", "cyclonedx-2.0-bundled.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def module_key(name):
    return name if name.startswith("cyclonedx-") else f"cyclonedx-{name}-2.0"


def short_module(key):
    return key[len("cyclonedx-"):-len("-2.0")] if key.startswith("cyclonedx-") and key.endswith("-2.0") else key


def resolve(root, ref):
    node = root
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def ref_label(ref):
    """'#/$defs/cyclonedx-common-2.0/$defs/refLinkType' -> 'common:refLinkType'."""
    if not ref.startswith("#/$defs/"):
        return ref
    parts = ref[len("#/$defs/"):].split("/$defs/")
    if len(parts) == 2:
        return f"{short_module(parts[0])}:{parts[1]}"
    return short_module(parts[0])


def describe_type(node, root, depth=0):
    """A one-line human summary of a schema node's type."""
    if not isinstance(node, dict):
        return "?"
    if "$ref" in node:
        label = ref_label(node["$ref"])
        if label in ("common:refLinkType",):
            return "ref (refId in this document)"
        if label in ("common:elementLink", "common:bomLink"):
            return "ref (refId or BOM-Link)"
        if label == "common:bomLinkElementType":
            return "BOM-Link element (urn:cdx:...#ref)"
        if label == "common:refIdType":
            return "refId"
        # Inline small enums behind a $ref so the outline is useful on its own.
        if depth < 1 and node["$ref"].startswith("#"):
            target = resolve(root, node["$ref"])
            inner = enum_summary(target, root)
            if inner:
                return f"{label} — {inner}"
        return f"→ {label}"
    if "const" in node:
        return f"const {json.dumps(node['const'])}"
    summary = enum_summary(node, root)
    if summary:
        return summary
    t = node.get("type")
    if t == "array":
        return f"array of {describe_type(node.get('items', {}), root, depth)}"
    for kw in ("oneOf", "anyOf"):
        if kw in node:
            return " | ".join(describe_type(b, root, depth + 1) for b in node[kw])
    if "allOf" in node and len(node["allOf"]) == 1:
        return describe_type(node["allOf"][0], root, depth)
    if isinstance(t, list):
        return " | ".join(t)
    return t or "object"


def enum_summary(node, root, depth=0):
    """Summarize an enumeration, showing whether values are plain strings or wrapped in an object.

    'enum: a, b'                                   plain string values
    'enum: a, b — or custom {name, description}'   plain string, or a custom object
    '{type: enum a, b} — or custom {name, …}'      the value must be an object wrapping the enum
    Returns None when the node is not an enumeration.
    """
    if not isinstance(node, dict) or depth > 3:
        return None
    if "enum" in node:
        return "enum: " + ", ".join(map(str, node["enum"]))
    branches = node.get("oneOf") or node.get("anyOf")
    if not branches:
        return None
    plain, wrapped, custom = [], None, None
    for b in branches:
        if isinstance(b, dict) and "$ref" in b and b["$ref"].startswith("#"):
            target = resolve(root, b["$ref"])
            # A branch that is a full object (a component, a reference) is not an enumeration.
            if len((target or {}).get("properties", {})) > 3:
                return None
        if isinstance(b, dict) and "$ref" in b:
            b = resolve(root, b["$ref"]) if b["$ref"].startswith("#") else {}
        if not isinstance(b, dict):
            return None
        if "enum" in b:
            plain.extend(b["enum"])
            continue
        props = b.get("properties") if b.get("type") == "object" or "properties" in b else None
        if props:
            enum_props = {k: v for k, v in props.items() if isinstance(v, dict) and (
                "enum" in v or ("$ref" in v and enum_summary(resolve(root, v["$ref"]), root, depth + 1)))}
            if enum_props and wrapped is None:
                k, v = next(iter(enum_props.items()))
                inner = v if "enum" in v else resolve(root, v["$ref"])
                inner_text = enum_summary(inner, root, depth + 1) or ""
                others = [p for p in props if p != k]
                wrapped = "{" + f"{k}: {inner_text}" + (", " + ", ".join(others) if others else "") + "}"
            else:
                custom = "{" + ", ".join(props.keys()) + "}"
            continue
        if b.get("type") == "string":
            return None
    if wrapped:
        return wrapped + (f" — or custom {custom}" if custom else "")
    if not plain:
        return None
    text = "enum: " + ", ".join(map(str, plain))
    if custom:
        text += f" — or custom {custom}"
    return text


def clip(text, limit=240):
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def outline_object(name, node, root, out):
    out.append(f"### `{name}`\n")
    desc = node.get("description") or node.get("title")
    if desc:
        out.append(clip(desc, 600) + "\n")
    if node.get("type") == "array" or ("$ref" in node and "properties" not in node):
        out.append(f"Type: {describe_type(node, root)}\n")
        return
    # A union with no fields of its own (oneOf/anyOf of enums or objects): show each variant.
    branches = node.get("oneOf") or node.get("anyOf")
    if branches and "properties" not in node:
        out.append("One of:")
        for b in branches:
            target = resolve(root, b["$ref"]) if isinstance(b, dict) and str(b.get("$ref", "")).startswith("#") else b
            label = ref_label(b["$ref"]) if isinstance(b, dict) and "$ref" in b else (target.get("title") or "variant")
            if isinstance(target, dict) and "enum" in target:
                out.append(f"- {label}: a plain string, enum: " + ", ".join(map(str, target["enum"])))
            elif isinstance(target, dict) and target.get("properties"):
                fields = ", ".join(f"`{k}`" for k in target["properties"])
                req = ", ".join(f"`{k}`" for k in target.get("required") or [])
                inner = enum_summary(target, root)
                out.append(f"- {label}: an object with {fields}" + (f" (required: {req})" if req else "")
                           + (f"; {inner}" if inner else ""))
            else:
                out.append(f"- {label}: {describe_type(target, root)}")
        out.append("")
        return
    req = node.get("required")
    if req:
        out.append("Required: " + ", ".join(f"`{r}`" for r in req) + "\n")
    for kw in ("oneOf", "anyOf"):
        alts = [b.get("required") for b in node.get(kw, []) if isinstance(b, dict) and b.get("required")]
        if alts and "properties" in node:
            label = "Exactly one of" if kw == "oneOf" else "At least one of"
            out.append(f"{label}: " + " | ".join("{" + ", ".join(a) + "}" for a in alts) + "\n")
    props = node.get("properties")
    if props:
        out.append("| Field | Type | Description |")
        out.append("|---|---|---|")
        for k, v in props.items():
            t = describe_type(v, root).replace("|", "\\|")
            d = clip(v.get("description") or v.get("title"), 200).replace("|", "\\|")
            out.append(f"| `{k}` | {t} | {d} |")
        out.append("")
    conditional = False
    for cond in node.get("allOf", []):
        if not (isinstance(cond, dict) and isinstance(cond.get("if"), dict) and isinstance(cond.get("then"), dict)):
            continue
        ifp = cond["if"].get("properties", {})
        conds = ", ".join(f"{k} = {json.dumps(v.get('const'))}" for k, v in ifp.items()
                          if isinstance(v, dict) and "const" in v)
        for k, v in cond["then"].get("properties", {}).items():
            s = enum_summary(v, root) if isinstance(v, dict) else None
            if s and conds:
                out.append(f"- When {conds}: `{k}` {s}")
                conditional = True
    if conditional:
        out.append("")
    # Nested object arrays declared inline (e.g. threat.categories items)
    for k, v in (props or {}).items():
        items = v.get("items") if isinstance(v, dict) else None
        if isinstance(items, dict) and items.get("type") == "object" and "properties" in items:
            outline_object(f"{name}.{k}[]", items, root, out)


REFERENCE_DOCS = {
    "system-schema.md": {
        "title": "CycloneDX 2.0 system schema reference (system BOM)",
        "intro": "The modules a **system BOM** uses: `blueprint` (zones, boundaries, actors, flows, relationships), "
                 "`usecase`, `definitions`, `inventories`/`component`, and `party`.",
        "targets": ["blueprint", "usecase:useCases", "usecase:useCase", "usecase:step", "usecase:flow",
                    "usecase:exception", "definition:definitions", "component:inventory", "component:component",
                    "component:componentReference", "party:party", "party:partyReference", "party:persona",
                    "party:system", "party:role"],
    },
    "tm-schema.md": {
        "title": "CycloneDX 2.0 threat-model schema reference (TM-BOM)",
        "intro": "The modules a **threat-model BOM** uses: `threat`, `control`, the core of `risk`, `weakness`, "
                 "and `standard` (for control catalogues such as NIST SP 800-53 and CSA AICM).",
        "targets": ["threat", "control", "risk:risks", "risk:risk", "risk:damageScenario", "risk:rating",
                    "risk:likelihood", "risk:impact", "risk:riskResponse", "risk:riskAttribute",
                    "weakness:weakness", "weakness:weaknessReference", "weakness:weaknessIdentifier",
                    "standard:standard", "standard:requirement", "common:externalReference"],
    },
}


def render_reference(root, name):
    spec = REFERENCE_DOCS[name]
    body = outline_text(root, spec["targets"])
    return (
        "<!-- GENERATED from schema/2.0/cyclonedx-2.0-bundled.schema.json. Do not edit by hand; regenerate with:\n"
        "     python .bob/skills/cyclonedx/scripts/schema_tool.py write-references -->\n"
        f"# {spec['title']}\n\n"
        f"{spec['intro']} Generated from the bundled schema, so it is exact for this copy of the schema. "
        "For any other module, run `python .bob/skills/cyclonedx/scripts/schema_tool.py outline <module>`.\n\n"
        "In the Type column, `enum: a, b` means a plain string value, `{role: enum: …}` means an object that "
        "wraps the value (for example `{ \"role\": \"developer\" }`), and `or custom {name, description}` means "
        "a custom object is also accepted.\n\n"
        f"{body}\n"
    )


def cmd_write_references(root, args):
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reference")
    for name in REFERENCE_DOCS:
        path = os.path.normpath(os.path.join(folder, name))
        text = render_reference(root, name)
        if args.check:
            with open(path, encoding="utf-8") as f:
                current = f.read().replace("\r\n", "\n")
            if current != text:
                sys.exit(f"{path} is out of date; run: python .bob/skills/cyclonedx/scripts/schema_tool.py write-references")
            print(f"{path} is current")
        else:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(f"Wrote {path}")


def cmd_modules(root, _args):
    for key, mod in root["$defs"].items():
        names = list(mod.get("$defs", {}).keys())
        print(f"{short_module(key)}: {', '.join(names)}")


def cmd_outline(root, args):
    print(outline_text(root, args.targets))


def outline_text(root, targets):
    out = []
    for target in targets:
        mod, _, obj = target.partition(":")
        key = module_key(mod)
        if key not in root["$defs"]:
            sys.exit(f"Unknown module '{mod}'. Run 'schema_tool.py modules' to list them.")
        defs = root["$defs"][key].get("$defs", {})
        if obj:
            if obj not in defs:
                sys.exit(f"Unknown object '{obj}' in module '{mod}'. It has: {', '.join(defs)}")
            outline_object(f"{short_module(key)}:{obj}", defs[obj], root, out)
        else:
            out.append(f"## Module `{short_module(key)}` ({key})\n")
            for name, node in defs.items():
                outline_object(f"{short_module(key)}:{name}", node, root, out)
    return "\n".join(out)


def collect_refs(node, acc):
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            acc.add(ref)
        for v in node.values():
            collect_refs(v, acc)
    elif isinstance(node, list):
        for v in node:
            collect_refs(v, acc)


def cmd_extract(root, args):
    mod, _, obj = args.target.partition(":")
    key = module_key(mod)
    if not obj or key not in root["$defs"] or obj not in root["$defs"][key].get("$defs", {}):
        sys.exit("Give a target as <module>:<object>, e.g. threat:threats. Run 'modules' to list them.")
    start = f"#/$defs/{key}/$defs/{obj}"
    seen, todo = set(), [start]
    while todo:
        ref = todo.pop()
        if ref in seen:
            continue
        seen.add(ref)
        found = set()
        collect_refs(resolve(root, ref), found)
        todo.extend(found - seen)
    defs = {}
    for ref in sorted(seen):
        parts = ref[len("#/$defs/"):].split("/$defs/")
        if len(parts) != 2:
            continue
        m, o = parts
        defs.setdefault(m, {"$defs": {}})["$defs"][o] = copy.deepcopy(root["$defs"][m]["$defs"][o])
    for m in defs:
        title = root["$defs"][m].get("title")
        if title:
            defs[m]["title"] = title
    schema = {
        "$schema": root.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "$id": root["$id"].replace("bundled.schema.json", f"extract-{short_module(key)}-{obj}.schema.json"),
        "title": f"CycloneDX 2.0 extract: {short_module(key)}:{obj}",
        "$comment": f"Extracted from {os.path.basename(args.schema)} by schema_tool.py. "
                    "Regenerate rather than edit. External $refs (SPDX, crypto, behavior taxonomies) are left as in the bundle.",
        "$ref": start,
        "$defs": defs,
    }
    text = json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
    if args.output and args.output != "-":
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"Wrote {args.output} ({len(seen)} definitions, {len(text) // 1024} KB)", file=sys.stderr)
    else:
        sys.stdout.write(text)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--schema", default=DEFAULT_SCHEMA, help="path to the bundled CycloneDX 2.0 schema")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("modules", help="list modules and their objects")
    o = sub.add_parser("outline", help="print a module or object outline as Markdown")
    o.add_argument("targets", nargs="+", metavar="module[:object]")
    w = sub.add_parser("write-references", help="regenerate reference/system-schema.md and reference/tm-schema.md")
    w.add_argument("--check", action="store_true", help="fail if the files are out of date instead of writing")
    e = sub.add_parser("extract", help="write a standalone schema for one object")
    e.add_argument("target", metavar="module:object")
    e.add_argument("-o", "--output", help="output file (default: stdout)")
    args = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = load(args.schema)
    {"modules": cmd_modules, "outline": cmd_outline, "extract": cmd_extract,
     "write-references": cmd_write_references}[args.cmd](root, args)


if __name__ == "__main__":
    main()
