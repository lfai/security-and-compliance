"""
Generate a Graphviz DOT diagram and SVG from the CycloneDX JSON embedded in
definition.md for the Code Assistant use case.

Usage:
    python3 generate_diagram.py

Outputs (written to the same directory as this script):
    code_assistant_diagram.dot
    code_assistant_diagram.svg
"""

import graphviz
import os

DIAGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Boundary definitions ──────────────────────────────────────────────────
# Maps boundary-name → { label, color (fill), border }
BOUNDARIES = {
    "internal": {
        "label": "Internal",
        "fillcolor": "#e8f5e9",
        "color": "#2e7d32",
    },
    "external_saas": {
        "label": "External SaaS",
        "fillcolor": "#fff3e0",
        "color": "#e65100",
    },
    "external_cloud": {
        "label": "External Cloud",
        "fillcolor": "#e3f2fd",
        "color": "#1565c0",
    },
}

# ─── Nodes ─────────────────────────────────────────────────────────────────
# Each entry: bom_ref → (display_label, cdx_type, boundary_key)
NODES = [
    # Internal
    ("actor-developer",           "Developer",                           "device",                "internal"),
    ("local-ide",                 "IDE",                                 "application",           "internal"),
    ("code-asst-plugin",          "Code Assistant\nPlugin",              "data",                  "internal"),
    ("data-local-codebase",       "Local Codebase\nClone",               "data",                  "internal"),
    ("authn-service",             "Authentication\nService",             "application",           "internal"),
    ("authz-service",             "Authorization\nService",              "application",           "internal"),
    ("local-mcp-server-third-party", "Third Party\nMCP Server",         "application",           "internal"),
    ("code-asst-agent-static-data",  "Code Assistant\nAgent",           "application",           "internal"),
    ("local-code-asst-agent",     "Code Assistant Agent\n(local, dynamic)", "application",       "internal"),
    ("framework-1a",              "Agentic Framework\n(Internal)",       "framework",             "internal"),
    ("model-local",               "Local Code\nAssistant Model",         "machine-learning-model","internal"),
    ("rag-local",                 "Local RAG",                           "application",           "internal"),
    ("ctx-local",                 "Local Context\nStore",                "data",                  "internal"),
    # External SaaS
    ("remote-code-asst-agent",    "Remote Code Assistant\nAgent (remote, dynamic)", "application", "external_saas"),
    ("framework-1b",              "Agentic Framework\n(External SaaS)",  "framework",             "external_saas"),
    ("model-remote",              "Remote Code\nAssistant Model",        "machine-learning-model","external_saas"),
    ("rag-remote",                "Remote RAG",                          "application",           "external_saas"),
    ("ctx-remote",                "Remote Context\nStore",               "data",                  "external_saas"),
    ("mcp-gateway",               "MCP Gateway",                         "application",           "external_saas"),
    ("mcp-agentic-saas",          "MCP Server —\nAgentic SaaS",          "application",           "external_saas"),
    ("external-plugin-marketplace","External Plugin\nMarketplace",       "platform",              "external_saas"),
    ("agentic-saas",              "Agentic SaaS",                        "platform",              "external_saas"),
    # External Cloud
    ("mcp-cloud",                 "MCP Server —\nCloud Service",         "application",           "external_cloud"),
    ("cloud-service",             "Cloud Service\n(AWS/GCP/etc.)",       "application",           "external_cloud"),
]

# ─── Node visual style by CycloneDX type ──────────────────────────────────
TYPE_STYLE = {
    "device":                {"shape": "oval",      "fillcolor": "#c8e6c9", "style": "filled"},
    "application":           {"shape": "box",       "fillcolor": "#ffffff", "style": "filled,rounded"},
    "data":                  {"shape": "cylinder",  "fillcolor": "#ffe0b2", "style": "filled"},
    "framework":             {"shape": "component", "fillcolor": "#e1bee7", "style": "filled"},
    "machine-learning-model":{"shape": "hexagon",   "fillcolor": "#b3e5fc", "style": "filled"},
    "platform":              {"shape": "tab",       "fillcolor": "#f8bbd0", "style": "filled"},
}

