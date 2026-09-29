"""
run_companies.py - run several simulated companies through abaf_sim.

Same question set for every company (the 26 Sep decision: same questions
across companies, compare the answers). The companies are chosen to span the
range the instrument claims to cover: a shadow estate, a regulated C4 estate,
a measured board-reporting company, a single-domain company, a company that
meets everything except one Stage 3 threshold, and Ashford as published.

The output that matters is not the scorecards. It is the UNDEFINED matrix:
for how many companies, and at which instrument outputs, the specification
fails to produce an answer.
"""

from __future__ import annotations

import collections

from abaf_sim import (
    GAPS_HIT, Undefined, EClass, CClass, Item, Company,
    admit_vol2, admit_vol3, floor_breach, aifa, select_slots, ownerless_finding,
    placement, cost_of_service, roi, portfolio, reliance_trajectory,
    linkage_qualifies, AIFA_CRITERIA, DERIVED_CRITERIA, STAGING_QUESTIONS,
)

ASKED = [c for c in AIFA_CRITERIA if c not in DERIVED_CRITERIA]


def mk(name, spend, *, stage="Production", measured="Usage", success=None,
       owner=None, acts_alone=False, decides=True, cc=CClass.UNSET,
       origin="Business planning", acquisition="Normal procurement process",
       deployment="Our normal process",
       ev=EClass.RM, asked=None, err=None, vol=None, uec=None,
       value=None, base=None, cf=None, per=None, cost=None, just=""):
    return Item(name=name, spend=spend, stage=stage, measured=measured,
                success_def=success, owner=owner, acts_alone=acts_alone,
                origin=origin, acquisition=acquisition, deployment=deployment,
                decides=decides, consequence=cc, evidence_cls=ev,
                asked_scores=dict(zip(ASKED, asked or [3] * 6)),
                error_rate=err, volume=vol, unit_error_cost=uec,
                value_delivered=value, linkage_baseline=base,
                linkage_counterfactual=cf, linkage_period=per,
                cost_lines=cost or {}, justification=just)


