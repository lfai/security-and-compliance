# Getting started: CycloneDX 2.0 system BOMs and threat models

This guide takes you from a system diagram to a validated threat model, using either IBM Bob or Claude Code. Each assistant does the modelling; you run a few commands to check its work. Allow about 15 minutes for setup and the first check, and plan for the assistant to take an hour or more on a full threat model.

```
 diagram + notes ──▶ system BOM ──▶ one threat-model BOM per use case
   (you)          (step 1, AI)      (step 2, AI)        │
                       ▲                                │
                       └─────── linked by BOM-Link ─────┘
```

## 1. Set up (once)

You need:
- a clone of this repository;
- **IBM Bob** or **Claude Code**, opened on the repository root;
- **Python 3.9 or later**.

Install the Python packages the skill's scripts use. A virtual environment keeps them separate from the rest of your system. Run these from the repository root.

**macOS / Linux:**

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r .bob/skills/cyclonedx/scripts/requirements.txt
```

**Windows (PowerShell):**

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r .bob/skills/cyclonedx/scripts/requirements.txt
```

**Windows (Git Bash):**

```
python -m venv .venv
source .venv/Scripts/activate
pip install -r .bob/skills/cyclonedx/scripts/requirements.txt
```

On macOS and Linux, use `python3` to create the environment: many systems have no `python` command. Once the environment is activated, `python` works on every platform, so the commands in the rest of this guide use `python`. Activate it again in each new terminal. On Debian or Ubuntu, if creating the environment fails with an `ensurepip` error, install the venv package first (`sudo apt install python3-venv`).

`.venv` is not tracked by git; do not commit it.

Check that everything works by validating the worked example:

```
python .bob/skills/cyclonedx/scripts/validate_bom.py .bob/skills/cyclonedx/examples/system-bom.code-assistant.json --linked .bob/skills/cyclonedx/examples/tm-bom.code-assistant-1b.json
```

The last line should read `result: 0 error(s), 0 warning(s)`.

