# ABAF v0.8 — validation of the instrument mechanics

**Date:** 29 September 2026
**Covers:** Volume I *The Methodology* · Volume II *The Instruments* (both 16 Sep) · Volume III parts (a) Integrations, (b) Vendor connector catalogue, (c) Consolidated object model, (d) Portfolio ROI report (all 26 Sep)
**Also tested:** the deployed Outcomes Captain, live over Tailscale, 29 Sep
**Supersedes:** the first-pass reports in `superseded/`. This is a rebuild, not an edit.
**Builds on:** the 19 September document review, which is referenced by the names its own findings carry.

---

## In short

I checked whether ABAF v0.8 works as an instrument — three ways: read every rule, recompute every number, run companies through it.

| | |
| :---- | :---- |
| **Reading** | 649 rules extracted from the six documents and read in same-topic groups. **21 places the documents contradict each other; 11 where a rule an implementer needs is simply not written.** The sharpest: the admission test cannot exclude anything, because "undetermined" is itself a passing answer — and a second, working admission test sits in Volume III, unreconciled with it. |
| **Numbers** | All 40 published figures recomputed from their inputs. **30 reproduce exactly — Jay's arithmetic is sound.** 8 fail; the worst is the ROI page contradicting itself by $655k on its own headline number. |
| **Simulation** | Six companies through the instrument, on Jay's own question set. **50 of 66 outputs could not be produced at all.** Seven outputs failed for every company. A bank doing everything right still cannot get a maturity placement. |
| **Live Captain** | All twelve September findings still reproduce — but the cause is **one unauthorised knowledge release**, in Backlog with no owner since 4 September. Not twelve bugs, one gate. |

**What to do with this:** 21 findings are edits to text Jay already wrote. 11 need new specification. The Captain needs one decision, not a bug queue. Details in §6 and §7.

---

## How this was done, and what that buys

The first attempt was expert reading: read the volumes, notice problems, verify the wording, write them down. It found real defects but could not report **coverage** — no way to say what fraction of the problems it caught, because there was no denominator.

This rebuild works from a **rule register**. Every normative statement in the six documents was extracted mechanically — each sentence, list item and table row that carries an obligation, a definition, a threshold, a computation or a constraint. Each rule is tagged with the framework objects it touches. That index is what makes the consistency check systematic: rules touching the same object can be read side by side, so a contradiction is *found* rather than *remembered*.

| | |
| :---- | ----: |
| Candidate rules extracted | **649** |
| Of which prose and table rules | **509** |
| Of which catalogue data rows | 140 |
| Framework objects indexed | 20 |
| Numeric claims recomputed from their stated inputs | **40** |
| Live turns against the deployed Captain | 8 |

**What this still does not buy.** One reader. The register removes luck from consistency checking and gives a denominator for coverage, but judging whether a rule is *executable* remains a judgement call. Two assessors could still differ — which is the framework's own inter-rater problem, applied to its reviewer.

Reproduce with `python extract_rules.py`, `python check_vocab.py`, `python verify_numbers.py`.

---

## 1 · The numbers

**40 numeric claims recomputed from their stated inputs. 30 reproduce exactly. 8 fail. 2 cannot be settled from the text.**

Everything in the cost chain is sound: all eight cost-of-service row totals, all five column totals, the $3,201k grand total, all three line ROIs, the 147% portfolio ROI, the $3.15M value delivered, the $13.2k cost per adoption point, and the row-2 expected cost of error. Jay's four fit-assessment slot totals (33, 25, 15, 10) also reproduce exactly, which independently confirms the arithmetic check in the 19 September review.

### The eight that fail

**The ROI page's most important number contradicts the finding that cites it.** The header prints *"Cost of service with no value side: $1.93M · 60% of the total"* and the page calls it "the most important on the page". $1.93M is the total minus the ROI-carrying lines, which sweeps in rows 5 and 6 — lines the same page marks *"n/a by rule"* and decides to **Keep** against met targets. The findings table then attributes $1.93M to *"Rows 4, 7, 8"*, which total **$1,274k / 40%**. The gap is **$655k**. The page's own count ("3 have no qualifying value side") agrees with $1.27M, not $1.93M.

