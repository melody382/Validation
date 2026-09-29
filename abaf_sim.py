"""
abaf_sim.py - an executable model of the ABAF v0.8 instrument.

Design rule: THE MODEL DOES NOT INVENT.

Where the specification decides something, this implements it. Where it does
not, the function returns UNDEFINED carrying the reason and the section that
should have decided it. Nothing is silently filled in. That way, running N
companies measures how often the instrument cannot produce an answer, which
is the thing item 2 was asked to find.

Every implemented rule cites the section it comes from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional, Union


# ---------------------------------------------------------------------------

class Undefined:
    """Returned where the specification does not decide. Not a value."""

    __slots__ = ("what", "why", "where")

    def __init__(self, what: str, why: str, where: str):
        self.what, self.why, self.where = what, why, where

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"UNDEFINED({self.what})"


Result = Union[float, int, str, None, Undefined]
GAPS_HIT: list[Undefined] = []


def undefined(what: str, why: str, where: str) -> Undefined:
    u = Undefined(what, why, where)
    GAPS_HIT.append(u)
    return u


# --- Vol II 13.2 evidence classes ------------------------------------------
class EClass(IntEnum):
    RM = 0
    STATED = 1
    REPORTED = 2
    OBSERVED = 3

    @property
    def label(self) -> str:
        return ["REQUIRES MEASUREMENT", "STATED", "REPORTED", "OBSERVED"][int(self)]


class Mode(IntEnum):
    UNDETERMINED = 0
    AUGMENTATION = 1
    AUTOMATION = 2


class CClass(IntEnum):
    UNSET = 0
    C1 = 1
    C2 = 2
    C3 = 3
    C4 = 4


# ---------------------------------------------------------------------------
# The question set. Same questions for every company (the 26 Sep meeting rule:
# same questions across companies, compare the answers).
# Mirrors Jay's scripted run: per-item inventory, ten criteria, five staging.
# ---------------------------------------------------------------------------

# Jay's actual per-item intake, read off the scripted run's S1B table
# ("asked once per inventory item, recorded never scored, 7 items").
INVENTORY_FIELDS = ["item", "spend", "origin", "acquisition", "deployment",
                    "measured", "success_def", "stage", "since"]

# Answer values observed in the scripted run for the deployment-model question,
# the one Vol II 12.5 derives four criteria and the complexity band from.
DEPLOYMENT_ANSWERS = ["Our normal process", "A test group", "A special process"]

# Benefits owner is NOT in Jay's intake (19 Sep review, Q10) although Vol II
# 11.1 calls it "the most predictive single field" and Vol I 4.3 requires it
# before funding. Anything needing it therefore has no input to read.
INTAKE_COLLECTS_BENEFITS_OWNER = False

AIFA_CRITERIA = [
    "Standardization", "Interoperability", "Scalability", "Reconfigurability",
    "Sovereignty", "Implementation flexibility", "Manageability",
    "Documentation", "Standards compliance", "Monitoring",
]
DERIVED_CRITERIA = {"Standardization", "Scalability",
                    "Reconfigurability", "Implementation flexibility"}

STAGING_QUESTIONS = [
    "principles_endorsed",
    "scored_repeatable_evaluation",
    "outcome_stated_per_investment",
    "adoption_measured_behaviourally",
    "portfolio_owned",
]


@dataclass
class Item:
    """One inventory line, answered against the common question set."""
    name: str
    spend: float
    stage: str
    measured: str
    success_def: Optional[str]
    owner: Optional[str]
    acts_alone: bool
    decides: bool                      # does the thing decide anything at all
    consequence: CClass = CClass.UNSET
    evidence_cls: EClass = EClass.RM
    origin: str = ""
    acquisition: str = ""
    deployment: str = ""
    asked_scores: dict[str, Optional[int]] = field(default_factory=dict)
    error_rate: Optional[float] = None
    volume: Optional[float] = None
    unit_error_cost: Optional[float] = None
    value_delivered: Optional[float] = None
    linkage_baseline: Optional[float] = None
    linkage_counterfactual: Optional[str] = None
    linkage_period: Optional[str] = None
    cost_lines: dict[str, Optional[float]] = field(default_factory=dict)
    justification: str = ""


@dataclass
class Company:
    name: str
    sector: str
    headcount: int
    items: list[Item]
    staging: dict[str, bool]
    stage3: dict[str, bool]
    knowledge_every_host: bool = False


# ---------------------------------------------------------------------------
# 1. Admission — Vol II 12.1 vs Vol III 25.3
# ---------------------------------------------------------------------------

def admit_vol2(item: Item) -> tuple[bool, str]:
    """Vol II 12.1: admitted if a mode can be assigned. UNDETERMINED counts."""
    return True, "mode assignable (UNDETERMINED always available) - 12.1"


def admit_vol3(item: Item) -> tuple[bool, str]:
    """Vol III 25.3: substrate where no admissible component sits beneath."""
    if not item.decides:
        return False, "no admissible component beneath it - 25.3"
    return True, "decides something - 25.3"


# ---------------------------------------------------------------------------
# 2. Evidence floor — Vol II 11.3, against Vol III 23.3
# ---------------------------------------------------------------------------

FLOOR_GRADE = {CClass.C1: "Estimated", CClass.C2: "Monitored",
               CClass.C3: "Monitored, moving to Measured", CClass.C4: "Measured"}


def floor_breach(item: Item) -> Union[bool, Undefined]:
    if item.consequence is CClass.UNSET:
        return undefined(
            "floor for an UNSET consequence class",
            "11.2 calls UNSET a finding but gives it no floor, and M.3 has no "
            "Finding kind for it",
            "Vol II 11.2 / M.3")
    if item.consequence is CClass.C3:
        return undefined(
            "C3 floor test",
            "the floor reads 'Monitored, moving to Measured' - two values and a "
            "trajectory with no date, which cannot be tested pass/fail",
            "Vol II 11.3")
    if item.consequence in (CClass.C1, CClass.C2) and item.evidence_cls is EClass.RM:
        return undefined(
            "whether a C1/C2 with no evidence breaches",
            "11.3 gives C1 and C2 a floor; 23.3 restricts breach to C3 and C4",
            "Vol II 11.3 vs Vol III 23.3")
    if item.consequence is CClass.C4:
        return item.evidence_cls < EClass.OBSERVED
    return False


# ---------------------------------------------------------------------------
# 3. The fit assessment — Vol II 12
# ---------------------------------------------------------------------------

def aifa(item: Item) -> dict:
    scores: dict[str, Result] = {}
    for c in AIFA_CRITERIA:
        if c in DERIVED_CRITERIA:
            # The input exists: Jay's intake asks the deployment-model question
            # and the answer is in hand. What is missing is the mapping.
            scores[c] = undefined(
                f"derived criterion {c}",
                f"12.5 derives it from the deployment-model question, which IS "
                f"asked and answered ('{item.deployment}'), but no table maps "
                f"that answer to a 1-5 score. The implementation abandoned the "
                f"derivation entirely (scripted run R27: 'nothing derived')",
                "Vol II 12.5")
        else:
            scores[c] = item.asked_scores.get(c)

    band = undefined("complexity band",
                     "12.5 derives the band from the same missing table",
                     "Vol II 12.4 / 12.5")

    asked = [v for k, v in scores.items() if k not in DERIVED_CRITERIA]
    provided = [v for v in asked if isinstance(v, int)]
    nulls = sum(1 for v in asked if v is None)

    total: Result
    if any(isinstance(v, Undefined) for v in scores.values()):
        total = undefined("fit assessment total out of 50",
                          "four of the ten criteria cannot be produced",
                          "Vol II 12.5")
    elif nulls:
        total = undefined("total with NOT PROVIDED criteria",
                          "12.3 fixes the total at /50 and allows NOT PROVIDED "
                          "but never states the denominator",
                          "Vol II 12.3")
    else:
        total = sum(provided)

    return {"scores": scores, "band": band, "total": total,
            "nulls": nulls, "asked_subtotal": sum(provided)}


def select_slots(items: list[Item]) -> Union[list[Item], Undefined]:
    """Vol II 12.5: largest by spend, widest by reach, least governed."""
    scored = [i for i in items if admit_vol3(i)[0]]
    if not scored:
        return []
    largest = max(scored, key=lambda i: i.spend)
    least_governed = undefined(
        "least-governed slot",
        "'least governed' is measured by criteria 7 and 10, which are outputs "
        "of the assessment this rule is selecting the subject for",
        "Vol II 12.5")
    return undefined(
        "slot selection",
        f"largest-by-spend resolves ({largest.name}); 'widest by reach' has no "
        f"reach field in the question set; 'least governed' is circular; and no "
        f"de-duplication rule exists when one capability satisfies two",
        "Vol II 12.5")


# ---------------------------------------------------------------------------
# 4. Placement — Vol I 5.2, 5.3, Vol II 14
# ---------------------------------------------------------------------------

def placement(c: Company, practice_scores: dict[str, Result]) -> dict:
    inputs: dict[str, Result] = {}

    stage3_met = all(c.stage3.values())
    inputs["stage3_gate"] = 3 if stage3_met else undefined(
        "which stage a company that fails Stage 3 sits at",
        "thresholds exist for Stage 3 only; stages 1, 2, 4 and 5 have narrative "
        "characteristics and no thresholds",
        "Vol I 5.2")

    strong = sum(1 for q in STAGING_QUESTIONS if c.staging.get(q))
    inputs["staging"] = undefined(
        "level from the five staging questions",
        f"{strong} of 5 answered strongly, but no question carries a level "
        f"scale - each has one 'weak answer' exemplar and nothing else",
        "Vol II 14")

    for crit in ("Standardization", "Monitoring"):
        v = practice_scores.get(crit)
        inputs[f"practice:{crit}"] = (
            v if isinstance(v, int) else
            undefined(f"company-practice roll-up for {crit}",
                      "5.3 rolls these up 'at their floor' but never maps a 1-5 "
                      "criterion score onto a 1-5 stage",
                      "Vol I 5.3"))

    numeric = [v for v in inputs.values() if isinstance(v, int)]
    result: Result = (min(numeric) if numeric and
                      not any(isinstance(v, Undefined) for v in inputs.values())
                      else undefined(
                          "maturity placement",
                          "'the level every input clears' cannot run while any "
                          "input has no level",
                          "Vol I 5.3"))
    return {"inputs": inputs, "placement": result, "stage3_met": stage3_met}


# ---------------------------------------------------------------------------
# 5. Cost of service and ROI — Vol I 4.5, 4.4, M.7
# ---------------------------------------------------------------------------

COST_LINES = ["licence_seat", "usage", "build", "enablement"]


def expected_cost_of_error(item: Item) -> Result:
    if item.consequence is CClass.UNSET:
        return undefined("expected cost of error",
                         "no consequence class set", "Vol I 4.5")
    if item.error_rate is None or item.volume is None or item.unit_error_cost is None:
        return undefined("expected cost of error",
                         "no observed error rate - 4.5 says an unmeasured C4 is "
                         "an unbounded line, and that is the finding",
                         "Vol I 4.5")
    # volume in units, unit_error_cost in dollars, result in $k to match
    # the cost lines (Vol I 4.5 exposure = volume x cost per wrong output)
    return item.error_rate * item.volume * item.unit_error_cost / 1000.0


def cost_of_service(item: Item) -> dict:
    parts = {k: item.cost_lines.get(k) for k in COST_LINES}
    ece = expected_cost_of_error(item)
    known = [v for v in parts.values() if v is not None]
    incomplete = any(v is None for v in parts.values()) or isinstance(ece, Undefined)
    total = sum(known) + (ece if isinstance(ece, (int, float)) else 0)
    return {"lines": parts, "ece": ece, "total": total, "incomplete": incomplete}


def linkage_qualifies(item: Item) -> bool:
    """Vol I 4.3 - baseline OR counterfactual OR period."""
    return any(x is not None for x in
               (item.linkage_baseline, item.linkage_counterfactual, item.linkage_period))


def roi(item: Item) -> Result:
    cos = cost_of_service(item)
    if item.value_delivered is None:
        return None
    if not linkage_qualifies(item):
        return None
    if item.linkage_baseline is None:
        return undefined(
            "value delivered from a qualifying linkage",
            "4.3 qualifies a linkage on baseline OR counterfactual OR period, "
            "but M.7 computes (current - baseline) x unit value, which needs a "
            "baseline",
            "Vol I 4.3 vs M.7")
    if cos["incomplete"]:
        return undefined("ROI", "cost side incomplete - total marked incomplete "
                                "rather than understated", "M.7")
    if not cos["total"]:
        return None
    return (item.value_delivered - cos["total"]) / cos["total"]


def portfolio(items: list[Item]) -> dict:
    rows = []
    for i in items:
        rows.append({"item": i, "cos": cost_of_service(i), "roi": roi(i)})
    total = sum(r["cos"]["total"] for r in rows)
    roi_rows = [r for r in rows if isinstance(r["roi"], float)]
    roi_cost = sum(r["cos"]["total"] for r in roi_rows)
    roi_val = sum(r["item"].value_delivered for r in roi_rows)
    return {
        "rows": rows,
        "total_cost": total,
        "portfolio_roi": (roi_val - roi_cost) / roi_cost if roi_cost else None,
        "unlinked_cost": sum(r["cos"]["total"] for r in rows
                             if r["item"].value_delivered is None),
        "rebalance": undefined(
            "portfolio rebalance ranking",
            "4.7 ranks investments on fit score against consequence-weighted "
            "exposure, but fit score is keyed to a component and portfolio rows "
            "to an investment line, with no line-level roll-up and no weighting "
            "formula",
            "Vol I 4.7 / 22"),
    }


def ownerless_finding(item: Item) -> Union[bool, Undefined]:
    """Vol III 23.3 finding 2: investment lines with no benefits owner."""
    if not INTAKE_COLLECTS_BENEFITS_OWNER:
        return undefined(
            "ownerless-investment finding",
            "23.3 makes it one of the four findings discovery is built to "
            "surface, and 11.1 calls benefits owner the most predictive single "
            "field, but the intake does not ask for it",
            "Vol III 23.3 vs the delivered intake")
    return item.owner is None


def reliance_trajectory(item: Item) -> Undefined:
    return undefined(
        "reliance trajectory",
        "11.1 requires it on every component; 24.2 confirms no host returns it "
        "and no metric, surface or derivation is defined anywhere",
        "Vol II 11.1 / Vol III 24.2")
