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
**Documentation impact:** none | structural | semantic

## Intent
Why this exists. One paragraph. What becomes possible that isn't today.

## Interpretations
Every choice made where the request was ambiguous, including the chosen interpretation and what
the alternative would have produced. "None; the request was unambiguous" is valid. This heading
must appear immediately after `## Intent`.

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

For tasks numbered 018 onward, documentation-impact metadata is mandatory. A `structural` task
also declares `**Affected paths:**`; a `semantic` task also declares `**Sweep terms:**`. The
classification is reviewed by the spec auditor, not inferred by the documentation checker. See
**Documentation impact sweeps** below for the semantic requirements.

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
3. Codex commits **only the task file** directly to local `main`; the code stays on the task
   branch, untouched. It asks for explicit push authorization in the current session and reports
   that the blocker is not remotely visible until that push is authorized. The blocker exception
   does not permit any other task work directly on `main`.
4. Codex stops work on that task.
5. The human syncs the repository context.
6. Claude sees the blocker on `main`, decides, and amends the task file.
7. Claude, having amended the task file, performs the durable amendment and cross-document sweep
   below before implementation resumes.
8. Codex pulls `main`, reads the decision, sets `Status: in progress`, and resumes.

This means a blocked task is visible to Claude without merging unfinished code, and the
question and its answer both end up in version control next to the work.

**Codex must never resolve a product or architecture question by choosing for itself and
noting it as an assumption.** Assumptions in `PROGRESS.md` are for gaps discovered after the
fact. A question known at the time is a blocker.

---

## Amending a specification

Any user/chat change to scope, terminology, an interpretation, or a criterion must be copied into
the task artifact before implementation begins or resumes and before review. Record its date,
durable wording or faithful decision summary, affected scope or criteria, and changed sweep
terms.

For a terminology change, collect all known synonyms and hits into one amendment pass. Search the
declared cross-document scope, apply only mechanically equivalent wording substitutions without
escalation, and record one complete resweep before resuming. A replacement that changes product
meaning is a blocker. This consolidation prevents one blocker round trip per synonym without
turning wording authority into product authority.

Both blockers raised so far had this same cause. Task 006: criterion 1's status vocabulary
was corrected to match the implementation while criteria 4 and 6 kept the old values, so a
CHECK constraint built from criterion 1 would have rejected what criteria 4 and 6 required.
Task 007: `PRD.md` section 8 was replaced correctly while section 9 kept describing the
component that had just been deleted.

Exact-text criteria verify precisely what they name and are blind to everything that
depends on it. The sweep is what closes that gap.

Report the sweep with the amendment: which term, which lines matched, what was done with
each.

---

## Documentation impact sweeps

For Task 018 onward:

- `none` means no documentation dependency analysis is required beyond recording and reviewing
  the classification.
- `structural` means files or headings move without changing meaning; list every affected path in
  `**Affected paths:**`.
- `semantic` means wording, policy, terminology, or meaning changes. Declare search terms and all
  known synonyms in `**Sweep terms:**`. Give an included or excluded-with-reason disposition for
  `PRD.md`, `docs/DECISIONS.md`, the current-state block of `PROGRESS.md`, `docs/CONTEXT.md`, and
  the task file itself; list additional dependents; and record every pre-Gate-1 search hit with a
  disposition.

The spec writer performs this declaration and sweep before Gate 1. The spec auditor fails an
incomplete declaration and reviews the chosen classification. Genuinely identical or irrelevant
hits may share one disposition only when the entry enumerates every grouped file and line; an
unnumbered "other matches are fine" bucket is incomplete.

The dependency-free checker validates only configured mechanical structure and paths. It cannot
infer the semantic classification, judge prose consistency or sweep-disposition quality or
completeness, or ban unconfigured or context-valid historical terms. The spec auditor and
reviewer own those semantic judgments; a passing checker is not evidence that the dispositions
are meaningful or complete.

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

### Canonical verification for documentation-only tasks

`docs/tasks/README.md` owns this policy. When the final diff changes nothing under `src/`,
`tests/`, `migrations/`, or `config/` and adds no executable tooling, the implementer runs
`uv run pytest` and `uv run ruff check .` once after the last substantive change. The task's
`PROGRESS.md` session entry records the exact commands, exit codes, test count or concise output,
and that the run covered the final substantive diff. The reviewer and orchestrator reuse that
evidence while the diff remains relevantly unchanged.

Run both commands again and replace the evidence, recording why, if relevant content changed
after the run, evidence is missing or stale, either command failed, or a reviewer identifies a
concrete verification gap. Editing only the evidence record does not invalidate the run.
Non-documentation tasks retain their normal verification behavior and reporting requirements.

---

## Merge policy

All task work uses a task branch. Ordinary documentation-only work gets one independent pre-merge
reviewer. A diff matching the canonical list below gets two reviewers with independent context.
Reviewer disagreement on any criterion is a hard blocker. After review and the quality gates,
**every diff stops for explicit human merge approval in the current session**.

<!-- CANONICAL HIGH-RISK LIST START -->
A diff requires two independent reviewers if it:

- changes `src/core/models.py`;
- changes any file under `migrations/`;
- changes `src/connectors/base.py`;
- changes `.codex/agents/orchestrator.toml`;
- changes `docs/AGENT_ARCHITECTURE.md`;
- amends `docs/DECISIONS.md`; or
- changes any numerical threshold, confidence value, or scoring weight in any path.
<!-- CANONICAL HIGH-RISK LIST END -->

Every push of `main` or a named branch requires explicit user authorization in the current
session. Merge permission and push permission are separate; neither implies the other unless the
user explicitly grants both together. A pull request is optional.

The implementer has task-scoped write authority only over the approved **Files expected to
change** list. The task file and `PROGRESS.md` must be listed if they will be edited. A needed path
outside that list requires a task amendment or a blocker before it is changed.

Do not dispatch the researcher for ordinary documentation editing, repository terminology sweeps,
or policy changes. Use it only for external web research, source audits, back-tests, dossier
assembly, or fetching external artifacts.

**Corrections are always fix-forward.** Add a commit, or `git revert` a merged one. Never
rewrite pushed history — `AGENTS.md` forbids it, and a rebased `main` silently invalidates
every synced context Claude holds.

---

## Behavioural tests and proxy tests

`conftest.py` blocks all network access, so some behaviour cannot be proven in the default
suite. A test may then verify a **proxy** rather than the behaviour itself.

Two exist today. `tests/test_migration_protections.py` asserts the migration file *defines*
the immutability triggers, not that they fire. The task-006 CHECK constraint test runs
against in-memory SQLite while production is Postgres.

Both are reasonable. Neither is coverage. Real behaviour was confirmed manually against
Neon, once, in a way nothing repeats.

Any task adding a proxy test must say so in its completion report, naming what is proven,
what is not, and how the real behaviour was verified. A proxy test presented as coverage is
a false green, and false greens are worse than absent tests because they stop anyone
looking.

These belong in an integration suite excluded from the default run, once CI exists.

---

## Task sizing

One concern per task. If a task's acceptance criteria span two pipeline layers, split it.

A task that cannot be verified by a test or an inspectable artifact is not ready to be
accepted.
