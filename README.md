# ABAF v0.8 validation — where everything is

29 September 2026 · `\.claude\projects\advisor-bridge\validation\`

**Read this one:** `ABAF-VALIDATION.md` — opens with an "In short" table, four rows.

| Want | File |
| :---- | :---- |
| The report | `ABAF-VALIDATION.md` |
| Six companies, simulation output | `six-companies-result.txt` |
| 40 numeric checks, pass/fail | `numeric_results.json` |
| Live Captain, full scorecard (5 turns) | `captain-regression/short/captain-run.md` |
| Live Captain, opening flow (3 turns) | `captain-regression/full/captain-run.md` |
| The 24 questions used, and the Dana questions not used | `question-set-used.json` |
| The 649-rule register | `rules.json`, `rules.csv` |

**Code** — all run clean, `python <name>.py`, no arguments:
`extract_rules.py` (builds the register) · `check_vocab.py` (vocabulary sweep) · `verify_numbers.py` (recomputes published figures) · `abaf_sim.py` (the instrument as code) · `run_companies.py` (six companies through it) · `view_object.py`, `brief.py` (viewers)

**Also here:** `superseded/` — first-pass reports, kept for provenance. And a pre-edit backup of the to-do file.

**Not here:**
- The updated `Todo Sep.txt` is in `files\`, where it belongs — the only file there I changed.
- The 19 Sep review stays at `.claude\projects\ethikal\abaf-v0.8-review.md`, referenced but not edited.

**Headline:** 30 of 40 published numbers reproduce — Jay's arithmetic is sound. 21 places the documents contradict each other, 11 where a needed rule is not written. 50 of 66 instrument outputs could not be produced at all. The Captain's twelve regressions are one unauthorised knowledge release, not twelve bugs.

**Still blocked:** BAC is undefined. Charlie, Diana, JohnQ and Spock all asked; none would guess.