**Row 2's value delivered is arithmetically wrong.** 88,100 × $9.40 = **$828.1k**, published $827k. It does not change the ROI, but it sits on the tap-back page — the one place the framework promises every input is disputable at the input that produced it.

**Six catalogue roll-up failures.** The A.4 summary publishes 83 Agentic / 53 Assisted / 3 Manual / 1 Excluded. The sheet parses to **80 / 52 / 1 / 1 with 6 dual-mode rows** A.4 has no column for — rows like #6 Vertex ("Agentic (billing); Assisted (Gemini Enterprise)") and #116 Bloomberg ("Manual (seats from billing); Assisted (usage)"). Four of eight group rows differ. The prose claim "six in ten … without a person in the loop" needs 57% on unambiguous rows, reaching 61% only if every dual-mode row is counted as Agentic — so the claim survives and the table does not.

**Placement is not reproducible.** Applying Vol I §5.3 in full to Jay's scripted run gives **stage 1**; the 19 September review, using the five staging answers alone, gives **stage 2**. §5.3 requires company-practice fit criteria to roll up at their floor as well, and those floor at 1. Same rule, same company, two stages apart.

### The two the text cannot settle

**Expected cost of error is a risk provision inside the ROI denominator.** It is the fifth cost line, so it enters cost of service, which is the ROI denominator — but it is an expected loss, not money spent. No document says whether it is an accrual or a memo line. At Ashford it is **$135k of $1,272k (10.6%)**: portfolio ROI reads **147% with it, 177% without**. Twenty-nine points hanging on an unstated convention.

**Catalogue verification coverage** is 3 of 140 rows — which is *consistent* with A.2's own statement that only the three starting hosts were checked, so it is a disclosure, not a defect.

---

## 1b · Six companies run through the instrument

The numeric checks above test *Jay's* arithmetic. This tests the **instrument**: six companies, the same question set for each (the 26 September rule — same questions, compare the answers), driven through every scored output.

The model is built on one rule: **it does not invent.** Where the specification decides something it implements it; where the specification does not, it returns UNDEFINED carrying the reason and the section that should have decided it. My first attempt filled those gaps with a made-up derivation table, which hid exactly what needed measuring.

**On the question set.** The 26 September decision was to keep Jay's existing questions and vary the companies, so the answers are comparable. Jay's set lives in `data/assessment/question-set.json` in the `Ethikal-Inc/outcomes` repo, which is not on this machine, so it was reconstructed from the volumes and from the structure visible in the scripted run: the nine per-item intake fields of S1B (Item, Spend, Origin, Acquisition, Deployment, Measured, Success def., Stage, Since), the ten fit criteria, and the five staging questions. The same set is used for all six companies.

One correction that came out of checking the reconstruction against Jay's transcript: an earlier version of this model added a **benefits owner** field to the intake. Jay's intake does not ask for it (19 Sep review, Q10), so the model was handing the instrument an input it never receives — flattering it. Removed, and the ownerless-investment finding of §23.3 is now correctly shown as unproducible.

**This also sharpens the derivation finding.** The deployment-model question that §12.5 derives four criteria and the complexity band from **is asked**, and its answers are in hand — "Our normal process", "A test group", "A special process". The input exists. What does not exist is any table mapping those answers to a 1–5 score, and the implementation abandoned the derivation outright (scripted run R27: *"nothing derived"*).

The companies span the range the framework claims to cover: Ashford on its scripted-run profile, a shadow estate (Ravensworth Retail), a regulated C4 estate (Pemberton Health), a fully measured board-reporting bank (Northgate), a company meeting everything except one Stage 3 threshold (Strathmore Energy), and one with an unset consequence class (Calder Logistics). Sixteen investments in total.

| Output | Ashford | Ravensworth | Pemberton | Northgate | Strathmore | Calder |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| admission | **disagree** | ok | ok | ok | ok | ok |
| fit assessment total | — | — | — | — | — | — |
| complexity band | — | — | — | — | — | — |
| slot selection | — | — | — | — | — | — |
| evidence floor | 4 undecidable | 2 | 1 | ok | 1 | 1 |
| ownerless finding | — | — | — | — | — | — |
| maturity placement | — | — | — | — | — | — |
| cost of service | 4 incomplete | 2 | 3 | ok | 2 | 2 |
| ROI | ok | n/a | n/a | ok | — | — |
| portfolio rebalance | — | — | — | — | — | — |
| reliance trajectory | — | — | — | — | — | — |