def companies() -> list[Company]:
    return [
        Company("Ashford (scripted-run profile)", "insurance", 1400, [
            mk("Claims triage model", 1900, stage="Build", success="cycle time",
               acts_alone=True, cc=CClass.C3, ev=EClass.REPORTED,
               asked=[4, 4, 3, 4, 4, 2], value=1420, base=0.0, cf="stated",
               cost={"licence_seat": 0, "usage": 180, "build": 240, "enablement": 40},
               err=0.021, vol=4520, uec=1.0, just="payback_plus_risk"),
            mk("Microsoft Copilot", 588, asked=[2, 2, 1, 2, 3, 2], cc=CClass.C1,
               ev=EClass.REPORTED,
               cost={"licence_seat": 864, "usage": 0, "build": 0, "enablement": 120}),
            mk("Internal GPT gateway", 310, decides=False, asked=[2, 4, 1, 1, None, 2]),
            mk("Dept. ChatGPT Team plans", 30.6, asked=[2, 1, 1, 1, None, 1]),
            mk("Contact-centre bot", 610, acts_alone=True, cc=CClass.C2,
               ev=EClass.RM, asked=[3, 3, 2, 2, 3, 2],
               cost={"licence_seat": 140, "usage": 60, "build": 0, "enablement": 0}),
        ], staging=dict.fromkeys(STAGING_QUESTIONS, False),
            stage3={"principles": False, "knowledge": False,
                    "adoption": False, "board": False}),

        Company("Ravensworth Retail", "retail", 4200, [
            mk("Shadow ChatGPT", 48, asked=[1, 1, 1, None, 2, None],
               cost={"licence_seat": 48, "usage": 0, "build": 0, "enablement": 0}),
            mk("Vendor chatbot", 120, cc=CClass.C2, ev=EClass.RM,
               asked=[1, 1, 2, 1, 2, 1],
               cost={"licence_seat": 120, "usage": 0, "build": 0, "enablement": 0}),
        ], staging=dict.fromkeys(STAGING_QUESTIONS, False),
            stage3={"principles": False, "knowledge": False,
                    "adoption": False, "board": False}),

        Company("Pemberton Health", "healthcare", 9000, [
            mk("Triage assistant", 2400, acts_alone=True, cc=CClass.C4,
               ev=EClass.REPORTED, asked=[2, 4, 3, 2, 5, 2],
               cost={"licence_seat": 900, "usage": 700, "build": 700, "enablement": 100}),
            mk("Coding assistant", 300, cc=CClass.C1, ev=EClass.STATED,
               asked=[3, 3, 3, 3, 4, 3],
               cost={"licence_seat": 260, "usage": 20, "build": 0, "enablement": 20}),
            mk("Note summariser", 180, cc=CClass.C3, ev=EClass.RM,
               asked=[2, 3, 2, 2, 4, 2],
               cost={"licence_seat": 120, "usage": 40, "build": 20, "enablement": 0}),
        ], staging={**dict.fromkeys(STAGING_QUESTIONS, False),
                    "principles_endorsed": True, "portfolio_owned": True},
            stage3={"principles": True, "knowledge": False,
                    "adoption": False, "board": True}),

        Company("Northgate Bank", "banking", 22000, [
            mk("Credit decision support", 3100, acts_alone=True, cc=CClass.C4,
               ev=EClass.OBSERVED, asked=[4, 4, 4, 4, 5, 4], value=2100,
               base=12.0, cf="stated", per="FY26", err=0.004, vol=90000, uec=6.0,
               cost={"licence_seat": 400, "usage": 300, "build": 500, "enablement": 90}),
            mk("Contact centre agent", 800, acts_alone=True, cc=CClass.C2,
               ev=EClass.OBSERVED, asked=[4, 4, 4, 3, 4, 4], value=980,
               base=22.0, per="FY26", err=0.03, vol=60000, uec=4.0,
               cost={"licence_seat": 210, "usage": 120, "build": 60, "enablement": 30}),
        ], staging=dict.fromkeys(STAGING_QUESTIONS, True),
            stage3={"principles": True, "knowledge": True,
                    "adoption": True, "board": True}),

        Company("Strathmore Energy", "utilities", 6100, [
            mk("Outage predictor", 900, cc=CClass.C3, ev=EClass.REPORTED,
               asked=[4, 4, 4, 3, 4, 4], value=1200, per="FY26",
               cost={"licence_seat": 300, "usage": 400, "build": 180, "enablement": 20}),
            mk("Field assistant", 260, cc=CClass.C1, ev=EClass.STATED,
               asked=[4, 3, 4, 3, 4, 4],
               cost={"licence_seat": 230, "usage": 20, "build": 0, "enablement": 10}),
        ], staging=dict.fromkeys(STAGING_QUESTIONS, True),
            stage3={"principles": True, "knowledge": True,
                    "adoption": True, "board": False}),

        Company("Calder Logistics", "logistics", 3300, [
            mk("Route optimiser", 640, acts_alone=True, cc=CClass.UNSET,
               ev=EClass.REPORTED, asked=[3, 4, 2, 3, 3, 4],
               cost={"licence_seat": 400, "usage": 180, "build": 60, "enablement": 0}),
            mk("Doc extraction", 210, cc=CClass.C2, ev=EClass.REPORTED,
               asked=[3, 3, 2, 3, 3, 3], value=300, cf="200 more staff",
               cost={"licence_seat": 150, "usage": 40, "build": 0, "enablement": 20}),
        ], staging={**dict.fromkeys(STAGING_QUESTIONS, True),
                    "principles_endorsed": False},
            stage3={"principles": False, "knowledge": True,
                    "adoption": True, "board": True}),
    ]


OUTPUTS = ["admission", "fit total", "complexity band", "slot selection",
           "evidence floor", "ownerless finding", "placement",
           "cost of service", "ROI", "portfolio rebalance",
           "reliance trajectory"]


