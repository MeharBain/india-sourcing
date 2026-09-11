# 020 — Consolidate current-state ownership

**Status:** complete
**Branch:** task/020-current-state-owner
**Depends on:** 018 merged
**Documentation impact:** semantic
**Sweep terms:** `What exists and works`; `Research state`; `current position`;
`what has been built`; `what is next`; `what is blocked`; `docs/CONTEXT.md section`; `section 2`;
`section 3`; `section 4`; `section 5`; `section 7`; `BIG-21`; `4 of 51`; `800`; `shortlist gate`;
`Nothing renders`; `review surface`; `researcher`; `current state`; `current-state`

---

## Intent

Make `PROGRESS.md` the single trustworthy owner of current implementation, next work, blockers,
and partial research status. `docs/CONTEXT.md` remains a durable orientation index and warning
guide without maintaining a second snapshot that can drift.

## Interpretations

- **Preserve numbered references.** Replace CONTEXT section 2 with a pointer and delete section 7,
  but leave sections 3–6 numbered as they are. Renumbering them would force unrelated agent-policy
  edits and risk redirecting safety instructions to the wrong content. The alternative—compact
  renumbering—would make this content migration a second agent-policy migration.
- **Unique facts to move.** Preserve only the four current facts named in Scope; the detailed
  implementation facts already appear in `PROGRESS.md`’s current block or session log. Copying the
  whole CONTEXT snapshot would preserve the duplication this task removes.
- **Researcher use.** This is repository-local document editing, so Task 018’s researcher boundary
  applies: no researcher is needed merely because one moved fact concerns research.
- **Task 019 reconciliation.** The approved blocker resolution treats superseded ownership prose
  in a live task artifact as stale, not historical. Task 020 therefore makes only the bounded
  wording and dependency corrections needed to identify Task 020 as the owner. The alternative
  would leave contradictory live claims in the repository.

## Scope

### Bootstrap authorization

Task 020 runs after Task 018, whose approved expected-file rule gives its implementer access to
the paths listed here. Independently, the user’s request explicitly authorizes the Task 020
implementer to edit these four documentation artifacts to remove current-state duplication. This
authorization does not permit merging or pushing; both retain Task 018’s human gates.

Task 020 must land before the concurrent, user-owned Task 019 proceeds to implementation. Both
would append to `PROGRESS.md`; ordering them avoids parallel conflicts. The only Task 019 changes
authorized here are replacing its two stale Task-018 ownership statements with Task 020 and adding
`020 merged` to its dependency metadata. Task 019 remains blocked and is not implemented here.

### Pre-approval impact sweep

The spec writer ran:

```powershell
rg -n -i "What exists and works|Research state|what has been built|what is next|what is blocked" AGENTS.md docs/CONTEXT.md docs/tasks/README.md docs/AGENT_ARCHITECTURE.md .codex/agents
rg -n -i "docs/CONTEXT.md section|section [23457]" AGENTS.md docs/CONTEXT.md docs/AGENT_ARCHITECTURE.md .codex/agents
rg -n -i "BIG-21|4 of 51|800|shortlist gate|Nothing renders|review surface|researcher" docs/CONTEXT.md .codex/agents/researcher.toml
Get-Content PROGRESS.md -TotalCount 40 | Select-String -CaseSensitive:$false -Pattern "current position|BIG-21|4 of 51|800|shortlist gate|Nothing renders|review surface|researcher"
```

Core-file dispositions:

- `PRD.md` — excluded: stable product truth does not own project status.
- `docs/DECISIONS.md` — excluded: no architecture decision changes.
- the current-state block of `PROGRESS.md` — included: it receives the missing current facts.
- `docs/CONTEXT.md` — included: its duplicated snapshots are replaced/deleted.
- `docs/tasks/020-current-state-owner.md` — included: its ownership language and numbered-reference
  plan were checked together.

Hit dispositions:

Contiguous hits are grouped below only when every line is named and the disposition is identical,
as permitted by Task 018’s sweep rule.