(— = the specification does not decide)

**50 of 66 instrument outputs could not be produced. 76%.**

Three results matter more than the percentage.

**Seven of the eleven outputs were never produced for any company.** The fit assessment total, the complexity band, slot selection, the ownerless-investment finding, maturity placement, portfolio rebalance and reliance trajectory failed 42 times out of 42. These are not edge cases — they are the instrument's headline outputs, and no company profile makes them computable.

**A perfect company still cannot be placed.** Northgate Bank meets all four Stage 3 thresholds, answers all five staging questions strongly, holds OBSERVED evidence on every component, breaches no floor and produces a clean 79% portfolio ROI. It is the best-run company in the set by every measure the framework has. **It still returns UNDEFINED for maturity placement**, because three of the four placement inputs have no level scale. The instrument cannot reward a company that does everything right.

**The two admission tests disagree on exactly the case the framework uses as its example.** Only Ashford holds a gateway, and only Ashford's admission result differs between §12.1 and §25.3.

### The gaps ranked by how often they bite

| Times hit | Gap | Section |
| ----: | :---- | :---- |
| 80 | The four derived criteria and the complexity band — the question is asked, no table maps the answer to a score | Vol II §12.5 |
| 26 | Expected cost of error — no error rate, or no consequence class to price it | Vol I §4.5 |
| 16 | The fit assessment total, blocked by the four derived criteria | Vol II §12.5 |
| 12 | Company-practice roll-up — no map from a 1–5 score to a 1–5 stage | Vol I §5.3 |
| 6 | Portfolio rebalance — no line-level fit score | Vol I §4.7 |
| 6 | Maturity placement — cannot run while any input has no level | Vol I §5.3 |
| 6 | Slot selection — no reach field, circular "least governed", no de-duplication | Vol II §12.5 |
| 6 | "Least governed" measured by criteria that are outputs of the assessment | Vol II §12.5 |
| 5 | Which stage a company that fails Stage 3 sits at | Vol I §5.2 |
| 4 | Floor for an UNSET consequence class | Vol II §11.2 |
| 3 | The C3 floor — a trajectory with no date cannot be tested pass/fail | Vol II §11.3 |
| 2 | Whether a C1/C2 with no evidence breaches | §11.3 vs §23.3 |
| 16 | The ownerless-investment finding — benefits owner is not an intake field | Vol III §23.3 vs the intake |
| 2 | Value from a linkage qualifying on a counterfactual or period but no baseline | §4.3 vs M.7 |

Reproduce with `python run_companies.py`.

---

## 2 · Rules that cannot be executed as written

### The admission test cannot exclude anything — and a second, working test exists elsewhere

Vol II §12.1 is titled the admission test for the whole framework: *"A capability that can be assigned a mode — automation, augmentation **or undetermined** — is a unit of the instrument. A thing that cannot is substrate."*

UNDETERMINED is itself an assignable mode, and Vol III §23.1 has the Captain propose one of the three with the user confirming. **No answer fails the test.**

Reading all twelve admission rules together surfaced something a single-pass read missed: **Vol III §25.3 contains a different admission test that works** — *"A host category with no admissible component beneath it (general chat, **a gateway**) maps to substrate and is recorded, not scored."* That one excludes the gateway by name, which is exactly the case Vol II §12.1 uses as its example and then fails to exclude.

So the framework has two admission tests, in two volumes, that do not agree, and the one labelled canonical is the one that does not work.

This also reframes the 19 September finding that the gateway was scored. It was not admitted by a bug. It was admitted by the rule.

The converse bites too: §11.4 maps the market's **Observe** tier — *"read-only; summarizes, retrieves… No proposal is made"* — to AUGMENTATION, so it is admitted. The stated ground for excluding a gateway is that "it decides nothing". A read-only summariser also decides nothing.

### Maturity placement cannot place

