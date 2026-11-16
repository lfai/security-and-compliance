"""Regression tests for the CycloneDX skill scripts.

Run from the repository root:
    python -m pytest .bob/skills/cyclonedx/scripts/tests -q
Needs pytest and jsonschema (see ../requirements.txt).
"""

import copy
import json
import os
import subprocess
import sys

import pytest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.dirname(SCRIPTS)
EXAMPLES = os.path.join(SKILL, "examples")
SYSTEM = os.path.join(EXAMPLES, "system-bom.code-assistant.json")
TM = os.path.join(EXAMPLES, "tm-bom.code-assistant-1b.json")
UC_1B = "usecase:code-assistant-1b"


def run(script, *args):
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout + proc.stderr


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, doc):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    return path


@pytest.fixture
def system():
    return load(SYSTEM)


def blueprint(doc):
    return doc["blueprints"][0]


def component(doc, ref):
    return next(c for c in doc["definitions"]["components"] if c["refId"] == ref)


# ------------------------------------------------------------------ examples

def test_examples_validate():
    code, out = run("validate_bom.py", TM, "--system", SYSTEM)
    assert code == 0, out
    code, out = run("validate_bom.py", SYSTEM, "--linked", TM)
    assert code == 0, out


def test_working_group_bom_validates():
    wg = os.path.join(SKILL, "..", "..", "..", "subgroups", "use-cases-and-threat-models",
                      "use_cases", "code_assistant", "code_assistant_bom_2.0.json")
    code, out = run("validate_bom.py", wg)
    assert code == 0, out


def test_fresh_slice_matches_example(tmp_path):
    out_path = tmp_path / "tm.json"
    code, out = run("slice_use_case.py", SYSTEM, "--use-case", UC_1B, "-o", out_path)
    assert code == 0, out
    fresh, example = load(out_path), load(TM)
    assert fresh["blueprints"] == example["blueprints"]
    assert fresh["definitions"]["components"] == example["definitions"]["components"]
    assert fresh["definitions"]["useCases"] == example["definitions"]["useCases"]


def test_slice_refuses_to_overwrite(tmp_path):
    out_path = tmp_path / "tm.json"
    assert run("slice_use_case.py", SYSTEM, "--use-case", UC_1B, "-o", out_path)[0] == 0
    code, out = run("slice_use_case.py", SYSTEM, "--use-case", UC_1B, "-o", out_path)
    assert code != 0 and "--update" in out


def test_update_keeps_serial_and_threats(tmp_path):
    tm_path = save(tmp_path / "tm.json", load(TM))
    code, out = run("slice_use_case.py", SYSTEM, "--use-case", UC_1B, "-o", tm_path, "--update")
    assert code == 0, out
    before, after = load(TM), load(tm_path)
    assert after["serialNumber"] == before["serialNumber"]
    assert after["version"] == before["version"] + 1
    assert after["threats"] == before["threats"]
    assert after["controls"] == before["controls"]
    assert {p["refId"] for p in after["definitions"]["parties"]} >= {"party:external-attacker"}
    assert run("validate_bom.py", tm_path, "--system", SYSTEM)[0] == 0


# ----------------------------------------------- slices stay reference-closed

def slice_ok(tmp_path, system_doc):
    """Slice 1b from a modified system BOM; both must validate."""
    sys_path = save(tmp_path / "system.json", system_doc)
    code, out = run("validate_bom.py", sys_path)
    assert code == 0, "modified system BOM should be valid: " + out
    tm_path = tmp_path / "tm.json"
    code, out = run("slice_use_case.py", sys_path, "--use-case", UC_1B, "-o", tm_path)
    assert code == 0, out
    code, out = run("validate_bom.py", tm_path, "--system", sys_path)
    assert code == 0, out
    return load(tm_path)


def test_slice_includes_identifier_party(tmp_path, system):
    system["definitions"]["parties"] = [{"refId": "party:pypi", "roles": [{"role": "publisher"}],
                                         "organization": {"name": "PyPI"}}]
    component(system, "component:local-ide")["identifiers"] = [
        {"party": "party:pypi", "identities": [{"scheme": "purl", "value": "pkg:pypi/example@1.0"}]}]
    tm = slice_ok(tmp_path, system)
    assert "party:pypi" in {p["refId"] for p in tm["definitions"]["parties"]}


def test_slice_includes_zone_ancestors(tmp_path, system):
    zones = blueprint(system)["zones"]
    zones.append({"refId": "zone:site", "name": "Site", "type": "physical", "parent": "zone:corp"})
    zones.append({"refId": "zone:corp", "name": "Corp", "type": "organizational"})
    next(z for z in zones if z["refId"] == "zone:internal")["parent"] = "zone:site"
    tm = slice_ok(tmp_path, system)
    assert {"zone:site", "zone:corp"} <= {z["refId"] for z in blueprint(tm)["zones"]}


def test_slice_includes_actor_zone(tmp_path, system):
    blueprint(system)["zones"].append({"refId": "zone:office", "name": "Office", "type": "physical"})
    blueprint(system)["actors"][0]["zone"] = "zone:office"
    tm = slice_ok(tmp_path, system)
    assert "zone:office" in {z["refId"] for z in blueprint(tm)["zones"]}


