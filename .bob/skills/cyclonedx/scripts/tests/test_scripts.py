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
    code, out = run("validate_bom.py", tm_path, "--system", sys_path)
    assert code == 0, out


def test_slice_includes_asset_component(tmp_path, system):
    blueprint(system)["assets"] = [{"refId": "asset:rag", "componentRef": "component:rag-local"}]
    flow = blueprint(system)["flows"][0]
    flow["destination"] = "asset:rag"
    tm = slice_ok(tmp_path, system) if flow["refId"] in next(
        u for u in blueprint(system)["useCases"] if u["ref"] == UC_1B)["flows"] else None
    assert tm is not None
    assert "component:rag-local" in {c["refId"] for c in tm["definitions"]["components"]}


def test_slice_keeps_assets_held_by_sliced_components(tmp_path, system):
    # Data assets (keys, tokens, weights) hang off components by a relationship,
    # not by componentRef. Found by the chatbot blind test: all were dropped.
    blueprint(system)["assets"] = [
        {"refId": "asset:plugin-token", "type": "data", "name": "Plugin token"},
        {"refId": "asset:local-model-weights", "type": "data", "name": "Local model weights"},
    ]
    blueprint(system)["relationships"] += [
        {"ref": "component:code-asst-plugin", "contains": ["asset:plugin-token"]},
        {"ref": "component:code-assistant-model-local", "contains": ["asset:local-model-weights"]},
    ]
    tm = slice_ok(tmp_path, system)
    kept = {a["refId"] for a in blueprint(tm).get("assets", [])}
    assert "asset:plugin-token" in kept          # plugin is in the 1b slice
    assert "asset:local-model-weights" not in kept  # local model is 1a only


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


# ------------------------------------------------------- threat-model checks

def tm_with(tmp_path, mutate):
    tm = load(TM)
    mutate(tm)
    return run("validate_bom.py", save(tmp_path / "tm.json", tm), "--system", SYSTEM)


def first_threat(tm):
    return tm["threats"]["threats"][0]


def test_unknown_capec_is_an_error(tmp_path):
    code, out = tm_with(tmp_path, lambda tm: tm["threats"]["attackPatterns"][0].update(capecId=99999))
    assert code == 1 and "CAPEC-99999 is not in" in out


def test_unknown_and_deprecated_cwe_are_errors(tmp_path):
    def mutate(tm):
        tm["definitions"]["weaknesses"][0]["identifiers"][0]["value"] = "CWE-999999"
        tm["definitions"]["weaknesses"][1]["identifiers"][0]["value"] = "CWE-613"
    code, out = tm_with(tmp_path, mutate)
    assert code == 1
    assert "CWE-999999 is not in the CWE catalogue" in out
    assert "CWE-613 is deprecated" in out


def test_unknown_technique_is_an_error(tmp_path):
    def mutate(tm):
        tm["threats"]["attackPaths"][0]["steps"][1]["technique"]["id"] = "T9999"
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "technique T9999" in out


def test_unknown_nist_and_aicm_are_errors(tmp_path):
    def mutate(tm):
        tm["definitions"]["standards"][0]["requirements"][0]["identifier"] = "ZZ-99"
        tm["definitions"]["standards"][1]["requirements"][0]["identifier"] = "AIS-99"
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "ZZ-99" in out and "AIS-99" in out


def test_unknown_nist_800_30_is_an_error(tmp_path):
    def mutate(tm):
        first_threat(tm)["properties"][0]["value"] = "TS-ZZZ-01 Nothing"
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "TS-ZZZ-01" in out


def test_unregistered_lfai_property_is_an_error(tmp_path):
    def mutate(tm):
        first_threat(tm)["properties"].append({"name": "lfai:made-up", "value": "x"})
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "lfai:made-up" in out


def test_bad_catalogue_citation_is_an_error(tmp_path):
    def mutate(tm):
        first_threat(tm)["properties"].append({"name": "lfai:catalogue-item", "value": "owasp-top10-web:A99:2025"})
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "A99:2025" in out


def test_coverage_and_sweep_are_warnings_then_errors_with_strict(tmp_path):
    code, out = run("validate_bom.py", TM, "--system", SYSTEM)
    assert code == 0
    assert "WARNING coverage:" in out and "WARNING sweep:" in out
    code, out = run("validate_bom.py", TM, "--system", SYSTEM, "--strict")
    assert code == 1 and "ERROR   coverage:" in out