- `docs/CONTEXT.md:14` already names `PROGRESS.md` as the owner of what is built, next, and
  blocked — retain it.
- `docs/CONTEXT.md:40-59`, section 2 “What exists and works” — replace the snapshot with a short
  `## 2. Current-state pointer` directing readers to `PROGRESS.md`; retain no counts/status here.
- `docs/CONTEXT.md:197-213`, section 7 “Research state” — move the four unique facts below to the
  top/current portion of `PROGRESS.md`, then delete the section.
- `PROGRESS.md:3`, `## Current position` — retain and extend it with the absent-surface fact and
  concise BIG-21/gate status. Preserve the append-only session log.
- `.codex/agents/orchestrator.toml:20-22`, `.codex/agents/spec-writer.toml:12`,
  `.codex/agents/spec-auditor.toml:12,42`, and `.codex/agents/implementer.toml:13` point to CONTEXT
  section 3 — retain section 3 and its number.
- `.codex/agents/reviewer.toml:15` points to CONTEXT section 4 — retain section 4 and its number.
- `.codex/agents/implementer.toml:11` and `.codex/agents/researcher.toml:22` point to CONTEXT
  section 5 — retain section 5 and its number.
- `.codex/agents/researcher.toml:23-24` currently points to CONTEXT section 7; Task 018 removes this
  live dependency and points research-state intake at `PROGRESS.md` before Task 020 deletes the
  section.
- `docs/AGENT_ARCHITECTURE.md:140` says escalations record what is blocked; this is workflow, not a
  competing current-state snapshot, and remains unchanged.
- `docs/AGENT_ARCHITECTURE.md:22,29,76` describe historical sweep failures and the auditor’s sweep
  duty; `:100-105` describes reviewer/researcher roles. The broader Task 018 sweep found them, but
  none claims current-state ownership, so Task 020 leaves them unchanged.
- `AGENTS.md:206` refers to PRD section 5, not CONTEXT, and is unrelated.
- `docs/CONTEXT.md:50` (BIG cohort counts) is part of the duplicated section 2 snapshot and is
  removed; the same 102-signal fact already appears in `PROGRESS.md`’s current position.
- `docs/CONTEXT.md:59`, `:204`, `:210-211`, and `:213` are the four unique current-state items
  moved to the top of `PROGRESS.md` and then removed from CONTEXT.
- `docs/CONTEXT.md:142`, `:157-158`, and `:169` are durable BIG domain facts in section 5, not
  research-progress state; retain them unchanged.
- `.codex/agents/researcher.toml:1` is the role name, not a state-owner claim; retain it.
- The current first 40 lines of `PROGRESS.md` match only `## Current position`; the four unique
  fact searches return no hit there before editing, which is why this migration is required.
- Historical `PROGRESS.md` session references to PRD/CONTEXT sections describe completed edits and
  remain historical.

The implementer records all four commands again after editing and disposes every remaining hit.

### Post-edit impact sweep

After the content migration, the implementer reran the four declared commands against the final
substantive document state:

```powershell
rg -n -i "What exists and works|Research state|what has been built|what is next|what is blocked" AGENTS.md docs/CONTEXT.md docs/tasks/README.md docs/AGENT_ARCHITECTURE.md .codex/agents
rg -n -i "docs/CONTEXT.md section|section [23457]" AGENTS.md docs/CONTEXT.md docs/AGENT_ARCHITECTURE.md .codex/agents
rg -n -i "BIG-21|4 of 51|800|shortlist gate|Nothing renders|review surface|researcher" docs/CONTEXT.md .codex/agents/researcher.toml
Get-Content PROGRESS.md -TotalCount 40 | Select-String -CaseSensitive:$false -Pattern "current position|BIG-21|4 of 51|800|shortlist gate|Nothing renders|review surface|researcher"
```

Remaining-hit dispositions:

- First command: `docs/CONTEXT.md:14` is the retained authoritative-owner row;
  `docs/AGENT_ARCHITECTURE.md:146` describes what a blocker escalation contains rather than
  owning project state; `.codex/agents/researcher.toml:25` correctly directs current research-state
  intake to `PROGRESS.md`. The removed section 2 and section 7 headings produced no hit.
