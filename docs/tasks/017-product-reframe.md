# 017 — Product reframe reconciliation

**Status:** blocked
**Branch:** task/017-product-reframe
**Depends on:** 016 merged.

---

## Intent

Commit `2126079` added `docs/SHORTLIST_SCHEMA.md` and an updated
`docs/FEASIBILITY_TEST.md` to `main`. Those documents record a product reframe that `PRD.md`
does not reflect, so the repository currently contradicts itself: the PRD describes a system
that predicts which companies will raise, while the research documents state the product
assembles evidence and explicitly does not predict funding events.

The reframe, in one line: **a company living on non-dilutive grants with no institutional equity
is the target, not a false positive.** The earlier framing treated it as a precision problem.
That was wrong, and it made the readiness model look intractable — it was the wrong task, not an
unfittable curve.

This task also clears schema drift in PRD section 6, which has fallen four changes behind the
code.

Documentation only.

---

## Scope

### 1. PRD section 1 — positioning

Replace the paragraph beginning "The product bet is" with exactly:

> The product bet is **discovery**, not prediction. Incumbents cover companies after
> incorporation, after a website, after press, and after a round. Grant and incubator records
> make Indian deeptech companies visible years earlier — see `docs/FEASIBILITY_TEST.md`.
>
> The product surfaces deeptech companies with credible technical validation that private
> capital has not yet reached, and presents enough evidence per company for a human to decide
> whether to take a meeting. **It does not predict funding events.** A company living on
> non-dilutive grants with no institutional equity is the target, not a false positive.
>
> Detection is not the hard problem. Ranking is. Roughly eight BIRAC BIG cohorts are live at any
> moment — about 800 entities — and they differ enormously in the strength of their investment
> case. A four-year-old with no website, one founder and no patents is not the same proposition
> as an eighteen-month-old with five patents and a working device. The discriminator is evidence
> assembled per company, specified in `docs/SHORTLIST_SCHEMA.md`.

### 2. PRD section 12 — success metrics

Replace the paragraph beginning "**The metric that matters" with exactly:

> **The metric that matters: meeting conversion.** Of the companies surfaced on a shortlist,
> what fraction were worth an hour of a partner's time? Measurable from `review_event`, and it
> is what the product is felt to be doing week to week.
>
> **Tracked qualitatively: discovery credit.** Companies met because of this system that would
> otherwise have been missed. This is the truest measure of a deal sourcer and the hardest to
> instrument. Record it in prose each quarter rather than pretending it is a metric.
>
> **Explicitly not a metric: whether surfaced companies subsequently raise.** That measures
> prediction, which is not the job. A company that never takes institutional capital may still
> have been worth the meeting.

### 3. PRD section 6 — data model block

The code block is four changes behind. Update it to include:

- `signal.person_id`, nullable, with the `ck_signal_single_entity` note that at most one of
  `company_id` and `person_id` is set (task 016, ADR-013)
- `classification_review`, with its columns and the note that it is global rather than
  tenant-scoped, and that it overrides rather than mutates `signal_type` (task 015, ADR-022)
- `source.consecutive_failures`, `last_error`, `last_failure_at`, and the constrained
  `health_status` (task 006)
- Correct the `resolution_candidate` comment. It currently reads "the review queue for entity
  resolution." It is a candidate-pair adjudication table and cannot represent a signal with no
  candidate entity — that is what `classification_review` exists for.

### 4. ADR-016 — amend the reason

ADR-016 records the readiness component as disabled at weight 0 because three data points cannot
fit a curve. Amend it: the deeper reason is that predicting a funding event is not the product's
job. Evidence assembly replaces it. Do not delete the original reasoning — amend, so the record
of how the understanding changed survives.

### 5. The BIG panel score

`PRD.md` and `config/sources.yaml` both describe the Final Score column as BIRAC's own quality
ranking, implying it is a usable model input. Amend both to state that it is **evidence in a
dossier, not a weighted predictor**, citing the back-test observation that Magnimous Info Tech
scored highest in its cohort at 77.86 with no traceable outcome, while Theranautilus — the only
awardee found to have raised — scored third of four at 73.19. Note n=4.

### 6. Reference the schema

PRD section 9 should reference `docs/SHORTLIST_SCHEMA.md` as the specification of what a
surfaced row must carry, including its hard gate: an individual awardee whose name has not been
resolved to a specific person does not reach a shortlist.

---

## Out of scope

- Any change under `src/`, `tests/`, `migrations/`
- Re-enabling the readiness component
- Implementing the shortlist schema. This task points at it; building it is later.
- Editing `docs/SHORTLIST_SCHEMA.md` or `docs/FEASIBILITY_TEST.md`. They are the source.
- PRD section 13's build plan, still stale and still deferred.

---

## Acceptance criteria

1. PRD section 1 reads exactly as specified. The string `ranking probability` does not appear
   anywhere in `PRD.md`.
2. PRD section 12 reads exactly as specified.
3. PRD section 6's data model block includes all four updates in scope item 3. List each and
   quote the added lines.
4. ADR-016 is amended, not replaced. Both the original curve-fitting reasoning and the
   wrong-task reasoning are present.
5. `PRD.md` and `config/sources.yaml` both describe the BIG score as evidence rather than a
   predictor, with the n=4 caveat.
6. PRD section 9 references `docs/SHORTLIST_SCHEMA.md` and its hard gate on unresolved
   individual awardees.
