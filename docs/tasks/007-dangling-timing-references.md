# 007 — Remove dangling references to the deleted timing component

**Status:** blocked
**Branch:** task/007-dangling-timing-references
**Depends on:** 005 merged. Independent of 006 — disjoint files, and 006 is a code task on the
separate merge track.

---

## Intent

Task 005 replaced the timing component in `PRD.md` section 8 exactly as specified and its
acceptance criteria all passed. But the criteria were written as exact-text replacements scoped
to named sections, and were therefore blind to other parts of the document that depend on the
removed concept.

Three references survive. One of them specifies a digest feature that can never populate.

This is a defect in the task-005 specification, not in its execution.

---

## Scope

Four corrections in `PRD.md`, plus a note in `PROGRESS.md`. Documentation only.

### 1. Section 9, weekly digest — the one that matters

Currently:

> - **Entering the window** (3 to 5). Companies whose timing component just crossed into the
>   12-to-20-month band.

The timing component is gone and the 12-to-20-month band was the error being corrected.
A digest section driven by it would always be empty. Replace the bullet with:

> - **Entering the window.** *Deferred.* This section was defined by the timing component,
>   which is disabled at weight 0 (see section 8). It cannot be built until a readiness model
>   exists. Do not implement a placeholder that silently returns nothing.

### 2. Section 8 preamble — internal contradiction

The section opens with `Score is 0 to 100, computed per tenant.` while the readiness block a
few paragraphs later states the maximum is 85. Replace the opening sentence with:

> Score is 0 to 85 per tenant while the readiness component is disabled; the nominal range is
> 0 to 100 and will be restored when readiness is built. Weights live in `config/scoring.yaml`
> so they can be tuned without a deploy.

Note the `Score.total` CHECK constraint permits 0–100 and needs **no** change. 85 is within
range and tightening it would require a migration to loosen later.

### 3. Section 13, Phase 5 — stale completion condition

`Done when: you have a number for median lead time you'd be willing to put on a sales deck.`
contradicts the new section 12, where lead time is explicitly no longer the headline metric.
Replace with:

> Done when: you have a defensible precision figure for the readiness ranking — of the top 10
> surfaced, how many raised institutional capital within 18 months.

### 4. Section 14, risk table — stale row

The row `Lead-time premise doesn't hold | Fatal | Phase 0 test before any code` describes a
risk that has now materialised and been resolved. Replace that row with:

> | Lead-time premise did not hold as stated | Resolved | Measured at 5–13 years, not 9–18 months. Product reframed around readiness ranking. See ADR-015 and `docs/FEASIBILITY_TEST.md` |
> | Readiness ranking cannot be modelled | Fatal | Detection is solved; if readiness cannot be predicted the digest is unrankable. Open — no mitigation yet |

The second row is the live version of this risk and currently appears nowhere.

---

## Out of scope

- Any change under `src/`, `tests/`, `migrations/` or `config/`
- The `Score.total` CHECK constraint — explicitly unchanged, see above
- Designing the readiness model
- Any further edit to sections 1 or 12, which task 005 handled correctly

---

## Acceptance criteria

1. `PRD.md` contains no occurrence of the string `12-to-20` or `12–20` outside section 8's
   readiness block, where it appears only in the historical explanation of what was removed.
   Report the result of searching for both forms.

2. Section 9's "Entering the window" bullet reads exactly as specified above.

3. Section 8's opening sentence reads exactly as specified above.

4. Section 13 Phase 5's "Done when" line reads exactly as specified above.

5. Section 14's risk table contains both replacement rows and no longer contains the original
   lead-time row.

6. **A full-document consistency sweep is reported.** Search `PRD.md` for every occurrence of
   `timing`, `lead time`, `lead-time`, `9 to 18`, `9-to-18` and `months` and list each hit with
   a one-line judgement: correct as-is, or corrected by this task. This is the step task 005
   lacked. If the sweep finds anything not covered by criteria 1–5, **stop and raise it as a
   blocker** rather than fixing it silently — the spec should be amended to cover it.

7. `Score.total` CHECK constraint in `src/core/models.py` is unchanged. Confirm explicitly.

8. `uv run pytest` passes at 50; `uv run ruff check .` passes.

