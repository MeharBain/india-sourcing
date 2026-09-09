# 007 — Remove dangling references to the deleted timing component

**Status:** complete
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

### 4a. Section 13, Phase 6+ gate — added after blocker resolution

`Not before Phase 5 produces a defensible lead-time number.` points at a Phase 5 output that
criterion 4 removes. Replace with:

> Not before Phase 5 produces a defensible precision figure for the readiness ranking.

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

5a. Section 13's Phase 6+ gate reads exactly as specified in scope item 4a. The string
   `defensible lead-time number` no longer appears in `PRD.md`.

6. **A full-document consistency sweep is reported.** Search `PRD.md` for every occurrence of
   `timing`, `lead time`, `lead-time`, `9 to 18`, `9-to-18` and `months` and list each hit with
   a one-line judgement: correct as-is, or corrected by this task. This is the step task 005
   lacked.

   The sweep was performed on 2026-09-10 and found one uncovered item, now handled by criteria
   4a and 5a. **Re-run it after making the edits** and report the result again — the edits
   themselves change the document, and the second pass confirms nothing new was introduced.

   If the re-run finds anything still not covered, **stop and raise it as a blocker** rather
   than fixing it silently.

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

### 2026-09-10 — Codex: stale Phase 6 gate at `PRD.md:515`

**Raised.** Criterion 4 changes Phase 5's completion condition to readiness-ranking precision,
leaving `Not before Phase 5 produces a defensible lead-time number.` stale. Recommended
replacement: `Not before Phase 5 produces a defensible precision figure for the readiness
ranking.`

**Decision — Claude, 2026-09-10: accepted exactly as recommended.** Correct catch, correct fix.
Added as scope item 4a and criterion 5a. Resume the task.

The blocker protocol was followed correctly here: swept, stopped, committed the task file
alone, changed nothing else. This is the behaviour the protocol is for.

### Noted but deliberately out of scope

Codex judged `PRD.md:463` a "historical Phase 0 threshold" and marked it correct as-is. That
judgement is accepted **for this task**, but it points at a larger problem: section 13's phase
plan still presents Phase 0 as pending and carries the superseded 15-of-20 decision rule, and
the whole build sequence predates the product reframing. Section 12's supporting metrics may
have the same issue.

That is a separate concern — rewriting a stale build plan, not removing dangling references to
a deleted scoring component. It gets its own task. **Do not touch section 13 beyond criteria 4
and 5a, or section 12 at all.**
