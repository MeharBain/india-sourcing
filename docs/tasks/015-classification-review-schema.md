# 015 — Classification review schema

**Status:** complete
**Branch:** task/015-classification-review-schema
**Depends on:** 013 merged.

**Execution order: this runs before task 014**, which is blocked on it. Task numbers are
monotonic, not an execution sequence.

---

## Intent

Task 014 confirmed by inspection that no existing table can represent *a signal awaiting human
classification*:

- `resolution_candidate` is keyed `(signal_id, company_id)` with a non-null `company_id`. It
  answers "which existing company is this signal about?" It cannot answer "is this a company at
  all?"
- `review_event` is keyed to `company_id`, non-null, and is tenant-scoped deal triage.
- `signal.signal_type` is a fact column on an append-only table and cannot be corrected in
  place.

Twelve signals need this state today — 4 classed `ambiguous` and 8 `person` by name shape at
0.50 confidence. Task 010 deliberately routed them to review rather than guessing, on the
grounds that a confident misclassification silently corrupts the watchlist. Without somewhere
to put them, that decision has nowhere to land.

---

## Design decisions, already made

These are settled. Implement them; do not re-litigate.

### Global, not tenant-scoped

`classification_review` carries **no `tenant_id`**. Whether an applicant is a company or a
person is a fact about the world, identical for every customer. ADR-004 scopes the shared
entity graph globally and workflow state per tenant; classification is graph.

`review_event` remains tenant-scoped and is unaffected — "is this interesting to us" is
genuinely a per-tenant question.

### The signal is never mutated

The human decision is recorded on the review row, not written back to `signal.signal_type`.
Resolution reads the review row as an **override** when one exists.

This preserves ADR-001, keeps the parser's original output intact as a record of what it
actually said, and yields a measurable comparison between parser output and human judgement
later. It is explicitly **not** an `extractor_version` bump — that mechanism corrects a parser
for all rows; this is one human judging one row.

### Vocabulary reuses ADR-012

`resolved_class` is constrained to the same five classes ADR-012 defines. Do not invent a
second vocabulary.

---

## Scope

One table, one migration, one ADR.

| Column | Type | Null | Default | Notes |
|---|---|---|---|---|
| `id` | UUID | no | uuid4 | |
| `signal_id` | UUID FK → `signal.id` | no | — | **Unique.** One review per signal. |
| `status` | VARCHAR + CHECK | no | `'pending'` | `'pending'`, `'resolved'`, `'undecidable'` |
| `reason` | VARCHAR + CHECK | no | — | Why review was required: `'ambiguous_class'`, `'low_confidence'` |
| `resolved_class` | VARCHAR + CHECK | yes | — | One of ADR-012's five classes. Null unless `status = 'resolved'` |
| `reviewed_by` | VARCHAR | yes | — | Who examined the row |
| `reviewed_at` | TIMESTAMPTZ | yes | — | When the row was examined |
| `notes` | TEXT | yes | — | |
| `created_at` | TIMESTAMPTZ | no | `now()` | |

CHECK constraint names follow `ck_classification_review_*`, matching the existing convention.

`undecidable` exists because "a human looked and still cannot tell" is a real outcome that must
be distinguishable from "nobody has looked yet". Without it, undecidable rows sit in `pending`
forever and the queue never drains.

---

## Out of scope

- Populating the table. Task 014 does that.
- Reading the override during resolution. Task 014.
- Any UI.
- Touching `resolution_candidate` or `review_event`.
- A generalised polymorphic review queue. One subject type exists; generalise when a second
  appears, per AGENTS.md.

---

## Acceptance criteria

1. `ClassificationReview` in `src/core/models.py` matches the table above, with CHECK
   constraints on `status`, `reason` and `resolved_class`, and a unique constraint on
   `signal_id`.

2. A **consistency constraint** implements these three explicit state clauses as a table-level
   CHECK:

   ```sql
   (status = 'pending' AND resolved_class IS NULL
       AND reviewed_by IS NULL AND reviewed_at IS NULL)
   OR (status = 'resolved' AND resolved_class IS NOT NULL
       AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)
   OR (status = 'undecidable' AND resolved_class IS NULL
       AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)
   ```

   State the constraint expression. This prevents pending rows from carrying review metadata,
   resolved rows from omitting their decision or reviewer, and undecidable rows from losing who
   examined them and when.

