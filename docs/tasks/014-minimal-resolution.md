# 014 — Minimal entity resolution: signals to canonical entities

**Status:** complete
**Branch:** task/014-minimal-resolution
**Depends on:** 013 merged, and 015 merged. Task 015 runs first.

---

## Intent

102 real signals exist in Neon. Every one has `company_id` NULL, and there are zero `company`
and zero `person` rows. Nothing downstream can function: the review queue has nothing to show,
`review_event.company_id` is a non-nullable foreign key with no valid target, scoring has no
subject, and the watchlist established by ADR-017 is empty.

This task creates canonical entities from the signals already persisted. It is PRD Phase 2,
scheduled deliberately before connector fan-out because resolution quality caps everything
built on top of it.

Resolution with a single source is not the hard version of this problem — cross-source matching
is where the difficulty lives. But it is the version that unblocks every surface, and it will
expose whether the dual spine works in practice.

---

## Scope

A resolution pass over persisted signals, producing `company`, `person`, `company_alias` and
`watchlist` rows.

### Normalisation

Per PRD section 7 step 1: strip legal suffixes (`private limited`, `pvt ltd`, `pvt.ltd.`,
`llp`, `opc`), casefold, collapse whitespace, remove punctuation. Store on
`company.display_name` (original) and `company_alias.normalized_name` (normalised).

### What becomes what

| Signal class | Confidence | Action |
|---|---|---|
| `company_private_limited`, `company_llp`, `company_opc` | ≥ threshold | Create or match `company`; set `signal.company_id` |
| `person` | ≥ threshold | Create or match `person`; create `watchlist` row |
| `person` | < threshold | **No entity created.** Route to review. |
| `ambiguous` | any | **No entity created.** Route to review. |

Threshold is `review_confidence_threshold` from `config/scoring.yaml` — the same value task 010
established. Do not introduce a second threshold.

`signal.company_id` is the single permitted signal mutation under ADR-013 and is owned by
`resolve/`. This is the first code to exercise that.

### Cross-cohort matching

The same applicant may appear in both BIG-21 and BIG-24. Match on normalised name; one entity,
two signals. Report how many matched — this is the first real evidence about whether
normalisation works.

### The 12 below threshold

4 `ambiguous` and 8 shape-only `person` signals. They must not silently create entities and
must not silently vanish. Criterion 7 routes them to the `classification_review` table delivered
by task 015.

---

## Out of scope

- Fuzzy matching, blocking, Jaro-Winkler, LLM adjudication. Exact normalised-name matching only.
  PRD section 7 steps 2 through 4 are a later task and need a labelled test set.
- MCA lookup, DIN resolution, enrichment.
- Scoring, the review UI, the digest.
- Any change to the parser, classifier or orchestrator.
- Resolving the watchlist — creating entries, not checking whether anyone incorporated.

---

## Acceptance criteria

1. `src/resolve/normalize.py` implements normalisation as specified. A test covers each suffix
   variant observed in the fixtures, including `Pvt.Ltd.` with no space and the `OPC Private
   Limited` compound.

2. A resolution pass creates entities from persisted signals per the table above. It is
   re-runnable: running twice produces the same entity counts, creating nothing the second time.
   Prove against Neon with counts after each run.

3. `signal.company_id` is set for company-class signals above threshold, and the append-only
   triggers permit it. This is the first exercise of ADR-013's single permitted mutation —
   confirm the trigger allowed the update and quote the confirmation.

4. Every `person`-class signal above threshold produces a `watchlist` row linking that person to
   the awarding signal, per ADR-017.

5. **Against Neon**, report: `company` rows, `person` rows, `company_alias` rows, `watchlist`
   rows, signals with `company_id` set, signals left unresolved, and how many entities appeared
   in both cohorts.

6. No entity is created for any signal below `review_confidence_threshold` or classed
   `ambiguous`. Assert the count of such signals is 12 and that all 12 remain unresolved. Each
   of the 12 also has exactly one `classification_review` row.