**Check the skill is loaded.**
- **IBM Bob:** start a new task and type `/cyclonedx`; it should appear in the list. If it does not, see [Troubleshooting](#7-troubleshooting).
- **Claude Code:** type `/claude-cyclonedx`, or just ask a CycloneDX question; it is used automatically.

## 2. Prepare your inputs

Put these in a working folder **outside** the repository (or in a new use-case folder under `subgroups/use-cases-and-threat-models/use_cases/` if you intend to commit them):

| Input | Required | Notes |
|---|---|---|
| The system diagram | Yes | An image (PNG, JPG) or a text diagram (Mermaid `.mmd`, draw.io, PlantUML). Text diagrams give better results: the assistant reads labels exactly. |
| Supporting notes (`.md`) | Strongly recommended | What each element is, which data assets it holds, the use cases, and who hosts what. Without notes the assistant has to guess, and records every guess as an open question. |

The more your notes say about **trust** (which organisation runs each part), **data** (what is sensitive), and **use cases** (the steps of each scenario), the better the threat model.

## 3. Step 1: diagram to system BOM

Ask the assistant, naming your files:

> Turn this system diagram into a system BOM. Diagram: `<path>/diagram.mmd`. Notes: `<path>/notes.md`. Write it to `<path>/system-bom.json`.

The assistant follows [workflows/diagram-to-system-bom.md](workflows/diagram-to-system-bom.md). It lists every element it found, writes the BOM, validates it, and reports back:
- the counts of components, actors, zones, flows and use cases;
- each component's **classification tags** (`web-app`, `api`, `ai-model`, `agent`, …), which decide what the threat sweep covers;
- the **open questions**: everything it had to assume.

**Review before going on.** Read the open questions and the tags, answer what you can, and ask the assistant to update the BOM. Mistakes here carry into every threat model. Then check it yourself:

```
python .bob/skills/cyclonedx/scripts/validate_bom.py <path>/system-bom.json
```

## 4. Step 2: system BOM to threat models

Ask:

> Please generate a threat model from this system BOM: `<path>/system-bom.json`. Write one TM-BOM per use case into `<path>/`.

The assistant follows [workflows/system-bom-to-threat-model.md](workflows/system-bom-to-threat-model.md). It will ask you to confirm which use cases to model (it skips "umbrella" use cases that only combine others) and which methodologies to use (STRIDE and MAESTRO by default). It may ask before editing the system BOM to add a serial number or links.

For each use case it:
1. cuts a **slice** of the system BOM into a new TM-BOM (with `scripts/slice_use_case.py`);
2. finds threats in three passes: STRIDE on every element and flow; a **sweep** of the catalogues that apply to each element, recording every catalogue item as a threat or as "not applicable" with a reason; and a review of the use case and its assumptions for anything system-specific;
3. adds NIST SP 800-30 sources, events and impacts, CAPEC and CWE, and controls mapped to NIST SP 800-53 and CSA AICM;
4. validates the result and reports coverage;
5. writes a **threat table**, `<name>.tm-bom.<use-case>.threats.md`, next to the TM-BOM (with `scripts/tm_to_markdown.py`).

A full threat model takes time: in testing, about 1.5 to 2 hours for a system with three use cases.

## 5. Check the result yourself

Run the validator in strict mode on each TM-BOM, with its system BOM:

```
python .bob/skills/cyclonedx/scripts/validate_bom.py <path>/<name>.tm-bom.<use-case>.json --system <path>/system-bom.json --strict --report-json <path>/<use-case>.coverage.json
```

Read the `threat model:` line, for example:

```
threat model: 29 threats; 30/30 elements covered; 28/28 controls mapped; catalogue sweep 120/120 item decisions
```

- **0 errors** is required. Errors mean a wrong ID, a broken reference, a contradiction, or a format problem.
- With `--strict`, **0 warnings** means every element is covered, every control is used, every catalogue item has a decision, and every assumption was reviewed.
- The `--report-json` file has the details: uncovered elements, unmapped controls, per-element sweep counts, and the items scoped out for a lifecycle stage.

**The validator cannot judge quality.** It proves a decision was recorded, not that it is right. Read the threats and, above all, the "not applicable" reasons: each should give a reason specific to that element.

### Read the threat table

The TM-BOM is JSON for tools. To read and review the threat model, open the threat table the assistant wrote next to it, or write one yourself:

```
python .bob/skills/cyclonedx/scripts/tm_to_markdown.py <path>/<name>.tm-bom.<use-case>.json
```

It writes `<path>/<name>.tm-bom.<use-case>.threats.md`, with three tables: the threats (in the shape of the working group's [Code Assistant threat table](../../../subgroups/use-cases-and-threat-models/use_cases/code_assistant/threats/code_assistant_threats.md), plus controls and risk), the controls with their NIST SP 800-53 and CSA AICM requirements, and every "not applicable" decision with its reason. The page is generated: to change it, change the TM-BOM and run the script again.

### See how the BOMs link together

To see where each element is declared and what references it, within a BOM and across the system BOM and its TM-BOMs, write a map and open it in a browser:

```
python .bob/skills/cyclonedx/scripts/visualise_bom.py bom <path>/system-bom.json <path>/<name>.tm-bom.<use-case>.json [...] -o bom-map.html
```

The page works offline and has three tabs:

- **Documents:** each BOM, the BOM-Links between them, problems (broken references, slice copies that differ from the system BOM), and a table of which element types reference which.
- **Elements:** select any element to see where it is declared, what it references, and what references it. For a system element this includes its copies in each TM-BOM and the threats, controls and risks that reference those copies.
- **Schema:** each schema object, where it sits in a BOM, whether it declares a `refId`, and its reference fields with the element types they were seen pointing at.

`visualise_bom.py schema -o schema-map.html` writes the Schema tab alone. Keep the map out of the repository, or delete it after use: it is generated, and a large set of BOMs gives a page of a few MB.

## 6. Try it on the example first

To see the whole flow without your own diagram, ask the assistant to threat-model the example:

> Please generate a threat model from `.bob/skills/cyclonedx/examples/system-bom.code-assistant.json` for use case `usecase:code-assistant-1a`. Write it to a scratch folder outside the repository.

Compare it with the worked example for Sub Use Case 1b, [examples/tm-bom.code-assistant-1b.json](examples/tm-bom.code-assistant-1b.json). That file holds a single threat to show the shape, so its own validator run reports many coverage warnings; that is expected.

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `jsonschema is not installed` | Activate your virtual environment and run the `pip install` in section 1. |
| Bob does not list the skill | Start a **new** task (skills load at task start). The directory name must be lowercase kebab-case and match the `name` in `SKILL.md`. |
| `has no serialNumber, so a TM-BOM cannot BOM-Link to it` | Let the assistant run `slice_use_case.py <system-bom> --assign-serial`, or run it yourself. It edits the system BOM in place. |
| `<file> already exists. Use --update` | A TM-BOM for that use case exists. To refresh it after the system BOM changed, use `--update`; it keeps the threats and bumps the version. |
| `differs from the system BOM at …` | A copied element in the TM-BOM was edited. Change the system BOM instead, then re-slice with `--update`. |
| `sweep: no catalogue chosen yet for 'tool-server'` | Expected: the MCP catalogue is pending a licence decision (see [the skills README](../README.md)). Tool servers are still covered by STRIDE and the use-case review. |
| `classified by component type because the system BOM gives no classification tag` | Add `tags` to those components in the system BOM (see step 1), then re-slice with `--update`. |
| `python: command not found` | Activate the virtual environment (section 1). Before it is activated, use `python3` on macOS and Linux. |
| `No module named venv`, or an `ensurepip` error, when creating the environment | On Debian or Ubuntu, run `sudo apt install python3-venv`, then create the environment again. |

## 8. Keep your results

Threat models are design artefacts the working group reviews. If you want to share them, put the diagram, notes, system BOM, TM-BOMs and their threat tables together in a folder under `subgroups/use-cases-and-threat-models/use_cases/`, and open a pull request (`git commit -s`, as [CONTRIBUTING.md](../../../CONTRIBUTING.md) requires).
