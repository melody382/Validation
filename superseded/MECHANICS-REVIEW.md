
# ABAF v0.8 — do the instrument mechanics work as described?

**Date:** 29 September 2026
**Read in full:** Vol I *The Methodology* · Vol II *The Instruments* (both v0.8, 16 Sep) · Vol III *The Integrations* (a) Integrations, (b) Vendor connector catalogue, (c) Consolidated object model, (d) Portfolio ROI report (all v0.8, 26 Sep)
**Companion documents:** `VALIDATION-REPORT.md` (V1–V22, findings from the independent model) · `ethikal/abaf-v0.8-review.md` (Q1–Q23, E, F — the 19 Sep review)

**Method.** Each instrument traced end to end and asked four questions: *are its inputs obtainable? is its rule executable? does its output have a defined consumer? do the rule and the consumer agree?* This is the reading pass. Where a finding was reproduced numerically, it points at a V-number.

**Result.** Of ten instruments, **three work as described**, four work with a gap that has a named owner, and **three do not execute as written**. Findings are M1–M14; none duplicates a Q- or V-number.

---

## 1 · Instrument-by-instrument verdict

| Instrument | Inputs obtainable? | Rule executable? | Output consumed? | Verdict |
| :---- | :----: | :----: | :----: | :---- |
| **§11 Decision component** | partly | yes | yes | Works. The attribute set is coherent; two attributes have no source (M7, V20) |
| **§12.1 Admission test** | yes | **vacuous** | yes | **Does not execute** — admits everything (M1) |
| **§12 AIFA** | partly | **no** | yes | **Does not execute** — 4 of 10 criteria underivable (V11), denominator undefined (V12) |
| **§12.4 Complexity band** | no | no | yes | Blocked on the same missing table (V11) |
| **§13 Evidence classes** | yes | yes | yes | Works. Ordering unpublished but inferable (V22); rule 1 silently suspended in Phase 1 (M8) |
| **§13.3 Grades** | yes | yes | yes | Works — grade set only by Review, cleanly modelled |
| **§14 Staging + §5.3 placement** | yes | **no** | yes | **Does not execute** — no level scale, thresholds for one stage of five (V15, M14) |
| **§15 Company profile** | yes | partial | yes | Descriptors unwritten (self-flagged); bottleneck rule missing (M10) |
| **§4 Investment and portfolio** | partly | partly | yes | Two taxonomies with no crosswalk (M4); provision folded into ROI (M5); rebalance uncomputable (V14) |
| **§23/§26/§27 Discovery → Verification → Monitoring** | yes | yes | yes | Works. The strongest-specified part of the framework |

The integration machinery in Volume III is the best-engineered material here. The failures sit in the older instruments, and in the joins between volumes.

---

## 2 · The three that do not execute

### M1 · The admission test admits everything

Vol II §12.1: *"A capability that can be assigned a mode — automation, augmentation **or undetermined** — is a unit of the instrument. A thing that cannot is substrate."*

UNDETERMINED is itself an assignable mode (§11.1), and Vol III §23.1 step 4 has the Captain *propose* one of the three with the user confirming. There is no answer a user can give that fails the test. An assessor who does not know what a thing does says "undetermined" and the thing is admitted and scored.

This reframes the prior review's Q1/F4. The 19 Sep review found the model gateway scored and concluded *"the admission test is not operating."* It is operating exactly as written — the rule cannot exclude anything. The gateway was not admitted by a bug; it was admitted by the rule.

The converse bites too. §11.4 maps the market's **Observe** tier — *"read-only; summarizes, retrieves… Machine informs; person decides and authors. No proposal is made"* — to AUGMENTATION, so it is admitted. The stated ground for excluding the gateway is *"it decides nothing."* An Observe-tier read-only summariser also decides nothing. The framework admits one and excludes the other on a distinction it never draws.

**What would fix it:** the test needs a positive criterion — the thing must alter, propose or execute a decision the business names — with UNDETERMINED reclassified as *an admitted component whose mode is a finding*, not as a passing grade on admission.

### M2 · Method Step 1 has no content

Vol I §2 Step 1: *"**Build the fit assessment.** Establish the criteria by which **this company** will judge whether an agentic capability fits its business… Build it before assessing anything, because an assessment run against criteria invented during the assessment measures the assessor."*