def test_not_applicable_annotation_counts_as_a_decision(tmp_path):
    def mutate(tm):
        tm["annotations"] = [{
            "subjects": ["component:local-ide"],
            "annotator": {"component": {"type": "application", "name": "test"}},
            "timestamp": "2026-01-01T00:00:00Z",
            "text": "not-applicable owasp-top10-web:A07:2025: the IDE has no login of its own",
        }]
    tm_path = tmp_path / "tm.json"
    tm = load(TM)
    mutate(tm)
    save(tm_path, tm)
    report = tmp_path / "coverage.json"
    code, out = run("validate_bom.py", tm_path, "--system", SYSTEM, "--report-json", report)
    assert code == 0, out
    rows = {(r["element"], r["catalogue"]): r for r in load(report)["sweep"]}
    # The example's threat already cites A03 for the IDE; the annotation adds A07.
    assert rows[("component:local-ide", "owasp-top10-web")]["decided"] == 2
    assert "A07:2025" not in out.split("component:local-ide (owasp-top10-web)")[1].split("\n")[0]


def test_malformed_not_applicable_is_an_error(tmp_path):
    def mutate(tm):
        tm["annotations"] = [{
            "subjects": ["component:local-ide"],
            "annotator": {"component": {"type": "application", "name": "test"}},
            "timestamp": "2026-01-01T00:00:00Z",
            "text": "not-applicable because it is fine",
        }]
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "not-applicable text must be" in out


def test_tags_override_type_fallback(tmp_path):
    def mutate(tm):
        for c in tm["definitions"]["components"]:
            if c["refId"] == "component:local-ide":
                c["tags"] = ["none"]
    tm = load(TM)
    mutate(tm)
    system = load(SYSTEM)
    mutate(system)
    sys_path = save(tmp_path / "system.json", system)
    code, out = run("validate_bom.py", save(tmp_path / "tm.json", tm), "--system", sys_path)
    assert "component:local-ide (owasp-top10-web)" not in out


def na_annotation(subjects, text):
    return {"subjects": subjects, "annotator": {"component": {"type": "application", "name": "test"}},
            "timestamp": "2026-01-01T00:00:00Z", "text": text}


def test_thin_not_applicable_reason_is_an_error(tmp_path):
    def mutate(tm):
        tm["annotations"] = [na_annotation(["component:local-ide"], "not-applicable owasp-top10-web:A07:2025: not relevant")]
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "too thin" in out


def test_multi_item_not_applicable_counts_each_item(tmp_path):
    tm = load(TM)
    tm["annotations"] = [na_annotation(
        ["component:local-ide"],
        "not-applicable owasp-top10-web:A07:2025, owasp-top10-web:A10:2025: the IDE has no login and no server-side error handling of its own")]
    tm_path = save(tmp_path / "tm.json", tm)
    report = tmp_path / "coverage.json"
    code, out = run("validate_bom.py", tm_path, "--system", SYSTEM, "--report-json", report)
    assert code == 0, out
    rows = {(r["element"], r["catalogue"]): r for r in load(report)["sweep"]}
    assert rows[("component:local-ide", "owasp-top10-web")]["decided"] == 3  # A03 cited + A07 + A10


def test_contradiction_between_citation_and_not_applicable(tmp_path):
    def mutate(tm):
        tm["annotations"] = [na_annotation(
            ["component:local-ide"],
            "not-applicable owasp-top10-web:A03:2025: the IDE installs nothing from outside the organisation")]
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "marked not applicable but a threat" in out


def test_citation_outside_swept_catalogues_warns(tmp_path):
    def mutate(tm):
        first_threat(tm)["properties"].append({"name": "lfai:catalogue-item", "value": "owasp-mcp-top10:MCP01:2025"})
    code, out = tm_with(tmp_path, mutate)
    assert "owasp-mcp-top10 is not swept for any element it affects" in out


def test_nist_800_30_text_mismatch_warns(tmp_path):
    def mutate(tm):
        first_threat(tm)["properties"][0]["value"] = "TS-ADV-01 Accidental - Privileged User"
    code, out = tm_with(tmp_path, mutate)
    assert "TS-ADV-01" in out and "but the value says" in out


def test_tactic_must_be_an_id(tmp_path):
    def mutate(tm):
        tm["threats"]["attackPaths"][0]["steps"][1]["technique"]["tactic"] = "initial-access"
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "must be a tactic ID" in out