Thresholds exist for **Stage 3 only**, and they are marked PROPOSED. Stages 1, 2, 4 and 5 carry narrative characteristics and no thresholds. The five staging questions have **no level scale** — each has a single "weak answer" exemplar. And nothing maps a 1–5 criterion score onto a 1–5 stage, which is what §5.3's roll-up requires. Hence the stage 1 / stage 2 split above.

### The fit assessment cannot be scored from the specification

Vol II §12.5: one deployment-model question carries Standardization, Scalability, Reconfigurability, Implementation flexibility **and** the complexity band. **No derivation table exists in any of the six documents** — the register contains 21 rules touching the fit assessment and none of them defines it. Four of ten criteria and the band are unobtainable.

Compounding it, the NOT PROVIDED denominator is undefined (already ruled on 19 September). Measured effect on Jay's own slots: excluding nulls moves the gateway from 30% to 43% of achievable and Dept. ChatGPT from 20% to 29% — 13 and 9 points. Rank order survives; magnitude does not.

### Method Step 1 has no content

*"Build the fit assessment. Establish the criteria by which **this company** will judge whether an agentic capability fits its business."* But §12.2 fixes all ten criteria for every company, and §12.3 freezes the only remaining variable: *"Weights stay unset."* A company arriving at Step 1 decides nothing.

### The company profile's stated output has no derivation rule

§15 produces *"nine positions plus the identification of which dimension is holding the others back."* No rule identifies the bottleneck. Nine positions, no weighting, no dependency graph and an explicit prohibition on summing gives an assessor nothing to derive one from. This is separate from the unwritten descriptors the section already declares — descriptors would give the nine positions and still not give the bottleneck.

---

## 3 · Rules that contradict each other

Found by reading each object's rule group as a set. Each row names both sides.

| What contradicts | The two rules |
| :---- | :---- |
| **Whether a low-consequence component can breach its evidence floor** | §11.3 sets a floor for **all four** classes — C1 requires Estimated, C2 Monitored. §23.3 says an empty evidence row is a floor breach **"for C3 and C4 components"** only. A C1 with no evidence either breaches or does not, depending on which you read. |
| **Whether Measurement Phase 2 can supply the Stage 3 adoption threshold** | Vol I §16 says Phase 2 *"supplies the adoption-measured threshold of Stage 3."* Vol III §27.4 says monitoring *"does not produce proficiency or behaviour."* §13.6 splits activity / behaviour / proficiency three ways; §27.4 lumps two of them. Stage 3 is the chartered year-one outcome sold to Stage 2 entrants. |
| **Whether a component can hold a grade** | §11.3 states the evidence floor in grades. §13.1, §13.3 and M.3 make grade a property of an **artifact**, set by a Review. Four separate rules attribute a grade to a component; the object model makes that impossible. |
| **Whether evidence class is capped by surface or assigned by metric** | §22 gives each surface a "best class it can earn" — Hosts cap at REPORTED. §29 says *"OBSERVED is earned by provenance, not by source type… assigned per metric, not per connector."* They disagree on a live case: Google's per-event audit log, which §24.1 calls "the closest of the three to an activity record." |
| **Whether Management may create a Finding** | M.5 says `Finding | Management: Resolve; never create`. Vol I §5.5's three health-check audits and §4.7's portfolio review are Management activities that produce findings by construction. |
| **Whether a "movement" finding exists** | M.5 instructs Monitoring to *create* findings of kind "movement". M.3's Finding kind enumeration — nine kinds — does not contain it. Vol III(d) is forced to log a period-over-period change as "Divergent", which §25.4 defines as a within-period feed-versus-stated disagreement. |
| **How many reconciliation outcomes there are** | Vol III's own vocabulary table lists three (*"confirmed, undeclared, idle"*). §25.4 and M.3 define five. |
| **Whether Idle means zero** | §25.4 defines Idle as *"no activity in the period"* — absolute zero. Vol III(d) raises an Idle finding at **6 of 80 seats**. No partial threshold is published. |
| **Whether maturity is technology-limited** | §5.4: *"None describes a capability a vendor sells."* Stage 3 threshold 2 requires knowledge *"delivered into every host"* — the Company Domain Environment, with connectors for three hosts and the rest unbuilt. |
| **Whether the evidence discipline's first rule applies in Phase 1** | §13.5 rule 1: *"Never ask a question whose answer can be looked up."* §22: *"The free scorecard reads nothing by default."* §23.1 sources spend from *"Recall, then the last invoice."* Phase 1 breaks rule 1 everywhere, by design, and neither section acknowledges the other. |
| **Two investment taxonomies with no crosswalk** | §4.2 classes investments four ways with four return rules; §4.4 classes them seven ways with seven justification methods. No mapping. Vol III(d) mixes both — row 1 uses a §4.4 method, row 3 a §4.2 class rule — which is why its "ROI-method lines only" column means something other than what it says. |
| **The expected-cost-of-error formula** | Vol I §4.5 **and** M.7 both write *"consequence class × observed error rate × exposure."* Consequence class is an ordinal label. Computed literally with C2 as a multiplier the row-2 cell gives $43.7k; the published figure is $22k, i.e. the class contributes nothing. The formula appears twice and is wrong both times. |
| **What the signup sentence promises** | §28.5: *"aggregates … are not reversed, **and the signup sentence says so**."* The sentence, quoted at §28, does not say that. |
| **Where a $210k cost sits** | Booked to "Licence and seat" in the cost table and to "Investment line usage" in the tap-back. Same figure, two of the five cost lines, same page. |
| **Which outcome row 2's value comes from** | The Target names first-contact resolution (28% → 41%). The value is automated-resolution volume × unit value. M.7 step 5 computes against the named outcome. |
| **The Bench's access to company data** | §27.1 assigns quarterly re-baselining to *"Reviewer with the Bench."* §28.3: *"the framework's own staff and the Outcomes Captain see aggregates only."* Re-baselining moves a reference on that company's own cells. |

