# 006 — Typed source health tracking

**Status:** complete
**Branch:** task/006-source-health-columns
**Depends on:** 004 merged. Independent of 005 — the two touch disjoint files.

---

## Intent

Task 004 records source health as a JSON document serialised into `source.health_status`,
which is a `VARCHAR` column (`models.py` declares `health_status: str`; migration
`f9fda2306f8a` emits `sqlmodel.sql.sqltypes.AutoString()`).

`PRD.md` section 10 requires that three consecutive connector failures escalate to the digest
and to an alert. That is a numeric comparison and it must be expressible in SQL. Against a
VARCHAR it requires a cast that throws on any non-JSON value, including every row written
before task 004.

It also diverges from the schema's own convention. Every other structured field is JSONB, and
`tests/test_models.py::test_postgres_json_fields_use_jsonb` enumerates exactly those four —
so a fifth JSON-bearing field stored as text sits outside the test written to catch this.

The failure mode is silent. Nothing errors; the string round-trips correctly. It surfaces
only when escalation is built and returns nothing.

---

## Scope

Replace the JSON-in-VARCHAR arrangement with typed columns. **JSONB is not the fix here** —
the one query that matters is an integer comparison, and a plain integer column is cheaper,
indexable and self-documenting.

Target shape for `source`:

| Column | Type | Null | Default | Purpose |
|---|---|---|---|---|
| `health_status` | VARCHAR + CHECK | no | `'unknown'` | Current state, constrained to `'healthy'`, `'failed'`, `'unknown'` |
| `consecutive_failures` | INTEGER | no | `0` | Reset to 0 on success, incremented on failure |
| `last_error` | TEXT | yes | — | Message from the most recent failure |
| `last_failure_at` | TIMESTAMPTZ | yes | — | When the most recent failure occurred |

`last_success_at` already exists and is unchanged.

The CHECK constraint follows the existing pattern in `ReviewEvent.action`.

---

## Out of scope

- Digest escalation itself. This task makes escalation *expressible*; it does not build it.
- A source health history table. Current state plus a counter satisfies the PRD. Retaining
  every health transition is a larger design question and would be its own task.
- Any change to the orchestrator's failure-isolation behaviour, which is correct.
- Any change to connectors, storage, provenance or the scoring model.
- Backfill of existing rows. The table is empty in every environment.

---

## Acceptance criteria

1. `src/core/models.py` `Source` declares the four columns as specified above, with
   `health_status` carrying a `CheckConstraint` restricting it to `'healthy'`, `'failed'`,
   `'unknown'`, named following the existing convention (`ck_source_health_status`).

   These three values match what `orchestrator.py` already writes, plus the `'unknown'` seed
   used in `tests/test_orchestrator.py::_source`. Today those live in three places with two
   different shapes — a bare string in the fixture, JSON elsewhere. The CHECK constraint makes
   the vocabulary single-sourced and unrepresentable-if-wrong.

2. A new Alembic migration exists with `down_revision = 'f9fda2306f8a'`. The initial migration
   is **not** edited — it is already applied and immutability of applied migrations is the
   same principle as immutability of raw docs.

3. The full round-trip is demonstrated against Neon, with output shown for each step:
   `alembic upgrade head`, confirmation the four columns exist with correct types via
   `information_schema.columns`, `alembic downgrade -1`, confirmation the three new columns are
   gone and `health_status` survives, `alembic upgrade head` again.

4. The orchestrator writes the typed columns rather than a serialised document. Specifically:
   on connector success, `health_status = 'healthy'`, `consecutive_failures = 0`,
   `last_success_at` set. On failure, `health_status = 'failed'`, `consecutive_failures`
   incremented,
   `last_error` and `last_failure_at` set.

5. No JSON is written into `health_status`. Demonstrate by quoting the orchestrator's
   assignment statements. `json` should no longer be imported by `orchestrator.py` unless it
   is used for something unrelated.

5a. **`_failure_count` and its silent exception handler are deleted.** The current
   implementation is:

   ```python
   def _failure_count(health_status: str) -> int:
       try:
           health = json.loads(health_status)
       except (json.JSONDecodeError, TypeError):
           return 0
   ```

   This returns 0 on any unparseable value, silently resetting the escalation counter. A
   source that has failed nine times escalates never if its health value is written by
   anything but this module, and nothing logs that it happened. `AGENTS.md` lists silently
   swallowing an exception as a forbidden pattern.

   With a typed integer column there is nothing to parse and no exception to swallow.
   Incrementing becomes `source.consecutive_failures += 1`. Do not replace the try/except with
   a logged variant — remove the parsing entirely.

6. A test asserts that after three simulated consecutive failures of one connector,
   `consecutive_failures == 3`, and that a subsequent success resets it to `0` and sets
   `health_status` to `'healthy'`.

7. A test asserts the escalation predicate is expressible as a plain filter — that querying
   sources with `consecutive_failures >= 3` returns the failing source and not a healthy one.
   This is the criterion the task exists for.

7a. A test asserts that a source whose `health_status` holds an unexpected value cannot be
   written at all — the CHECK constraint rejects it. This replaces the defensive parsing with
   a database guarantee.

8. `tests/test_models.py::test_postgres_json_fields_use_jsonb` still lists exactly four JSON
   columns and still passes. `health_status` must not appear in it.

9. Task 004's existing failure-isolation tests still pass unmodified. If any needed changing,
   say which and why — a test changing to accommodate a schema fix deserves scrutiny.

10. `uv run pytest` passes; state the count before and after. `uv run ruff check .` passes.

11. `PROGRESS.md` gains a session entry. No new ADR is required — this restores the schema's
    existing convention rather than establishing a new one. If you believe an ADR is warranted,
    raise it as a blocker rather than writing one.

---

## Files expected to change

```
src/core/models.py                  Source gains three columns and a CheckConstraint
migrations/versions/<new>.py        new revision, down_revision f9fda2306f8a
src/connectors/base.py              orchestrator health recording (or wherever 004 put it)
tests/test_models.py                assertions for the new columns
tests/<004's orchestrator test>     consecutive-failure and reset coverage
PROGRESS.md                         session entry
```

---

## Risks

- **Editing the applied migration instead of adding one.** Criterion 2 exists because it is
  the tempting shortcut and it breaks every environment already at head.
- **Reaching for JSONB out of habit.** It would work and it would be worse. The requirement is
  an integer comparison; give it an integer.
- **Loosening a task-004 test to accommodate the change.** Criterion 9 asks for this to be
  declared. A schema fix should not require weakening an assertion about failure isolation.
  Note that `tests/test_orchestrator.py::_health` currently does `json.loads(...)` and will
  need rewriting — that is expected and is not a loosening.
- **Preserving `_failure_count` "just in case".** Defensive parsing of a typed integer column
  is not defence, it is a place for the counter to silently reset. Criterion 5a requires
  deletion, not hardening.
- **Scope creep into escalation.** Escalation is a digest feature and does not exist yet. This
  task ends when the predicate is queryable and tested.