def test_agent_actor_and_component_are_one_element(tmp_path, system):
    tm = slice_ok(tmp_path, system)
    tm["threats"]["threats"] = [{"refId": "threat:x", "name": "x", "affects": ["component:remote-code-asst-agent"],
                                 "mitigations": []}]
    report = tmp_path / "coverage.json"
    run("validate_bom.py", save(tmp_path / "tm2.json", tm), "--system", tmp_path / "system.json", "--report-json", report)
    elements = [r["element"] for r in load(report)["sweep"] if r["catalogue"] == "owasp-agentic-top10"]
    assert "actor:remote-code-asst-agent" not in elements
    assert "actor actor:remote-code-asst-agent" not in load(report)["uncovered"]


def test_lifecycle_scope_skips_training_items(tmp_path, system):
    uc = next(u for u in system["definitions"]["useCases"] if u["refId"] == UC_1B)
    uc["properties"] = [{"name": "lfai:lifecycle", "value": "training"}]
    tm = slice_ok(tmp_path, system)
    tm["threats"]["threats"] = [{"refId": "threat:x", "name": "x", "affects": ["component:local-ide"]}]
    report = tmp_path / "coverage.json"
    run("validate_bom.py", save(tmp_path / "tm2.json", tm), "--system", tmp_path / "system.json", "--report-json", report)
    data = load(report)
    assert data["lifecycle"] == "training"
    assert "LLM01:2025" in data["outOfScopeForLifecycle"]["owasp-llm-top10"]
    llm_rows = [r for r in data["sweep"] if r["catalogue"] == "owasp-llm-top10"]
    assert llm_rows and all(r["items"] == 5 for r in llm_rows)


def test_review_annotations(tmp_path):
    code, out = run("validate_bom.py", TM, "--system", SYSTEM)
    assert "review: usecase:code-assistant-1b" not in out   # the example records its review
    code, out = tm_with(tmp_path, lambda tm: tm.pop("annotations"))
    assert "review: usecase:code-assistant-1b has no" in out
    code, out = tm_with(tmp_path, lambda tm: tm.update(annotations=[
        na_annotation(["usecase:code-assistant-1b"], "reviewed usecase:code-assistant-1b")]))
    assert code == 1 and "review text must be" in out


def test_element_check_annotation_is_accepted(tmp_path):
    """An element-check review (review.elementFormat) parses as a review of the element, not as an error."""
    policy = load(os.path.join(SKILL, "reference", "threat-model-policy.json"))
    fmt = policy["review"]["elementFormat"]
    assert fmt.startswith(policy["review"]["annotationPrefix"] + " <refId>: <check>: ")
    checks = [k for k in policy["elementChecks"] if not k.startswith("$")]
    assert "data store" in checks and "own controls" in checks and "harms outside STRIDE" in checks

    def mutate(tm):
        tm.setdefault("annotations", []).append(na_annotation(
            ["component:context-store-remote"],
            "reviewed component:context-store-remote: data store: modification led to threat:malicious-marketplace-plugin"))
    code, out = tm_with(tmp_path, mutate)
    assert code == 0, out
    assert "review text must be" not in out


def test_slice_keeps_assumptions_linked_by_flow(tmp_path, system):
    flow = next(u for u in blueprint(system)["useCases"] if u["ref"] == UC_1B)["flows"][0]
    blueprint(system)["assumptions"] = [{"refId": "assumption:by-flow", "description": "x", "relatedAssets": [flow]}]
    tm = slice_ok(tmp_path, system)
    assert [a["refId"] for a in blueprint(tm).get("assumptions", [])] == ["assumption:by-flow"]


def test_extract_to_stdout_writes_no_file(tmp_path):
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "schema_tool.py"), "extract", "threat:threatProfile",
                           "-o", "-"], capture_output=True, text=True, encoding="utf-8", cwd=tmp_path)
    assert proc.returncode == 0 and proc.stdout.lstrip().startswith("{")
    assert not (tmp_path / "-").exists()


def test_policy_names_whole_catalogues_only():
    """The sweep rules and notes name catalogues, never items (lifecycleScope is the documented exception)."""
    import re
    policy = load(os.path.join(SKILL, "reference", "threat-model-policy.json"))
    index = load(os.path.join(SKILL, "reference", "catalogues", "catalogues.json"))["catalogues"]
    item_id = re.compile(r"\b(?:LLM\d{2}|ASI\d{2}|API\d{1,2}|A\d{2}:20\d{2}|MCP\d{2}|AML\.T\d{4}|T\d{4}|CWE-\d+|CAPEC-\d+)\b")
    for rule in policy["sweeps"]:
        for key in rule.get("sweep", []) + rule.get("consult", []):
            assert key in index, f"{rule['tag']}: '{key}' is not a catalogue in catalogues.json"
        assert not item_id.search(json.dumps(rule)), f"sweep rule {rule['tag']} names a catalogue item"
    for note in policy["sweepNotes"]:
        assert not item_id.search(note), f"sweep note names a catalogue item: {note}"
    for check, text in (policy.get("elementChecks") or {}).items():
        assert not item_id.search(text), f"element check {check} names a catalogue item: {text}"
    assert "lifecycleScope" in policy["$comment"], "the exception must be stated in the policy comment"


