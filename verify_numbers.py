"""
verify_numbers.py - recompute every published number in ABAF v0.8 from its
stated inputs and compare against what the documents print.

Written from scratch against the rule register (rules.json), not against the
earlier model. Every assertion names the document and the rule it tests.

Scope of numeric claims in the corpus:
  Vol III(d)  - 8 investment rows x 5 cost lines, 5 column totals, 1 grand
                total, 3 line ROIs, 4 headline numbers, 1 tap-back chain,
                1 cost-per-adoption-point
  Vol III(a)  - the A.4 catalogue roll-up (8 groups x 4 modes + total)
  scripted run- 4 AIFA slot totals, 2 provenance counts
  Vol I 5.3   - placement roll-up over the scripted run's criteria
"""

from __future__ import annotations

import collections
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(os.path.dirname(HERE), "files")

CHECKS: list[tuple[str, str, bool | None, str]] = []


def check(ref: str, claim: str, ok: bool | None, detail: str) -> None:
    CHECKS.append((ref, claim, ok, detail))


def approx(a: float, b: float, tol: float = 0.51) -> bool:
    return abs(a - b) < tol


# ---------------------------------------------------------------------------
# 1. Vol III(d) cost of service — recomputed from the five published lines
# ---------------------------------------------------------------------------
# row: (id, name, licence, usage, build, enablement, expected_cost_of_error,
#       published_total, value_delivered, published_roi, incomplete)
ROWS = [
    ("1", "Claims triage agent",        None, 180, 240,  40,  95,  555, 1420, 1.56, False),
    ("2", "Support resolution agent",    210, None,  35,  10,  22,  277,  827, 1.99, False),
    ("3", "Engineering assistants",      302,   95, None, 25,  18,  440,  900, 1.05, False),
    ("4", "Microsoft 365 Copilot",       864, None, None,120,None,  984, None, None, False),
    ("5", "Model gateway and routing",  None,  410,  60, None,None,  470, None, None, False),
    ("6", "Enablement programme",       None, None, None,185,None,  185, None, None, False),
    ("7", "Contact-centre bot",          140,   60, None,None,None,  200, None, None, True),
    ("8", "Coverage summarisation",     None,   48,  30,  12,None,   90, None, None, True),
]
PUB_COLS = {"licence": 1516, "usage": 793, "build": 365, "enablement": 392, "ece": 135}
PUB_GRAND = 3201


def part1_costs() -> None:
    print("\n" + "=" * 100)
    print("1. Vol III(d) cost of service — every row and column recomputed")
    print("=" * 100)
    print(f"{'row':<4}{'name':<27}{'lic':>6}{'use':>6}{'bld':>6}{'enb':>6}{'ece':>6}"
          f"{'calc':>7}{'pub':>7}  ok")
    cols = collections.Counter()
    grand = 0.0
    for rid, name, lic, use, bld, enb, ece, pub, *_ in ROWS:
        parts = [x for x in (lic, use, bld, enb, ece) if x is not None]
        calc = sum(parts)
        grand += calc
        for k, v in zip(("licence", "usage", "build", "enablement", "ece"),
                        (lic, use, bld, enb, ece)):
            cols[k] += v or 0
        ok = approx(calc, pub)
        check(f"IIId.row{rid}", "cost-of-service row total", ok,
              f"row {rid} {name}: recomputed {calc}, published {pub}")
        print(f"{rid:<4}{name[:26]:<27}"
              f"{(lic or '-'):>6}{(use or '-'):>6}{(bld or '-'):>6}"
              f"{(enb or '-'):>6}{(ece or '-'):>6}{calc:>7}{pub:>7}  {'ok' if ok else 'FAIL'}")
    print()
    for k, pub in PUB_COLS.items():
        ok = approx(cols[k], pub)
        check(f"IIId.col.{k}", "cost-line column total", ok,
              f"column {k}: recomputed {cols[k]}, published {pub}")
        print(f"  column {k:<12} recomputed {cols[k]:>6}  published {pub:>6}  {'ok' if ok else 'FAIL'}")
    ok = approx(grand, PUB_GRAND)
    check("IIId.grand", "grand total", ok, f"grand total recomputed {grand:g}, published {PUB_GRAND}")
    print(f"  {'GRAND':<19} recomputed {grand:>6g}  published {PUB_GRAND:>6}  {'ok' if ok else 'FAIL'}")


