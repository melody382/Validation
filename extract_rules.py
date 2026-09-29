"""
extract_rules.py - build a register of every normative statement in ABAF v0.8.

Purpose: give the validation a denominator. The first pass found defects by
reading and noticing, which cannot report coverage. This walks all six
documents, splits them into addressable units (paragraph sentences, list
items, table rows), and flags every unit that carries a rule an implementer
would have to obey.

Output: rules.json + rules.csv, one row per candidate rule, with
  rule_id, doc, section, subsection, kind, text, objects[]

"objects" is the framework noun(s) the rule touches. That index is what makes
pairwise consistency checking systematic rather than lucky: rules that touch
the same object must agree, and they can now be read side by side.
"""

from __future__ import annotations

import csv
import json
import os
import re

FILES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files"
)

DOCS = {
    "I":     "Outcomes ABAF Methodology v0.8 · Vol I The Methodology.md",
    "II":    "Outcomes ABAF Methodology v0.8 · Vol II The Instruments.md",
    "IIIa":  "Outcomes ABAF Methodology v0.8 · Vol III(a) The Integrations.md",
    "IIIc":  "Outcomes ABAF Methodology v0.8 · Vol III(c) · Consolidated object model.md",
    "IIId":  "Outcomes ABAF Methodology v0.8 · Vol III(d) · Portfolio ROI report (worked example).md",
}
CSV_DOC = ("IIIb", "Outcomes ABAF Methodology v0.8 · Vol III(b) · "
                   "Vendor connector catalogue - Untitled.csv")

# --- what makes a unit normative -------------------------------------------
# Deontic / definitional / constraint language an implementer must obey.
NORMATIVE = re.compile(
    r"\b("
    r"must|shall|may not|must not|cannot|can never|never|always|only|"
    r"is defined as|is the|are the|is a property|is not a|is never|"
    r"requires?|required|sets? how|decides?|governs?|applies|"
    r"qualifies only|admitted|excluded|scored|not scored|"
    r"is satisfied|threshold|floor|ceiling|tolerance|"
    r"rounds?|sums?|summed|computed|derived|aggregat|"
    r"per cell|per artifact|at their floor|every input|"
    r"stays?|remain|retired|reserved|prohibited|forbidden|"
    r"renders?|records?|carries|carry"
    r")\b",
    re.I,
)

# Framework nouns. A rule is indexed under every object it mentions; the
# index drives the consistency pass.
OBJECTS = {
    "mode":            r"\b(mode|AUTOMATION|AUGMENTATION|UNDETERMINED|division of labour)\b",
    "admission":       r"\b(admission|admitted|substrate|unit of the instrument)\b",
    "evidence_class":  r"\b(STATED|REPORTED|OBSERVED|REQUIRES MEASUREMENT|evidence class|NOT PROVIDED|EST)\b",
    "grade":           r"\b(Estimated|Monitored|Measured|evidence grade|grade)\b",
    "consequence":     r"\b(consequence class|C1|C2|C3|C4|reversibility|UNSET)\b",
    "evidence_floor":  r"\b(evidence floor|floor|autonomy may rise|autonomy rises)\b",
    "aifa":            r"\b(AIFA|fit assessment|criterion|criteria|out of 50|complexity band|slot)\b",
    "placement":       r"\b(placement|maturity|stage|Experimenting|Adopting|Managed|Optimized|Augmented|roll-up|threshold)\b",
    "finding":         r"\b(finding|findings|unnamed gap|ownerless|undeclared|idle|divergent|floor breach|ungoverned change)\b",
    "artifact":        r"\b(artifact|artefact|scorecard|baseline|Verified Baseline|profile|brief)\b",
    "reconciliation":  r"\b(reconcil|confirmed|undeclared|idle|divergent|unreachable|tolerance)\b",
    "cost":            r"\b(cost of service|licence and seat|usage|build and integration|enablement|expected cost of error|ROI|payback)\b",
    "linkage":         r"\b(outcome linkage|benefits owner|baseline, a counterfactual|counterfactual|unit value|target)\b",
    "reliance":        r"\b(reliance trajectory|reliance audit|reliance)\b",
    "knowledge":       r"\b(knowledge source|freshness|conflict|portability|Company Domain Environment)\b",
    "grant":           r"\b(grant|key|consent|custody|revocation|read-only)\b",
    "feed":            r"\b(feed|surface|connector|host|metric|normalized record|retrieved_at)\b",
    "role":            r"\b(Principal Architect|Captain|Bench|reviewer|role|owner)\b",
    "portfolio":       r"\b(portfolio|investment line|rebalance|retire|cancel|lifecycle)\b",
    "method_step":     r"\b(Step 1|Step 2|Step 3|Step 4|Step 5|cadence|daily|weekly|monthly|quarterly|annually)\b",
}