def test_empty_threat_model_fails_strict(tmp_path):
    tm_path = tmp_path / "tm.json"
    assert run("slice_use_case.py", SYSTEM, "--use-case", UC_1B, "-o", tm_path)[0] == 0
    code, out = run("validate_bom.py", tm_path, "--system", SYSTEM, "--strict")
    assert code == 1 and "has no threats" in out


def test_empty_threat_model_still_checks_annotations(tmp_path):
    tm_path = tmp_path / "tm.json"
    run("slice_use_case.py", SYSTEM, "--use-case", UC_1B, "-o", tm_path)
    tm = load(tm_path)
    tm["annotations"] = [na_annotation(["component:local-ide"], "not-applicable owasp-top10-web:A07:2025: n/a")]
    code, out = run("validate_bom.py", save(tm_path, tm), "--system", SYSTEM)
    assert code == 1 and "too thin" in out


def test_untagged_agent_gets_the_agentic_sweep(tmp_path):
    report = tmp_path / "coverage.json"
    run("validate_bom.py", TM, "--system", SYSTEM, "--report-json", report)
    agentic = [r["element"] for r in load(report)["sweep"] if r["catalogue"] == "owasp-agentic-top10"]
    assert agentic == ["component:remote-code-asst-agent"]


def test_slice_keeps_assets_of_components_that_join_late(tmp_path, system):
    component(system, "component:local-ide")["components"] = [{"ref": "component:rag-local"}]
    blueprint(system)["assets"] = [{"refId": "asset:rag-index", "type": "data", "name": "RAG index"}]
    blueprint(system)["relationships"].append({"ref": "component:rag-local", "contains": ["asset:rag-index"]})
    tm = slice_ok(tmp_path, system)
    assert "asset:rag-index" in {a["refId"] for a in blueprint(tm).get("assets", [])}


@pytest.mark.parametrize("name,value,needle", [
    ("lfai:mitigates", "CAPEC-99999", "CAPEC-99999 is not in"),
    ("lfai:mitigates", "CWE-999999", "CWE-999999 is not in"),
    ("lfai:capec-rationale", "CAPEC-99999: made up", "CAPEC-99999 is not in"),
    ("lfai:cwe-rationale", "CWE-999999: made up", "CWE-999999 is not in"),
    ("lfai:aicm-parent", "req:nope < req:nope2", "both declared"),
    ("lfai:control-tier", "seven", "must be 1 or 2"),
    ("lfai:lifecycle", "Training", "lower case"),
])
def test_property_values_are_checked(tmp_path, name, value, needle):
    def mutate(tm):
        tm["controls"][0].setdefault("properties", []).append({"name": name, "value": value})
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and needle in out, out


def test_not_applicable_unknown_item_is_an_error(tmp_path):
    def mutate(tm):
        tm["annotations"] = [na_annotation(["component:local-ide"],
            "not-applicable owasp-top10-web:A99:2025, made-up-cat:X1: the IDE has no web interface of its own")]
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "A99:2025" in out and "made-up-cat" in out


def test_nist_800_30_id_must_match_its_kind(tmp_path):
    def mutate(tm):
        first_threat(tm)["properties"][0]["value"] = "TE-20 Deliver/insert/install malicious capabilities"
    code, out = tm_with(tmp_path, mutate)
    assert code == 1 and "not a threat-source" in out


def test_slicer_writes_stdout_for_dash(tmp_path):
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "slice_use_case.py"), SYSTEM,
                           "--use-case", UC_1B, "-o", "-"], capture_output=True, text=True, encoding="utf-8",
                          cwd=tmp_path)
    assert proc.returncode == 0 and proc.stdout.lstrip().startswith("{")
    assert not (tmp_path / "-").exists()


def test_mcp_catalogue_is_pending_not_included():
    policy = load(os.path.join(SKILL, "reference", "threat-model-policy.json"))
    index = load(os.path.join(SKILL, "reference", "catalogues", "catalogues.json"))["catalogues"]
    assert "owasp-mcp-top10" not in index
    rule = next(r for r in policy["sweeps"] if r["tag"] == "tool-server")
    assert rule["sweep"] == [] and "DECISION NEEDED" in rule["pending"]
    assert "PENDING DECISION" in policy["catalogueDecisions"]["tool-server"]


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