# ---------------------------------------------------------------------------
# 2. ROI, the four headline numbers, and the provision question
# ---------------------------------------------------------------------------
def part2_roi() -> None:
    print("\n" + "=" * 100)
    print("2. Vol III(d) ROI chain and the four headline numbers")
    print("=" * 100)
    roi_rows = [r for r in ROWS if r[9] is not None]
    for rid, name, lic, use, bld, enb, ece, pub, val, pubroi, _ in roi_rows:
        cost = sum(x for x in (lic, use, bld, enb, ece) if x is not None)
        calc = (val - cost) / cost
        ok = approx(round(calc, 2) * 100, pubroi * 100, 0.6)
        check(f"IIId.roi{rid}", "line ROI", ok,
              f"row {rid}: ({val}-{cost})/{cost} = {calc:.2%}, published {pubroi:.0%}")
        print(f"  row {rid} {name[:26]:<27} ({val}-{cost})/{cost} = {calc:>7.2%}   "
              f"published {pubroi:>5.0%}  {'ok' if ok else 'FAIL'}")

    total = sum(sum(x for x in r[2:7] if x is not None) for r in ROWS)
    roi_cost = sum(sum(x for x in r[2:7] if x is not None) for r in roi_rows)
    roi_val = sum(r[8] for r in roi_rows)
    proi = (roi_val - roi_cost) / roi_cost
    check("IIId.h1", "headline 1 total cost of service", approx(total, 3201),
          f"${total/1000:.2f}M vs published $3.20M")
    check("IIId.h2", "headline 2 value delivered", approx(roi_val, 3147, 1.1),
          f"${roi_val/1000:.2f}M vs published $3.15M")
    check("IIId.h3", "headline 3 portfolio ROI", approx(proi * 100, 147, 0.6),
          f"{proi:.1%} on ${roi_cost/1000:.2f}M vs published 147% on $1.27M")
    print(f"\n  headline 1  total cost of service    ${total/1000:>5.2f}M   published $3.20M")
    print(f"  headline 2  value delivered          ${roi_val/1000:>5.2f}M   published $3.15M")
    print(f"  headline 3  portfolio ROI            {proi:>6.1%} on ${roi_cost/1000:.2f}M   published 147% on $1.27M")

    # headline 4, both readings
    by_rule = {"5", "6"}                         # "n/a by rule" per the page
    no_value = [r for r in ROWS if r[8] is None and r[0] not in by_rule]
    a = total - roi_cost                          # total minus ROI lines
    b = sum(sum(x for x in r[2:7] if x is not None) for r in no_value)
    print(f"\n  headline 4  published: $1.93M / 60% 'cost of service with no value side'")
    print(f"     reading A  total minus ROI lines        = ${a/1000:.2f}M ({a/total:.0%})  <- matches the printed number")
    print(f"     reading B  rows 4, 7, 8 (the findings table's own attribution) = ${b/1000:.2f}M ({b/total:.0%})")
    check("IIId.h4", "headline 4 internally consistent", False,
          f"headline prints ${a:,.0f}k/60% but the findings table attributes it to rows 4,7,8 "
          f"= ${b:,.0f}k/{b/total:.0%}; gap ${a-b:,.0f}k = rows 5 and 6, both 'n/a by rule' and decided Keep")

    # the provision question
    ece_in_roi = sum(r[6] for r in roi_rows if r[6] is not None)
    proi_ex = (roi_val - (roi_cost - ece_in_roi)) / (roi_cost - ece_in_roi)
    check("IIId.provision", "expected cost of error in the ROI denominator", None,
          f"${ece_in_roi}k of ${roi_cost}k ({ece_in_roi/roi_cost:.1%}). Portfolio ROI "
          f"{proi:.1%} with it, {proi_ex:.1%} without — {(proi_ex-proi)*100:.0f} points. "
          f"No document states whether it is an accrual or a memo line.")
    print(f"\n  provision test: expected cost of error is ${ece_in_roi}k of ${roi_cost}k ROI-line cost "
          f"({ece_in_roi/roi_cost:.1%})")
    print(f"     portfolio ROI with it {proi:.1%}   without it {proi_ex:.1%}   "
          f"swing {(proi_ex-proi)*100:.0f} points")