3. New Alembic migration with `down_revision` pointing at the current head. Report the current
   head and confirm no existing migration was edited.

4. Full Neon round-trip with output at each step: `alembic upgrade head`, the new table's
   columns and constraints from `information_schema`, `alembic downgrade -1`, confirmation the
   table is gone, `alembic upgrade head` again.

5. Tests asserting each CHECK rejects an invalid value: a bad `status`, a bad `reason`, a bad
   `resolved_class`, and both directions of criterion 2's consistency rule.

5a. Tests assert each of the three states is accepted, and that these are rejected: an
    `undecidable` row with no `reviewed_by`, a `pending` row with a `reviewed_by`, and a
    `resolved` row with no `resolved_class`.

6. A test asserts the unique constraint on `signal_id` rejects a second review for the same
   signal.

7. `tests/test_models.py::test_postgres_json_fields_use_jsonb` still lists exactly four JSONB
   columns. This table has none.

8. **ADR-022**: signal classification review is a global, signal-scoped record that overrides
   rather than mutates `signal.signal_type`. Record the tenant-scope reasoning and the
   append-only reasoning, and state reversal conditions.

9. No table is populated and no resolution logic is written. Confirm `src/resolve/` is
   unchanged.

10. `uv run pytest` and `uv run ruff check .` pass. Report counts before and after.

11. `PROGRESS.md` session entry.

---

## Files expected to change

```
src/core/models.py                    ClassificationReview
migrations/versions/<new>.py          new revision
tests/test_models.py                  constraint coverage
docs/DECISIONS.md                     ADR-022
PROGRESS.md
docs/tasks/015-classification-review-schema.md   this file, committed
```

---

## Risks

- **Adding `tenant_id` out of habit.** Every other workflow table has one. This is not a
  workflow table. Criterion 8's ADR must state why.
- **Making `resolved_class` unconstrained text.** It would accept `"Person"`, `"person "`,
  `"individual"` and quietly fragment the vocabulary that ADR-012 exists to fix.
- **Skipping criterion 2.** Nullable resolution columns with no consistency rule permit a row
  marked resolved with no decision recorded. That is the review-queue equivalent of a silent
  failure, and nothing else would catch it.
- **Editing the applied migration.** Same rule as task 006 — add a revision, never modify one
  already at head.

---

## Blockers and questions

*(none at creation)*

### Amendment — Claude, 2026-09-10: consistency constraint was wrong

Criterion 2 as written bundles `resolved_class`, `resolved_by` and `resolved_at` into a single
rule keyed on `status = 'resolved'`. That was my error. Those columns mean different things:
`resolved_class` is the decision, while `resolved_by` and `resolved_at` record that a human
examined the row at all.

The consequence is that an `undecidable` row — someone looked and could not tell — cannot record
who looked or when. You then cannot re-surface it when better information arrives, and it
contributes nothing to the labelled dataset ADR-007 treats as an asset.

The table is empty and the branch unmerged, so this is free now and needs a data migration later.

Rename `resolved_by` → `reviewed_by` and `resolved_at` → `reviewed_at`. They apply to examination,
not decision. `resolved_class` keeps its name.

Replace criterion 2's constraint with three explicit state clauses:

```sql
(status = 'pending'     AND resolved_class IS NULL
    AND reviewed_by IS NULL     AND reviewed_at IS NULL)
OR (status = 'resolved'    AND resolved_class IS NOT NULL
    AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)
OR (status = 'undecidable' AND resolved_class IS NULL
    AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)
```

Add criterion 5a: tests assert each of the three states is accepted, and that these are rejected
— an `undecidable` row with no `reviewed_by`, a `pending` row with a `reviewed_by`, and a
`resolved` row with no `resolved_class`.

Amend the column table at lines 72–73 to match the new names, and update line 102.

My sweep: `resolved_by`/`resolved_at` appear at lines 72, 73 and 102, all amended above.
`undecidable` appears at 69, 79 and 80 — vocabulary unchanged, and line 79's rationale now holds
more fully than it did.