# ---------------------------------------------------------------- visualiser

def visualise_data(tmp_path, *boms, cmd="bom"):
    out = tmp_path / "map.html"
    args = [cmd, *boms] if cmd == "bom" else [cmd, "--observe", *boms]
    code, text = run("visualise_bom.py", *args, "-o", out)
    assert code == 0, text
    page = out.read_text(encoding="utf-8")
    start = page.index("const D = ") + len("const D = ")
    data, _ = json.JSONDecoder().raw_decode(page[start:])
    return data, page


def test_visualiser_matches_validator_references(system):
    sys.path.insert(0, SCRIPTS)
    import validate_bom
    import visualise_bom
    schema = load(validate_bom.DEFAULT_SCHEMA)
    for doc in (system, load(TM)):
        expected = validate_bom.find_refs(doc, schema)[0]
        refs, _ = visualise_bom.walk_bom(doc, visualise_bom.Schema(schema))
        assert [(p, v, k) for p, v, k, _ctx in refs] == expected


def test_visualiser_links_slice_copies_to_the_system_bom(tmp_path):
    data, _ = visualise_data(tmp_path, SYSTEM, TM)
    assert [d["role"] for d in data["docs"]] == ["system", "threat-model"]
    assert data["docs"][1]["system"] == 0
    by_key = {e["k"]: e for e in data["elements"]}
    copies = {by_key[c["a"]]["id"]: c for c in data["copies"]}
    copy = copies["component:code-asst-plugin"]
    assert by_key[copy["a"]]["d"] == 1 and by_key[copy["b"]]["d"] == 0 and copy["drift"] is None
    # A threat in the TM-BOM references the copy, and the copy BOM-Links back to the original.
    threat_refs = [r for r in data["refs"] if r["t"] == copy["a"] and by_key[r["s"]]["t"] == "threat:threat"]
    assert threat_refs
    back = [r for r in data["refs"] if r["s"] == copy["a"] and r["kind"] == "bomlink"]
    assert back and back[0]["t"] == copy["b"]
    assert not [p for p in data["problems"] if p["sev"] == "error"]


def test_visualiser_reports_drift_and_dangling_refs(tmp_path):
    tm = load(TM)
    component(tm, "component:code-asst-plugin")["name"] = "Edited in the TM-BOM"
    tm["threats"]["threats"][0]["affects"].append("component:missing")
    data, _ = visualise_data(tmp_path, SYSTEM, save(tmp_path / "tm.json", tm))
    texts = [p["text"] for p in data["problems"] if p["sev"] == "error"]
    assert any("'component:code-asst-plugin' differs" in t for t in texts)
    assert any("'component:missing' does not match any refId" in t for t in texts)


def test_visualiser_relationship_targets_belong_to_their_subject(tmp_path):
    data, _ = visualise_data(tmp_path, SYSTEM)
    by_key = {e["k"]: e for e in data["elements"]}
    rel = [r for r in data["refs"] if r["sf"].startswith("blueprint:relationship.") and r.get("role") != "subject"]
    assert rel
    assert all(by_key[r["s"]]["id"] and "v" in r for r in rel)


def test_visualiser_escapes_bom_text(tmp_path):
    doc = load(SYSTEM)
    component(doc, "component:code-asst-plugin")["description"] = "</script><img src=x onerror=alert(1)><!--"
    data, page = visualise_data(tmp_path, save(tmp_path / "sys.json", doc))
    assert "</script><img" not in page and "<!--" not in page.split("const D = ", 1)[1]
    plugin = next(e for e in data["elements"] if e["id"] == "component:code-asst-plugin")
    assert plugin["x"].startswith("</script><img")


def test_visualiser_schema_map(tmp_path):
    data, _ = visualise_data(tmp_path, SYSTEM, TM, cmd="schema")
    flow = data["schema"]["objects"]["blueprint:flow"]
    assert flow["refId"] and flow["at"][0] == "blueprints[].flows[]"
    assert {f["f"] for f in flow["fields"]} == {"source", "destination"}
    assert data["schema"]["observed"]["blueprint:flow.source"]
    assert data["schema"]["objects"]["component:component"]["at"][0] == "definitions.components[]"


def test_visualiser_refuses_to_overwrite_other_files(tmp_path):
    other = tmp_path / "notes.html"
    other.write_text("<p>mine</p>", encoding="utf-8")
    code, out = run("visualise_bom.py", "bom", SYSTEM, "-o", other)
    assert code != 0 and "not written by this tool" in out
    assert other.read_text(encoding="utf-8") == "<p>mine</p>"
