# ABAF v0.8 — instrument mechanics validated against an independent model

**Date:** 29 September 2026
**Scope:** Vol I *The Methodology* and Vol II *The Instruments* (v0.8, 16 Sep) · Vol III *The Integrations* parts (a)–(d) (v0.8, 26 Sep) · the Vol III(b) connector catalogue (140 rows)
**Method:** a model of the instrument mechanics written from the volumes alone (`abaf_model.py`), driven against the published worked example, five synthetic companies and the catalogue (`run_validation.py`). The scoring anchors, question set and `run-scripted.mts` were not used to build it and are not on this machine; §6 reads the four published slot scores out of Jay's simulation as *input to be checked*, not as a source of rules.
**Companion:** `MECHANICS-REVIEW.md` — the reading pass (M1–M14), which asks whether each instrument executes at all. This document is the numeric pass.
**Relation to prior work:** extends the 19 Sep document review (`ethikal/abaf-v0.8-review.md`, Q1–Q23 / E4–E7 / F1–F10). Findings already on that record are **not re-raised**; where this work extends or contradicts one, it says so.

**Result:** 31 of 39 numeric checks reproduce the published figures exactly. 8 fail. 16 questions could not be decided because the specification does not contain the rule. The model needed **4 invented assumptions** to run at all.

---

## 0 · Prior state: Jay's simulation and what it reaches

Jay's simulation is `scripted-run-ashford-mutual DRAFT.md` (v0.1, 27 Aug 2026, in `ethikal/inbox/`) — one company, Ashford Mutual, driven end to end and written down: 121 answers, a 7-item inventory with per-item baselines, a two-way ledger reconciliation, four AIFA slots at 33/25/15/10, and the five staging questions. It is emitted by `tools/assessment/run-scripted.mts` from `question-set.json` and one fixture. The repo is not on this machine, the run is stamped `aifa-scoring-anchors-v0.5-pending` (PENDING), and it is labelled "illustrative, nothing measured".

**It covers Measurement Phase 1 discovery plus the AIFA, and stops there.** Its coverage boundary falls almost exactly at the volume boundary:

| Mechanic | Jay's simulation | This model |
| :---- | :----: | :----: |
| Inventory intake and per-item baseline | yes | — |
| Ledger reconciliation, both directions | yes | — |
| Quick-look AIFA, four slots × ten criteria | yes | yes, plus the competing denominators |
| Five staging questions | asked | asked |
| **Maturity placement computed** | **no — asked, never computed** | yes, and finds it is not computable |
| Consequence class, reversibility, evidence floor | no | yes |
| Benefits owner, outcome linkage, targets | no | yes |
| Cost of service (five lines), expected cost of error | no | yes |
| ROI, portfolio ROI, portfolio decisions | no | yes |
| Host-feed reconciliation, tolerances | no (ledger only) | yes |
| Verification, Verified Baseline, monitoring periods, grades | no | yes |

Everything Volume III added on 26 September — the cost-and-ROI chain, the feed reconciliation, the object model — sits outside the simulation's reach. That is where the defects in §2 and §3 cluster, and it is why the 19 Sep document review could not have caught them.

It also reframes the prior review's Q9. The simulation asks all five staging questions and then has nowhere to send the answers. That is not a generator omission; the placement rule cannot be executed (V15). The simulation stopping at exactly that point is evidence for the finding, not merely a gap in coverage.

**No second company exists.** The Vol III(d) "Ashford (reference case)" is a different Ashford — eight investment lines not seven, Management phase not Measurement — and the two are nowhere reconciled. So "run several simulated companies through it" had no prior art to extend, and independence was satisfiable only against the volumes.

---

## 1 · What checks out

Worth stating first, because most of the arithmetic is sound and the failures below are narrow.

