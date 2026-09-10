# 021 — Close the Task 009 artifact

**Status:** proposed
**Branch:** task/021-close-task-009
**Depends on:** 020 merged
**Documentation impact:** semantic
**Sweep terms:** `Task 009`; `task 009`; `009-task-convention-fixes`;
`**Status:** proposed`; `**Status:** complete`; `cf7a70d`; `f7609a9`; `7d68949`;
`whole-file amendment`; `proxy test`

---

## Intent

Make Task 009’s artifact reflect work that is already on `main`, so future task discovery does
not treat a completed convention change as proposed or duplicate its landed safeguards.

## Interpretations

- **Complete, not abandoned.** Commit `cf7a70d` implemented Task 009 and is an ancestor of `main`;
  `PROGRESS.md` records its successful checks. Commit `f7609a9` later restored the omitted spec.
  Marking it abandoned would falsely say the accepted work was not completed.
- **No retroactive rewrite.** Add provenance and status only. Rewriting the old criteria to the
  post-Task-018 template would obscure the historical specification and exceed this cleanup.

## Scope

### Bootstrap authorization

Task 021 runs after Task 018 establishes expected-file-scoped implementer authority. The user’s
request also explicitly authorizes this Task 009 reconciliation. The Task 021 implementer may edit
only the three expected documentation files below; this does not authorize merge or push.

### Pre-approval impact sweep

The spec writer checked:

```powershell
git log --oneline --all -- docs/tasks/009-task-convention-fixes.md docs/tasks/README.md
git merge-base --is-ancestor cf7a70d main
rg -n -i "Task 009|009-task-convention-fixes|\*\*Status:\*\* (proposed|complete)|cf7a70d|f7609a9|7d68949|whole-file amendment|proxy test" docs/tasks/009-task-convention-fixes.md docs/tasks/018-documentation-fast-lane.md docs/tasks/020-current-state-owner.md PROGRESS.md docs/CONTEXT.md docs/AGENT_ARCHITECTURE.md .codex/agents AGENTS.md docs/tasks/README.md
```

Core-file dispositions:

- `PRD.md` — excluded: no product content changes.
- `docs/DECISIONS.md` — excluded: no ADR changes.
- the current-state block of `PROGRESS.md` — excluded; only a new append-only Task 021 session
  entry is added.
- `docs/CONTEXT.md` — excluded: it contains no Task 009 status claim.
- `docs/tasks/021-close-task-009.md` — included by a section-by-section self-audit rather than the
  historical-dependency `rg` input: its status/provenance wording, criteria, and file scope were
  checked together, without counting the search declaration itself as a dependent hit.

Additional dependents are `docs/tasks/018-documentation-fast-lane.md`, which delegates this
closure to Task 021; `docs/tasks/020-current-state-owner.md`, which defers Task 009 closure to
Task 021; `PROGRESS.md`, which has the authoritative completed-work record;
`docs/AGENT_ARCHITECTURE.md`, which cites Task 009 as a historical file-list defect; and
`docs/tasks/README.md`, which defines status vocabulary and contains the safeguards Task 009
implemented. None requires a semantic edit beyond the expected Task 021 session entry.

Pre-approval hit dispositions:

Contiguous hits are grouped below only when every line is named and the disposition is identical,
as permitted by Task 018’s sweep rule.

- The commit search returns `7d68949`, which originally created `docs/tasks/README.md`,
  `cf7a70d`, which implemented Task 009’s three safeguards, and `f7609a9`, which later added the
  omitted Task 009 artifact. Retain all three commits; only `cf7a70d` is the implementation commit.
- `docs/tasks/009-task-convention-fixes.md:3` is the stale `Status: proposed` hit; change it to
  `complete`. Line 4 is its historical branch, and lines 91, 104-105 are its proxy-test criterion;
  retain those and every other original task line unchanged.
- `PROGRESS.md:394,396-397,403` is the existing completed Task 009 session record. Retain it
  byte-for-byte; append only the new Task 021 session at the bottom.