# ─── Edges ─────────────────────────────────────────────────────────────────
# (source_bom_ref, dest_bom_ref, label, flow_type, encrypted, synchronous)
FLOWS = [
    ("actor-developer",            "local-ide",                  "submits request",             "control",  False, True),
    ("local-ide",                  "code-asst-plugin",           "activates plugin",            "control",  False, True),
    ("code-asst-agent-static-data","authn-service",              "authenticates",               "control",  True,  True),
    ("code-asst-agent-static-data","authz-service",              "checks permissions",          "control",  True,  True),
    ("code-asst-agent-static-data","data-local-codebase",        "reads codebase",              "data",     False, True),
    ("code-asst-agent-static-data","local-mcp-server-third-party","calls MCP (3rd party)",      "control",  False, True),
    ("code-asst-agent-static-data","framework-1a",               "delegates (1a)",              "control",  False, True),
    ("local-code-asst-agent",      "model-local",                "invokes local model",         "data",     False, True),
    ("local-code-asst-agent",      "rag-local",                  "queries local RAG",           "data",     False, True),
    ("local-code-asst-agent",      "ctx-local",                  "reads context",               "data",     False, True),
    ("local-code-asst-agent",      "mcp-cloud",                  "calls cloud MCP (1a)",        "control",  True,  True),
    ("mcp-cloud",                  "cloud-service",              "calls cloud service",         "control",  True,  True),
    ("model-local",                "actor-developer",            "returns response",            "data",     False, True),
    # 1b flows
    ("code-asst-agent-static-data","mcp-gateway",                "forwards request (1b)",       "control",  True,  True),
    ("mcp-gateway",                "mcp-agentic-saas",           "routes to SaaS MCP",          "control",  True,  True),
    ("mcp-agentic-saas",           "remote-code-asst-agent",     "dispatches to remote agent",  "control",  False, True),
    ("remote-code-asst-agent",     "model-remote",               "invokes remote model",        "data",     False, True),
    ("remote-code-asst-agent",     "rag-remote",                 "queries remote RAG",          "data",     False, True),
    ("remote-code-asst-agent",     "ctx-remote",                 "reads remote context",        "data",     False, True),
    ("remote-code-asst-agent",     "local-mcp-server-third-party","calls MCP (3rd party, 1b)",  "control",  True,  True),
    ("remote-code-asst-agent",     "mcp-cloud",                  "calls cloud MCP (1b)",        "control",  True,  True),
    ("model-remote",               "actor-developer",            "returns response",            "data",     False, True),
    ("external-plugin-marketplace","code-asst-plugin",           "delivers plugin",             "data",     False, False),
]

# Flow type → edge color
FLOW_COLOR = {
    "control": "#555555",
    "data":    "#1565c0",
    "process": "#2e7d32",
}


def build_dot() -> graphviz.Digraph:
    dot = graphviz.Digraph(
        name="code_assistant_threat_model",
        comment="Code Assistant Threat Model — generated from CycloneDX JSON",
    )
    dot.attr(
        rankdir="LR",
        fontname="Helvetica",
        fontsize="12",
        compound="true",
        splines="ortho",
        nodesep="0.5",
        ranksep="1.2",
        bgcolor="white",
    )
    dot.attr("node", fontname="Helvetica", fontsize="10")
    dot.attr("edge", fontname="Helvetica", fontsize="8")

    # Collect nodes per boundary
    boundary_nodes: dict[str, list] = {k: [] for k in BOUNDARIES}
    node_lookup = {}
    for bom_ref, label, cdx_type, boundary in NODES:
        boundary_nodes[boundary].append((bom_ref, label, cdx_type))
        node_lookup[bom_ref] = (label, cdx_type, boundary)

    # Render boundary subgraphs
    for bkey, bdef in BOUNDARIES.items():
        with dot.subgraph(name=f"cluster_{bkey}") as sub:
            sub.attr(
                label=bdef["label"],
                style="filled,rounded",
                fillcolor=bdef["fillcolor"],
                color=bdef["color"],
                penwidth="2",
                fontname="Helvetica Bold",
                fontsize="13",
                margin="20",
            )
            for bom_ref, label, cdx_type in boundary_nodes[bkey]:
                style = TYPE_STYLE.get(cdx_type, {"shape": "box", "fillcolor": "#ffffff", "style": "filled"})
                sub.node(
                    bom_ref,
                    label=label,
                    shape=style["shape"],
                    fillcolor=style["fillcolor"],
                    style=style["style"],
                    margin="0.15,0.1",
                )

    # Render edges
    for src, dst, label, ftype, encrypted, synchronous in FLOWS:
        color = FLOW_COLOR.get(ftype, "#333333")
        attrs = {
            "label": ("🔒 " if encrypted else "") + label,
            "color": color,
            "fontcolor": color,
            "arrowsize": "0.7",
        }
        if not synchronous:
            attrs["style"] = "dashed"
        dot.edge(src, dst, **attrs)

    return dot


def main():
    dot = build_dot()

    dot_path = os.path.join(DIAGRAM_DIR, "code_assistant_diagram")
    dot.save(dot_path + ".dot")
    print(f"✓  DOT written  → {dot_path}.dot")

    dot.format = "svg"
    out = dot.render(filename=dot_path, cleanup=True)
    print(f"✓  SVG rendered → {out}")


if __name__ == "__main__":
    main()