- Second command: `AGENTS.md:206` refers to PRD section 5 and is unrelated. Every CONTEXT reference
  names a retained, unchanged section: `.codex/agents/implementer.toml:11` and
  `.codex/agents/researcher.toml:24` name section 5; `.codex/agents/implementer.toml:13`,
  `.codex/agents/orchestrator.toml:21`, `.codex/agents/spec-writer.toml:12`, and
  `.codex/agents/spec-auditor.toml:12,42` name section 3; `.codex/agents/reviewer.toml:15` names
  section 4. No live agent instruction names CONTEXT section 2 or 7.
- Third command: `.codex/agents/researcher.toml:1` is the role name. `docs/CONTEXT.md:121`,
  `:136-137`, and `:148` are durable BIG award-date, honorific, and panel-score domain facts in
  section 5 and remain there intentionally. CONTEXT has no remaining `4 of 51`, `800`, shortlist
  gate, rendering-gap, review-surface, or current research-state snapshot.
- Fourth command: `PROGRESS.md:3` is the current-position heading. `PROGRESS.md:14`, `:16`, and
  `:19-20` are the four required migrated facts: the rendering/review-surface gap, the BIG-21
  `4 of 51` three-class result, the roughly 800-entity shortlist-gate question, and the researcher
  requirement. They are the intended authoritative current-state copy.

These results leave `PROGRESS.md` as the only owner of live build, next-work, blocker, and research
status. The remaining matches in other files are pointers, durable domain facts, or workflow
language, not competing snapshots.

### Content migration

Keep `docs/CONTEXT.md` section 1. Replace section 2 with a pointer containing no implementation
counts or research progress. Keep sections 3–6, including their numbers and unique warnings,
failure patterns, domain facts, and epistemic limits. Delete section 7.

Before deleting the snapshots, put these four current facts above `PROGRESS.md`’s `# Session log`:

1. Nothing renders the collected data yet; the review surface is the largest operational gap.
2. The BIG-21 back-test has examined 4 of 51 awardees and observed three outcome classes: first
   institutional equity, grant treadmill, and no public outcome found.
3. The key open product-validation question is what fraction of roughly 800 live entities passes
   the shortlist gate.
4. Completing that external back-test requires the researcher because it requires web access.

Do not delete or rewrite historical session entries.

### Task 019 ownership reconciliation

In `docs/tasks/019-business-advisor-agent.md`, add `020 merged` to `Depends on`, replace the two
pre-approval sweep statements assigning current-state consolidation to Task 018 with equivalent
Task 020 ownership wording, and leave its later blocker record intact as the durable explanation
for the correction. Do not resolve Task 019's other blockers or begin its implementation.

## Out of scope

- Workflow/Git/checker changes from Task 018.
- Task 009 closure from Task 021.
- Product requirements, ADRs, code, tests, configuration, or research execution.
- Renumbering CONTEXT sections 3–6 or rewriting their durable warnings and domain facts.
- Reorganizing or pruning the append-only `PROGRESS.md` session log.

## Acceptance criteria

1. `docs/CONTEXT.md` retains the “Where truth lives” row naming `PROGRESS.md` as authority for what
   is built, next, and blocked. Section 2 is titled `## 2. Current-state pointer`, directs readers
   to `PROGRESS.md`, and contains no implementation count or research-progress snapshot.
2. `rg -n "What exists and works|^## 7\. Research state" docs/CONTEXT.md` returns no matches.
   CONTEXT sections 3, 4, 5, and 6 retain their existing numbers and subject headings.
3. Above `# Session log`, `PROGRESS.md` contains short, directly quotable statements for all four
   facts enumerated in Scope’s content migration. “No public outcome found” is not rewritten as a
   company failure.
4. The implementation diff deletes no unique warning, failure pattern, domain fact, or epistemic
   limit from CONTEXT sections 3–6 and deletes no historical `PROGRESS.md` session entry. The
   reviewer verifies this from the bounded diff of those sections, not a whole-file prose review.