Two further gaps with no counterpart rule anywhere: **reliance trajectory** has four rules in the whole corpus, two asserting it *can* be read and none defining a metric, surface or derivation — while §24.2 confirms no host returns it. And the **Portfolio ROI report** carries a grade and a reviewer signature, but is not one of M.6's artifact kinds, and only Artifacts carry grades.

---

## 4 · The deployed Captain, tested live

Eight turns against the real Outcomes Captain over Tailscale, 29 September. **Every finding from 19 September still reproduces. Nothing has been fixed in ten days.**

| September finding, by its own name | Today |
| :---- | :---- |
| The Captain does not retain state between calls | Unchanged. Two consecutive calls gave session ids `6947d894` then `c223defc`; it answered *"I have no record of a previous message."* |
| "EST" is live in the running product | Unchanged — *"EST flag applied"* on turn 1 |
| The evidence vocabulary is one word deep | Unchanged. STATED now appears; REPORTED, OBSERVED and REQUIRES MEASUREMENT do not. It has invented "MISSING" |
| The live flow does not match the scripted run | Unchanged, now a third variant — two opening questions, versus three in September and five in the fixture |
| The checklist is never offered | Unchanged. Asked directly, it said *"Yes — I should have offered that."* It knows the step and skips it |
| The fit assessment it produces is not the fit assessment | Unchanged, new shape: four dimensions scored 0–4. September gave a single 0–10. Specification is ten criteria, 1–5, out of 50, three slots, complexity band |
| The maturity placement uses the wrong vocabulary | Unchanged, third vocabulary: "Exploring / Initiating / Developing / Establishing / Optimising" |
| It publishes a scored profile the framework forbids | Worse. Four dimensions explicitly averaged — *"Weighted mean = 1.0"* — and an overall **0.8 / 4 (20%)**. Decimals now, not half-points |
| The model gateway was scored | Unchanged. Classified "Infrastructure", then scored on all four dimensions |
| It recorded an estimate for a number it could look up | Unchanged. 20% recorded as EST, then listed as action MA-10: "pull instrumented Copilot usage" |
| The free tier produced recommendations | Worse. **Fifteen** numbered actions in four priority tiers with deadlines — *"This must be conducted before go-live, not after"* |
| The wrong session id reaches the client document | Unchanged. Scorecard footer reads `cfe03c39`; the call ran under `1f869a49` |

### Root cause — and it is one gate, not twelve bugs

