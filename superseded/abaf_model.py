"""
abaf_model.py — an independent implementation of the ABAF v0.8 instrument mechanics.

Built from the rules as *written* in Volumes I, II and III (16/26 Sep 2026).
It deliberately reuse the  question-set, scoring anchors or the
run-scripted generator. Where the specification does not define a mechanic
that an implementer must have, this module raises SpecGap or applies an
explicitly labelled ASSUMPTION, so the report can distinguish
"the framework says X and X is wrong" from "the framework does not say".

Every ASSUMPTION id (A1..A9) and every SPECGAP id (G1..G..) is cross-referenced
in VALIDATION-REPORT.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Callable, Iterable, Optional

# ---------------------------------------------------------------------------
# Registry of assumptions and gaps, so the report is generated, not asserted
# ---------------------------------------------------------------------------

ASSUMPTIONS: dict[str, str] = {}
GAPS: dict[str, str] = {}


def assumption(aid: str, text: str) -> str:
    ASSUMPTIONS.setdefault(aid, text)
    return aid


def gap(gid: str, text: str) -> str:
    GAPS.setdefault(gid, text)
    return gid


class SpecGap(Exception):
    """Raised where the spec does not define a mechanic the instrument needs."""


# ---------------------------------------------------------------------------
# §13 Evidence classes and grades
# ---------------------------------------------------------------------------

assumption(
    "A1",
    "Evidence classes are totally ordered RM < STATED < REPORTED < OBSERVED. "
    "Vol II 13.2 lists four classes and never publishes an ordering, but "
    "Vol III 21 ('computed from REPORTED inputs') and M.7 ('a cell computed "
    "from a REPORTED cost and a STATED unit value is computed-from-STATED') "
    "both require one to evaluate a computed cell.",
)


class EClass(IntEnum):
    RM = 0          # REQUIRES MEASUREMENT
    STATED = 1
    REPORTED = 2
    OBSERVED = 3

    @property
    def label(self) -> str:
        return {0: "REQUIRES MEASUREMENT", 1: "STATED", 2: "REPORTED", 3: "OBSERVED"}[int(self)]


class Grade(IntEnum):
    """Vol II 13.3. Artifact-level only; M.3 says a grade is set by a Review."""
    NONE = 0
    ESTIMATED = 1
    MONITORED = 2
    MEASURED = 3

    @property
    def label(self) -> str:
        return {0: "—", 1: "Estimated", 2: "Monitored", 3: "Measured"}[int(self)]


@dataclass
class Cell:
    """Vol II 13, Vol III 25.5. A value with a class and a provenance chain."""
    ref: str
    value: Optional[float]
    cls: EClass
    unit: str = ""
    source: str = ""
    computed: bool = False
    inputs: tuple[str, ...] = ()
    formula: str = ""
    incomplete: bool = False

    @property
    def render_class(self) -> str:
        if self.computed:
            return f"computed from {self.cls.label}"
        return self.cls.label

    def __repr__(self) -> str:  # pragma: no cover - display only
        v = "—" if self.value is None else f"{self.value:,.4g}"
        return f"<{self.ref}={v} {self.render_class}{' INCOMPLETE' if self.incomplete else ''}>"


def compute(ref: str, fn: Callable[..., float], inputs: list[Cell], formula: str,
            unit: str = "") -> Cell:
    """Vol III 21 rule 3 + M.7 'class propagates': weakest input governs."""
    if not inputs:
        raise SpecGap(f"{ref}: computed cell with no inputs")
    weakest = min(c.cls for c in inputs)
    any_rm = any(c.cls is EClass.RM or c.incomplete for c in inputs)
    if any_rm:
        # M.7: "A line with no source renders as REQUIRES MEASUREMENT and the
        # total is marked incomplete rather than understated."
        usable = [c for c in inputs if c.value is not None]
        val = fn(*[c.value for c in usable]) if usable else None
        return Cell(ref, val, EClass.RM, unit, computed=True,
                    inputs=tuple(c.ref for c in inputs), formula=formula, incomplete=True)
    return Cell(ref, fn(*[c.value for c in inputs]), weakest, unit, computed=True,
                inputs=tuple(c.ref for c in inputs), formula=formula)


# ---------------------------------------------------------------------------
# §11 The decision component, consequence class, evidence floor
# ---------------------------------------------------------------------------

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


# Vol II 11.3 states the floor in *grades*, but a grade is an artifact-level
# property set by a Review (Vol II 13.1/13.3, M.3) and a component is not an
# artifact. To evaluate the floor at all, the required grade is read onto the
# component's evidence-row *cell class*.
assumption(
    "A2",
    "The Vol II 11.3 evidence floor is evaluated against the component's "
    "evidence-row cell class, not against an artifact grade: "
    "C1->STATED, C2->REPORTED, C3->REPORTED, C4->OBSERVED. "
    "The spec states the floor in grades, which a component cannot hold.",
)

FLOOR_AS_GRADE: dict[CClass, str] = {
    CClass.C1: "Estimated",
    CClass.C2: "Monitored",
    CClass.C3: "Monitored, moving to Measured",
    CClass.C4: "Measured",
}

FLOOR_AS_CELL_CLASS: dict[CClass, EClass] = {
    CClass.C1: EClass.STATED,
    CClass.C2: EClass.REPORTED,
    CClass.C3: EClass.REPORTED,   # "moving to Measured" is not a threshold — see G7
    CClass.C4: EClass.OBSERVED,
}


@dataclass
class OutcomeLinkage:
    """Vol I 4.3: qualifies only where it names a baseline, a counterfactual, or a period."""
    outcome: str = ""
    baseline: Optional[float] = None
    counterfactual: Optional[str] = None
    period: Optional[str] = None
    unit_value: Optional[float] = None
    unit_value_cls: EClass = EClass.STATED

    @property
    def qualifies(self) -> bool:
        # Spec wording is an OR across the three.
        return any(x is not None for x in (self.baseline, self.counterfactual, self.period))

    @property
    def valuable(self) -> bool:
        """Can the M.7 value chain actually run? (current - baseline) x unit_value."""
        return self.baseline is not None and self.unit_value is not None


@dataclass
class DecisionComponent:
    dc_id: str
    work: str
    mode: Mode
    consequence: CClass
    reversibility: str = "unknown"
    evidence_cls: EClass = EClass.RM
    error_rate: Optional[float] = None
    volume: Optional[float] = None
    unit_error_cost: Optional[float] = None
    linkage: OutcomeLinkage = field(default_factory=OutcomeLinkage)
    reliance_trajectory: Optional[str] = None
    is_substrate: bool = False

    # --- admission (Vol II 12.1) -------------------------------------------
    @property
    def admitted(self) -> bool:
        """Mode is the admission test. Substrate is recorded, not scored."""
        return not self.is_substrate

    # --- floor (Vol II 11.3) ------------------------------------------------
    @property
    def floor_required(self) -> Optional[EClass]:
        if self.consequence is CClass.UNSET:
            return None
        return FLOOR_AS_CELL_CLASS[self.consequence]

    @property
    def floor_breach(self) -> bool:
        req = self.floor_required
        if req is None:
            return False
        return self.evidence_cls < req

    # --- expected cost of error --------------------------------------------
    def expected_cost_of_error(self) -> Cell:
        """
        Vol I 4.5 states: consequence class x observed error rate x exposure.
        M.7 states exposure = volume x cost per wrong output.
        Consequence class is an ordinal label (C1..C4) and cannot be a
        multiplicand; the Vol III(d) tap-back confirms it is not one
        (C2 x 3.4% x 88,100 x $7.30 == 3.4% x 88,100 x $7.30). See G2.
        """
        ref = f"{self.dc_id}.ece"
        if self.error_rate is None or self.volume is None or self.unit_error_cost is None:
            return Cell(ref, None, EClass.RM, "$k",
                        source="no observed error rate", incomplete=True)
        val = self.error_rate * self.volume * self.unit_error_cost
        return Cell(ref, val, self.evidence_cls, "$k", computed=True,
                    formula="error_rate x volume x unit_error_cost")


# ---------------------------------------------------------------------------
# §12 The AI Fit Assessment
# ---------------------------------------------------------------------------

CRITERIA = [
    (1, "Standardization", "derived"),
    (2, "Interoperability across hosts", "asked"),
    (3, "Scalability", "derived"),
    (4, "Reconfigurability", "derived"),
    (5, "Sovereignty / exportability", "asked"),
    (6, "Implementation flexibility", "derived"),
    (7, "Manageability", "asked"),
    (8, "Documentation", "asked"),
    (9, "Standards compliance", "asked"),
    (10, "Monitoring", "asked"),
]

NOT_PROVIDED = None  # Vol II 12.3: a label on a score, not an evidence class

# Vol II 12.5: "One question — the deployment model — carries Standardization,
# Scalability, Reconfigurability and Implementation flexibility, plus the
# complexity band." No derivation table is published anywhere in Vols I-III.
gap(
    "G1",
    "Vol II 12.5 derives 4 of 10 AIFA criteria and the complexity band from a "
    "single deployment-model question, but no derivation table exists in any "
    "volume. The short-form AIFA cannot be implemented without inventing it.",
)
assumption(
    "A3",
    "A deployment-model -> (C1,C3,C4,C6, band) table is invented here purely so "
    "the mechanics can be exercised. The values carry no authority.",
)

DEPLOYMENT_DERIVATION: dict[str, tuple[int, int, int, int, str]] = {
    # deployment model      : (standardization, scalability, reconfig, impl_flex, band)
    "vendor_saas_default":        (2, 4, 2, 1, "Low"),
    "vendor_saas_configured":     (3, 4, 3, 2, "Low"),
    "platform_pattern_applied":   (5, 4, 4, 3, "Moderate"),
    "bespoke_build":              (3, 3, 4, 5, "High"),
    "bespoke_unpatterned":        (1, 2, 2, 5, "High"),
    "shadow_departmental":        (1, 2, 2, 4, "Low"),
}


@dataclass
class AIFAScore:
    subject: str
    scores: dict[int, Optional[int]]      # criterion no -> 1..5 or None (NOT PROVIDED)
    band: str
    deployment_model: str = ""

    @property
    def n_not_provided(self) -> int:
        return sum(1 for v in self.scores.values() if v is None)

    @property
    def raw_total(self) -> int:
        return sum(v for v in self.scores.values() if v is not None)

    # Vol II 12.3 says the total is "out of 50" and that NOT PROVIDED
    # "asserts nothing about the capability". It does not say what happens to
    # the denominator, and the three readings diverge materially.
    @property
    def totals(self) -> dict[str, float]:
        n_scored = 10 - self.n_not_provided
        return {
            "out_of_50_hole": self.raw_total,                       # reading 1
            "out_of_scored": self.raw_total,                        # reading 2 numerator
            "scored_denominator": n_scored * 5,
            "pro_rated_to_50": (self.raw_total / (n_scored * 5) * 50) if n_scored else 0.0,
        }


gap(
    "G3",
    "Vol II 12.3 fixes the AIFA total 'out of 50' and allows NOT PROVIDED "
    "criteria, but never states the denominator when a criterion is NOT "
    "PROVIDED. A 3-null assessment reads 15/50, 15/35 or 21/50 depending on "
    "the choice, and the spec permits all three.",
)

gap(
    "G4",
    "Vol II 12.5 selects three scored slots by rule (largest by spend, widest "
    "by reach, least governed) with no de-duplication rule when one capability "
    "satisfies two or three, and 'least governed' is defined by criteria 7 and "
    "10, which are outputs of the assessment being selected for.",
)

gap(
    "G5",
    "Vol I 2 step 2 and 5.3 refer to 'the AIFA total' (singular) feeding "
    "maturity placement, but Vol II 12.5 produces one total per scored slot "
    "and M.3 keys AIFA score on dc_id. No aggregation rule from N slot totals "
    "to one company total is published.",
)

gap(
    "G6",
    "Vol I 4.7 rebalances 'investments ... on fit score against "
    "consequence-weighted exposure', but AIFA score is keyed to a decision "
    "component and Portfolio rows are keyed to an investment line, related "
    "many-to-many via LINE_COMPONENT. No line-level fit score is defined, so "
    "the rebalance action is not computable. (Vol I 22 concedes only the "
    "weighting formula is unwritten; the roll-up is missing too.)",
)

gap(
    "G7",
    "Vol II 11.3 sets the C3 floor at 'Monitored, moving to Measured'. That is "
    "two values and a trajectory with no date, so it cannot be evaluated as a "
    "pass/fail threshold in a non-compensatory instrument.",
)

gap(
    "G8",
    "Vol II 11.3 states the evidence floor in artifact *grades*, but Vol II "
    "13.1/13.3 and M.3 make grade an artifact-level property set by a Review. "
    "A decision component is not an artifact and can never hold a grade, so "
    "the floor as written is not evaluable against the object model.",
)

gap(
    "G9",
    "Vol II 11.2 declares an UNSET consequence class 'a finding', and Vol II "
    "11.1 makes reliance trajectory a required attribute, but the M.3 Finding "
    "kind enumeration (unnamed gap, ownerless, undetermined, empty evidence, "
    "undeclared, idle, divergent, floor breach, ungoverned change) has no kind "
    "for either, nor for the period-over-period movement of Vol III 27.3.",
)

gap(
    "G10",
    "Vol II 11.1 requires reliance trajectory on every component and Vol I 5.5 "
    "makes the reliance audit one of three checks, but Vol III 24.2 confirms no "
    "host returns it and no surface, metric or derivation for it appears in "
    "Vol III 25.2. The framework's signature attribute has no measurement path.",
)


# ---------------------------------------------------------------------------
# §5 / §14 Maturity placement
# ---------------------------------------------------------------------------

STAGE_NAMES = {1: "Experimenting", 2: "Adopting", 3: "Managed", 4: "Optimized", 5: "Augmented"}

assumption(
    "A4",
    "A 1-5 AIFA criterion score is read as a 1-5 maturity stage for the "
    "company-practice criteria (Standardization, Monitoring). Vol I 5.3 says "
    "they 'roll up to placement at their floor', which requires a mapping the "
    "spec never states.",
)

COMPANY_PRACTICE_CRITERIA = (1, 10)   # Vol I 5.3 names these two "among them"

gap(
    "G11",
    "Vol I 5.3 says company-practice criteria roll up to placement 'at their "
    "floor' but names only two 'among them', so the input set to a "
    "non-compensatory placement is open-ended and two assessors can use "
    "different inputs.",
)

gap(
    "G12",
    "Only Stage 3 has thresholds (Vol I 5.2, and PROPOSED). Stages 2, 4 and 5 "
    "have narrative characteristics and no thresholds, so a threshold-based, "
    "non-compensatory model can decide exactly one of its five admissions. "
    "Placement at 2, 4 or 5 is not computable.",
)

gap(
    "G13",
    "The five staging questions (Vol II 14) are the stated source of the stage "
    "but have no level scale — each has only a 'weak answer' exemplar. Vol I "
    "5.3's 'placement is the level every input clears' cannot consume them "
    "without a per-question level rubric that is not published.",
)


@dataclass
class StagingAnswers:
    """Vol II 14 — five questions."""
    principles_endorsed: bool
    scored_repeatable_evaluation: bool
    outcome_stated_per_investment: bool
    adoption_measured_behaviourally: bool
    portfolio_owned: bool


@dataclass
class Stage3Thresholds:
    """Vol I 5.2 — four thresholds, each satisfied or not."""
    principles_published: bool
    knowledge_governed_every_host: bool
    adoption_measured_behaviourally: bool
    board_reads_scorecard: bool

    @property
    def all_met(self) -> bool:
        return all((self.principles_published, self.knowledge_governed_every_host,
                    self.adoption_measured_behaviourally, self.board_reads_scorecard))

    @property
    def missed(self) -> list[str]:
        return [k for k, v in self.__dict__.items() if v is False]


def place_company(staging: StagingAnswers, t3: Stage3Thresholds,
                  practice_scores: dict[int, Optional[int]]) -> dict:
    """
    Vol I 5.3: placement is the level every input clears (non-compensatory).
    Implemented as far as the spec permits; returns the ceiling it can prove.
    """
    inputs: dict[str, Optional[int]] = {}

    # Company-practice AIFA criteria, under A4.
    for c in COMPANY_PRACTICE_CRITERIA:
        v = practice_scores.get(c)
        inputs[f"aifa_c{c}"] = v  # None == NOT PROVIDED

    # Stage 3 thresholds: a single gate, not a scale.
    inputs["stage3_gate"] = 3 if t3.all_met else 2

    # Staging questions: G13 — no level scale exists. The only defensible
    # reading is that all five must be strong to be consistent with Stage 3.
    strong = sum(staging.__dict__.values())
    inputs["staging_5q"] = 3 if strong == 5 else 2

    scored = [v for v in inputs.values() if v is not None]
    placement = min(scored) if scored else None

    return {
        "inputs": inputs,
        "placement": placement,
        "placement_name": STAGE_NAMES.get(placement, "—") if placement else "—",
        "not_provided_inputs": [k for k, v in inputs.items() if v is None],
        "ceiling_note": (
            "capped at 3: stages 4 and 5 have no thresholds (G12)"
            if placement and placement >= 3 else ""
        ),
        "stage3_missed": t3.missed,
    }


# ---------------------------------------------------------------------------
# §25.4 Reconciliation
# ---------------------------------------------------------------------------

TOLERANCE_SPEND = 0.10   # Vol III 25.4
TOLERANCE_REACH = 0.20

gap(
    "G14",
    "Vol III 25.4 sets divergence tolerances at 10% spend / 20% reach without "
    "naming the denominator. Against the STATED value vs against the feed "
    "value the same pair can classify differently; the asymmetry is "
    "demonstrated in the simulation output.",
)

gap(
    "G15",
    "Vol III 25.4 defines Idle as 'an inventory line with seats or spend and "
    "no activity in the period' — an absolute-zero test — but Vol III(d) "
    "raises an Idle finding on a line with 6 of 80 seats active. No partial-"
    "idleness threshold is published, and the two readings disagree on the "
    "worked example.",
)

gap(
    "G16",
    "Vol III 25.4's Confirmed and Divergent conditions are both true of a line "
    "whose feed differs beyond tolerance ('has matching feed records'). No "
    "evaluation order is stated.",
)


@dataclass
class InventoryLine:
    line_id: str
    vendor: str
    stated_spend: Optional[float] = None
    stated_reach: Optional[int] = None
    feed_spend: Optional[float] = None
    feed_reach: Optional[int] = None
    feed_active: Optional[int] = None
    host_connected: bool = True
    grant_ok: bool = True
    benefits_owner: Optional[str] = None
    gl_id: Optional[str] = None


def reconcile(line: InventoryLine, denominator: str = "stated") -> dict:
    """Vol III 25.4. `denominator` exposes the G14 asymmetry."""
    if not line.host_connected or not line.grant_ok:
        return {"outcome": "unreachable", "detail": "no connector or no grant"}

    if line.feed_spend is None and line.feed_reach is None and line.feed_active is None:
        return {"outcome": "undeclared_check", "detail": "no feed records"}

    def diverges(stated, feed, tol) -> Optional[float]:
        if stated is None or feed is None:
            return None
        base = stated if denominator == "stated" else feed
        if base == 0:
            return None if feed == 0 else float("inf")
        return abs(feed - stated) / abs(base)

    d_spend = diverges(line.stated_spend, line.feed_spend, TOLERANCE_SPEND)
    d_reach = diverges(line.stated_reach, line.feed_reach, TOLERANCE_REACH)

    # Idle, strict reading (G15): absolute zero activity.
    idle_strict = (line.feed_active == 0) and bool(line.stated_reach or line.stated_spend)
    # Idle, Vol III(d) reading: materially under-used.
    idle_material = (
        line.feed_active is not None and line.feed_reach
        and line.feed_active / line.feed_reach < 0.20
    )

    if idle_strict:
        return {"outcome": "idle", "reading": "strict", "detail": "zero activity"}
    if (d_spend is not None and d_spend > TOLERANCE_SPEND) or \
       (d_reach is not None and d_reach > TOLERANCE_REACH):
        return {"outcome": "divergent", "d_spend": d_spend, "d_reach": d_reach,
                "denominator": denominator}
    if idle_material:
        return {"outcome": "idle", "reading": "material(VolIIId)",
                "detail": f"{line.feed_active}/{line.feed_reach} active"}
    return {"outcome": "confirmed", "d_spend": d_spend, "d_reach": d_reach}


# ---------------------------------------------------------------------------
# §4.5 Cost of service, §4.4 methods, M.7 ROI
# ---------------------------------------------------------------------------

gap(
    "G2",
    "Vol I 4.5 writes expected cost of error as 'consequence class x observed "
    "error rate x exposure'. Consequence class is an ordinal label and cannot "
    "be a multiplicand; the Vol III(d) tap-back computes the same cell without "
    "it (3.4% x 88,100 x $7.30 = $21.9k). The formula as published is not the "
    "formula in use.",
)

gap(
    "G17",
    "Vol I 4.3 and M.7 qualify an outcome linkage on 'a baseline, a "
    "counterfactual, OR a period', but the M.7 value chain computes "
    "(current - baseline) x unit value, which requires a baseline and a unit "
    "value. A linkage qualifying only on a period passes the gate and then "
    "produces no value.",
)

JUSTIFICATION_METHOD_PRODUCES_ROI = {
    # Vol I 4.4 + M.7 "formula follows investment type"
    "scenario_or_real_options": False,
    "roi_or_npv_outcome_metrics": True,
    "scenario_peer": False,
    "risk_analysis": False,
    "payback_plus_risk": True,
    "payback_npv_platform": False,     # unit-cost against target
    "cost_per_adoption_point": False,
    "cost_of_service_vs_use": None,    # G18 — ambiguous in Vol III(d)
}

gap(
    "G18",
    "Vol III(d) gives rows 3, 4 and 7 the same justification method ('cost of "
    "service vs delivered use'), then shows an ROI for row 3 and none for rows "
    "4 and 7. Whether a row shows ROI is therefore decided by the presence of "
    "a value side, not by the method, which contradicts the report's own "
    "'ROI-method lines only' column header.",
)


@dataclass
class InvestmentLine:
    line_id: str
    name: str
    inv_class: str                  # people | agents | systems | vendor_tools
    method: str
    licence_seat: Optional[float] = None
    usage: Optional[float] = None
    build_integration: Optional[float] = None
    enablement: Optional[float] = None
    components: list[DecisionComponent] = field(default_factory=list)
    value_delivered: Optional[float] = None
    value_cls: EClass = EClass.STATED
    benefits_owner: Optional[str] = None
    explicit_ece: Optional[float] = None      # where the doc gives it directly

    # --- cost of service (Vol I 4.5, five lines) ---------------------------
    def cost_of_service(self) -> Cell:
        parts: list[Cell] = []
        for nm, v in (("licence_seat", self.licence_seat), ("usage", self.usage),
                      ("build", self.build_integration), ("enablement", self.enablement)):
            if v is not None:
                parts.append(Cell(f"{self.line_id}.{nm}", v, EClass.REPORTED, "$k"))
        if self.explicit_ece is not None:
            parts.append(Cell(f"{self.line_id}.ece", self.explicit_ece, EClass.REPORTED, "$k"))
        else:
            eces = [c.expected_cost_of_error() for c in self.components]
            for e in eces:
                parts.append(e)
        if not parts:
            return Cell(f"{self.line_id}.cos", None, EClass.RM, "$k", incomplete=True)
        return compute(f"{self.line_id}.cos", lambda *xs: sum(xs), parts,
                       "sum of five cost lines", "$k")

    # --- value side ---------------------------------------------------------
    @property
    def has_qualifying_value(self) -> bool:
        if self.value_delivered is None:
            return False
        return any(c.linkage.qualifies for c in self.components) or bool(self.components) is False

    @property
    def method_produces_roi(self) -> Optional[bool]:
        return JUSTIFICATION_METHOD_PRODUCES_ROI.get(self.method)

    def roi(self) -> Optional[Cell]:
        cos = self.cost_of_service()
        if not self.has_qualifying_value or cos.value in (None, 0):
            return None
        if self.method_produces_roi is False:
            return None
        v = Cell(f"{self.line_id}.value", self.value_delivered, self.value_cls, "$k")
        return compute(f"{self.line_id}.roi",
                       lambda value, cost: (value - cost) / cost,
                       [v, cos], "(value - cost) / cost", "ratio")


@dataclass
class Portfolio:
    name: str
    lines: list[InvestmentLine]

    def totals(self) -> dict:
        cos_cells = [ln.cost_of_service() for ln in self.lines]
        total_cos = sum(c.value or 0 for c in cos_cells)
        incomplete = [c.ref for c in cos_cells if c.incomplete]

        roi_lines = [ln for ln in self.lines if ln.roi() is not None]
        roi_cost = sum(ln.cost_of_service().value or 0 for ln in roi_lines)
        roi_value = sum(ln.value_delivered or 0 for ln in roi_lines)
        portfolio_roi = (roi_value - roi_cost) / roi_cost if roi_cost else None

        # Two competing definitions of the fourth number — see G19.
        no_roi_cost = total_cos - roi_cost                      # Vol III(d)'s number
        # Rows whose method produces no ROI *by rule* (People, Systems) are not
        # "lines with no value side"; the page says so itself and decides Keep.
        no_value_cost = sum((ln.cost_of_service().value or 0)
                            for ln in self.lines
                            if ln.value_delivered is None
                            and ln.method_produces_roi is not False)

        return {
            "total_cost_of_service": total_cos,
            "incomplete_lines": incomplete,
            "roi_line_ids": [ln.line_id for ln in roi_lines],
            "roi_cost": roi_cost,
            "roi_value": roi_value,
            "portfolio_roi": portfolio_roi,
            "cost_without_roi_calc": no_roi_cost,
            "cost_without_value_side": no_value_cost,
            "share_without_roi_calc": no_roi_cost / total_cos if total_cos else None,
            "share_without_value_side": no_value_cost / total_cos if total_cos else None,
        }


gap(
    "G19",
    "Vol III(d)'s fourth headline number, 'Cost of service with no value side "
    "$1.93M / 60%', is computed as total minus the ROI-carrying lines, which "
    "sweeps in rows 5 and 6 — lines the same page says are 'n/a by rule' and "
    "decides to Keep against met targets. The findings table then attributes "
    "the same $1.93M to rows 4, 7 and 8, which total $1.27M. The headline "
    "number and the finding disagree by $655k.",
)


# ---------------------------------------------------------------------------
# Prior art: the 19 Sep 2026 document review (abaf-v0.8-review.md).
# Findings already on the record are not re-raised as new. Where this model
# extends one, the extension is named.
# ---------------------------------------------------------------------------

PRIOR: dict[str, str] = {
    "G1": "extends Q6 — Q6 records that the prototype retired the four derived "
          "criteria; this adds that the derivation table §12.5 relies on was "
          "never published, so §12.5 could not have been implemented either way.",
    "G3": "already raised as Q2/Q3 and ruled #1 on the 19 Sep fix list. This "
          "model only quantifies the distortion (see Part D).",
    "G4": "already raised as Q5 (four slots, not three) and Q12 (mode ignored "
          "in slot selection). Adds only the de-duplication and circularity points.",
    "G2": "extends Q11 — Q11 records that expected cost of error is never "
          "produced; this adds that the formula as published cannot be evaluated.",
    "G12": "extends Q9, and disagrees with it. Q9 infers 'Stage 2 · Adopting at "
           "best' from the five answers. This model finds placement is not "
           "computable for any stage but 3.",
    "G13": "extends Q9 / Q16 — Q16 asks whether §14 should be restated as four "
           "asked and one computed; this adds that none of the five carries a "
           "level scale, so the roll-up has nothing to consume.",
}

PRIOR_UNCHANGED = [
    "Q1/F4  model gateway admitted to the instrument (blocking)",
    "Q2/Q3  NOT PROVIDED scores 0 and is summed into /50 (blocking)",
    "Q4     NOT PROVIDED used as a cell value in the S1B inventory",
    "Q5/Q12 four slots, not three; mode answer ignored in slot selection",
    "Q6     'six asked, four derived' retired in the implementation",
    "Q7/E5  EST live in fixture and in the running product",
    "Q8     consequence class absent from the Quick Look, so §12.6 is dormant",
    "Q10    benefits owner missing from intake",
    "Q13    scoring anchors PENDING while §12 reads ACCEPTED",
    "Q21-23 fixture defects: Since:4, privacy wording, undelivered checklist",
    "E4/F9  no session state; wrong session id on the client artifact",
    "F1-F3  deployed Captain runs a different instrument from v0.8",
    "F8     Rung 1 produced ranked recommendations",
]