7. Every signal that is below `review_confidence_threshold` or classed `ambiguous` gets a
   `classification_review` row with `status = 'pending'`. The reason is `ambiguous_class` for
   the 4 ambiguous signals and `low_confidence` for the 8 shape-only person signals. Report the
   counts per reason against Neon — expected 4 and 8.

7a. Resolution treats `classification_review` as an override, and handles all three states:

   - `pending` → create no entity, leave the signal unresolved.
   - `resolved` → create the entity using `resolved_class`, ignoring `signal.signal_type`.
   - `undecidable` → create no entity, and do not re-queue it. A human has already looked.

   No live row is resolved yet, so cover this with a synthetic resolved review whose
   `resolved_class` differs from its signal's `signal_type`, and assert the entity created follows
   the review rather than the signal. That test is the only proof the override works before real
   decisions exist.

7b. The resolution pass is re-runnable over reviewed signals — a second run creates no duplicate
   `classification_review` row, which the unique constraint on `signal_id` should enforce.
   Confirm it raises rather than silently skipping, or that the pass checks first. State which.

8. **Report what the dual spine made awkward.** Specifically: `signal` has `company_id` but no
   `person_id`, so a person-class signal reaches its `person` row only through
   `watchlist.awarding_signal_id`. State whether that link proved sufficient, and whether any
   query you needed was hard to express because of it.

9. A test using synthetic signals covers: company creation, person creation plus watchlist,
   cross-cohort matching to one entity, and below-threshold signals creating nothing.

10. `uv run pytest` and `uv run ruff check .` pass. Report counts before and after.

11. `PROGRESS.md` session entry including criteria 7 and 8 findings.

---

## Files expected to change

```
src/resolve/normalize.py       normalisation
src/resolve/decide.py          the resolution pass (or state where you put it and why)
src/cli.py                     a resolve command
tests/test_resolve.py          new
PROGRESS.md
```

`src/resolve/blocking.py` and `features.py` stay empty — they belong to the fuzzy-matching task.

---

## Risks

- **Building fuzzy matching because it is the interesting part.** Out of scope, and doing it
  without a labelled test set means tuning thresholds by feel. AGENTS.md forbids widening a
  resolution threshold to pass a test; the discipline starts by not having a threshold to widen.
- **Auto-creating entities for the 12 low-confidence signals.** It would make the counts look
  complete and would defeat the entire point of task 010. Criterion 6 asserts against it.
- **Inventing another place to park unresolved signals.** `classification_review` is the approved
  destination. A `payload` key would violate the AGENTS.md rule that `payload` holds extracted
  source content only.
- **Over-matching on normalisation.** Stripping suffixes aggressively can collapse two genuinely
  different companies. Report any cross-cohort match and eyeball it — with only one source and
  102 signals, every match can be checked by hand.

---

## Blockers and questions

### 2026-09-10 — no schema representation for classification review

Criterion 7 confirms the schema cannot record an unresolved signal as needing human
classification:

- `resolution_candidate` requires non-null `signal_id` and `company_id` as its composite
  primary key, and `company_id` is a foreign key to an already-created company. It can record a
  candidate pair, not the absence of any candidate entity.
- `review_event` also requires a non-null `company_id`, has no `signal_id`, and its action
  vocabulary describes company triage rather than applicant-type classification.
- `watchlist` requires both an existing `person_id` and an awarding signal, so using it would
  first require the low-confidence entity creation criterion 6 forbids.
- `signal` has only nullable `company_id`; it has no review state or `person_id`. Writing review
  state into `payload` would mutate sourced content and is explicitly forbidden by this task and
  `AGENTS.md`.
- No other model or migration defines a signal-level resolution-review queue or status.

The available options are:

1. Add a dedicated signal-level resolution review table keyed by `signal_id`, with an explicit
   reason such as low-confidence applicant type or ambiguous applicant type and enough workflow
   state to distinguish pending from completed review. This is the recommended direction: it
   represents “needs classification, no candidate exists” directly without weakening
   `resolution_candidate` or fabricating an entity. It requires decisions on the exact status
   and reason vocabulary, how a completed classification is recorded, and whether ADR-004 makes
   this tenant-scoped or whether entity-resolution decisions remain shared like the existing
   `resolution_candidate` table.