Put to the internal advisors after the live run. **Spock (Technical Architecture) and JohnQ (QA) both evidence the same cause from Linear PRO-2291:**

> *"The knowledge release is not authorized — `publicationAuthorized: false`, `activationState: 'not-activated'` at version `2026.9.1`."*

The Captain loads the last *activated* knowledge version. Version 2026.9.1 was never authorised, so it is serving older content — which is why it returns a four-dimension 0–4 score, the Exploring/Initiating ladder and the retired word EST. Its own reply is accurate about its loaded substrate: the ten-criterion format *"is not what the P1A substrate produces."*

Spock's conclusion, which I accept and which corrects how I first framed this: **the Captain is operating correctly given what it has loaded. This is a product-state problem, not a platform bug.** Filing the twelve regressions as defects would route them to the wrong queue. They are one release-authorisation decision.

PRO-2291 is assigned to jay@ethikal.com, has sat in Backlog since 2026-09-04, and **has no active owner**. The authorisation is listed in the issue itself as a hard prerequisite for the system to work as designed.

Two further things the advisors evidenced:

- **The ABAF work is in a separate repository.** `Ethikal-Inc/outcomes`, split out on 2026-08-23, which is why neither the generator nor the scoring anchors are on this machine and why they are absent from the main platform repo.
- **The governing spec is not ratified.** `SPEC-OUTCOMES-CAPTAIN-RUNGS-001` (the ADR-236 amendment) sits at `AUTHOR_APPROVAL`; the quorum policy returned `escalate_human` because the five approving reviewers were same-model-family. The Bronze/Silver definition of done is inside that unmerged document — so there is currently **no ratified launch-readiness definition** to validate against.

### Six things that are new

**It does not recognise the fit assessment as its own.** Asked for the ten-criterion assessment out of 50, it replied that the format *"is not what the P1A substrate produces"* and speculated the board *"may be referencing a different framework (e.g., an internal format, a vendor scorecard, or a third-party AI maturity model)."* It treats ABAF's central instrument as possibly foreign.

**Maturity is seeded by self-assessment.** Scoping question 3 asks the respondent to pick their own stage A–D, *"to calibrate the measurement scope and maturity anchors correctly."* Vol I §5's first inherited property is that levels are defined by thresholds **rather than** self-assessment.

**Consequence class has appeared, on the wrong scale.** It now assesses consequence and reversibility, which it did not in September — but returns HIGH/MEDIUM/LOW, not C1–C4, and replaces the evidence floor with an ad-hoc five-item checklist carrying no grade. It asserts specification authority for this: *"The @ethikal/outcomes-instrument applies consequence and reversibility framing."*

**A third mode taxonomy:** "Archetype: Assisted / Agentic / Infrastructure."

**An arithmetic error in the client-facing scorecard.** Dimension 4A's table sums to 5; the narrative says "Recorded = 7" and reports a mean of 1.0. It states "5 of 7 investments score 0" where its own table shows 4, and its counts total 8 across 7 investments. Corrected, that dimension is 0.71 and the overall score is **0.75, not 0.8**.

**It fabricated the respondent's next turn**, writing Dana's reply for her at the end of turn 4. Observed once.

### What it does well

It refused to fabricate. Explicitly authorised to assume answers, it declined and explained that a scorecard built on assumed values *"could be used as if it were evidence — which it is not"*, offering MISSING flags instead. It handled the near-miss caveat correctly, flagged that total spend is understated by an unknown amount, and caught the shadow ChatGPT procurement.

**The nine Outcomes Bench advisors are not built.** Not merely absent from the internal, external and platform tiers — PRO-2291 records zero `COMPANY_CAPTAIN` entries in `advisor-domains.ts` against seven services and three controllers already built under `spaces/`, and the Outcomes Phase 2 project (rungs 3 and 4) is empty. The Company Captain is the foundation the bench sits on, and it has no template. This upgrades the to-do's "five of nine lack real content" to "none of nine is deployed, and the tier below them does not exist either."

**Nothing from Volume III has reached it**: no Verification, no connected baseline, no evidence classes. Its four artifacts are unchanged from September.

---

## 5 · What works and should be protected