5. After Task 018 and this task, every `.codex/agents/*.toml` reference to a numbered CONTEXT
   section targets an existing unchanged section 3, 4, or 5; no live instruction references
   CONTEXT section 2 or 7. Report the output of
   `rg -n -i "docs/CONTEXT.md section|section [23457]" .codex/agents`.
6. All four post-edit sweep commands from Scope and the approved blocker amendment resweep for
   `current state|current-state` are recorded in this task file with every remaining hit disposed.
   No other file claims to own current build/next/blocker/research status.
7. Under Task 018’s documentation-only verification policy, one final
   `uv run pytest` and `uv run ruff check .` run passes after the last substantive edit; the Task
   020 `PROGRESS.md` entry records exact commands, exit codes, concise output/test count, final-diff
   coverage, and whether any rerun trigger occurred.
8. `PROGRESS.md` contains a Task 020 session entry with criterion-level evidence, undeclared-file
   accounting, and unfinished work. This task is marked `complete` only after every criterion
   passes.
9. The header says `**Depends on:** 018 merged`; the pre-merge completion report confirms Task 019
   implementation has not begun and records that Task 019 must remain blocked until Task 020
   lands; and Task 020’s diff changes `docs/tasks/019-business-advisor-agent.md` only to add the
   `020 merged` dependency and correct the two stale current-state ownership statements authorized
   above.

## Files expected to change

```
docs/CONTEXT.md
docs/tasks/019-business-advisor-agent.md
docs/tasks/020-current-state-owner.md
PROGRESS.md
```

## Risks

- **Broken numbered instructions.** Keeping sections 3–6 stable and checking every TOML reference
  prevents a deletion from silently redirecting safety guidance.
- **Losing a unique live fact.** The four-item migration list is exact and cheaply quotable.
- **Recreating duplication in the pointer.** Section 2 links to current truth; it does not summarize
  counts, milestones, or research progress.
- **Rewriting history.** Only the top/current portion and a new session entry change in
  `PROGRESS.md`; old entries remain append-only.
- **Expanding into Task 019.** The explicit three-change boundary prevents the ownership correction
  from resolving its other blockers or beginning implementation.

## Blockers and questions

### 2026-09-11 — reviewer found a Task 019 ownership contradiction

The implementation and its canonical verification pass, but independent review found that
`docs/tasks/019-business-advisor-agent.md:84,86` still assigns current-state consolidation to
Task 018. Task 019's later blocker correctly says those statements are false because Task 020 owns
the work, but leaving both statements in the same live task artifact conflicts with criterion 6's
requirement that no other file claim current-state ownership.

The approved Task 020 specification also requires its diff not to change Task 019 (criterion 9 and
the expected-file list), so the implementer cannot fix those lines without an explicit amendment.

Two coherent options remain:

1. **Recommended — reconcile Task 019 here.** Add `current state` and `current-state` to Task 020's
   sweep terms; authorize only the corresponding Task 019 wording and dependency corrections;
   replace the stale Task-018 ownership statements with Task 020; add `020 merged` to Task 019's
   dependency; and amend criterion 9 plus the expected-file list to permit this bounded fourth
   file. This also resolves Task 019's recorded current-state blocker before its next audit.
2. **Treat superseded task prose as historical.** Amend criterion 6 to exclude pre-approval sweep
   statements that a later blocker explicitly supersedes, retain Task 019 unchanged, and record
   why those lines are not considered a competing live ownership claim.

Decision needed: choose option 1 or 2. Task 020 remains unmerged and Task 019 implementation must
not start until the decision is recorded, implemented, and reviewed.

**Resolution — approved by the user on 2026-09-11:** Option 1. Task 020 owns the bounded Task 019
wording and dependency corrections described above. The sweep terms, scope, criteria, expected-file
list, and risks are amended accordingly. Task 019 remains blocked for its other recorded decisions
and cannot begin implementation until Task 020 is merged.

### 2026-09-11 — approved amendment resweep

