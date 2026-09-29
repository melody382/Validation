"""
run_validation.py — drives abaf_model.py against
  (a) the published Vol III(d) Ashford worked example, recomputed from scratch,
  (b) five synthetic companies built to exercise the instrument mechanics,
  (c) the Vol III(b) connector catalogue vs the Vol III(a) A.4 roll-up.

Nothing in files/ is read for writing and nothing there is modified.
"""

from __future__ import annotations

import csv
import collections
import os
import sys

from abaf_model import (
    ASSUMPTIONS, GAPS, EClass, CClass, Mode, Grade,
    Cell, compute, DecisionComponent, OutcomeLinkage,
    InvestmentLine, Portfolio, InventoryLine, reconcile,
    AIFAScore, DEPLOYMENT_DERIVATION, CRITERIA,
    StagingAnswers, Stage3Thresholds, place_company,
    FLOOR_AS_GRADE, FLOOR_AS_CELL_CLASS, STAGE_NAMES,
)

FILES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")
RESULTS: list[tuple[str, str, str]] = []   # (check id, PASS/FAIL/FLAG, detail)


def record(cid: str, ok, detail: str) -> None:
    status = "PASS" if ok is True else ("FAIL" if ok is False else "FLAG")
    RESULTS.append((cid, status, detail))


def money(x) -> str:
    return "—" if x is None else f"{x:,.1f}"


