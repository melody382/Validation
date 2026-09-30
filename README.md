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

```
ABAF-VALIDATION.md          ← THE REPORT. Read this.
                              Everything below is its evidence.
```

| The report says | Tested by | Details in |
| :---- | :---- | :---- |
| §1 — 30 of 40 numbers reproduce | `verify_numbers.py` | `numeric_results.json` |
| §1b — 50 of 66 outputs impossible | `abaf_sim.py` + `run_companies.py` | `six-companies-result.txt` |
| §2 + §3 — 21 contradictions | **nobody — a human read them** | nowhere. Prose only. |
| §4 — the Captain's 12 regressions | a live session over Tailscale | `captain-regression/short/captain-run.md` |

Two supporting pieces: `extract_rules.py` built the 649-rule index (`rules.json`) that made the human reading pass possible, and `files/` holds the six ABAF documents everything was tested against.

Ignore `superseded/` — earlier drafts, kept for provenance only.

**The weak link:** §2 and §3 are the biggest part of the report and the only part with no stored result. The 21 contradictions exist as paragraphs, not data.

**Code** — all run clean, `python <name>.py`, no arguments:
`extract_rules.py` (builds the register) · `check_vocab.py` (vocabulary sweep) · `verify_numbers.py` (recomputes published figures) · `abaf_sim.py` (the instrument as code) · `run_companies.py` (six companies through it) · `view_object.py`, `brief.py` (viewers)

**Also here:** `superseded/` — first-pass reports, kept for provenance. And a pre-edit backup of the to-do file.

**Headline:** 30 of 40 published numbers reproduce — Jay's arithmetic is sound. 21 places the documents contradict each other, 11 where a needed rule is not written. 50 of 66 instrument outputs could not be produced at all. The Captain's twelve regressions are one unauthorised knowledge release, not twelve bugs.

**Still blocked:** BAC is undefined. Charlie, Diana, JohnQ and Spock all asked; none would guess.