After applying the three bounded Task 019 corrections, the implementer ran:

```powershell
rg -n -i "current state|current-state" AGENTS.md PRD.md PROGRESS.md docs .codex/agents
```

Every remaining hit is disposed below. Grouped entries enumerate every file and line sharing the
same disposition.

- `PROGRESS.md:45` is the live Task 019 blocker, updated to say its ownership issue is resolved
  while its other two questions remain. `PROGRESS.md:1110`, `:1141`, `:1152`, and `:1154-1155`
  are Task 018 and Task 020 session evidence that correctly assigns the migration to Task 020.
- `docs/CONTEXT.md:40` is the intended pointer to the authoritative live status in `PROGRESS.md`.
- `.codex/agents/spec-auditor.toml:49` and `.codex/agents/spec-writer.toml:44` define the semantic
  sweep's required core-file coverage; neither owns repository status.
- `docs/tasks/006-source-health-columns.md:39,53` uses the words for a source-health field's value,
  not repository status. `docs/tasks/017-product-reframe.md:366,371` is historical rework evidence.
- `docs/tasks/018-documentation-fast-lane.md:45,78-79,158,160,172,235,390,460,535` consistently
  delegates this migration to Task 020 or describes the documentation-sweep policy and history.
- `docs/tasks/019-business-advisor-agent.md:82,84,86,123,145` now either assigns consolidation to
  Task 020 or describes the advisor's future repository intake. Its later blocker at `:372-374`
  remains unchanged as required historical context for the approved correction.
- `docs/tasks/README.md:157` defines the semantic sweep's core files and is not a status claim.
- `docs/tasks/020-current-state-owner.md:1,4,10,42,65,67,78,93,96,100,143,169,184,199,211,218`
  defines or records this task's ownership migration. Lines `:239,242,249,253` are its durable
  blocker record. Lines `:271,291` are the exact resweep command and this self-disposition record.
- `docs/tasks/021-close-task-009.md:41,48,56,77,108` scopes Task 021 against Task 020 and retains
  its own pre-approval sweep/history; it does not compete for ownership.
- `AGENTS.md` and `PRD.md` returned no hits. All remaining matches are accurate policy, history,
  domain-field descriptions, pointers, or Task 020 ownership records; no competing live snapshot
  or owner remains.

### 2026-09-11 — criterion 9 pre-merge evidence correction

The prior criterion required the completion report to confirm that Task 020 had landed, which is
impossible to prove during the required review before merge. This mechanically equivalent
amendment replaces only that circular proof with pre-merge evidence: Task 019 implementation has
not begun, Task 019 must remain blocked until Task 020 lands, and its diff contains exactly the
three authorized corrections. The post-merge sequencing gate is unchanged: Task 020 must still
land before Task 019 proceeds.

The implementer searched the relevant task and progress artifacts with:

```powershell
rg -n -i "Task 020 landed|Task 020 lands|before Task 019 implementation|Task 019 implementation has not begun|Task 019 remains blocked|must remain blocked|cannot begin implementation until Task 020 is merged|must land before" docs/tasks/019-business-advisor-agent.md docs/tasks/020-current-state-owner.md PROGRESS.md
```

Every final hit is disposed below:

- `PROGRESS.md:1166,1168,1188-1189` records the still-blocked Task 019 status, the corrected
  pre-merge evidence, and criterion-level proof. These are the intended live status records.
- `docs/tasks/020-current-state-owner.md:45,48` states the unchanged sequencing gate and bounded
  Task 019 status; `:209`, `:264-265`, and `:306` are the amended criterion, approved resolution,
  and durable rationale. `:313` is this sweep's command and is the only hit containing the retired
  completed-state wording.
- `docs/tasks/019-business-advisor-agent.md:127,297` sets the future Task 019 pre-edit sweep and
  verification timing. Both remain accurate and are additionally constrained by its `020 merged`
  dependency; neither claims that implementation has started.

No live assertion claims the merge has already happened. Every replacement hit preserves the
unchanged rule that Task 019 cannot proceed until Task 020 is on main.