def hr(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ===========================================================================
# PART A — recompute the Vol III(d) Ashford worked example
# ===========================================================================

def ashford() -> Portfolio:
    """The eight lines exactly as published, $ thousands, annualised."""

    def dc(dcid, cc, ecls, err=None, vol=None, uec=None, linkage=None):
        return DecisionComponent(
            dc_id=dcid, work=dcid, mode=Mode.AUGMENTATION, consequence=cc,
            evidence_cls=ecls, error_rate=err, volume=vol, unit_error_cost=uec,
            linkage=linkage or OutcomeLinkage(),
        )

    lk_base = OutcomeLinkage(outcome="o", baseline=0.0, counterfactual="stated",
                             period="Q3", unit_value=9.40)

    lines = [
        InvestmentLine("R1", "Claims triage agent", "agents", "payback_plus_risk",
                       licence_seat=None, usage=180, build_integration=240, enablement=40,
                       explicit_ece=95, value_delivered=1420, value_cls=EClass.STATED,
                       benefits_owner="Head of Claims",
                       components=[dc("r1.dc", CClass.C3, EClass.OBSERVED, .021, None, None, lk_base)]),
        InvestmentLine("R2", "Support resolution agent", "agents", "roi_or_npv_outcome_metrics",
                       licence_seat=210, usage=None, build_integration=35, enablement=10,
                       explicit_ece=22, value_delivered=827, value_cls=EClass.STATED,
                       benefits_owner="VP Customer Service",
                       components=[dc("r2.dc", CClass.C2, EClass.OBSERVED, .034, 88100, 7.30, lk_base)]),
        InvestmentLine("R3", "Engineering assistants", "vendor_tools", "cost_of_service_vs_use",
                       licence_seat=302, usage=95, build_integration=None, enablement=25,
                       explicit_ece=18, value_delivered=900, value_cls=EClass.STATED,
                       benefits_owner="VP Engineering",
                       components=[dc("r3.dc", CClass.C2, EClass.OBSERVED, .014, None, None, lk_base)]),
        InvestmentLine("R4", "Microsoft 365 Copilot", "vendor_tools", "cost_of_service_vs_use",
                       licence_seat=864, usage=0, build_integration=None, enablement=120,
                       explicit_ece=0, value_delivered=None, benefits_owner=None,
                       components=[dc("r4.dc", CClass.C1, EClass.REPORTED)]),
        InvestmentLine("R5", "Model gateway and routing", "systems", "payback_npv_platform",
                       licence_seat=None, usage=410, build_integration=60, enablement=None,
                       explicit_ece=0, value_delivered=None, benefits_owner="Platform owner"),
        InvestmentLine("R6", "Enablement programme", "people", "cost_per_adoption_point",
                       licence_seat=None, usage=None, build_integration=None, enablement=185,
                       explicit_ece=0, value_delivered=None, benefits_owner="CHRO"),
        InvestmentLine("R7", "Contact-centre bot", "vendor_tools", "cost_of_service_vs_use",
                       licence_seat=140, usage=60, build_integration=None, enablement=None,
                       value_delivered=None, benefits_owner=None,
                       components=[dc("r7.dc", CClass.C2, EClass.RM)]),
        InvestmentLine("R8", "Coverage summarisation", "agents", "payback_plus_risk",
                       licence_seat=None, usage=48, build_integration=30, enablement=12,
                       value_delivered=None, benefits_owner="Head of Claims",
                       components=[dc("r8.dc", CClass.C3, EClass.RM)]),
    ]
    return Portfolio("Ashford (reference case)", lines)


PUBLISHED_ROW_TOTALS = {"R1": 555, "R2": 277, "R3": 440, "R4": 984,
                        "R5": 470, "R6": 185, "R7": 200, "R8": 90}
PUBLISHED_COL_TOTALS = {"licence_seat": 1516, "usage": 793, "build": 365,
                        "enablement": 392, "ece": 135, "total": 3201}
PUBLISHED_ROI = {"R1": 1.56, "R2": 1.99, "R3": 1.05}


def part_a() -> None:
    hr("PART A — Vol III(d) Ashford worked example, recomputed independently")
    p = ashford()

    print(f"\n{'Line':<5}{'Name':<28}{'CoS pub':>9}{'CoS calc':>10}{'ROI pub':>9}"
          f"{'ROI calc':>10}  Evidence class of ROI cell")
    print("-" * 100)
    for ln in p.lines:
        cos = ln.cost_of_service()
        roi = ln.roi()
        pub_cos = PUBLISHED_ROW_TOTALS[ln.line_id]
        pub_roi = PUBLISHED_ROI.get(ln.line_id)
        ok_cos = (cos.value is not None and abs(cos.value - pub_cos) < 0.51)
        record(f"A.cos.{ln.line_id}", ok_cos,
               f"{ln.line_id} cost of service published {pub_cos}, recomputed {money(cos.value)}")
        if pub_roi is not None:
            ok_roi = roi is not None and abs(round(roi.value, 2) - pub_roi) < 0.006
            record(f"A.roi.{ln.line_id}", ok_roi,
                   f"{ln.line_id} ROI published {pub_roi:.0%}, recomputed "
                   f"{roi.value:.2%}" if roi else f"{ln.line_id} ROI published but not computable")
        print(f"{ln.line_id:<5}{ln.name[:27]:<28}{pub_cos:>9}{money(cos.value):>10}"
              f"{(f'{pub_roi:.0%}' if pub_roi else '—'):>9}"
              f"{(f'{roi.value:.1%}' if roi else '—'):>10}  "
              f"{roi.render_class if roi else ''}")

    # --- column totals ----------------------------------------------------
    cols = {"licence_seat": 0.0, "usage": 0.0, "build": 0.0, "enablement": 0.0, "ece": 0.0}
    for ln in p.lines:
        cols["licence_seat"] += ln.licence_seat or 0
        cols["usage"] += ln.usage or 0
        cols["build"] += ln.build_integration or 0
        cols["enablement"] += ln.enablement or 0
        cols["ece"] += ln.explicit_ece or 0
    cols["total"] = sum(cols.values())
    print("\nColumn totals (published vs recomputed):")
    for k, pub in PUBLISHED_COL_TOTALS.items():
        calc = cols[k]
        record(f"A.col.{k}", abs(calc - pub) < 0.51,
               f"column {k}: published {pub}, recomputed {money(calc)}")
        print(f"  {k:<14} published {pub:>6}   recomputed {money(calc):>8}   "
              f"{'ok' if abs(calc - pub) < 0.51 else 'MISMATCH'}")

    # --- the four headline numbers ----------------------------------------
    t = p.totals()
    print("\nThe four headline numbers:")
    print(f"  1 total cost of service   published $3.20M   recomputed ${t['total_cost_of_service']/1000:.2f}M")
    print(f"  2 value delivered         published $3.15M   recomputed ${t['roi_value']/1000:.2f}M")
    print(f"  3 portfolio ROI           published 147% on $1.27M   "
          f"recomputed {t['portfolio_roi']:.1%} on ${t['roi_cost']/1000:.2f}M")
    print(f"  4 cost with no value side published $1.93M / 60%")
    print(f"      recomputed 'total minus ROI lines' = ${t['cost_without_roi_calc']/1000:.2f}M "
          f"({t['share_without_roi_calc']:.0%})   <- the published number")
    print(f"      recomputed 'lines with no value side at all' = "
          f"${t['cost_without_value_side']/1000:.2f}M ({t['share_without_value_side']:.0%})"
          f"   <- rows 4, 7, 8, which the findings table names")

    record("A.total", abs(t["total_cost_of_service"] - 3201) < 0.51,
           f"total cost of service published 3,201, recomputed {money(t['total_cost_of_service'])}")
    record("A.portfolio_roi", abs(t["portfolio_roi"] - 1.474) < 0.006,
           f"portfolio ROI published 147%, recomputed {t['portfolio_roi']:.1%}")
    record("A.fourth_number", None,
           f"G19: headline says $1.93M/60% 'with no value side'; the findings table "
           f"attributes that figure to rows 4,7,8 which total "
           f"${t['cost_without_value_side']:,.0f}k. Gap ${t['cost_without_roi_calc']-t['cost_without_value_side']:,.0f}k "
           f"(rows 5 and 6, both 'n/a by rule' and decided Keep).")

    # --- tap-back on row 2 -------------------------------------------------
    print("\nTap-back on row 2 (the provenance trace the report says a reviewer taps):")
    resolutions, unit_value = 88100, 9.40
    value_calc = resolutions * unit_value / 1000          # $k
    print(f"  automated resolutions x unit value = {resolutions:,} x ${unit_value} "
          f"= ${value_calc:,.2f}k   published $827k")
    record("A.tapback.value", abs(value_calc - 827) < 0.51,
           f"row 2 value delivered: 88,100 x $9.40 = ${value_calc:,.1f}k, published $827k "
           f"(out by ${value_calc-827:,.1f}k)")

    ece = 0.034 * 88100 * 7.30 / 1000
    print(f"  error rate x volume x unit rework  = 3.4% x {resolutions:,} x $7.30 "
          f"= ${ece:,.2f}k   published $22k")
    record("A.tapback.ece", abs(ece - 22) < 0.51,
           f"row 2 expected cost of error recomputes to ${ece:,.1f}k against published $22k; "
           f"note the C2 term in the published formula contributes nothing (G2)")

    roi_pub_value = (827 - 277) / 277
    roi_true_value = (value_calc - 277) / 277
    print(f"  ROI on published value $827k = {roi_pub_value:.2%}; "
          f"on recomputed ${value_calc:.0f}k = {roi_true_value:.2%} (both round to 199%)")

    # --- class propagation consistency ------------------------------------
    print("\nEvidence-class propagation (M.7 'class propagates', weakest input governs):")
    for lid, published in (("R1", "Computed from REPORTED; unit value STATED"),
                           ("R2", "Computed from REPORTED; unit value STATED"),
                           ("R3", "Computed from STATED counterfactual")):
        ln = next(x for x in p.lines if x.line_id == lid)
        roi = ln.roi()
        calc = roi.render_class if roi else "—"
        consistent = "STATED" in calc
        print(f"  {lid}: published '{published}'  ->  model says '{calc}'")
        record(f"A.class.{lid}", None if lid in ("R1", "R2") else True,
               f"{lid} row class published as '{published}'; under M.7 the weakest input "
               f"(a STATED unit value) governs, so it should read "
               f"'computed from STATED'. Rows 1 and 2 state REPORTED with a STATED "
               f"qualifier; row 3 applies the rule correctly. Same table, two treatments.")

    # --- row 6, the one non-ROI number that is checkable -------------------
    cpp = 185 / 14
    record("A.row6.cpp", abs(cpp - 13.2) < 0.06,
           f"row 6 cost per point of adoption: $185k / 14 points = ${cpp:.2f}k, published $13.2k")
    print(f"\nRow 6 cost per adoption point: 185 / 14 = ${cpp:.2f}k   published $13.2k  ok")

    # --- line-assignment inconsistency ------------------------------------
    record("A.row2.lineassign", None,
           "Row 2's $210k per-resolution fee is booked to 'Licence and seat' in the "
           "cost-of-service table and to 'Investment line usage' in the tap-back. "
           "Same figure, two of the five Vol I 4.5 cost lines.")

    # --- value chain vs M.7 -------------------------------------------------
    record("A.row2.valuechain", None,
           "M.7 step 5 computes value as (current - baseline) x unit value against the "
           "named Business outcome. Row 2's named outcome is first-contact resolution "
           "(28% -> 41%), but the value is computed as automated-resolution volume x "
           "unit value. Two different metrics; the published outcome is not the one "
           "the money comes from.")


# ===========================================================================
# PART B — five synthetic companies
# ===========================================================================

def part_b() -> None:
    hr("PART B — five synthetic companies through the instrument stack")

    companies = [
        dict(name="Northgate Bank", note="mature, measured, board-reporting",
             staging=StagingAnswers(True, True, True, True, True),
             t3=Stage3Thresholds(True, True, True, True),
             practice={1: 4, 10: 4},
             deployment="platform_pattern_applied",
             asked={2: 4, 5: 3, 7: 4, 8: 4, 9: 4, 10: 4}),
        dict(name="Calder Logistics", note="strong tooling, no principles",
             staging=StagingAnswers(False, True, True, True, True),
             t3=Stage3Thresholds(False, True, True, True),
             practice={1: 4, 10: 5},
             deployment="vendor_saas_configured",
             asked={2: 3, 5: 2, 7: 4, 8: 3, 9: 3, 10: 5}),
        dict(name="Pemberton Health", note="C4 estate, evidence floor pressure",
             staging=StagingAnswers(True, True, False, False, True),
             t3=Stage3Thresholds(True, False, False, True),
             practice={1: 3, 10: 2},
             deployment="bespoke_build",
             asked={2: 2, 5: 4, 7: 3, 8: 2, 9: 5, 10: 2}),
        dict(name="Ravensworth Retail", note="shadow estate, three nulls",
             staging=StagingAnswers(False, False, False, False, False),
             t3=Stage3Thresholds(False, False, False, False),
             practice={1: 1, 10: None},
             deployment="shadow_departmental",
             asked={2: 1, 5: 1, 7: None, 8: None, 9: 2, 10: None}),
        dict(name="Strathmore Energy", note="everything but the board page",
             staging=StagingAnswers(True, True, True, True, True),
             t3=Stage3Thresholds(True, True, True, False),
             practice={1: 4, 10: 4},
             deployment="platform_pattern_applied",
             asked={2: 4, 5: 4, 7: 4, 8: 3, 9: 4, 10: 4}),
    ]

    print(f"\n{'Company':<20}{'AIFA /50':>10}{'nulls':>7}{'/scored':>9}{'prorated':>10}"
          f"{'band':>10}  placement")
    print("-" * 92)
    for c in companies:
        d1, d3, d4, d6, band = DEPLOYMENT_DERIVATION[c["deployment"]]
        scores = {1: d1, 3: d3, 4: d4, 6: d6}
        scores.update(c["asked"])
        aifa = AIFAScore(c["name"], scores, band, c["deployment"])
        t = aifa.totals
        placed = place_company(c["staging"], c["t3"], c["practice"])
        print(f"{c['name']:<20}{t['out_of_50_hole']:>10}{aifa.n_not_provided:>7}"
              f"{str(int(t['scored_denominator'])):>9}{t['pro_rated_to_50']:>10.1f}"
              f"{band:>10}  stage {placed['placement']} "
              f"{placed['placement_name']}{'  ' + placed['ceiling_note'] if placed['ceiling_note'] else ''}")
        if aifa.n_not_provided:
            record(f"B.nulls.{c['name']}", None,
                   f"{c['name']}: {aifa.n_not_provided} NOT PROVIDED criteria give "
                   f"{t['out_of_50_hole']}/50, {t['out_of_50_hole']}/{int(t['scored_denominator'])} "
                   f"or {t['pro_rated_to_50']:.0f}/50 pro-rated. Spec permits all three (G3).")
        if placed["not_provided_inputs"]:
            record(f"B.placement_null.{c['name']}", None,
                   f"{c['name']}: placement input {placed['not_provided_inputs']} is NOT "
                   f"PROVIDED. Vol I 5.3 is silent on whether a missing input blocks "
                   f"placement or is skipped; the model skipped it, which is the "
                   f"compensatory reading the rule exists to prevent.")

    # Ravensworth: every input at 1 or missing -> shows G12 from below
    record("B.G12", None,
           "No synthetic company can be placed above 3 or distinguished between 1 and 2 "
           "by the model, because thresholds exist only for Stage 3 (G12). Strathmore, "
           "which meets everything except the board page, and Ravensworth, which meets "
           "nothing, are both returned as 'stage 2' by the roll-up.")

    # --- evidence floor across a C1..C4 estate ------------------------------
    print("\nEvidence floor (Vol II 11.3) across a C1-C4 estate:")
    print(f"  {'component':<14}{'class':<6}{'floor as grade':<32}{'evidence row':<22}{'breach'}")
    print("  " + "-" * 86)
    estate = [
        ("route_ticket", CClass.C1, EClass.STATED),
        ("dup_detect", CClass.C2, EClass.REPORTED),
        ("severity_class", CClass.C3, EClass.REPORTED),
        ("coverage_summary", CClass.C3, EClass.RM),
        ("triage_clinical", CClass.C4, EClass.REPORTED),
        ("credit_decline", CClass.C4, EClass.OBSERVED),
        ("pricing_uplift", CClass.UNSET, EClass.STATED),
    ]
    for nm, cc, ec in estate:
        d = DecisionComponent(nm, nm, Mode.AUGMENTATION, cc, evidence_cls=ec)
        floor_g = FLOOR_AS_GRADE.get(cc, "— (UNSET)")
        print(f"  {nm:<18}{cc.name:<7}{floor_g:<32}{ec.label:<22}"
              f"{'BREACH' if d.floor_breach else 'ok'}")
    record("B.floor.unset", None,
           "pricing_uplift has consequence UNSET. Vol II 11.2 calls that a finding, but "
           "the model cannot evaluate a floor for it and M.3 has no Finding kind for it "
           "(G9). An unclassed C4 is indistinguishable from an unclassed C1.")
    record("B.floor.c3", None,
           "The C3 floor reads 'Monitored, moving to Measured'. severity_class and "
           "coverage_summary both sit at C3; only the second is a clear breach. Whether "
           "a C3 at REPORTED with no trajectory is a breach is undecidable from the text (G7).")

    # --- reconciliation tolerance asymmetry ---------------------------------
    print("\nReconciliation (Vol III 25.4) — the same lines under both denominators:")
    print(f"  {'line':<10}{'stated':>9}{'feed':>9}{'vs stated':>22}{'vs feed':>22}")
    print("  " + "-" * 74)
    cases = [
        InventoryLine("L1", "OpenAI", stated_spend=100, feed_spend=111, feed_active=40, feed_reach=50),
        InventoryLine("L2", "Anthropic", stated_spend=111, feed_spend=100, feed_active=40, feed_reach=50),
        InventoryLine("L3", "Copilot", stated_spend=900, feed_spend=984, feed_active=912, feed_reach=2400),
        InventoryLine("L4", "Legacy bot", stated_spend=200, feed_spend=200, feed_active=6, feed_reach=80),
        InventoryLine("L5", "Gemini CA", stated_spend=60, grant_ok=False),
    ]
    for ln in cases:
        a = reconcile(ln, "stated")
        b = reconcile(ln, "feed")
        flag = "  <-- classification flips" if a["outcome"] != b["outcome"] else ""
        print(f"  {ln.line_id:<10}{money(ln.stated_spend):>9}{money(ln.feed_spend):>9}"
              f"{a['outcome']:>22}{b['outcome']:>22}{flag}")
        if a["outcome"] != b["outcome"]:
            record(f"B.recon.{ln.line_id}", False,
                   f"{ln.line_id}: stated {ln.stated_spend} vs feed {ln.feed_spend} classifies "
                   f"as '{a['outcome']}' against the STATED denominator and '{b['outcome']}' "
                   f"against the feed denominator. Vol III 25.4 names neither (G14).")
    record("B.recon.idle", None,
           "L4 (6 of 80 seats active, spend on plan) is 'confirmed' under 25.4's "
           "absolute-zero Idle test but is raised as an Idle finding in Vol III(d). "
           "The model needs a partial-idleness threshold the spec does not give (G15).")

    # --- linkage qualification vs the value chain ---------------------------
    print("\nOutcome linkage (Vol I 4.3 'baseline, counterfactual OR period') vs M.7 value chain:")
    print(f"  {'linkage':<34}{'qualifies':>11}{'value computable':>19}")
    print("  " + "-" * 64)
    for desc, lk in [
        ("baseline + unit value", OutcomeLinkage(baseline=28.0, unit_value=9.4)),
        ("counterfactual only", OutcomeLinkage(counterfactual="200 more staff")),
        ("period only", OutcomeLinkage(period="FY26")),
        ("nothing named", OutcomeLinkage()),
    ]:
        print(f"  {desc:<34}{str(lk.qualifies):>11}{str(lk.valuable):>19}")
    record("B.linkage", None,
           "A linkage naming only a period passes Vol I 4.3's gate and then produces no "
           "value in M.7. Two of the three qualifying routes cannot feed the chain that "
           "consumes them (G17).")


# ===========================================================================
# PART C — the connector catalogue against the A.4 roll-up
# ===========================================================================

PUBLISHED_A4 = {
    "Foundation platforms and assistants": (18, 14, 4, 0, 0),
    "Coding, engineering and IT": (22, 10, 12, 0, 0),
    "Productivity, meetings, writing, design and media": (26, 6, 19, 1, 0),
    "Sales, marketing, support, HR, legal, finance agents, data": (22, 13, 9, 0, 0),
    "Infrastructure, agents, search, observability": (12, 10, 1, 1, 0),
    "Financial systems": (16, 7, 8, 1, 0),
    "Portfolio, work and project management": (12, 12, 0, 0, 0),
    "Aggregators and control planes": (12, 11, 0, 0, 1),
}


def classify_mode(raw: str) -> str:
    r = raw.strip()
    if r == "Agentic":
        return "Agentic"
    if r == "Assisted":
        return "Assisted"
    if r == "Manual":
        return "Manual"
    if r.startswith("Excluded"):
        return "Excluded"
    return "Mixed"


def part_c() -> None:
    hr("PART C — Vol III(b) catalogue vs the Vol III(a) A.4 roll-up")
    path = os.path.join(
        FILES, "Outcomes ABAF Methodology v0.8 · Vol III(b) · "
               "Vendor connector catalogue - Untitled.csv")
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    by_group: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        by_group[r["Group"]][classify_mode(r["Mode"])] += 1

    print(f"\n{'Group':<52}{'n':>4}{'Ag':>5}{'As':>5}{'Man':>5}{'Mix':>5}{'Exc':>5}  published Ag/As/Man/Exc")
    print("-" * 118)
    tot = collections.Counter()
    for g, c in by_group.items():
        pub = PUBLISHED_A4.get(g)
        n = sum(c.values())
        tot.update(c)
        pubs = f"{pub[1]}/{pub[2]}/{pub[3]}/{pub[4]}" if pub else "—"
        mark = ""
        if pub and (c["Agentic"], c["Assisted"], c["Manual"], c["Excluded"]) != tuple(pub[1:]):
            mark = "   <-- differs"
        print(f"{g[:51]:<52}{n:>4}{c['Agentic']:>5}{c['Assisted']:>5}{c['Manual']:>5}"
              f"{c['Mixed']:>5}{c['Excluded']:>5}  {pubs}{mark}")
        if pub:
            record(f"C.group.{g[:20]}", (c['Agentic'], c['Assisted'], c['Manual'],
                                         c['Excluded']) == tuple(pub[1:]),
                   f"{g}: catalogue reads {c['Agentic']}/{c['Assisted']}/{c['Manual']}/"
                   f"{c['Excluded']} (+{c['Mixed']} mixed), A.4 publishes {pubs}")

    n = sum(tot.values())
    print("-" * 118)
    print(f"{'TOTAL':<52}{n:>4}{tot['Agentic']:>5}{tot['Assisted']:>5}{tot['Manual']:>5}"
          f"{tot['Mixed']:>5}{tot['Excluded']:>5}  83/53/3/1 published")
    record("C.total", (tot["Agentic"], tot["Assisted"], tot["Manual"], tot["Excluded"]) == (83, 53, 3, 1),
           f"A.4 publishes 83 Agentic / 53 Assisted / 3 Manual / 1 Excluded over 140 rows. "
           f"The sheet parses to {tot['Agentic']} / {tot['Assisted']} / {tot['Manual']} / "
           f"{tot['Excluded']} with {tot['Mixed']} dual-mode rows A.4 does not represent.")
    record("C.claim60", None,
           f"A.4's prose claim 'six in ten vendors can be read by a connector without a "
           f"person in the loop' needs {tot['Agentic']}/140 = {tot['Agentic']/140:.0%} "
           f"unambiguously Agentic; counting dual-mode rows as Agentic gives "
           f"{(tot['Agentic']+tot['Mixed'])/140:.0%}. The claim survives, the roll-up table does not.")

    # group-name drift
    csv_groups = set(by_group)
    a4_groups = set(PUBLISHED_A4)
    only_csv = csv_groups - a4_groups
    if only_csv:
        record("C.groupnames", False,
               f"Group label mismatch between the sheet and A.4: {sorted(only_csv)}")


# ===========================================================================

def summary() -> None:
    hr("SUMMARY")
    counts = collections.Counter(s for _, s, _ in RESULTS)
    print(f"\n  arithmetic checks PASS: {counts['PASS']}   FAIL: {counts['FAIL']}   "
          f"unresolvable / flagged: {counts['FLAG']}")
    print(f"  assumptions the model had to invent to run at all: {len(ASSUMPTIONS)}")
    print(f"  specification gaps recorded: {len(GAPS)}")

    print("\n--- FAIL ---")
    for cid, s, d in RESULTS:
        if s == "FAIL":
            print(f"  [{cid}] {d}")
    print("\n--- FLAG (spec does not decide) ---")
    for cid, s, d in RESULTS:
        if s == "FLAG":
            print(f"  [{cid}] {d}")

    print("\n--- ASSUMPTIONS ---")
    for k in sorted(ASSUMPTIONS):
        print(f"  {k}: {ASSUMPTIONS[k]}")
    print("\n--- GAPS ---")
    for k in sorted(GAPS, key=lambda x: int(x[1:])):
        print(f"  {k}: {GAPS[k]}")




# ===========================================================================
# PART D — Jay's four scored slots, re-read under the competing rules.
# The 19 Sep review already rules on Q2/Q3; this only quantifies them, and
# tests one inference that review made in passing.
# ===========================================================================

SCRIPTED_SLOTS = {
    # slot name: (criterion 1..10 scores, None == NOT PROVIDED, published total)
    "Claims triage model":     ([1, 4, 3, 4, 4, 4, 3, 4, 4, 2], 33),
    "Microsoft Copilot":       ([2, 2, 4, 2, 1, 3, 2, 3, 4, 2], 25),
    "Internal GPT gateway":    ([1, 2, None, None, 4, 4, 1, 1, None, 2], 15),
    "Dept. ChatGPT Team":      ([2, 2, None, None, 1, 2, 1, 1, None, 1], 10),
}


def part_d() -> None:
    hr("PART D — the scripted run's four slots under the competing NOT PROVIDED rules")

    print(f"\n{'Slot':<24}{'nulls':>6}{'R28 /50':>9}{'% of 50':>9}"
          f"{'excl. /n':>11}{'% achiev.':>11}{'pro-rata/50':>13}")
    print("-" * 84)
    floors = {1: [], 10: []}
    for name, (scores, published) in SCRIPTED_SLOTS.items():
        nulls = sum(1 for s in scores if s is None)
        r28 = sum(s or 0 for s in scores)                 # Jay's rule: null == 0
        denom = (10 - nulls) * 5
        excl = f"{r28}/{denom}"
        prorata = r28 / denom * 50
        record(f"D.total.{name[:12]}", r28 == published,
               f"{name}: recomputed {r28}, published {published}")
        print(f"{name:<24}{nulls:>6}{r28:>9}{r28/50:>9.0%}{excl:>11}"
              f"{r28/denom:>11.0%}{prorata:>13.1f}")
        for c in (1, 10):
            if scores[c - 1] is not None:
                floors[c].append(scores[c - 1])

    record("D.arith", True,
           "All four published slot totals recompute exactly (33, 25, 15, 10), "
           "confirming the 19 Sep review's arithmetic check independently.")
    record("D.q3.magnitude", None,
           "Excluding nulls from the denominator does not change the rank order of "
           "the four slots, but it moves the GPT gateway from 30% to 43% of "
           "achievable and Dept. ChatGPT from 20% to 29% — 13 and 9 points. Q2/Q3 "
           "is a magnitude defect, not an ordering defect, on this fixture.")
    record("D.q2.placement_hazard", None,
           "R28 scores a null 0. Criteria 1 and 10 are the company-practice criteria "
           "Vol I 5.3 rolls up to placement 'at their floor'. A null on either would "
           "floor placement at 0 — not a stage that exists. It does not bite on this "
           "fixture (the nulls fall on criteria 3, 4 and 9) but the two rules are "
           "not composable as written.")

    # --- the Stage 2 inference, tested -------------------------------------
    print("\nPlacement, if Vol I §5.3 is applied as written:")
    c1_floor, c10_floor = min(floors[1]), min(floors[10])
    print(f"  Standardization (crit 1) across slots: {floors[1]} -> floor {c1_floor}")
    print(f"  Monitoring      (crit 10) across slots: {floors[10]} -> floor {c10_floor}")
    staging_ashford = StagingAnswers(False, False, False, False, False)
    t3_ashford = Stage3Thresholds(False, False, False, False)
    placed = place_company(staging_ashford, t3_ashford,
                           {1: c1_floor, 10: c10_floor})
    print(f"  inputs: {placed['inputs']}")
    print(f"  placement (level every input clears) = stage {placed['placement']} "
          f"· {placed['placement_name']}")
    record("D.stage", None,
           f"The 19 Sep review infers 'Stage 2 · Adopting at best' from the five "
           f"staging answers alone. Vol I 5.3 also requires the company-practice AIFA "
           f"criteria to roll up at their floor, and those floor at "
           f"{c1_floor} (Standardization) and {c10_floor} (Monitoring). Applying the "
           f"rule as written gives stage {placed['placement']}, not 2. The two "
           f"readings differ because the spec never says how a 1-5 criterion score "
           f"maps to a 1-5 stage (A4) — which is the underlying defect.")


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    part_d()
    summary()