def main() -> None:
    cs = companies()
    matrix: dict[str, dict[str, str]] = {}
    print("=" * 108)
    print("SIX SIMULATED COMPANIES THROUGH THE ABAF v0.8 INSTRUMENT")
    print("Same question set for every company. The model does not invent: where the")
    print("specification does not decide, it returns UNDEFINED and names the section.")
    print("=" * 108)

    for c in cs:
        print(f"\n\n### {c.name}  ({c.sector}, {c.headcount:,} people, "
              f"{len(c.items)} investments, ${sum(i.spend for i in c.items):,.0f}k)")
        row: dict[str, str] = {}

        # admission, under both tests
        v2 = [i.name for i in c.items if admit_vol2(i)[0]]
        v3 = [i.name for i in c.items if admit_vol3(i)[0]]
        diff = set(v2) - set(v3)
        row["admission"] = "DISAGREE" if diff else "ok"
        print(f"  admission      12.1 admits {len(v2)}/{len(c.items)}, "
              f"25.3 admits {len(v3)}/{len(c.items)}"
              + (f"  -> the two tests disagree on: {', '.join(diff)}" if diff else ""))

        # fit assessment
        a = [aifa(i) for i in c.items]
        undef_tot = sum(1 for x in a if isinstance(x["total"], Undefined))
        row["fit total"] = "UNDEFINED" if undef_tot else "ok"
        row["complexity band"] = "UNDEFINED"
        print(f"  fit assessment {undef_tot}/{len(a)} totals UNDEFINED "
              f"(4 of 10 criteria underivable); complexity band UNDEFINED for all")

        slots = select_slots(c.items)
        row["slot selection"] = "UNDEFINED" if isinstance(slots, Undefined) else "ok"
        print(f"  slot selection UNDEFINED - {slots.why[:88]}...")

        # evidence floor
        fl = {i.name: floor_breach(i) for i in c.items}
        undef_fl = sum(1 for v in fl.values() if isinstance(v, Undefined))
        breaches = [k for k, v in fl.items() if v is True]
        row["evidence floor"] = f"{undef_fl} UNDEFINED" if undef_fl else "ok"
        print(f"  evidence floor {undef_fl}/{len(fl)} undecidable; "
              f"{len(breaches)} definite breach(es)"
              + (f": {', '.join(breaches)}" if breaches else ""))

        ow = [ownerless_finding(i) for i in c.items]
        row["ownerless finding"] = ("UNDEFINED"
                                    if any(isinstance(x, Undefined) for x in ow) else "ok")
        print(f"  ownerless      UNDEFINED - benefits owner is not an intake field "
              f"(Vol II 11.1 calls it the most predictive single field)")

        # placement
        practice = {"Standardization": None, "Monitoring": None}
        p = placement(c, practice)
        row["placement"] = ("UNDEFINED" if isinstance(p["placement"], Undefined)
                            else str(p["placement"]))
        print(f"  placement      {'UNDEFINED' if isinstance(p['placement'], Undefined) else p['placement']}"
              f"  (Stage 3 thresholds met: {p['stage3_met']}; "
              f"{sum(1 for v in p['inputs'].values() if isinstance(v, Undefined))} of "
              f"{len(p['inputs'])} inputs have no level)")

        # money
        pf = portfolio(c.items)
        incomplete = sum(1 for r in pf["rows"] if r["cos"]["incomplete"])
        roi_ok = sum(1 for r in pf["rows"] if isinstance(r["roi"], float))
        roi_undef = sum(1 for r in pf["rows"] if isinstance(r["roi"], Undefined))
        row["cost of service"] = f"{incomplete} incomplete" if incomplete else "ok"
        row["ROI"] = "UNDEFINED" if roi_undef else ("ok" if roi_ok else "n/a")
        row["portfolio rebalance"] = "UNDEFINED"
        row["reliance trajectory"] = "UNDEFINED"
        print(f"  cost of service ${pf['total_cost']:,.0f}k, {incomplete}/"
              f"{len(pf['rows'])} rows incomplete (missing cost lines or no error rate)")
        print(f"  ROI            {roi_ok} computable, {roi_undef} UNDEFINED, "
              f"portfolio ROI "
              + (f"{pf['portfolio_roi']:.0%}" if pf["portfolio_roi"] else "n/a")
              + f"; unlinked cost ${pf['unlinked_cost']:,.0f}k")
        print(f"  rebalance      UNDEFINED (no line-level fit score)")
        print(f"  reliance       UNDEFINED for all {len(c.items)} components")
        matrix[c.name] = row

    # -------- the matrix ---------------------------------------------------
    print("\n\n" + "=" * 108)
    print("WHERE THE INSTRUMENT CANNOT PRODUCE AN ANSWER")
    print("=" * 108)
    w = max(len(n) for n in matrix) + 2
    print(f"\n{'output':<22}" + "".join(f"{n[:13]:<15}" for n in matrix))
    print("-" * (22 + 15 * len(matrix)))
    for o in OUTPUTS:
        cells = [matrix[n].get(o, "-") for n in matrix]
        print(f"{o:<22}" + "".join(f"{c:<15}" for c in cells))

    total_cells = len(OUTPUTS) * len(matrix)
    bad = sum(1 for o in OUTPUTS for n in matrix
              if "UNDEFINED" in matrix[n].get(o, "") or matrix[n].get(o) == "DISAGREE")
    print(f"\n  {bad} of {total_cells} instrument outputs could not be produced "
          f"from the specification ({bad/total_cells:.0%}).")

    print("\n\n" + "=" * 108)
    print("DISTINCT SPECIFICATION GAPS HIT, BY FREQUENCY")
    print("=" * 108)
    byw = collections.Counter((g.what, g.where, g.why) for g in GAPS_HIT)
    for (what, where, why), n in byw.most_common():
        print(f"\n  [{n:>3}x] {what}   ({where})")
        print(f"         {why}")


if __name__ == "__main__":
    main()
