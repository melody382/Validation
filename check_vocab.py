"""
check_vocab.py - systematic consistency check on ABAF's controlled vocabularies.

The first validation pass found contradictions by remembering a clashing
sentence. This finds them mechanically: for every controlled vocabulary the
framework defines, locate each place the set is enumerated and diff the
member sets against the canonical definition.

A vocabulary is "enumerated" at a line that mentions >= 2 of its members.
Reports: foreign members, missing members, and lines that mix two vocabularies.
"""

from __future__ import annotations

import os
import re

FILES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files"
)

DOCS = {
    "I":    "Outcomes ABAF Methodology v0.8 · Vol I The Methodology.md",
    "II":   "Outcomes ABAF Methodology v0.8 · Vol II The Instruments.md",
    "IIIa": "Outcomes ABAF Methodology v0.8 · Vol III(a) The Integrations.md",
    "IIIc": "Outcomes ABAF Methodology v0.8 · Vol III(c) · Consolidated object model.md",
    "IIId": "Outcomes ABAF Methodology v0.8 · Vol III(d) · Portfolio ROI report (worked example).md",
}

# canonical set -> (members, where it is defined)
VOCABS = {
    "mode": (
        ["AUTOMATION", "AUGMENTATION", "UNDETERMINED"],
        "Vol II §11.1 / §12.1",
    ),
    "evidence class": (
        ["STATED", "REPORTED", "OBSERVED", "REQUIRES MEASUREMENT"],
        "Vol II §13.2",
    ),
    "grade": (
        ["Estimated", "Monitored", "Measured"],
        "Vol II §13.3",
    ),
    "consequence class": (
        ["C1", "C2", "C3", "C4"],
        "Vol II §11.2",
    ),
    "reversibility": (
        ["immediate", "same-cycle", "costly", "irreversible"],
        "Vol II §11.2",
    ),
    "maturity stage": (
        ["Experimenting", "Adopting", "Managed", "Optimized", "Augmented"],
        "Vol I §5",
    ),
    "reconciliation outcome": (
        ["Confirmed", "Undeclared", "Idle", "Divergent", "Unreachable"],
        "Vol III §25.4",
    ),
    "investment class": (
        ["People", "Agents", "Systems", "Vendor tools"],
        "Vol I §4.2",
    ),
    "cost line": (
        ["Licence and seat", "Usage", "Build and integration",
         "Enablement", "Expected cost of error"],
        "Vol I §4.5",
    ),
    "collection mode": (
        ["Agentic", "Assisted", "Manual"],
        "Vol III App A.2",
    ),
    "lifecycle": (
        ["Core", "Declining", "Emerging"],
        "Vol I §1.5 / §4.7",
    ),
    "portfolio decision": (
        ["keep", "grow", "fix", "retire"],
        "Vol III M.3 / §4.7",
    ),
}

# terms that should no longer appear anywhere (retired in 0.8)
RETIRED = {
    "EST": "retired in favour of STATED (Vol II §13.2)",
    "FOUND IN EXPENSE DATA": "folded into REPORTED (Vol II §13.2)",
    "MEASURED (as a cell value)": "grade/class collision removed (Vol II §13.1)",
    "Connected Baseline": "renamed Verified Baseline (Vol III §31.2)",
}


def load() -> dict[str, list[str]]:
    out = {}
    for k, fn in DOCS.items():
        with open(os.path.join(FILES_DIR, fn), encoding="utf-8") as fh:
            out[k] = fh.read().splitlines()
    return out


def main() -> None:
    docs = load()
    print("=" * 96)
    print("CONTROLLED VOCABULARIES — every line enumerating 2+ members, diffed against canon")
    print("=" * 96)

    for name, (members, defined_at) in VOCABS.items():
        hits = []
        for dk, lines in docs.items():
            for i, ln in enumerate(lines, 1):
                present = [m for m in members
                           if re.search(r"(?<![A-Za-z])" + re.escape(m) + r"(?![A-Za-z])", ln, re.I)]
                if len(present) >= 2:
                    hits.append((dk, i, present, ln.strip()))
        if not hits:
            continue
        partial = [h for h in hits if len(h[2]) < len(members)]
        print(f"\n### {name}  ({len(members)} members, defined at {defined_at})")
        print(f"    enumerated on {len(hits)} lines; {len(partial)} of them incomplete")
        for dk, i, present, ln in partial:
            missing = [m for m in members if m not in present]
            print(f"    [{dk}:{i}] missing {missing}")
            print(f"        {ln[:150]}")

    print("\n" + "=" * 96)
    print("RETIRED TERMS still present")
    print("=" * 96)
    for term, why in RETIRED.items():
        found = []
        for dk, lines in docs.items():
            for i, ln in enumerate(lines, 1):
                if re.search(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])", ln):
                    found.append((dk, i, ln.strip()[:130]))
        print(f"\n### {term!r} — {why}")
        if not found:
            print("    clean")
        for dk, i, ln in found:
            print(f"    [{dk}:{i}] {ln}")

    print("\n" + "=" * 96)
    print("CROSS-VOCABULARY MIXING — one line using members of two different sets")
    print("=" * 96)
    for dk, lines in docs.items():
        for i, ln in enumerate(lines, 1):
            used = []
            for name, (members, _) in VOCABS.items():
                n = sum(1 for m in members
                        if re.search(r"(?<![A-Za-z])" + re.escape(m) + r"(?![A-Za-z])", ln, re.I))
                if n >= 2:
                    used.append(name)
            if len(used) >= 2:
                print(f"  [{dk}:{i}] {used}")
                print(f"      {ln.strip()[:150]}")


if __name__ == "__main__":
    main()