7. **Full-document consistency sweep, reported hit by hit.** Search `PRD.md` for `predict`,
   `readiness`, `raise`, `raised`, `precision`, `false positive` and `probability`. Give each hit
   a one-line judgement: correct as-is, corrected by this task, or **blocker**. Anything not
   covered by criteria 1–6 must be raised as a blocker, not fixed silently. This is the task-007
   procedure, which found a real stale reference the criteria had missed.
8. Re-run the sweep after the edits and report it again.
9. `uv run pytest` passes at 117; `uv run ruff check .` passes.
10. `PROGRESS.md` session entry, and its Current position block updated to describe the product
    as a deal sourcer.

---

## Files expected to change

```
PRD.md                   sections 1, 6, 9, 12
config/sources.yaml      birac_big score note
docs/DECISIONS.md        ADR-016 amended
PROGRESS.md              session entry and current position
```

---

## Risks

- **Deleting ADR-016's original reasoning.** The record of how understanding changed is worth
  more than a tidy ADR. Criterion 4 requires both.
- **Fixing sweep findings silently.** Criterion 7 exists because the instinct on finding a fifth
  stale reference is to correct it while you are there, which reintroduces the unreviewed-change
  problem this procedure closes.
- **Treating this as cosmetic.** The repository currently tells a future reader that the product
  predicts funding events. That reader will be Codex, at the start of every task.

---

## Blockers and questions

### Blocker — Codex, 2026-09-10: the required sweep finds uncovered contradictions

Criterion 7 requires the task-007 procedure before editing and says that any hit not covered by
criteria 1–6 is a blocker. The pre-edit sweep found stale prediction/readiness claims in PRD
sections 5, 8, 9 and 13. Fixing them would exceed the accepted scope; leaving them would make the
reconciled PRD contradict the product reframe.

#### Pre-edit sweep, hit by hit

- Line 21, `raise` — **corrected by criterion 1**; it is inside the positioning paragraph being
  replaced.
- Line 23, `raise` — **corrected by criterion 1**; it is inside the same positioning paragraph.
- Line 160, `predictable funding clock` — **blocker**; section 5 still characterises BIRAC as a
  prediction signal, and no criterion covers that source-table row.
- Line 162, `will raise` — **blocker**; section 5 still characterises NIDHI-SSS as predicting a
  funding event, and no criterion covers that source-table row.
- Line 282, `readiness component is disabled` — **blocker**; section 8 presents readiness as a
  temporarily disabled component rather than a retired wrong task.
- Line 283, `restored when readiness is built` — **blocker**; this explicitly promises to restore
  the prediction component, contrary to the reframe.
- Line 288, `raise corroboration` — **correct as-is**; “raise” is the ordinary verb meaning
  increase, not a funding prediction.
- Line 323, `Component: readiness ... DISABLED` — **blocker**; the heading preserves readiness as
  a future scoring component, outside criteria 1–6.
- Line 330, `until a readiness model is built` — **blocker**; it promises the superseded model
  will return.
- Line 334, `readiness signals to model` — **blocker**; it frames evidence fields as inputs to a
  future funding-timing model rather than dossier evidence.
- Line 360, `Already raised ... suppress` — **correct as-is**; absence of institutional equity is
  a shortlist gate, so already-funded companies remain valid suppressions.
- Line 365, `Ayati Devices, which raised` — **correct as-is**; this is a factual example explaining
  why age alone is not a useful suppressor.
- Line 380, `until a readiness model exists` — **blocker**; section 9's “Entering the window”
  surface still depends on the superseded prediction model. Criterion 6 adds a schema reference
  and hard gate but does not authorise resolving this separate surface.
- Lines 440–441, `precision`, `readiness`, `raise` — **corrected by criterion 2**; these are the
  success-metric paragraph being replaced.
- Line 450, `Precision@10` — **correct as-is**; it measures human “interesting” judgements, which
  is consistent with meeting conversion despite the old label.
- Line 464, `companies that raised` — **blocker**; section 13 retains the old lead-time
  feasibility deliverable. Section 13 is explicitly out of scope.
- Lines 514–515, `precision`, `readiness`, `raised` — **blocker**; phase 5 is still completed by
  demonstrating funding-event prediction. Section 13 is explicitly out of scope.
- Line 520, `precision ... readiness` — **blocker**; productisation still depends on the obsolete
  prediction metric. Section 13 is explicitly out of scope.
- Line 528, `readiness ranking` — **blocker**; the risk register says the product was reframed
  around the very model this task says was the wrong task.
- Line 529, `Readiness ... predicted` — **blocker**; the risk register still calls failure to
  predict readiness fatal and says the digest is otherwise unrankable.

#### Decision needed

Option 1 — expand task 017 so the same reconciliation also covers the stale hits in sections 5,
8, 9 and 13. Retire the funding-clock/readiness-prediction language, preserve the weight-0 fact
as historical context where useful, treat the named readiness fields as dossier evidence, remove
the “Entering the window” dependency, and rewrite the phase/risk statements around shortlist
quality and meeting conversion. **Recommended:** these are direct consequences of the already
approved product reframe, and leaving them for a later task defeats this task's stated purpose.

Option 2 — declare the listed passages intentionally stale and exempt them from criteria 7–8.
This keeps the current narrow file scope but leaves `PRD.md` internally contradictory after a
task named product reframe reconciliation.

No source document or implementation file has been changed.
