#!/usr/bin/env python3
"""Fetch the threat catalogues the threat-model workflow sweeps, as ID + title + URL.

Writes one CSV per catalogue to reference/catalogues/, plus catalogues.json
(the index: edition, item count, source, licence and fetch date). Only
identifiers, titles and links are kept: the OWASP lists are CC BY-SA 4.0, and
the MITRE lists require their copyright notice in every copy (it is kept in
catalogues.json and in each CSV's header comment).

Usage (from the repository root, needs network access):
  python .bob/skills/cyclonedx/scripts/fetch_catalogues.py           # fetch all
  python .bob/skills/cyclonedx/scripts/fetch_catalogues.py --only cwe

Editions: the OWASP lists are pinned to the edition named below. MITRE
ATLAS, MITRE ATT&CK and CWE are fetched at their current release, and the
release fetched is recorded in catalogues.json; rerun and review the diff to
move to a newer one.

Catalogues marked "pending" in CATALOGUES (awaiting a licence decision) are
not fetched by default; name them with --only to fetch them anyway.

Each catalogue is written to a temporary file first and the index is updated
only after all requested catalogues succeed, so a failure leaves the existing
files unchanged.

Standard library only, except PyYAML for ATLAS and pypdf for the agentic
Top 10 (pip install pyyaml pypdf); if one is missing, that catalogue is
skipped with a message.
"""

import argparse
import csv
import datetime
import html
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "reference", "catalogues"))
UA = {"User-Agent": "cyclonedx-skill-catalogue-fetch"}

OWASP_LICENCE = ("CC BY-SA 4.0 (OWASP Foundation), https://creativecommons.org/licenses/by-sa/4.0/. "
                 "IDs, titles and links only are copied.")
# The MITRE terms require the copyright designation and the licence text in every copy, so both are reproduced.
MITRE_ATTACK_NOTICE = (
    "\u00a9 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE "
    "Corporation. ATT&CK\u00ae is a registered trademark of The MITRE Corporation. Licence "
    "(https://attack.mitre.org/resources/legal-and-branding/terms-of-use/): The MITRE Corporation (MITRE) hereby "
    "grants you a non-exclusive, royalty-free license to use ATT&CK\u00ae for research, development, and commercial "
    "purposes. Any copy you make for such purposes is authorized provided that you reproduce MITRE's copyright "
    "designation and this license in any such copy.")
MITRE_CWE_NOTICE = (
    "Copyright \u00a9 The MITRE Corporation. CWE is a trademark of The MITRE Corporation. Licence "
    "(https://cwe.mitre.org/about/termsofuse.html): The MITRE Corporation hereby grants you a non-exclusive, "
    "royalty-free license to use CWE for research, development, and commercial purposes. Any copy you make for "
    "such purposes is authorized on the condition that you reproduce MITRE's copyright designation and this "
    "license in any such copy.")