def test_slice_trims_assumption_links(tmp_path, system):
    blueprint(system)["assumptions"] = [{"refId": "assumption:a1", "description": "x",
                                         "relatedAssets": ["component:local-ide", "component:rag-local"]}]
    tm = slice_ok(tmp_path, system)
    assert blueprint(tm)["assumptions"][0]["relatedAssets"] == ["component:local-ide"]


def test_slice_includes_nested_component(tmp_path, system):
    component(system, "component:local-ide")["components"] = [{"ref": "component:rag-local"}]
    tm = slice_ok(tmp_path, system)
    assert "component:rag-local" in {c["refId"] for c in tm["definitions"]["components"]}


def test_slice_drops_use_case_requirements(tmp_path, system):
    system["definitions"]["requirements"] = [{"refId": "requirement:r1", "name": "r1"}]
    uc = next(u for u in system["definitions"]["useCases"] if u["refId"] == UC_1B)
    uc["requirements"] = ["requirement:r1"]
    sys_path = save(tmp_path / "system.json", system)
    assert run("validate_bom.py", sys_path)[0] == 0
    tm_path = tmp_path / "tm.json"
    assert run("slice_use_case.py", sys_path, "--use-case", UC_1B, "-o", tm_path)[0] == 0
    assert "requirements" not in load(tm_path)["definitions"]["useCases"][0]


def test_slice_includes_asset_component(tmp_path, system):
    blueprint(system)["assets"] = [{"refId": "asset:rag", "componentRef": "component:rag-local"}]
    flow = blueprint(system)["flows"][0]
    flow["destination"] = "asset:rag"
    tm = slice_ok(tmp_path, system) if flow["refId"] in next(
        u for u in blueprint(system)["useCases"] if u["ref"] == UC_1B)["flows"] else None
    assert tm is not None
    assert "component:rag-local" in {c["refId"] for c in tm["definitions"]["components"]}


def test_relationships_have_one_kind(tmp_path, system):
    tm = slice_ok(tmp_path, system)
    kinds = {"aggregates", "associates", "composes", "contains", "dependsOn",
             "generalizes", "realizes", "serves", "custom"}
    for rel in blueprint(tm)["relationships"]:
        assert len(kinds & set(rel)) == 1, rel


# ----------------------------------------------------------- validator checks

def validate(tmp_path, doc, *extra):
    return run("validate_bom.py", save(tmp_path / "bom.json", doc), *extra)


def minimal(**extra):
    return {"specFormat": "CycloneDX", "specVersion": "2.0", **extra}


@pytest.mark.parametrize("no_schema", [False, True])
def test_bomlink_in_threat_reference_is_an_error(tmp_path, no_schema):
    doc = minimal(threats={"threats": [{"refId": "threat:x", "name": "x",
                                        "affects": ["urn:cdx:3e671687-395b-41f5-a30f-a58921a69b79/1#component:a"]}]})
    code, out = validate(tmp_path, doc, *(["--no-schema"] if no_schema else []))
    assert code == 1 and "not allowed here" in out


@pytest.mark.parametrize("no_schema", [False, True])
def test_v17_keys_are_errors(tmp_path, no_schema):
    doc = minimal(bomFormat="CycloneDX",
                  definitions={"components": [{"type": "library", "name": "a", "bom-ref": "a"}]})
    code, out = validate(tmp_path, doc, *(["--no-schema"] if no_schema else []))
    assert code == 1 and "bomFormat" in out and "bom-ref" in out


def test_two_relationship_kinds_is_an_error_without_schema(tmp_path):
    doc = minimal(definitions={"components": [{"type": "library", "name": "a", "refId": "c:a"},
                                              {"type": "library", "name": "b", "refId": "c:b"}]},
                  blueprints=[{"name": "b", "modelTypes": ["logical"],
                               "relationships": [{"ref": "c:a", "contains": ["c:b"], "dependsOn": ["c:b"]}]}])
    code, out = validate(tmp_path, doc, "--no-schema")
    assert code == 1 and "exactly one relationship kind" in out


def test_dangling_and_duplicate_refs(tmp_path, system):
    blueprint(system)["flows"][0]["source"] = "actor:nobody"
    system["definitions"]["components"][1]["refId"] = "component:local-ide"
    code, out = validate(tmp_path, system)
    assert code == 1 and "actor:nobody" in out and "declared 2 times" in out


def test_edited_slice_is_an_error(tmp_path):
    tm = load(TM)
    blueprint(tm)["flows"][0]["source"] = "component:local-ide"
    component(tm, "component:local-ide")["description"] = "changed"
    code, out = validate(tmp_path, tm, "--system", SYSTEM)
    assert code == 1 and "differs from the system BOM" in out


def test_bad_timestamp_format(tmp_path):
    code, out = validate(tmp_path, minimal(metadata={"timestamp": "yesterday"}))
    assert code == 1 and "timestamp" in out


# ---------------------------------------------------------------- schema tool

def test_outline_shows_wrapped_enums():
    code, out = run("schema_tool.py", "outline", "party:party", "blueprint:visualization", "weakness:weakness")
    assert code == 0, out
    assert "{role: enum:" in out
    assert "{type: enum: activity" in out
    assert "At least one of: {name} | {identifiers}" in out


def test_every_module_outlines():
    code, out = run("schema_tool.py", "modules")
    assert code == 0
    for line in out.splitlines():
        module = line.split(":")[0]
        assert run("schema_tool.py", "outline", module)[0] == 0, module


def test_reference_docs_are_current():
    code, out = run("schema_tool.py", "write-references", "--check")
    assert code == 0, out
