# 020 — Consolidate current-state ownership

**Status:** proposed
**Branch:** task/020-current-state-owner
**Depends on:** 018 merged
**Documentation impact:** semantic
**Sweep terms:** `What exists and works`; `Research state`; `current position`;
`what has been built`; `what is next`; `what is blocked`; `docs/CONTEXT.md section`; `section 2`;
`section 3`; `section 4`; `section 5`; `section 7`; `BIG-21`; `4 of 51`; `800`; `shortlist gate`;
`Nothing renders`; `review surface`; `researcher`

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

## Scope

### Bootstrap authorization

Task 020 runs after Task 018, whose approved expected-file rule gives its implementer access to
the paths listed here. Independently, the user’s request explicitly authorizes the Task 020
implementer to edit these three documentation artifacts to remove current-state duplication. This
authorization does not permit merging or pushing; both retain Task 018’s human gates.

Task 020 must land before the concurrent, user-owned Task 019 proceeds to implementation. Both
would append to `PROGRESS.md`; ordering them avoids parallel conflicts without editing, renumbering,
or otherwise changing Task 019.

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
6. All four post-edit sweep commands from Scope are recorded in this task file with every remaining
   hit disposed. No other file claims to own current build/next/blocker/research status.
7. Under Task 018’s documentation-only verification policy, one final
   `uv run pytest` and `uv run ruff check .` run passes after the last substantive edit; the Task
   020 `PROGRESS.md` entry records exact commands, exit codes, concise output/test count, final-diff
   coverage, and whether any rerun trigger occurred.
8. `PROGRESS.md` contains a Task 020 session entry with criterion-level evidence, undeclared-file
   accounting, and unfinished work. This task is marked `complete` only after every criterion
   passes.
9. The header says `**Depends on:** 018 merged`, the completion report confirms Task 020 landed
   before Task 019 implementation began, and Task 020’s diff contains no change to
   `docs/tasks/019-business-advisor-agent.md`.

## Files expected to change

```
docs/CONTEXT.md
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

## Blockers and questions

*(none at creation)*