| Verified | Result |
| :---- | :---- |
| Vol III(d) all eight cost-of-service row totals | exact |
| Vol III(d) all five cost-line column totals, and the $3,201k grand total | exact |
| Vol III(d) three line ROIs (156%, 199%, 105%) | exact to the rounding shown |
| Vol III(d) portfolio ROI, 147% on $1.27M of cost | exact (147.4%) |
| Vol III(d) value delivered, $3.15M over qualifying lines | exact |
| Vol III(d) row 6, $185k ÷ 14 points = $13.2k per adoption point | exact |
| Vol III(d) row 2 expected cost of error, 3.4% × 88,100 × $7.30 = $21.9k | exact |
| Scripted run's four AIFA slot totals (33, 25, 15, 10) | exact — confirms the 19 Sep arithmetic check independently |

The Management-phase cost chain adds up. What follows is about what it is adding up, and about the rules that cannot be executed at all.

---

## 2 · Defects — a published number is wrong

| # | Finding | Where | Severity |
| :---- | :---- | :---- | :---- |
| **V1** | **The fourth headline number contradicts the finding that cites it.** The header reads *"Cost of service with no value side: $1.93M · 60% of the total"* and the page calls it *"the most important on the page."* $1.93M is total minus the ROI-carrying lines, which sweeps in rows 5 and 6 — lines the same page marks *"n/a by rule"* and decides to **Keep** against met targets. The findings table then attributes $1.93M to *"Rows 4, 7, 8"*, which total **$1,274k / 40%**. The two disagree by **$655k**. The page's own line count ("3 have no qualifying value side") agrees with $1.27M, not with $1.93M. | Vol III(d) header, portfolio table, findings table | **Blocking** |
| **V2** | **The A.4 roll-up does not match the sheet it summarises.** A.4 publishes 83 Agentic / 53 Assisted / 3 Manual / 1 Excluded. The CSV parses to **80 / 52 / 1 / 1, with 6 dual-mode rows** A.4 has no column for (e.g. #6 Vertex "Agentic (billing); Assisted (Gemini Enterprise)", #116 Bloomberg "Manual (seats from billing); Assisted (usage)"). Four of the eight group rows differ. The prose claim "six in ten … without a person in the loop" needs 57% on unambiguous rows and reaches 61% only if every dual-mode row counts as Agentic — the claim survives, the table does not. | Vol III(a) A.4 vs Vol III(b) | High |
| **V3** | **Row 2 value delivered is out by $1.1k.** 88,100 × $9.40 = **$828.1k**, published $827k. Immaterial to the ROI (199% either way) but it sits on the tap-back page — the one place the framework promises every input is traceable and disputable at the input that produced it. | Vol III(d) tap-back | Medium |

---

## 3 · Contradictions — the documents disagree with each other

| # | Finding | Where | Severity |
| :---- | :---- | :---- | :---- |
| **V4** | **The class-propagation rule is applied two ways in one table.** M.7: *"a cell computed from a REPORTED cost and a STATED unit value is computed-from-STATED."* Rows 1 and 2 are published as *"Computed from REPORTED; unit value STATED"* — both have a STATED unit value, so both should read computed-from-STATED. Row 3 applies the rule correctly. A reader cannot tell whether row 1 is stronger evidence than row 3; it is not. | Vol III(d) portfolio table vs M.7 | High |
| **V5** | **The expected-cost-of-error formula contains a term that is not a number.** Vol I §4.5: *"Consequence class × observed error rate × exposure."* Consequence class is an ordinal label. The Vol III(d) tap-back computes the same cell without it — 3.4% × 88,100 × $7.30 = $21.9k — so C2 contributes a factor of 1. The published formula is not the formula in use. *(Extends Q11, which records that the line is never produced; it is also unevaluable as written.)* | Vol I §4.5 vs Vol III(d), M.7 | High |
| **V6** | **Idle is defined as zero and raised at 7.5%.** §25.4 defines Idle as *"an inventory line with seats or spend and **no activity** in the period"* — an absolute-zero test. Vol III(d) raises an Idle finding on row 7 at **6 of 80 seats active**. Under §25.4 as written that line is Confirmed. No partial-idleness threshold is published. | Vol III §25.4 vs Vol III(d) | High |
| **V7** | **Behaviour is promised by Vol I and refused by Vol III.** Vol I §16 says Measurement Phase 2 *"supplies the adoption-measured threshold of Stage 3."* Vol III §27.4: monitoring *"does not produce proficiency or behaviour."* §13.6 splits activity / behaviour / proficiency three ways and says behaviour needs a cross-host record with provenance — which the normalized record is. §27.4 lumps behaviour with proficiency and rules both out. Stage 3 is the chartered year-one outcome for Stage 2 entrants, so this decides whether the commercial commitment is deliverable from Measurement alone. | Vol I §16 vs Vol III §27.4, §13.6 | **Blocking** |
| **V8** | **Row 2's $210k is booked to two different cost lines.** "Licence and seat" in the cost-of-service table, "Investment line usage" in the tap-back. Two of the five Vol I §4.5 lines, same figure, same page. | Vol III(d) | Medium |
| **V9** | **Row 2's value is computed off a different metric than its named outcome.** The Target names first-contact resolution (28% → 41%). The value is 88,100 automated resolutions × $9.40. M.7 step 5 computes (current − baseline) × unit value *against the named Business outcome*. The outcome on the page is not the one the money comes from. | Vol III(d) vs M.7 | High |
| **V10** | **Cross-volume housekeeping.** Vols I and II say *"Volume I of two"*; Vol III(a) says *"Volume III of three."* Vol III(a) cites Vol I by v0.7 numbering throughout — "Vol I §2" for the four forces (now §1.4) and for "assembled by procurement" (now §1.2), "Vol I §9" for roles-not-people (now §4.1), "Vol I §3" for the peer threshold. A reader following a cross-reference lands in the wrong section. | Vol III(a) | Medium |

---

## 4 · Not computable — the rule is stated but no implementation can execute it

This is the section that bears on the engineering team's "missing specifications" item. Each entry is something the model hit and could not proceed past without inventing a rule.

| # | The rule | What is missing | Severity |
| :---- | :---- | :---- | :---- |
| **V11** | Vol II §12.5: one deployment-model question carries Standardization, Scalability, Reconfigurability, Implementation flexibility **and** the complexity band | **No derivation table exists in any volume.** 4 of 10 criteria and the band cannot be produced. *(Extends Q6: the prototype retired the derivation; §12.5 could not have been implemented either way.)* | **Blocking** |
| **V12** | Vol II §12.3: total out of 50, criteria may be NOT PROVIDED, and the label *"asserts nothing about the capability"* | **No denominator rule.** Three readings are all permitted. Quantified in §6 below. *(Already Q2/Q3 and ruled #1 on the 19 Sep fix list — listed here only for the measured effect.)* | **Blocking** |
| **V13** | Vol I §2 step 2 and §5.3 refer to *"the AIFA total"* (singular) feeding placement | Vol II §12.5 produces **one total per scored slot** and M.3 keys AIFA score on `dc_id`. No rule aggregates N slot totals into one company total. | High |
| **V14** | Vol I §4.7: *"Investments are re-ranked on fit score against consequence-weighted exposure"* | AIFA score is keyed to a decision component; Portfolio rows are keyed to an investment line; they relate many-to-many via `LINE_COMPONENT`. **No line-level fit score exists.** Vol I §22 concedes the weighting formula is unwritten — the roll-up is missing too, so Rebalance is not computable at all. | High |
| **V15** | Vol I §5.3: *"Placement is the level every input clears"* | **Only Stage 3 has thresholds** (and they are PROPOSED). Stages 1, 2, 4, 5 have narrative characteristics only. The five staging questions have **no level scale** — each carries one "weak answer" exemplar and nothing else. A non-compensatory, threshold-based model can decide exactly one of its five admissions. In the run, Strathmore (meets everything but the board page) and Ravensworth (meets nothing) both return "stage 2". | **Blocking** |
| **V16** | Vol II §11.3: the evidence floor, C1→Estimated … C4→Measured | A **grade** is an artifact-level property set by a Review (§13.1, §13.3, M.3). A decision component is not an artifact and can never hold one, so the floor as written cannot be evaluated against the object model. Separately, the C3 floor reads *"Monitored, moving to Measured"* — two values and a trajectory with no date, which is not a threshold. | High |
| **V17** | Vol III §25.4: divergence tolerance 10% spend / 20% reach | **The denominator is not named.** Demonstrated: stated 100 vs feed 111 is *divergent* against the stated base and *confirmed* against the feed base; stated 111 vs feed 100 flips the other way. Same pair of numbers, opposite finding. Also §25.4's Confirmed and Divergent conditions are both true of a beyond-tolerance line, and no evaluation order is given. | High |
| **V18** | Vol I §4.3 / M.7: a linkage qualifies where it names *"a baseline, a counterfactual, **or** a period"* | The M.7 value chain computes (current − baseline) × unit value, which **requires** a baseline and a unit value. Two of the three qualifying routes pass the gate and then produce nothing. | Medium |
| **V19** | Vol II §11.2: an UNSET consequence class *"is a finding"*; Vol III §27.3: movement is flagged | The M.3 Finding enumeration (unnamed gap, ownerless, undetermined, empty evidence, undeclared, idle, divergent, floor breach, ungoverned change) has **no kind for either**. Vol III(d) is forced to log a period-over-period move as "Divergent", which §25.4 defines as a within-period feed-vs-STATED disagreement. | Medium |
| **V20** | Vol II §11.1 makes reliance trajectory a required attribute; Vol I §5.5 makes the reliance audit one of three health checks | Vol III §24.2 confirms **no host returns it**, and no surface, metric or derivation appears in §25.2. The framework's signature attribute — the one that distinguishes it from the market's tier ladders — has no measurement path. | High |
| **V21** | Vol III(d) carries a grade ("Monitored") and a reviewer signature | M.6's artifact kinds are scorecard, AIFA (quick look, full), Profile, Verified Baseline, brief. **The Portfolio ROI report is not an artifact kind**, and only Artifacts carry grades and Reviews. | Medium |
| **V22** | M.7 and Vol III §21: class propagates; the weakest input governs | The four evidence classes are **never ordered**. "Weakest" is undefined. The model assumed RM < STATED < REPORTED < OBSERVED (A1) — defensible, but an implementer is guessing. | Medium |

---

## 5 · One disagreement with the 19 Sep review

The 19 Sep review notes in passing, on Q9: *"On the five answers given … placement looks like **Stage 2 · Adopting** at best."*

Applying Vol I §5.3 as written gives **Stage 1 · Experimenting**. §5.3 requires the company-practice AIFA criteria to roll up to placement at their floor, not just the staging answers. Across the scripted run's four slots:

| Input | Values | Floor |
| :---- | :---- | :---- |
| Standardization (criterion 1) | 1, 2, 1, 2 | **1** |
| Monitoring (criterion 10) | 2, 2, 2, 1 | **1** |
| Stage 3 threshold gate | none met | 2 |
| Five staging questions | all weak | 2 |

Level every input clears = **1**.

Neither reading is wrong, and that is the point: the gap between them is **V15 plus the missing score→stage mapping**. The spec never says how a 1–5 criterion score maps to a 1–5 stage, so two competent assessors reading the same rule land two stages apart on the same company. For a non-compensatory instrument whose whole claim is that thresholds beat self-assessment, that is the finding.

---

## 6 · What the NOT PROVIDED rule actually costs (Q2/Q3, measured)

The 19 Sep review ruled on this; the model quantifies it, using Jay's own four slots.

| Slot | Nulls | R28 (null = 0) | % of 50 | Nulls excluded | % achievable | Pro-rated to 50 |
| :---- | ----: | ----: | ----: | ----: | ----: | ----: |
| Claims triage model | 0 | 33 | 66% | 33/50 | 66% | 33.0 |
| Microsoft Copilot | 0 | 25 | 50% | 25/50 | 50% | 25.0 |
| Internal GPT gateway | 3 | 15 | 30% | 15/35 | **43%** | 21.4 |
| Dept. ChatGPT Team | 3 | 10 | 20% | 10/35 | **29%** | 14.3 |

Two things follow, and the second is new.

**It is a magnitude defect, not an ordering defect — on this fixture.** Rank order is preserved. But the gateway moves 13 points and Dept. ChatGPT 9 points as a share of what was actually assessed. Any band, threshold or portfolio cut applied to the total moves with it.

**The two rules are not composable.** R28 scores a null **0**. Criteria 1 and 10 are the company-practice criteria Vol I §5.3 rolls up to placement *at their floor*. A null on either would floor placement at **0** — not a stage that exists. It does not bite on this fixture (the nulls fall on criteria 3, 4 and 9), but nothing prevents it, and the failure would be silent.

---

## 7 · What I would fix first

Ordered by whether it changes a client-visible number or unblocks the build. The 19 Sep fix list still stands; this is additive.

| # | Action | Closes |
| :---: | :---- | :---- |
| 1 | Decide what the fourth number on the ROI page means — unlinked cost, or cost outside an ROI calculation — and make the headline and the finding agree | V1 |
| 2 | Rule the behaviour question: can Measurement Phase 2 supply the Stage 3 adoption threshold or not? The chartered outcome depends on it | V7 |
| 3 | Publish the deployment-model derivation table, or delete "six asked, four derived" from §12.5 and §18 | V11 |
| 4 | Write thresholds for stages 2, 4 and 5, and a level rubric for the five staging questions — or state that placement is Stage-3-gated only | V15 |
| 5 | Restate the evidence floor in cell classes, and give C3 a single testable value | V16 |
| 6 | Name the tolerance denominator in §25.4, give Idle a partial threshold, and order Confirmed before Divergent | V17, V6 |
| 7 | Publish the evidence-class ordering, and apply class propagation consistently in the ROI table | V22, V4 |
| 8 | Correct the §4.5 expected-cost-of-error formula to error rate × volume × cost per wrong output | V5 |
| 9 | Regenerate the A.4 roll-up from the sheet, and add a dual-mode column | V2 |
| 10 | Add Finding kinds for consequence-UNSET and movement; add an artifact kind for the portfolio report | V19, V21 |
| 11 | Fix Vol III(a)'s cross-references to Vol I's v0.8 numbering, and the "of two"/"of three" volume count | V10 |
| 12 | Decide where reliance trajectory is measured from, or mark it explicitly unmeasurable in this edition | V20 |

---

## Appendix A · Assumptions the model had to invent

The model could not run without these. None is authorised by the volumes; each marks a decision someone has to make.

| # | Assumption | Because |
| :---- | :---- | :---- |
| **A1** | Evidence classes are ordered RM < STATED < REPORTED < OBSERVED | Class propagation needs "weakest"; no ordering is published (V22) |
| **A2** | The evidence floor is read onto the component's evidence-row cell class: C1→STATED, C2→REPORTED, C3→REPORTED, C4→OBSERVED | The floor is stated in grades a component cannot hold (V16) |
| **A3** | A deployment-model → (criteria 1, 3, 4, 6 + band) table | None exists (V11). The values carry no authority and were chosen only to exercise the mechanics |
| **A4** | A 1–5 AIFA criterion score reads as a 1–5 maturity stage | §5.3 rolls criteria up to placement with no mapping (V15, §5 above) |

## Appendix B · Running it

```
cd .claude/projects/advisor-bridge/validation
PYTHONIOENCODING=utf-8 python run_validation.py
```

`abaf_model.py` is the engine — evidence classes and propagation, consequence class and the evidence floor, the AIFA and its denominators, placement and the roll-up, reconciliation and tolerances, the five cost lines, ROI and portfolio ROI. `run_validation.py` drives four parts: (A) the Vol III(d) worked example recomputed line by line, (B) five synthetic companies, (C) the catalogue against the A.4 roll-up, (D) the scripted run's four slots under the competing NOT PROVIDED rules.

Nothing in `files/` is written to. The catalogue CSV is opened read-only.
