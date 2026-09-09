# docs/tasks/ — task specifications

The unit of work in this project. Claude writes these; Codex implements against them; Claude
reviews the result against the acceptance criteria.

This replaces the numbered prompts in `docs/CODEX_KICKOFF.md`, which is now historical.

---

## Naming

`NNN-slug.md`, zero-padded, monotonically increasing. Numbers are never reused, even if a task
is abandoned. Abandoned tasks stay in place with `Status: abandoned` and a reason.

Task numbers 001–004 were executed as chat prompts before this convention existed. They are
recorded retrospectively in `PROGRESS.md`, not as task files.

---

## Required sections

Every task file has exactly these, in this order:

```
# NNN — Title

**Status:** proposed | accepted | in progress | blocked | complete | abandoned
**Branch:** task/NNN-slug
**Depends on:** task numbers, or "none"

## Intent
Why this exists. One paragraph. What becomes possible that isn't today.

## Scope
What to change. Specific enough that "done" is unambiguous.

## Out of scope
What NOT to touch. Prevents drift. At least one entry — if nothing is out of
scope, the task is too big.

## Acceptance criteria
Numbered, testable, independently checkable. See the verifiability rule below.

## Files expected to change
A list. Codex touching files outside it must say so and why.

## Risks
What could go wrong or be got subtly wrong.

## Blockers and questions
Empty at creation. Codex appends here. See the blocker protocol below.
```

---

## The verifiability rule

**Acceptance criteria must be checkable from artifacts that are cheap to paste into a chat.**

Claude's repository access is read-only, synced manually, and pinned to `main`. Work in
progress on a task branch is therefore invisible to Claude until merged. Review before merge
depends entirely on what can be reported.

So a criterion is well written if it can be verified by: a test name plus its assertion, a
command's output, a file existing or not existing, a specific line of a config file, or a
short quoted definition.

A criterion is badly written if verifying it requires reading three hundred lines of
implementation.

| Bad | Good |
|---|---|
| The rate limiter works correctly | `tests/test_storage.py` contains a test proving two requests to the same domain are separated by the configured interval, and one proving different domains are not serialised |
| The PRD is updated | `PRD.md` section 8 no longer contains the string "12–20" and the timing component weight is 0 |
| Scoring is sensible | Given the fixture in `tests/fixtures/scoring_cases.json`, computed totals match expected within 1 point |

Write criteria you could check over the phone.

---

## The blocker protocol

Codex cannot reach Claude directly, and Claude cannot see task branches. When Codex hits
something needing a product or architecture decision, the task file itself is the channel.

1. Codex appends to the **Blockers and questions** section of the task file: what it hit, what
   it needs decided, and the options it can see with a recommendation.
2. Codex sets `Status: blocked`.
3. Codex commits **only the task file** directly to `main`. Documentation commits to `main` are
   permitted by `AGENTS.md`; the code stays on the task branch, untouched.
4. Codex stops work on that task.
5. The human syncs the repository context.
6. Claude sees the blocker on `main`, decides, and amends the task file.
7. Codex pulls `main`, reads the decision, sets `Status: in progress`, and resumes.

This means a blocked task is visible to Claude without merging unfinished code, and the
question and its answer both end up in version control next to the work.

**Codex must never resolve a product or architecture question by choosing for itself and
noting it as an assumption.** Assumptions in `PROGRESS.md` are for gaps discovered after the
fact. A question known at the time is a blocker.

---

## Completion reporting

When Codex believes a task is done, before any merge it reports:

1. Each acceptance criterion, numbered, with **met / not met / partially met** and the
   specific evidence (test name, output line, file path).
2. Full `uv run pytest` output.
3. Full `uv run ruff check .` output.
4. Any file changed that was not in **Files expected to change**, with the reason.
5. Anything it chose not to do, and why.

Partially met is an acceptable answer. Silently rounding it up to met is not.

The human relays this to Claude for pre-merge review. After merge and sync, Claude verifies
the repository against the same criteria — the second pass catches what a self-report
naturally glosses.

---

## Merge policy

Review cost should match revert cost. Two tracks:

**Documentation-only tasks** — no change under `src/`, `tests/`, `migrations/` or `config/`.
Codex commits to the task branch, merges to `main`, and pushes without waiting. Claude reviews
the synced `main` afterwards and any correction is a follow-up commit. Reverting prose is
trivial, and criteria of the form "file X contains exactly this text" are verified far more
reliably against the repository than against a self-report.

**Everything else** — any change to code, schema, migrations or configuration. Codex commits
to the task branch and **stops**. It reports against the acceptance criteria; Claude reviews;
only then does it merge and push. A bad migration on `main` is expensive to unwind, and code
criteria usually depend on reading the implementation rather than matching text.

If a task described as documentation-only turns out to need a code change, that is a blocker,
not a judgement call. Stop and follow the blocker protocol.

**Corrections are always fix-forward.** Add a commit, or `git revert` a merged one. Never
rewrite pushed history — `AGENTS.md` forbids it, and a rebased `main` silently invalidates
every synced context Claude holds.

---

## Task sizing

One concern per task. If a task's acceptance criteria span two pipeline layers, split it.

A task that cannot be verified by a test or an inspectable artifact is not ready to be
accepted.