- `docs/tasks/018-documentation-fast-lane.md:3` is Task 018’s own proposed status; lines 43 and 271
  delegate Task 009 closure to Task 021. Retain all three.
- `docs/tasks/020-current-state-owner.md:127` defers Task 009 closure to Task 021; retain it
  unchanged.
- `docs/AGENT_ARCHITECTURE.md:75` cites Task 009’s historical missing-file-list defect and line 214
  lists proxy tests among past review defects; retain both.
- `docs/tasks/README.md:27` is generic status vocabulary; lines 172 and 184-185 are the landed
  proxy-test safeguard. Retain them. (The broader status lines 13, 88, and 98 do not match the
  declared exact-status regex and therefore are not raw hits.)
- `docs/CONTEXT.md:93` records the live proxy-test warning; Task 021 does not resolve it, so retain
  it unchanged.
- `PROGRESS.md:394,396-397,403` are the existing Task 009 completion record and remain byte-for-byte.
  Lines 573 and 736 are later tasks’ “no proxy test” disclosures and make no Task 009 claim; retain
  them.
- `.codex/agents/implementer.toml:40`, `.codex/agents/orchestrator.toml:154`, and
  `.codex/agents/reviewer.toml:40` are live generic proxy-test safeguards; retain them.
- The search returns no matching line in `AGENTS.md`; no AGENTS change is required.
- This Task 021 file’s self-audited mentions define the searched vocabulary, evidence, desired
  status, and bounded change; they are correct as proposed and must be updated only with the
  post-edit sweep report and final status.

The implementation content is already live; only the Task 009 artifact status and closure
provenance are stale.

Set Task 009 to `Status: complete`. Add a short closure note stating that implementation landed in
`cf7a70d`, the omitted task artifact was restored in `f7609a9`, and Task 018 extends rather than
reimplements its whole-file amendment and proxy-test safeguards. Change no old criterion or
historical completion record.

## Out of scope

- Rewriting Task 009’s original intent, scope, criteria, risks, or blocker section.
- Repeating Task 009’s landed convention prose in Task 021.
- Any workflow implementation from Task 018 or current-state migration from Task 020.
- Code, tests, configuration, ADRs, product documents, or external research.

## Acceptance criteria

1. `docs/tasks/009-task-convention-fixes.md` contains `**Status:** complete` and one concise closure
   note naming `cf7a70d`, `f7609a9`, and Task 018.
2. The closure note says Task 018 extends rather than reimplements Task 009’s whole-file amendment
   and proxy-test safeguards. No original Task 009 acceptance criterion changes, verifiable with a
   diff limited to its status line and closure note.
3. `git merge-base --is-ancestor cf7a70d main` exits 0, and the existing Task 009 session entry in
   `PROGRESS.md` remains unchanged.
4. The three pre-approval commands are rerun after editing and recorded in this task with every
   remaining Task 009 status/provenance hit disposed.
5. Under Task 018’s documentation-only verification policy, one final
   `uv run pytest` and `uv run ruff check .` run passes after the last substantive edit; the Task
   021 `PROGRESS.md` entry records the required exact command evidence and any rerun reason.
6. `PROGRESS.md` contains a Task 021 session entry with criterion-level evidence, undeclared-file
   accounting, and unfinished work. This task is marked `complete` only after every criterion
   passes.

## Files expected to change

```
docs/tasks/009-task-convention-fixes.md
docs/tasks/021-close-task-009.md
PROGRESS.md
```

## Risks

- **Calling unimplemented work complete.** The ancestry command and existing session record are the
  evidence; the status is not inferred from similar prose in README.
- **Rewriting history for neatness.** Task 009 remains a historical artifact, including its older
  template and acceptance wording.
- **Reintroducing overlap.** The closure note points to Task 018; it does not duplicate either
  task’s policy text.

## Blockers and questions

*(none at creation)*