def get(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", errors="replace")


# ------------------------------------------------------------- catalogues ---
# Each returns a list of {"id", "title", "url"} rows, plus optional "group".

def owasp_web():
    base = "https://api.github.com/repos/OWASP/Top10/contents/2025/docs/en"
    names = [x["name"] for x in json.loads(get(base))]
    rows = []
    for n in sorted(names):
        m = re.match(r"(A\d{2})_2025-(.+)\.md$", n)
        if m:
            rows.append({"id": f"{m.group(1)}:2025", "title": m.group(2).replace("_", " "),
                         "url": f"https://owasp.org/Top10/2025/{m.group(1)}_2025-{m.group(2)}/"})
    return rows


def owasp_api():
    text = get("https://raw.githubusercontent.com/OWASP/API-Security/master/editions/2023/en/0x11-t10.md")
    links = dict(re.findall(r"^\[(api\d+)\]:\s*(\S+)", text, re.M))
    rows = []
    for ident, title, key in re.findall(r"\|\s*\[(API\d+:2023) - ([^\]]+)\]\[(api\d+)\]", text):
        slug = links.get(key, "").replace(".md", "")
        rows.append({"id": ident, "title": title.strip(),
                     "url": f"https://owasp.org/API-Security/editions/2023/en/{slug}/"})
    return rows


def owasp_llm():
    text = html.unescape(get("https://genai.owasp.org/llm-top-10/"))
    found = {}
    for ident, title in re.findall(r"(LLM\d{2}):2025 ([A-Z][A-Za-z ,&-]{3,60}?)(?=<|\"|\n)", text):
        found.setdefault(ident, title.strip())
    return [{"id": f"{k}:2025", "title": v, "url": "https://genai.owasp.org/llm-top-10/"}
            for k, v in sorted(found.items())]


def mitre_atlas():
    try:
        import yaml
    except ImportError:
        print("  PyYAML is not installed; skipping ATLAS (pip install pyyaml)", file=sys.stderr)
        return None
    data = yaml.safe_load(get("https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml"))
    matrix = data["matrices"][0]
    rows = [{"id": t["id"], "title": t["name"], "group": "tactic",
             "url": f"https://atlas.mitre.org/tactics/{t['id']}"} for t in matrix["tactics"]]
    rows += [{"id": t["id"], "title": t["name"], "group": "technique",
              "url": f"https://atlas.mitre.org/techniques/{t['id']}"} for t in matrix["techniques"]]
    mitre_atlas.version = str(data.get("version", ""))
    return rows


def mitre_attack():
    index = json.loads(get("https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/index.json"))
    coll = next(c for c in index["collections"] if c["name"] == "Enterprise ATT&CK")
    version = coll["versions"][0]
    bundle = json.loads(get(version["url"]))
    rows = []
    for o in bundle["objects"]:
        if o.get("revoked") or o.get("x_mitre_deprecated"):
            continue
        if o["type"] not in ("x-mitre-tactic", "attack-pattern"):
            continue
        ref = next((r for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack"), None)
        if ref:
            rows.append({"id": ref["external_id"], "title": o["name"],
                         "group": "tactic" if o["type"] == "x-mitre-tactic" else "technique",
                         "url": ref.get("url", "")})
    rows.sort(key=lambda r: (r["group"] != "tactic", r["id"]))
    mitre_attack.version = version["version"]
    return rows


def mitre_cwe():
    raw = get("https://cwe.mitre.org/data/csv/2000.csv.zip", binary=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        text = z.read(z.namelist()[0]).decode("utf-8", errors="replace")
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        # Deprecated entries are kept and marked, so the validator can say "deprecated" rather than "unknown".
        rows.append({"id": f"CWE-{r['CWE-ID']}", "title": r["Name"],
                     "group": "deprecated" if r.get("Status") == "Deprecated" else "",
                     "url": f"https://cwe.mitre.org/data/definitions/{r['CWE-ID']}.html"})
    page = get("https://cwe.mitre.org/data/downloads.html")
    m = re.search(r"CWE List Version ([0-9.]+)", page)
    mitre_cwe.version = m.group(1) if m else ""
    return rows


def owasp_agentic():
    """OWASP Top 10 for Agentic Applications 2026. Published only as a PDF, so needs pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("  pypdf is not installed; skipping the agentic Top 10 (pip install pypdf)", file=sys.stderr)
        return None
    import logging
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    page = get("https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/")
    m = re.search(r'href="(https://genai\.owasp\.org/download/\d+/[^"]*)"', page)
    if not m:
        sys.exit("Could not find the agentic Top 10 PDF download link on its resource page.")
    reader = PdfReader(io.BytesIO(get(html.unescape(m.group(1)), binary=True)))
    text = "\n".join((p.extract_text() or "") for p in reader.pages[:6])  # table of contents
    found = {}
    for ident, title in re.findall(r"\b(ASI\d{2}): ([^\n]+?) \d+\s*\n", text):
        found.setdefault(ident, title.strip())
    return [{"id": f"{k}:2026", "title": v,
             "url": "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/"}
            for k, v in sorted(found.items())]


def owasp_mcp():
    """OWASP MCP Top 10 (2025). The project lists itself as beta; it is pinned like the others."""
    text = get("https://raw.githubusercontent.com/OWASP/www-project-mcp-top-10/main/tab_top10.md")
    rows = []
    for num, title, path in re.findall(r"^## MCP0?(\d+):2025\s*[–-]\s*\[([^\]]+)\]\(([^)]+)\)", text, re.M):
        rows.append({"id": f"MCP{int(num):02d}:2025", "title": title.strip(),
                     "url": f"https://owasp.org/www-project-mcp-top-10/{path}"})
    return rows


CATALOGUES = {
    "owasp-agentic-top10": {"name": "OWASP Top 10 for Agentic Applications", "edition": "2026",
                            "fetch": owasp_agentic, "expect": 10, "licence": OWASP_LICENCE,
                            "source": "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/"},
    "owasp-mcp-top10": {"name": "OWASP MCP Top 10", "edition": "2025 (beta, v0.1)", "fetch": owasp_mcp,
                        "expect": 10,
                        "pending": "licence unresolved; see threat-model-policy.json catalogueDecisions.tool-server",
                        "licence": "CC-BY-SA-4.0 per the project's LICENSE.md (the project page says CC BY-NC-SA 4.0; "
                                   "this mismatch is unresolved). IDs and titles only are copied.",
                        "source": "https://owasp.org/www-project-mcp-top-10/"},
    "owasp-top10-web": {"name": "OWASP Top 10 (web applications)", "edition": "2025", "fetch": owasp_web,
                        "expect": 10, "licence": OWASP_LICENCE, "source": "https://owasp.org/Top10/2025/"},
    "owasp-api-top10": {"name": "OWASP API Security Top 10", "edition": "2023", "fetch": owasp_api,
                        "expect": 10, "licence": OWASP_LICENCE,
                        "source": "https://owasp.org/API-Security/editions/2023/en/0x11-t10/"},
    "owasp-llm-top10": {"name": "OWASP Top 10 for LLM Applications", "edition": "2025", "fetch": owasp_llm,
                        "expect": 10, "licence": OWASP_LICENCE, "source": "https://genai.owasp.org/llm-top-10/"},
    "mitre-atlas": {"name": "MITRE ATLAS", "edition": None, "fetch": mitre_atlas, "expect": None,
                    "licence": "Apache-2.0 (Copyright The MITRE Corporation), "
                               "https://github.com/mitre-atlas/atlas-data/blob/main/LICENSE",
                    "source": "https://github.com/mitre-atlas/atlas-data"},
    "mitre-attack-enterprise": {"name": "MITRE ATT&CK Enterprise", "edition": None, "fetch": mitre_attack,
                                "expect": None, "licence": MITRE_ATTACK_NOTICE,
                                "source": "https://github.com/mitre-attack/attack-stix-data"},
    "cwe": {"name": "CWE (Comprehensive CWE Dictionary, view 2000)", "edition": None, "fetch": mitre_cwe, "expect": None,
            "licence": MITRE_CWE_NOTICE, "source": "https://cwe.mitre.org/data/downloads.html"},
}


def write_csv(key, spec, rows, edition, suffix=""):
    path = os.path.join(OUT, f"{key}.csv{suffix}")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"# {spec['name']}, edition {edition}. Source: {spec['source']}\n")
        f.write(f"# {spec['licence']}\n")
        w = csv.DictWriter(f, fieldnames=["id", "title", "group", "url"], lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({"id": r["id"], "title": r["title"], "group": r.get("group", ""), "url": r["url"]})
    return path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--only", choices=sorted(CATALOGUES), action="append", help="fetch just these catalogues")
    args = p.parse_args(argv)
    os.makedirs(OUT, exist_ok=True)
    index_path = os.path.join(OUT, "catalogues.json")
    index = {}
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f).get("catalogues", {})
    today = datetime.date.today().isoformat()
    keys = args.only or [k for k, spec in CATALOGUES.items() if not spec.get("pending")]
    for k in CATALOGUES:
        if CATALOGUES[k].get("pending") and k not in keys:
            print(f"Skipping {CATALOGUES[k]['name']}: {CATALOGUES[k]['pending']}", file=sys.stderr)
    written = []  # (temporary path, final path)
    try:
        for key in keys:
            spec = CATALOGUES[key]
            print(f"Fetching {spec['name']}...", file=sys.stderr)
            rows = spec["fetch"]()
            if rows is None:
                continue
            edition = spec["edition"] or getattr(spec["fetch"], "version", "")
            if spec["expect"] and len(rows) != spec["expect"]:
                raise SystemExit(f"{spec['name']}: expected {spec['expect']} items, got {len(rows)}. "
                                 "The source may have changed; no catalogue files were changed.")
            tmp = write_csv(key, spec, rows, edition, suffix=".tmp")
            written.append((tmp, tmp[:-len(".tmp")]))
            index[key] = {"name": spec["name"], "edition": edition, "items": len(rows),
                          "file": f"{key}.csv", "source": spec["source"],
                          "licence": spec["licence"], "fetched": today}
            print(f"  {len(rows)} items, edition {edition}", file=sys.stderr)
    except BaseException:
        for tmp, _ in written:
            os.remove(tmp)
        raise
    for tmp, final in written:
        os.replace(tmp, final)
        print(f"Wrote {os.path.relpath(final)}", file=sys.stderr)
    with open(index_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"$comment": "Generated by scripts/fetch_catalogues.py. Do not edit by hand.",
                   "catalogues": dict(sorted(index.items()))}, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