9. `PROGRESS.md` gains a session entry noting that task 005's exact-text criteria did not catch
   downstream references, as a lesson for future specifications.

---

## Files expected to change

```
PRD.md          sections 8, 9, 13, 14
PROGRESS.md     session entry
```

Nothing else.

---

## Risks

- **Fixing sweep findings silently.** Criterion 6 exists because the natural instinct on
  finding a fifth stale reference is to correct it while you are there. That reintroduces
  exactly the unreviewed-change problem this task exists to close. Raise it.
- **Tightening the score CHECK constraint to 85.** Tempting for consistency, wrong in
  substance: readiness will be re-enabled and the constraint would then need loosening via
  migration. Criterion 7 guards this.
- **Treating this as trivial.** It is small, but item 1 is a specification for a feature that
  cannot work, and those are the errors that survive longest because they read as complete.

---

## Blockers and questions

### 2026-09-10 — Phase 6 still depends on the removed Phase 5 lead-time output

The criterion-6 consistency sweep found one stale reference that criteria 1–5 do not cover:
section 13 Phase 6 says `Not before Phase 5 produces a defensible lead-time number.` The
specified Phase 5 correction instead makes its completion output a defensible precision figure
for the readiness ranking. Leaving the Phase 6 gate unchanged would preserve an internal
contradiction; changing it now would exceed the accepted scope.

Decision needed:

1. **Recommended:** amend the scope and acceptance criteria to replace the Phase 6 sentence
   with `Not before Phase 5 produces a defensible precision figure for the readiness ranking.`
2. Remove the Phase 6 gating sentence entirely.
3. Retain the lead-time gate and explain why a defensible lead-time number remains a separate
   prerequisite even though it is no longer Phase 5's completion condition.

Full consistency sweep, against `PRD.md` before any task-007 corrections:

| Search term | Line | Hit | Judgement |
|---|---:|---|---|
| `timing` | 378 | `timing component just crossed` | Corrected by criterion 2. |
| `lead time` | 16 | `The product bet is **lead time**` | Correct as-is: section 1 states the measured finding and reframed value proposition. |
| `lead time` | 325 | `9-to-18-month lead time` | Correct as-is: historical explanation inside section 8's readiness block. |
| `lead time` | 439 | `Lead time is no longer the headline metric` | Correct as-is: section 12 states the current metric decision. |
| `lead time` | 463 | `meaningful lead time` | Correct as-is: Phase 0's historical feasibility threshold. |
| `lead time` | 507 | `Measure lead time and recall` | Correct as-is: lead time remains a supporting validation measurement, not the completion gate. |
| `lead time` | 510 | `median lead time` | Corrected by criterion 4. |
| `lead-time` | 460 | `Lead-time feasibility test` | Correct as-is: the named Phase 0 test remains part of the build record. |
| `lead-time` | 515 | `defensible lead-time number` | **Blocker:** stale Phase 6 gate not covered by criteria 1–5. |
| `lead-time` | 523 | `Lead-time premise doesn't hold` | Corrected by criterion 5. |
| `9 to 18` | — | No hits. | Correct as-is. |
| `9-to-18` | 325 | `9-to-18-month lead time` | Correct as-is: historical explanation explicitly retained by criterion 1. |
| `months` | 147 | `fourteen months later` | Correct as-is: concrete watchlist example. |
| `months` | 175 | `18 months after filing` | Correct as-is: statutory patent-publication lag. |
| `months` | 324 | `months elapsed` | Correct as-is: historical description in the readiness block. |
| `months` | 325 | `12–20 months` | Correct as-is: historical explanation explicitly retained by criterion 1. |
| `months` | 360 | `last 36 months` | Correct as-is: current signal-recency suppressor. |
| `months` | 361 | `signal in 36 months` | Correct as-is: current sole-director suppressor. |
| `months` | 364 | `last 24 months` | Correct as-is: explicitly removed former suppressor. |
| `months` | 437 | `within 18 months` | Correct as-is: readiness-ranking outcome horizon. |
| `months` | 445 | `last 18 months` | Correct as-is: golden-set sampling window. |
| `months` | 461 | `last 18 months` | Correct as-is: Phase 0 cohort sampling window. |
| `months` | 462 | `by how many months` | Correct as-is: Phase 0 measurement instruction. |