| | |
| :---- | :---- |
| **Evidence classes and grades** | The class/grade separation is clean and the object model enforces it. "An unreviewed export is not Monitored" is the right rule. The negative-attestation rule — candour *raises* confidence — is a genuine contribution |
| **Consequence class and the evidence floor** | Right idea, new: the price of being wrong sets the evidence owed before autonomy rises. Only the statement is broken |
| **Discovery → Verification → Monitoring** | The best-specified material in the framework. Four discovery findings fall out of stated answers alone; single-use per-source keys are a real design; an unsigned period rendering Estimated "whatever the feeds did" is precisely stated |
| **The normalized record** | Host-neutral metrics, latency as a field, "the host's taxonomy is data, not schema", "fail visibly… never as zero" |
| **Consent and custody** | Content-returning APIs excluded *at code level, not by policy*. Aside from the Bench and signup-sentence issues, it would survive a security review |
| **The object model's integrity rule** | "Management never writes Evidence: a plan cannot change what a feed said," with append-only Evidence and versioned Architecture |

The documents are also **vocabulary-clean**: the only surviving "EST" occurrences are in the rename table's own "Was" column. The rename reached the documents. It did not reach the software.

---

## 6 · What to fix first

| # | Action |
| :-: | :--- |
| 1 | Decide what the ROI page's fourth number means, and make the headline and the finding agree |
| 2 | Rule whether Measurement Phase 2 can supply the Stage 3 adoption threshold — the chartered outcome depends on it |
| 3 | Replace §12.1's admission test with §25.3's, which works, and make UNDETERMINED a finding on an admitted component rather than a pass |
| 4 | Publish the deployment-model derivation table, or delete "six asked, four derived" |
| 5 | Write thresholds for stages 2, 4 and 5 and a level rubric for the five staging questions — or state that placement is Stage-3-gated only |
| 6 | Restate the evidence floor in cell classes; give C3 one testable value; reconcile §11.3 with §23.3 on whether C1 and C2 can breach |
| 7 | Correct the expected-cost-of-error formula in both §4.5 and M.7, and say whether the provision belongs in the ROI denominator |
| 8 | Name the tolerance denominator in §25.4, give Idle a partial threshold, order Confirmed before Divergent |
| 9 | Publish the evidence-class ordering; apply class propagation consistently in the ROI table; delete §22's per-surface ceiling in favour of §29's per-metric rule |
| 10 | Regenerate the A.4 roll-up from the sheet and add a dual-mode column |
| 11 | Add Finding kinds for movement and for unset consequence; add an artifact kind for the portfolio report |
| 12 | Resolve the Bench's re-baseline role against the aggregates-only promise before any security review; correct §28.5's attribution |
| 13 | Publish a crosswalk from the four investment classes to the seven justification methods |
| 14 | Decide where reliance trajectory is measured from, or mark it unmeasurable in this edition |
| 15 | Restate Step 1 as *adopt and calibrate*, naming what a company may vary |

For the deployed Captain the ordering is different, and the advisor evidence changed it. It is **not** a list of bugs:

| # | Action | Owner |
| :-: | :--- | :--- |
| 1 | Authorise knowledge release 2026.9.1, or state that the hold is deliberate. PRO-2291 has had no active owner since 4 Sep. Ten of the twelve regressions are downstream of this one gate | jay@ethikal.com |
| 2 | Ratify `SPEC-OUTCOMES-CAPTAIN-RUNGS-001`. Quorum returned `escalate_human` (same-model-family reviewers), so the Bronze/Silver definition of done is still unmerged and there is nothing to validate against | Author approval |
| 3 | Fix session state. This one is **not** downstream of the release gate — the Captain forgets every message, and a 121-answer instrument cannot run over it | Platform |
| 4 | Register `OutcomesCaptainProvisioning` in `outcomes.module.ts` — currently unreachable, its only caller is its own unit test | Platform |
| 5 | Re-run this regression after 1 and 3. Until the release is activated, the other findings cannot be confirmed as real defects | — |

Only items 3 and 4 are code. Items 1 and 2 are decisions, and they gate everything else.

---

## 7 · Which of these is Jay's to fix, and which is just unbuilt