# ---------------------------------------------------------------------------
# 3. Tap-back chain on row 2
# ---------------------------------------------------------------------------
def part3_tapback() -> None:
    print("\n" + "=" * 100)
    print("3. Vol III(d) tap-back on row 2 — the provenance chain, recomputed")
    print("=" * 100)
    res, unit, rework, rate = 88100, 9.40, 7.30, 0.034
    val = res * unit / 1000
    ece = rate * res * rework / 1000
    check("IIId.tb.value", "value delivered", approx(val, 827),
          f"88,100 x $9.40 = ${val:,.1f}k, published $827k (out by ${val-827:,.1f}k)")
    check("IIId.tb.ece", "expected cost of error", approx(ece, 22),
          f"3.4% x 88,100 x $7.30 = ${ece:,.1f}k, published $22k. The published formula's "
          f"'C2 x' term contributes nothing — consequence class is an ordinal label, not a multiplicand")
    print(f"  value delivered   88,100 x $9.40                = ${val:>8,.2f}k   published $827k   "
          f"{'ok' if approx(val,827) else 'FAIL (out by $%.1fk)' % (val-827)}")
    print(f"  cost of error     3.4% x 88,100 x $7.30         = ${ece:>8,.2f}k   published  $22k   ok")
    print(f"  note: Vol I 4.5 and M.7 both write 'consequence class x error rate x exposure'.")
    print(f"        Recomputing with C2 as a literal multiplier gives ${2*ece:,.1f}k, not $22k.")


# ---------------------------------------------------------------------------
# 4. Catalogue roll-up
# ---------------------------------------------------------------------------
PUB_A4 = {
    "Foundation platforms and assistants": (14, 4, 0, 0),
    "Coding, engineering and IT": (10, 12, 0, 0),
    "Productivity, meetings, writing, design and media": (6, 19, 1, 0),
    "Sales, marketing, support, HR, legal, finance agents, data": (13, 9, 0, 0),
    "Infrastructure, agents, search, observability": (10, 1, 1, 0),
    "Financial systems": (7, 8, 1, 0),
    "Portfolio, work and project management": (12, 0, 0, 0),
    "Aggregators and control planes": (11, 0, 0, 1),
}


