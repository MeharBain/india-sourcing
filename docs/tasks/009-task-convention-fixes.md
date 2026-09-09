# 009 — Process fixes to the task convention

**Status:** proposed
**Branch:** task/009-task-convention-fixes
**Depends on:** 006 merged.

---

## Intent

Three gaps in `docs/tasks/README.md` surfaced during tasks 006 and 007. Each cost a round trip
or nearly did. All three are wording fixes to the convention document.

---

## Scope

`docs/tasks/README.md` only. Documentation.

### 1. The blocker protocol never says to push

Step 3 currently reads: *Codex commits **only the task file** directly to `main`.*

In task 006 Codex followed this exactly and reported `main is one commit ahead of
origin/main`. Nothing was pushed, so there was nothing for the human to sync and nothing for
Claude to read. The protocol's entire purpose is to make a blocked question visible without
merging unfinished code, and it fails at the last step.

### 2. Amending a specification has no sweep requirement

Task 006's blocker was caused by amending criterion 1 to match the orchestrator's real status
vocabulary while leaving criteria 4 and 6 on the old one. Task 007's blocker had the same root
cause in `PRD.md`: an edit in one place with dependents left stale elsewhere.

Two occurrences of one failure mode is a rule, not bad luck.

### 3. Nothing distinguishes a test that proves behaviour from one that proves a proxy

Task 004's migration-protection tests assert that the *migration file defines* triggers, not
that the triggers fire. Task 006's CHECK-constraint test runs against in-memory SQLite while
production is Postgres. Both had their real behaviour verified manually against Neon, once,
unrepeatably.

Neither is wrong given `conftest.py` blocks the network. But the distinction currently lives
only in Codex's prose, and a future reader sees green tests and assumes coverage.

---

## Out of scope

- Building the integration test suite. That is a real task and needs CI first.
- Retrofitting the distinction onto tasks 004 and 006. Already recorded in `PROGRESS.md`.
- `AGENTS.md`, `PRD.md`, or any other document.
- The stale `PRD.md` section 13 build plan — that is task 010.

---

## Acceptance criteria

1. In the blocker protocol, step 3 reads exactly:

   > 3. Codex commits **only the task file** directly to `main` **and pushes it**. Documentation
   >    commits to `main` are permitted by `AGENTS.md`; the code stays on the task branch,
   >    untouched. Pushing is not optional — an unpushed blocker is invisible to the human's
   >    sync and therefore invisible to Claude, which defeats the protocol.

2. A new step is inserted between the current steps 6 and 7, and subsequent steps renumbered:

   > 7. Claude, having amended the task file, sweeps that file for every term the amendment
   >    touched, in the same edit. See "Amending a specification" below.

3. A new section titled `## Amending a specification` appears immediately after the blocker
   protocol, reading:

   > Whenever a task specification is amended — by Claude resolving a blocker, or by anyone
   > correcting an error — the amendment is not complete until the whole file has been searched
   > for the term that changed.
   >
   > Both blockers raised so far had this same cause. Task 006: criterion 1's status vocabulary
   > was corrected to match the implementation while criteria 4 and 6 kept the old values, so a
   > CHECK constraint built from criterion 1 would have rejected what criteria 4 and 6 required.
   > Task 007: `PRD.md` section 8 was replaced correctly while section 9 kept describing the
   > component that had just been deleted.
   >
   > Exact-text criteria verify precisely what they name and are blind to everything that
   > depends on it. The sweep is what closes that gap.
   >
   > Report the sweep with the amendment: which term, which lines matched, what was done with
   > each.

4. A new section titled `## Behavioural tests and proxy tests` appears immediately before
   `## Task sizing`, reading:

   > `conftest.py` blocks all network access, so some behaviour cannot be proven in the default
   > suite. A test may then verify a **proxy** rather than the behaviour itself.
   >
   > Two exist today. `tests/test_migration_protections.py` asserts the migration file *defines*
   > the immutability triggers, not that they fire. The task-006 CHECK constraint test runs
   > against in-memory SQLite while production is Postgres.
   >
   > Both are reasonable. Neither is coverage. Real behaviour was confirmed manually against
   > Neon, once, in a way nothing repeats.
   >
   > Any task adding a proxy test must say so in its completion report, naming what is proven,
   > what is not, and how the real behaviour was verified. A proxy test presented as coverage is
   > a false green, and false greens are worse than absent tests because they stop anyone
   > looking.
   >
   > These belong in an integration suite excluded from the default run, once CI exists.

5. No other file changes.

6. `uv run pytest` passes at 53; `uv run ruff check .` passes.

7. `PROGRESS.md` session entry.

---

## Files expected to change

```
docs/tasks/README.md
PROGRESS.md
```

---

## Risks

- **Treating this as cosmetic.** Item 1 is the reason a blocked task can stall invisibly. It
  has already happened once.
- **Rewriting surrounding prose while editing.** Insert and replace only what the criteria
  name. The convention document is referenced by every future task and unreviewed drift in it
  propagates everywhere.

---

## Blockers and questions

*(none at creation)*