The 26 September meeting asked that findings separate what the methodology *describes* from what exists today, since the scorecard/simulation product is not what is being delivered now. Applied to all 36 document findings, that split turns out to be the wrong axis — almost nothing here is a build gap, because this review read documents, not software. The useful split is three ways.

| Category | Count | What it means | Who fixes it |
| :---- | ----: | :---- | :---- |
| **The text contradicts itself, or states a rule that cannot execute** | 21 | True regardless of what is built | Editor |
| **The text is absent where an implementer must have it** | 11 | Not wrong — missing | Author |
| **Declared incomplete by an explicit status marker** | 4 | Legitimately not a finding | Nobody; track it |

**Category 3 is smaller than it looks.** Four findings touch a section carrying a status marker, but in **three of the four the gap found is not the gap the marker declares**:

- §5.2 declares the Stage 3 thresholds *PROPOSED*. It does **not** declare that stages 2, 4 and 5 have no thresholds at all.
- Vol I §22 declares the portfolio **weighting formula** unwritten. It does **not** declare that no line-level fit score exists to weight.
- §15 declares the **descriptors** unwritten. The missing **bottleneck derivation rule** is separate; writing 45 descriptors would not produce it.

Only the descriptor half of the §15 finding is cleanly covered.

**So the honest number to hand Jay is 32, not 36** — and 21 of those are edits to text he already wrote, not new specification.

The Captain findings sit outside this split entirely: they are product state, gated on one unauthorised knowledge release (§4).

---

## Appendix · What each script does

All five run clean from a cold start, exit 0. `python <name>.py`, no arguments, no dependencies beyond the standard library.

**`extract_rules.py`** — Walks all six documents and pulls out every sentence, list item and table row that states a rule. Tags each with the framework objects it mentions, so rules about the same thing can be read together. This is what gives the review a denominator instead of "I read it and noticed things."
*Produces `rules.json`, `rules.csv` — 649 rules.*

**`check_vocab.py`** — Takes each controlled vocabulary the framework defines and finds every line that enumerates it, then diffs against the canonical set. Also sweeps for retired terms that should no longer appear anywhere. Result: the documents are clean — the old vocabulary survives only in the deployed software.

**`verify_numbers.py`** — Recomputes every published number from its stated inputs and compares against what the documents print. Covers the eight cost rows, five column totals, three line ROIs, the four headline figures, the row-2 tap-back chain, the catalogue roll-up and the scripted-run slot totals. Reports 30 reproduce, 8 fail, 2 unsettleable from the text.
*Produces `numeric_results.json`.*

**`abaf_sim.py`** — The instrument written as executable code: admission, evidence floor, fit assessment, placement, cost of service, ROI, portfolio. Its one design rule is that it never invents — where the specification does not decide, it returns UNDEFINED carrying the reason and the section at fault. That is what makes the gaps countable rather than hidden behind a plausible guess.

**`run_companies.py`** — Defines six companies spanning the range the framework claims to cover and runs each through `abaf_sim` on the same question set. Produces the matrix of which outputs the instrument could not produce, and ranks the gaps by how often they bite. The missing derivation table alone is hit 64 times across six companies.

**`view_object.py`, `brief.py`** — Two small viewers. Given an object name they print every rule touching it, full text or one line each. Used for the same-topic reading pass in §2 and §3.

### Other files here

| | |
| :---- | :---- |
| `rules.json`, `rules.csv` | The rule register itself — inspect it to see what was covered |
| `numeric_results.json` | All 40 numeric checks with pass/fail and detail |
| `captain-regression/short/`, `/full/` | Live Captain transcripts and logs, 29 Sep |
| `superseded/` | The first-pass reports, kept for provenance |

Nothing in `files/` was modified except `Todo Sep.txt`, at your direction; a pre-edit backup sits in this folder.

**Still blocked:** BAC is named in the to-do and defined in no document. Charlie, Diana, JohnQ and Spock were all asked; none would guess. JohnQ's best evidenced lead is that it is pre-rename vocabulary from the "Boundaries → Measurement" rename in PRO-2291, or that it lives in the `Ethikal-Inc/outcomes` repo. Whoever wrote the line can settle it in thirty seconds.