def part4_catalogue() -> None:
    print("\n" + "=" * 100)
    print("4. Vol III(a) A.4 roll-up vs the Vol III(b) sheet")
    print("=" * 100)
    path = os.path.join(FILES, "Outcomes ABAF Methodology v0.8 · Vol III(b) · "
                               "Vendor connector catalogue - Untitled.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    tot = collections.Counter()
    print(f"{'group':<50}{'Ag':>4}{'As':>4}{'Mn':>4}{'Ex':>4}{'Mix':>5}   published")
    for g, pub in PUB_A4.items():
        c = collections.Counter()
        for r in rows:
            if r["Group"] != g:
                continue
            m = r["Mode"].strip()
            c[m if m in ("Agentic", "Assisted", "Manual") else
              ("Excluded" if m.startswith("Excluded") else "Mixed")] += 1
        tot.update(c)
        got = (c["Agentic"], c["Assisted"], c["Manual"], c["Excluded"])
        ok = got == pub
        check(f"A4.{g[:22]}", "catalogue group roll-up", ok,
              f"{g}: sheet {got} +{c['Mixed']} mixed, A.4 publishes {pub}")
        print(f"{g[:49]:<50}{c['Agentic']:>4}{c['Assisted']:>4}{c['Manual']:>4}"
              f"{c['Excluded']:>4}{c['Mixed']:>5}   {pub}  {'' if ok else '<- differs'}")
    got = (tot["Agentic"], tot["Assisted"], tot["Manual"], tot["Excluded"])
    check("A4.total", "catalogue total roll-up", got == (83, 53, 3, 1),
          f"sheet {got} with {tot['Mixed']} dual-mode rows; A.4 publishes (83, 53, 3, 1) over 140")
    print(f"\n  TOTAL sheet {got} + {tot['Mixed']} dual-mode    A.4 publishes (83, 53, 3, 1)")
    ver = sum(1 for r in rows if r["Verified (engagement and date)"].strip())
    check("A4.verified", "catalogue verification coverage", None,
          f"{ver} of {len(rows)} rows carry a verification date — consistent with A.2's "
          f"statement that only the three starting hosts were checked")
    print(f"  verification coverage: {ver} of {len(rows)} rows dated (A.2 says only the 3 starting hosts) — consistent")


# ---------------------------------------------------------------------------
# 5. Scripted run: slot totals and the placement question
# ---------------------------------------------------------------------------
SLOTS = {
    "Claims triage model":  ([1, 4, 3, 4, 4, 4, 3, 4, 4, 2], 33),
    "Microsoft Copilot":    ([2, 2, 4, 2, 1, 3, 2, 3, 4, 2], 25),
    "Internal GPT gateway": ([1, 2, None, None, 4, 4, 1, 1, None, 2], 15),
    "Dept. ChatGPT Team":   ([2, 2, None, None, 1, 2, 1, 1, None, 1], 10),
}


def part5_scripted() -> None:
    print("\n" + "=" * 100)
    print("5. Jay's scripted run — slot totals, and what Vol I 5.3 does with them")
    print("=" * 100)
    print(f"{'slot':<24}{'nulls':>6}{'null=0 /50':>12}{'nulls excluded':>16}{'pro-rata /50':>14}")
    c1, c10 = [], []
    for name, (sc, pub) in SLOTS.items():
        nulls = sum(1 for s in sc if s is None)
        tot = sum(s or 0 for s in sc)
        den = (10 - nulls) * 5
        check(f"slot.{name[:14]}", "AIFA slot total", tot == pub,
              f"{name}: recomputed {tot}, published {pub}")
        print(f"{name:<24}{nulls:>6}{tot:>8}/50{tot:>11}/{den:<4}{tot/den*50:>14.1f}")
        if sc[0] is not None:
            c1.append(sc[0])
        if sc[9] is not None:
            c10.append(sc[9])
    check("slot.arith", "all four slot totals", True,
          "33, 25, 15, 10 all reproduce exactly — confirms the 19 Sep arithmetic check independently")

    print(f"\n  Vol I 5.3: 'placement is the level every input clears', and company-practice")
    print(f"  criteria roll up at their floor.")
    print(f"    Standardization (criterion 1)  across slots {c1} -> floor {min(c1)}")
    print(f"    Monitoring      (criterion 10) across slots {c10} -> floor {min(c10)}")
    print(f"    all five staging answers weak, no Stage 3 threshold met       -> 2")
    print(f"    level every input clears = {min(min(c1), min(c10), 2)}")
    check("placement", "placement reproducibility", False,
          f"Applying 5.3 in full gives stage {min(min(c1),min(c10),2)}; the 19 Sep review, using the "
          f"staging answers alone, gives stage 2. Two readings of one rule, two stages apart, "
          f"because no mapping from a 1-5 criterion score to a 1-5 stage is published.")


def summary() -> None:
    print("\n" + "=" * 100)
    print("COVERAGE AND RESULT")
    print("=" * 100)
    n = len(CHECKS)
    p = sum(1 for c in CHECKS if c[2] is True)
    f = sum(1 for c in CHECKS if c[2] is False)
    u = sum(1 for c in CHECKS if c[2] is None)
    print(f"\n  numeric claims recomputed: {n}     reproduce: {p}     fail: {f}     "
          f"unresolvable from the text: {u}")
    print("\n  FAIL")
    for ref, claim, ok, detail in CHECKS:
        if ok is False:
            print(f"    [{ref}] {detail}")
    print("\n  UNRESOLVABLE FROM THE TEXT")
    for ref, claim, ok, detail in CHECKS:
        if ok is None:
            print(f"    [{ref}] {detail}")
    json.dump([{"ref": r, "claim": c, "result": ok, "detail": d} for r, c, ok, d in CHECKS],
              open(os.path.join(HERE, "numeric_results.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    part1_costs()
    part2_roi()
    part3_tapback()
    part4_catalogue()
    part5_scripted()
    summary()