But the criteria are not the company's. Vol II §12.2 fixes all ten for every company, and §12.3 freezes the only remaining degree of freedom: *"**Weights stay unset.** No weighting scheme is adopted until inter-rater reliability clears."*

So a company arriving at Step 1 chooses nothing. The step's stated rationale — don't invent criteria during the assessment — is satisfied by the framework having invented them in advance, which is a different thing and arguably a better one. As written, Step 1 describes work no one does, and the sequencing rule that depends on it (*"instruments before assessments"*) is vacuous for the AIFA.

**What would fix it:** either restate Step 1 as *adopt and calibrate* the framework's criteria (naming what a company may actually vary — thresholds? slot-selection? evidence minimums?), or delete it and renumber to four steps.

### M3 · Placement cannot be executed — see V15

Covered numerically in `VALIDATION-REPORT.md` V15 and §5. In summary: thresholds exist for Stage 3 only and are PROPOSED; the five staging questions carry no level scale; no mapping from a 1–5 criterion score to a 1–5 stage is published. Two competent assessors land two stages apart on the same company (Stage 1 vs the 19 Sep review's Stage 2).

Adding here, from the reading pass: **Vol I §5.4 claims *"A company is not stage-limited by its technology. Every threshold describes a management practice, an accountability or a class of evidence. None describes a capability a vendor sells."*** Stage 3 threshold 2 is *"Knowledge governed and **delivered into every host**… the company's knowledge reaches each host its people work in."* Delivery into every host is the Company Domain Environment (Vol I §19) — a technology capability, and one Vol III §24/§31 shows has connectors for three hosts with the rest unbuilt. Threshold 2 is technology-limited, and §5.4's claim is false of it. **(M6)**

---

## 3 · Joins between volumes that do not hold

| # | Finding | Where |
| :---- | :---- | :---- |
| **M4** | **Two investment taxonomies, no crosswalk.** §4.2 classes investments four ways (People, Agents, Systems, Vendor tools), each with its own return rule. §4.4 classes them seven ways by *type* (new business model, revenue generation, market defence, regulatory, cost reduction, platform cost, enablement), each with its own justification method. These are different partitions of the same objects and no mapping between them is given. Vol III(d) has to pick one per row and ends up mixing both — row 1 carries a §4.4 method ("Payback + risk"), row 3 a §4.2 class rule ("Cost of service vs delivered use"). That mixing is the direct cause of the report's "ROI-method lines only" column meaning something different from what it says (V-G18). | Vol I §4.2 vs §4.4 |
| **M5** | **A risk provision is summed into the ROI denominator, and it is material.** Expected cost of error is the fifth cost line (§4.5), so it enters cost of service, which is the ROI denominator. But it is an expected loss, not money spent. Nothing in Vol I or M.7 says whether it is an accrual or a memo line. At Ashford it is $135k of the $1,272k ROI-line cost — **10.6%**. Removing it moves the portfolio from **147% to 177%**, and row 1 from 156% to 209%. A reader cannot tell which convention produced the published figure, and the two answers differ by 29 points. | Vol I §4.5, M.7, Vol III(d) |
| **M7** | **The one worked example of a decision component omits half the attribute set.** §11.1 defines twelve attributes. The §11.5 first-notice-of-loss exhibit carries seven columns and omits six: division of labour, reversibility, dependencies, outcome linkage, **benefits owner** and **reliance trajectory**. Consequence class appears only in prose beneath the table. The two omitted are the two the surrounding text ranks highest — benefits owner is *"the most predictive single field"* and reliance trajectory is *"the attribute companies do not currently hold,"* the stated justification for the second modelling pass. The exemplar does not exemplify the instrument, which is the likeliest reason the intake omits benefits owner too (Q10). | Vol II §11.1 vs §11.5 |
| **M8** | **Evidence rule 1 is suspended for the entire free tier, and nothing says so.** §13.5 rule 1: *"Never ask a question whose answer can be looked up. Converting a REPORTED cell into a STATED cell downgrades the instrument."* Vol III §22: *"The free scorecard reads nothing by default."* §23.1 step 1 sources spend from *"Recall, then the last invoice per vendor."* Phase 1 therefore converts lookupable figures to STATED by design, across every row. This is a defensible product decision — it buys "no security review, an evening's work" — but the discipline states a rule the product's flagship deliverable breaks everywhere, and neither §13.5 nor §22 acknowledges the other. | Vol II §13.5 vs Vol III §22, §23.1 |
| **M9** | **Evidence class is capped per surface in one section and assigned per metric in another.** §22's table gives each surface a *"best class it can earn"* — Hosts cap at REPORTED, Work records reach OBSERVED. §29 states the opposite rule: *"OBSERVED is earned by provenance, not by source type… The class is assigned per metric in 25.1, not per connector."* Under §29, Google's per-event audit log — which §24.1 calls *"the closest of the three to an activity record"* and which holds app, feature source and action — should earn OBSERVED. Under §22 it cannot, because it is a Host. The two rules disagree on a live case. | Vol III §22 vs §29, §24.1 |
| **M10** | **The company profile's output has no derivation rule.** §15: the instrument produces *"nine positions plus the identification of which dimension is holding the others back, because that is where the year's work goes."* No rule identifies the bottleneck. Nine positions with no weighting, no dependency graph and an explicit prohibition on summing gives an assessor no way to derive one. This is separate from the unwritten descriptors the section already flags — descriptors would give you the nine positions and still not give you the bottleneck. | Vol II §15 |
| **M11** | **The Bench is given a role the data-handling promise appears to forbid.** §27.1 assigns quarterly re-baselining to *"Reviewer with the Bench."* §28.3: *"the framework's own staff and the Outcomes Captain see aggregates only."* Re-baselining an artifact means moving the baseline reference on that company's own cells; it is not an operation on aggregates. Either the Bench sees company-level data — in which case §28.3 is wrong as written and a CISO will find it — or the Bench's role in §27.1 is advisory and should say so. | Vol III §27.1 vs §28.3 |
| **M12** | **The object model forbids Management from creating Findings; Vol I requires it to.** M.5: `Finding | Management: Resolve; never create`, and M.1 states the integrity rule that Management writes no Evidence or Measurement objects. But Vol I §5.5 gives the Management-phase health check three audits — the reliance audit, the evidence audit and the supervision-capacity check — each of which produces findings by construction ("A control that has caught nothing in six months is either working perfectly or not being performed"). Vol I §4.7's portfolio review likewise produces Retire and Cancel decisions against lines. Under M.5 none of those can be recorded as a Finding. | Vol III(c) M.5 vs Vol I §5.5, §4.7 |
| **M13** | **A promise is attributed to a sentence that does not contain it.** §28.5: *"aggregates already contributed to the peer view above threshold are not reversed, **and the signup sentence says so**."* The signup sentence, quoted verbatim at §28: *"your answers stay yours; anonymized aggregates build the benchmark you benefit from; nothing is read from your systems unless you hand a key to a screen that says exactly what it will read."* It does not say aggregates survive deletion. This is the same shape as the prior review's Q22 and a second instance of it: the section describing how the promise is kept overstates what the promise said. | Vol III §28, §28.5 |
| **M14** | **One of the five staging questions is a ratio with no threshold.** §14 asks *"Can the company state, for each investment, the outcome it should move?"* with the weak answer *"Some investments linked, most not."* Jay's simulation does not ask it; it computes **2 of 7** from the inventory — correctly, under §13.5 rule 1. But no threshold converts a ratio to weak or strong. Is 2 of 7 weak? 4 of 7? The prior review's Q16 asks whether §14 should be restated as four asked and one computed; this adds that the computed one has no cut-point, so it cannot feed a non-compensatory placement either way. | Vol II §14 |

---

## 4 · Where the same instrument is selected by two different rules

**M3b · Slot selection.** Vol II §12.5 scores *"Three slots… chosen by rule: the capability largest by spend, the widest by reach, and the least governed."* Vol I §3.3's cadence pyramid then says the quarterly activity is *"AIFA re-run on **changed components**."* Those are different populations. A component that changed but is not largest, widest or least governed is re-scored quarterly and was never scored at baseline; a slot chosen at baseline that did not change is never re-scored. The Maturity Curve (§5.4) plots *"placement against successive assessments"* — but successive assessments are not over the same set, so the curve compares unlike to unlike.

Jay's simulation scores **four** slots, adding "Discovered, not declared" (prior review Q5), which is a third selection rule. Three rules, one instrument, no reconciliation.

---

## 5 · What works, and is worth protecting

Stated because a review that lists only faults misrepresents the document.

| Works | Why it holds up |
| :---- | :---- |
| **Evidence classes and grades (§13)** | The grade/class separation is clean and the object model enforces it: a grade is set only by a Review, on an Artifact, per period. "An unreviewed export is not Monitored" is exactly the right rule. Rule 4 — a negative attestation *raises* confidence — is a genuine contribution; most instruments read candour as a gap. |
| **Consequence class and the evidence floor (§11.2–11.3)** | The idea is right and new: the price of being wrong sets how much evidence is owed before autonomy rises. Only the statement is broken (V16), not the concept. |
| **Discovery → Verification → Monitoring (§23, §26, §27)** | The best-specified material in the framework. The four discovery findings fall out of STATED answers alone; Verification's per-source consent with single-use keys is a real design; the Monitored grade attaching at sign-off, with an unsigned period rendering Estimated "whatever the feeds did", is precisely stated. |
| **The normalized record (§25)** | Host-neutral metrics, latency as a field, "the host's taxonomy is data, not schema", "fail visibly… never as zero". This is engineering, not prose. |
| **Consent and custody (§28)** | Content-returning APIs excluded *at code level, not by policy*, is the right control and the right justification. Aside from M11 and M13, the section would survive a CISO. |
| **The object model's integrity rule (M.1)** | "Management never writes Evidence: a plan cannot change what a feed said," with append-only Evidence, versioned Architecture and Management referencing the versions it decided against. That is a sound temporal model. |

---

## 6 · What I would fix first, for item 1

Additive to the 19 Sep list and to `VALIDATION-REPORT.md` §7.

| # | Action | Closes |
| :---: | :---- | :---- |
| 1 | Give the admission test a positive criterion, and make UNDETERMINED a finding on an admitted component rather than a pass | M1, and the root of Q1/F4 |
| 2 | State whether expected cost of error is an accrual or a memo line, and show the ROI both ways if it is an accrual | M5 |
| 3 | Publish a crosswalk from the four investment classes to the seven justification methods, one method per class-and-type pair | M4, V-G18 |
| 4 | Reconcile the three slot-selection rules, and say which population the Maturity Curve plots | M3b, Q5 |
| 5 | Rewrite §11.5 to carry all twelve attributes, including benefits owner and reliance trajectory | M7, Q10 |
| 6 | Say in §13.5 that rule 1 is relaxed in Measurement Phase 1, and why | M8 |
| 7 | Delete the per-surface class ceiling in §22 and defer to §29's per-metric rule | M9 |
| 8 | Either drop §5.4's "not stage-limited by technology" claim or re-word Stage 3 threshold 2 | M6 |
| 9 | Give §15 a bottleneck derivation rule, or describe the output as nine positions and an assessor's judgement | M10 |
| 10 | Resolve the Bench's re-baseline role against the aggregates-only promise, before any security review | M11 |
| 11 | Add a Finding kind Management may create, or change M.5's "never create" | M12 |
| 12 | Correct §28.5's attribution to the signup sentence | M13, extends Q22 |
| 13 | Restate Step 1 as *adopt and calibrate*, naming what a company may vary | M2 |
| 14 | Give §14's outcome-linkage question a cut-point | M14 |

---

## 7 · Reading of the three reviews together

The 19 Sep review found that **the delivered instrument is not the specified instrument**. This pass finds that, in three places, **the specified instrument is not an instrument** — the admission test cannot exclude, placement cannot place, and one method step has nothing in it. The model in `VALIDATION-REPORT.md` finds that **the arithmetic is sound and the published totals mostly contradict each other rather than the maths**.

Those point at one thing. Volumes I and II were cut on 16 September from a 30,000-word predecessor down to 14,000, and Volume III was written ten days later against the older numbering. The instruments that survive intact are the ones Volume III specified fresh. The ones that break are the ones that were compressed — where a rule and its exception ended up in different volumes, or the exception was cut and the rule kept.

That suggests the remedy is not twenty-two edits. It is a pass that takes each instrument and asks what an implementer must know, with Volume III's §25 as the standard to hold the others to.