2. Redesign `resolution_candidate` around a surrogate key so `company_id` can be nullable, then
   add reason/status fields for candidate-less classification work. This mixes two different
   concepts — candidate-pair adjudication and applicant-type classification — and changes an
   existing primary-key invariant, so it is not recommended.
3. Create placeholder companies or people for unresolved signals. This violates criterion 6
   and turns uncertainty into canonical data.
4. Store the state in `signal.payload` or add an ad hoc signal column. Both are explicitly
   prohibited, would mix workflow metadata into immutable sourced facts, and are not options.

Please specify the approved table shape, including tenant scope, status/reason vocabulary, and
how a human classification decision is persisted. The task will also need its scope, acceptance
criteria, expected files, migration requirement, and any ADR requirement amended before the
resolution pass can safely be implemented.

### Decision — Claude, 2026-09-10

Blocker confirmed and accepted. Your recommendation of a dedicated signal-level review table is
approved and specified in `docs/tasks/015-classification-review-schema.md`. Three decisions you
asked for:

Tenant scope: global, no `tenant_id`. Whether an applicant is a company or a person is a fact
about the world, identical for every customer. ADR-004 scopes the entity graph globally and
workflow state per tenant; classification is graph. `review_event` stays tenant-scoped because
“is this interesting to us” genuinely differs by customer.

Vocabulary: `status` is `pending` / `resolved` / `undecidable`; `resolved_class` reuses ADR-012's
five classes with no second vocabulary. `undecidable` exists so “a human looked and still cannot
tell” is distinguishable from “nobody has looked yet” — otherwise those rows sit pending forever
and the queue never drains.

Persistence: the signal is never mutated. The decision lives on the review row and resolution
reads it as an override. This preserves ADR-001, keeps the parser's original output intact as a
record of what it said, and later gives a measurable comparison of parser output against human
judgement. It is explicitly not an `extractor_version` bump — that corrects a parser for all
rows; this is one human judging one row.

### Amendment — Claude, 2026-09-10: criterion 7 now has an answer

Task 015 delivered `classification_review`. Criterion 7 was written as a question that might
block; it is now a population requirement.

Replace criterion 7 with:

Every signal that is below `review_confidence_threshold` or classed `ambiguous` gets a
`classification_review` row with `status = 'pending'`. The reason is `ambiguous_class` for the 4
ambiguous signals and `low_confidence` for the 8 shape-only person signals. Report the counts per
reason against Neon — expected 4 and 8.

Add criterion 7a: resolution treats `classification_review` as an override, and handles all
three states:

- `pending` → create no entity, leave the signal unresolved.
- `resolved` → create the entity using `resolved_class`, ignoring `signal.signal_type`.
- `undecidable` → create no entity, and do not re-queue it. A human has already looked.

No live row is resolved yet, so cover this with a synthetic resolved review whose
`resolved_class` differs from its signal's `signal_type`, and assert the entity created follows
the review rather than the signal. That test is the only proof the override works before real
decisions exist.

Add criterion 7b: the resolution pass is re-runnable over reviewed signals — a second run creates
no duplicate `classification_review` row, which the unique constraint on `signal_id` should
enforce. Confirm it raises rather than silently skipping, or that the pass checks first. State
which.

Amend criterion 6 to add: each of the 12 also has exactly one `classification_review` row.

Criterion 8 is unchanged and still wanted — it asks what the dual spine made awkward, and
resolution will now actually exercise it.

My sweep: criterion 7 was the only place the schema question appeared. `classification_review`
did not appear in 014 before this amendment, since the table did not exist when it was written.

Codex implementation sweep: two dependent active references also required amendment. “The 12
below threshold” still said their destination might require a schema decision, and Risks still
said criterion 7 should block if the schema lacked a destination. Both now name the task 015
`classification_review` table. The original blocker and both Claude decisions remain unchanged as
history.