HEAD_RE = re.compile(r"^(#{1,4})\s+(.*)$")
TABLE_RE = re.compile(r"^\s*\|(.+)\|\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")
SEC_RE = re.compile(r"^(?:#{1,4}\s*)?(\d+(?:\.\d+)*)\s*[·.]?\s*")


def sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z*`\"'])", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def classify_objects(text: str) -> list[str]:
    return [name for name, pat in OBJECTS.items() if re.search(pat, text, re.I)]


def strip_md(s: str) -> str:
    s = re.sub(r"\*\*|\*|`", "", s)
    s = re.sub(r"\\([&_%#])", r"\1", s)
    return s.strip()


def walk(doc_key: str, path: str) -> list[dict]:
    out: list[dict] = []
    section = ""
    subsection = ""
    in_code = False
    n = 0

    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line.strip():
            continue
        if line.startswith("[image"):
            continue

        h = HEAD_RE.match(line)
        if h:
            level, title = len(h.group(1)), strip_md(h.group(2))
            m = SEC_RE.match(title)
            num = m.group(1) if m else ""
            if level <= 2:
                section, subsection = (num or title)[:60], ""
            else:
                subsection = (num or title)[:60]
            continue

        units: list[tuple[str, str]] = []
        t = TABLE_RE.match(line)
        if t:
            cells = [strip_md(c) for c in t.group(1).split("|")]
            joined = " | ".join(c for c in cells if c)
            if not joined or set(joined.replace("|", "").strip()) <= set(":- "):
                continue
            units.append(("table", joined))
        else:
            li = LIST_RE.match(line)
            body = strip_md(li.group(1)) if li else strip_md(line)
            kind = "list" if li else "prose"
            for s in sentences(body):
                units.append((kind, s))

        for kind, text in units:
            if len(text) < 25:
                continue
            if not NORMATIVE.search(text):
                continue
            n += 1
            out.append({
                "rule_id": f"{doc_key}-{n:03d}",
                "doc": doc_key,
                "section": section,
                "subsection": subsection,
                "kind": kind,
                "text": text[:600],
                "objects": classify_objects(text),
            })
    return out


def walk_csv(doc_key: str, path: str) -> list[dict]:
    """The catalogue's rules live in its column semantics, not prose."""
    out = []
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for i, r in enumerate(rows, 1):
        text = (f"row {r['#']}: {r['Vendor / product']} | mode={r['Mode']} | "
                f"feeds={r['Feeds / serves']} | connection={r['Connection']}")
        out.append({
            "rule_id": f"{doc_key}-{i:03d}",
            "doc": doc_key,
            "section": "catalogue",
            "subsection": r["Group"][:60],
            "kind": "csv-row",
            "text": text[:600],
            "objects": ["feed"] + (["grant"] if "key" in r["Connection"].lower() else []),
        })
    return out


def main() -> None:
    allrules: list[dict] = []
    print(f"{'doc':<6}{'file':<58}{'rules':>7}")
    print("-" * 72)
    for k, fn in DOCS.items():
        p = os.path.join(FILES_DIR, fn)
        rs = walk(k, p)
        allrules += rs
        print(f"{k:<6}{fn[:56]:<58}{len(rs):>7}")
    rs = walk_csv(CSV_DOC[0], os.path.join(FILES_DIR, CSV_DOC[1]))
    allrules += rs
    print(f"{CSV_DOC[0]:<6}{CSV_DOC[1][:56]:<58}{len(rs):>7}")
    print("-" * 72)
    print(f"{'TOTAL':<64}{len(allrules):>8}")

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "rules.json"), "w", encoding="utf-8") as fh:
        json.dump(allrules, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(here, "rules.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rule_id", "doc", "section", "subsection", "kind", "objects", "text"])
        for r in allrules:
            w.writerow([r["rule_id"], r["doc"], r["section"], r["subsection"],
                        r["kind"], ";".join(r["objects"]), r["text"]])

    # coverage by object - the index the consistency pass reads
    print("\nRules per framework object (a rule can touch several):")
    counts: dict[str, int] = {}
    for r in allrules:
        for o in r["objects"]:
            counts[o] = counts.get(o, 0) + 1
    for o, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {o:<18}{c:>5}")
    untagged = [r for r in allrules if not r["objects"]]
    print(f"\nuntagged (touch no known object): {len(untagged)}")


if __name__ == "__main__":
    main()
