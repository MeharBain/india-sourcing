# 016 — Signal-to-person symmetry

**Status:** complete
**Branch:** task/016-signal-person-id
**Depends on:** 014 merged.

---

## Intent

Task 014's criterion 8 reported that `signal.company_id IS NULL` returns 37 rows when only 12
signals are genuinely unresolved. The other 25 are resolved *people*.

`signal` has `company_id` but no `person_id`, so a person-class signal reaches its `person` row
only via `watchlist.awarding_signal_id`. That conflates two different facts: *this signal names
this person*, and *this person is being monitored for incorporation*. The first is resolution;
the second is a watchlist, and ADR-017 gives it its own meaning.

The practical damage is that the obvious query for unresolved work is wrong by a factor of
three, and it is wrong silently. Every surface still to be built — digest, review queue,
monitoring — will reach for `company_id IS NULL` first.

This is cheap now, with one connector and 102 signals. It gets expensive with ten.

Secondly, `AGENTS.md` states that entity resolution has a labelled test set at
`tests/fixtures/resolution_pairs.json` and that changes to `resolve/` must not regress accuracy
on it. That file has never existed. Task 014 reported this rather than inventing figures. An
unenforceable rule in `AGENTS.md` is worse than no rule, because the next agent may fabricate
compliance.

---

## Scope

### 1. `signal.person_id`

Add `person_id`, nullable UUID FK to `person.id`, indexed — symmetric with `company_id`.

A CHECK ensures at most one is set: a signal resolves to a company or a person, never both.

`resolve/` owns it, exactly as it owns `company_id`.

### 2. The append-only trigger

`signal_append_only` currently protects every column except `company_id`. `person_id` must be
added to the permitted-mutation set, in the migration, not by editing the applied one.

ADR-013 permits `company_id` as the single mutation. This makes it two, for the same reason —
resolution attaches an entity after the fact. **ADR-013 must be amended** rather than
contradicted.

### 3. Unresolved becomes expressible

`company_id IS NULL AND person_id IS NULL` returns exactly the genuinely unresolved signals.
Expected today: 12.

### 4. Backfill

25 person-class signals are already resolved with their link only in `watchlist`. Set their
`person_id` from `watchlist.awarding_signal_id`. This is a data operation, not a schema one —
report it separately from the migration.

### 5. The `AGENTS.md` fixture rule

Amend the testing section. The labelled set is required **when fuzzy matching is implemented**,
not now — exact normalised matching needs no accuracy metric. Reword so the rule becomes true,
and state that the fixture must be created by whichever task introduces fuzzy matching.

---

## Out of scope

- Fuzzy matching, blocking, scoring. Still deferred.
- Removing or changing `watchlist`. It keeps its ADR-017 meaning; it simply stops being the
  only path from signal to person.
- Any change to the parser, classifier or orchestrator.
- Creating `resolution_pairs.json`. Criterion 10 makes it a documented future requirement.

---

## Acceptance criteria

1. `Signal` declares `person_id` as a nullable indexed FK to `person.id`, with a CHECK named per
   convention ensuring `company_id` and `person_id` are not both non-null. State the
   expression.

2. New Alembic migration, `down_revision` at the current head. Report the head and confirm no
   applied migration was edited. The migration also replaces the `signal_append_only` trigger so
   `person_id` joins `company_id` as permitted to change.

3. Full Neon round-trip with output at each step, including the trigger definition after upgrade
   showing both `company_id` and `person_id` absent from the protected columns.

4. A test proves updating `person_id` on an existing signal succeeds, and that updating
   `signal_type` still raises. Both directions, or the trigger change is unverified.

5. A test proves the CHECK rejects a signal with both `company_id` and `person_id` set.

6. Resolution sets `person_id` for person-class signals above threshold, alongside the existing
   `watchlist` row. Both, not either.

7. **Backfill.** The 25 already-resolved person signals get `person_id` populated from their
   `watchlist` rows. Report the count updated, and confirm every `watchlist` row's person
   matches the signal's new `person_id`.

8. **Against Neon**, report all four counts: signals with `company_id`, with `person_id`, with
   neither, and with both. Expected 65, 25, 12, 0.

9. A second resolution run changes nothing. Report counts before and after.

10. `AGENTS.md`'s testing section is reworded so the `resolution_pairs.json` rule is true as
    written — the labelled set is required by whichever task introduces fuzzy matching, and does
    not exist yet. Quote the new wording.

11. **ADR-013 amended** to record that resolution owns two permitted signal mutations,
    `company_id` and `person_id`, with the same reasoning. Do not write a new ADR that silently
    contradicts an existing one.

12. `uv run pytest` and `uv run ruff check .` pass. Report counts before and after.

13. `PROGRESS.md` session entry, including the backfill result.

---

## Files expected to change

```
src/core/models.py                  Signal.person_id and CHECK
migrations/versions/<new>.py        column, index, CHECK, trigger replacement
src/resolve/decide.py               set person_id during resolution
src/cli.py                          backfill command or step
tests/test_models.py                CHECK coverage
tests/test_migration_protections.py trigger permits person_id
tests/test_resolve.py               person_id set alongside watchlist
AGENTS.md                           testing section wording
docs/DECISIONS.md                   ADR-013 amended
PROGRESS.md
```

---

## Risks

- **Editing the applied `signal_append_only` trigger migration.** It is at head in Neon. Replace
  the trigger in a new revision; criterion 2 requires it.
- **Setting `person_id` instead of the watchlist row rather than as well.** They mean different
  things. Criterion 6 says both.
- **Writing a new ADR that contradicts ADR-013.** ADR-013 states `company_id` is *the single*
  permitted mutation. That sentence becomes false. Amend it; criterion 11 exists because adding
  ADR-023 alongside a now-wrong ADR-013 leaves the repository self-contradictory.
- **Backfilling with a bare UPDATE that the trigger blocks.** The trigger must be replaced first,
  in the same migration, or the backfill fails — which is the correct order and worth confirming
  rather than discovering.
- **Treating the fixture rule as trivial.** An unenforceable rule invites fabricated compliance.
  Codex reported the absence honestly; the next agent might not.

---

## Blockers and questions

*(none at creation)*
