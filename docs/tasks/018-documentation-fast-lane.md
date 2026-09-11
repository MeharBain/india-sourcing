# 018 — Documentation fast lane

**Status:** complete
**Branch:** task/018-documentation-fast-lane
**Depends on:** none
**Documentation impact:** semantic
**Sweep terms:** `merge`; `push`; `autonomous`; `documentation-only`; `researcher`;
`Interpretations`; `amendment`; `sweep`; `verification`; `write isolation`; `write root`;
`section 3`; `section 4`; `section 5`; `section 7`; `task branch`; `direct to main`;
`pre-approval`; `disposition`; `additional dependents`; `hit dispositions`; `six .codex agents`

---

## Intent

Make ordinary documentation changes faster without weakening spec audit, independent review,
quality evidence, or human control of Git operations. The workflow will find semantic dependents
before approval, keep user amendments in the task artifact, avoid repeated unchanged test runs,
use one reviewer for ordinary documentation, reserve the researcher for external work, and catch
bounded mechanical documentation defects automatically.

## Interpretations

- **Merge and push are separate gates.** A user may explicitly approve both in one message, but
  merge approval alone permits only a local merge and push authorization alone does not authorize
  a merge. Treating either permission as implied would contradict the two instructions.
- **Canonical high-risk list.** The existing documents disagree about whether “the orchestrator”
  is high risk. The canonical list below names exact paths and makes both the orchestrator TOML and
  architecture document high risk. A wording-only architecture edit therefore gets dual review;
  this slight extra cost is preferable to a semantic exception that cannot be checked cheaply.
- **One verification run.** “One” means one implementer-owned run after the final substantive diff.
  Missing, failed, or stale evidence and reviewer-identified gaps require a replacement run. An
  unconditional one-run cap would weaken correctness.
- **Checker boundary.** The checker validates explicit structure, links, sweep declarations,
  canonical policy mirrors, and configured exact retired phrases. It does not infer semantics or
  judge prose. A semantic linter would create context-dependent false positives.
- **Researcher boundary.** Ordinary repository documentation uses the normal spec/implement/review
  roles. The researcher is dispatched only when external research or artifacts are actually part
  of the task; merely editing a research document does not require it.

## Scope

This task owns the documentation workflow, agent-policy reconciliation, and its small checker.
Current-state content ownership is Task 020. Closing the stale Task 009 artifact is Task 021.
After Task 018 lands, Task 020 lands before the concurrent user-owned Task 019 begins
implementation; this ordering avoids their shared `PROGRESS.md` write without editing Task 019.

### Bootstrap authorization

The user explicitly requested implementation of these workflow changes. For Task 018 only, that
request authorizes the implementer to edit every path in **Files expected to change**, including
`AGENTS.md`, `.codex/agents/`, `docs/`, `scripts/`, `tests/`, this task file, and `PROGRESS.md`,
despite the current write-isolation table not granting one role that complete set. This is the
bootstrap needed to change the boundary itself. It does not authorize a merge or any push.

Amend the future boundary so an implementer may edit only the paths explicitly listed in an
approved task’s **Files expected to change**. The task file and `PROGRESS.md` must be listed when
they will be touched. Files outside the approved list still require a task amendment or blocker;
the orchestrator, spec-writer, spec-auditor, reviewer, and researcher retain their narrower role
boundaries. Put this rule in `docs/AGENT_ARCHITECTURE.md`, `docs/tasks/README.md`, and
`.codex/agents/implementer.toml`.

### Pre-approval impact sweep

The spec writer ran these repository-wide searches before Gate 1:

```powershell
rg -n -i "merge|push|autonom|documentation-only" AGENTS.md docs/tasks/README.md docs/AGENT_ARCHITECTURE.md docs/CONTEXT.md .codex/agents
rg -n -i "researcher|section [0-9]|write root|write isolation|Interpretations" AGENTS.md docs/tasks/README.md docs/AGENT_ARCHITECTURE.md docs/CONTEXT.md .codex/agents
rg -n -i "amendment|sweep|verification|pytest|ruff" AGENTS.md docs/tasks/README.md docs/AGENT_ARCHITECTURE.md .codex/agents
```

Core-file dispositions:

- `PRD.md` — excluded: it contains product truth, not workflow policy.
- `docs/DECISIONS.md` — included and unchanged: no ADR governs agent dispatch or Git approval.
- the current-state block of `PROGRESS.md` — included and unchanged except for the required Task
  018 session entry; current-state ownership is deliberately Task 020.
- `docs/CONTEXT.md` — included only to delete the resolved `Interpretations` mismatch. Its current
  snapshots and section structure are deliberately Task 020.
- `docs/tasks/018-documentation-fast-lane.md` — included; its terminology, criteria, file list,
  bootstrap authority, and dependency split were checked together.

Additional dependents are the six `.codex/agents/*.toml` role contracts and
`docs/AGENT_ARCHITECTURE.md`; the hit dispositions below enumerate their affected lines. No other
dependent requires an edit.

Every live hit from the searches is disposed as follows:

- `AGENTS.md:279,285-287` — replace selective Gate 2/autonomous merge language with a universal
  merge gate and the canonical high-risk list below.
- `AGENTS.md:299-307` — qualify the allowed merge/push commands with the new approval rules while
  retaining force-push, history-rewrite, and unmerged-branch protections.
- `AGENTS.md:311-312` — remove the general direct-to-`main` documentation allowance; retain only
  the task-file-only blocker exception defined by the blocker protocol.
- `docs/tasks/README.md:61,131-167` — preserve pre-merge reporting and fix-forward history rules;
  replace mandatory blocker push and both old merge tracks with explicit push and universal merge
  gates, one-reviewer ordinary docs, and canonical verification reuse.
- `docs/tasks/README.md:89-91` — a blocker remains a task-file-only local `main` commit, but the
  agent asks before pushing and says remote visibility is pending.
- `docs/tasks/README.md:96` and `:109-125` — retain the existing task-file amendment sweep, but
  broaden it to the declared cross-document scope and consolidated synonym pass; the historical
  Task 006/007 examples remain labelled history.
- `docs/tasks/README.md:74` — retain the PRD-section example of cheap acceptance evidence; it is
  neither a live section dependency nor prediction-era product guidance.
- `docs/tasks/README.md:135-136` — keep pytest and Ruff evidence mandatory; add the bounded
  documentation-only concise/reuse exception without weakening non-documentation reporting.
- `docs/tasks/README.md:61,131,142` — retain the reasons work-in-progress review and completion
  reporting happen before merge; update only wording that assumes a post-merge documentation
  review.
- `docs/AGENT_ARCHITECTURE.md:12,153,173-174,223-226` — retain Gate 1 and independent review;
  replace high-risk-only Gate 2 and autonomous merge statements with universal Gate 2 and use the
  canonical list only to select dual review.
- `docs/AGENT_ARCHITECTURE.md:47-110,238-250` — retain all narrow non-implementer boundaries;
  change only the implementer write row/rationale to approved expected-file ownership and state
  that ordinary documentation does not dispatch the researcher.
- `docs/AGENT_ARCHITECTURE.md:22,29,76` — retain these historical/audit explanations of why term
  sweeps exist; they do not prescribe a narrower live sweep. The new procedure may point to them.
- `docs/AGENT_ARCHITECTURE.md:220` — replace the prose high-risk summary with the exact canonical
  block; do not leave a second paraphrased trigger list.
- `docs/AGENT_ARCHITECTURE.md:186-191` — keep `Interpretations` mandatory and delete the stale note
  that the convention omits it after `docs/tasks/README.md` is updated.
- `docs/AGENT_ARCHITECTURE.md:153,182,195` — retain Stage 0/Gate 1 interpretation handling; these
  hits describe approval visibility rather than a stale convention or Git authority.
- `.codex/agents/orchestrator.toml:2,7-12,83,165-183` — remove high-risk-only Gate 2 and autonomous
  merge; install the universal merge/push gates and the canonical high-risk list.
- `.codex/agents/orchestrator.toml:20-23` and `.codex/agents/spec-writer.toml:12-14` — retain the
  instruction to read CONTEXT section 3, but delete the now-false claim that unreconciled
  prediction-era PRD language is its notable warning. Refer generically to the live stale items so
  the agent contracts do not freeze another snapshot.
- `.codex/agents/orchestrator.toml:103-104` — replace automatic blocker-push verification with an
  authorization request and a clear warning that remote visibility is pending.
- `.codex/agents/orchestrator.toml:43,49-50,86,89-91,218` — retain interpretation visibility and
  approved-spec reporting; broaden the line 89-91 amendment sweep to the durable, consolidated
  cross-document procedure.
- `.codex/agents/orchestrator.toml:227-228` — replace the final report’s “merged autonomously” case
  with `AWAITING MERGE APPROVAL`, `MERGED LOCALLY`, or `PUSHED`, according to explicit authority.
- `.codex/agents/orchestrator.toml:235` — delete the final documentation auto-merge instruction;
  point to the universal policy instead.
- `.codex/agents/implementer.toml:20-46` — add expected-file ownership, canonical one-run evidence,
  and explicit merge/push prohibitions; replace its mandatory blocker push.
- `.codex/agents/implementer.toml:2,11-13` — retain the no-merge role description and CONTEXT
  section 3/5 safety inputs; Task 020 preserves those section numbers.
- `.codex/agents/reviewer.toml` — retain read-only independence; add reuse/staleness checks for the
  canonical documentation verification evidence. Its CONTEXT section 4 reference remains valid.
- `.codex/agents/spec-writer.toml:40-55` and `.codex/agents/spec-auditor.toml` — reconcile the
  `Interpretations` convention and add pre-Gate-1 impact declaration/sweep duties.
- `.codex/agents/spec-writer.toml:36-37` and `.codex/agents/spec-auditor.toml:33-35` — retain their
  dependent-sweep self-checks as the short form of the new declared procedure; the detailed duties
  are added without creating conflicting terminology.
- `.codex/agents/spec-auditor.toml:12,42` — retain both CONTEXT section 3 stale-context checks;
  Task 020 preserves section 3 and its meaning.
- `.codex/agents/researcher.toml:23-24` — replace the live `docs/CONTEXT.md` section 7 research-state
  reference with `PROGRESS.md`; retain the section 5 domain-facts reference until Task 020, whose
  structure preserves section 5. Add the ordinary-documentation exclusion.
- `.codex/agents/researcher.toml:1` — retain `name = "researcher"`; it is the role identity, not a
  dispatch-policy or current-state hit.
- `docs/CONTEXT.md:67-70` — delete only the resolved `Interpretations` mismatch in this task.
  `docs/CONTEXT.md:40`, `:197`, and `:213` are current-state migration hits deferred explicitly to
  Task 020, not silently omitted.
- `docs/CONTEXT.md:100` and `AGENTS.md:206` refer to PRD sections 13 and 5 respectively, not to
  agent-workflow sections; retain both unchanged.
- `AGENTS.md:178-184,227` — retain the canonical pytest/Ruff commands and connector test step;
  Task 018 changes how an unchanged documentation run is reused, not what commands validate the
  repository.
- `AGENTS.md:286` — replace the incomplete high-risk summary as part of lines 285-287 with the
  canonical block.
- References to pushed history, force push, review-before-merge, or an agent “running
  autonomously” between human gates describe safety/history/execution and remain when they do not
  authorize a merge or push.
- No relevant live hit occurs in `PRD.md`, `docs/DECISIONS.md`, or the current-state block of
  `PROGRESS.md`. This task file’s hits specify the new policy or quote the before-state for audit.

The implementer records a post-edit pass over the same commands and dispositions in this task.

### Post-edit impact sweep (2026-09-11)

The implementer reran all three pre-approval commands after the substantive edits. The first
command returned these current-policy or safety/history hits:

- `AGENTS.md:263,280,289,292,317-319,323,331,333-334` â€” retain. These lines require authorized
  blocker pushes, describe the dispatch stage, select one documentation reviewer, impose universal
  merge/push gates, and preserve force-push/history/branch protections.
- `docs/tasks/README.md:72,101-102,174,185,189,205,207,210,224-225,236-237` â€” retain. These lines
  explain branch visibility and pre-merge reporting, define canonical documentation verification,
  impose universal merge/push gates, and preserve fix-forward history.
- `docs/AGENT_ARCHITECTURE.md:12,179-180,222,238-239` â€” retain. These lines describe the two
  universal human gates, canonical reviewer selection, and separate push authorization.
- `.codex/agents/reviewer.toml:21`, `.codex/agents/implementer.toml:2,27,46,55,57-59` â€” retain.
  These are the reviewer reuse duty and implementer stop/authorization duties.
- `.codex/agents/orchestrator.toml:2,10,12-13,88,119-120,133,168,195,200-202,205,249-250,257` â€”
  retain. These are current gate, review, blocker-visibility, verification-reuse, history, and
  final-state instructions. â€œRun autonomouslyâ€ at line 12 describes execution between human gates,
  not autonomous merge or push authority.

The second command returned these current, historical, or explicitly deferred hits:

- `AGENTS.md:206,286` â€” retain. The first is PRD section 5 source scope; the second is the new
  researcher boundary.
- `docs/tasks/README.md:35,85,136,232` â€” retain. These are the required Interpretations heading,
  historical PRD-section examples, and the new researcher boundary.
- `docs/AGENT_ARCHITECTURE.md:103,113,159,188,192,198,252,256,263` â€” retain. These are the role,
  interpretation workflow, and write-isolation definitions; the stale mismatch note is gone.
- `docs/CONTEXT.md:95,208` â€” retain and defer to Task 020. Section 13 is a product-plan warning;
  the researcher line is the current research-state snapshot Task 020 moves to `PROGRESS.md`.
- `.codex/agents/orchestrator.toml:21,43,49-50,91,113,240` â€” retain. These require current CONTEXT
  intake, visible interpretations, the researcher boundary, and final reporting.
- `.codex/agents/implementer.toml:11,13`, `.codex/agents/reviewer.toml:15`,
  `.codex/agents/spec-writer.toml:12,50,52`, and `.codex/agents/spec-auditor.toml:12,42` â€” retain.
  Task 020 preserves CONTEXT sections 3-5; the spec-writer stale snapshot is gone and the required
  Interpretations rule remains.
- `.codex/agents/researcher.toml:1,24` â€” retain. These are the role name and durable CONTEXT
  section 5 input; the section 7 dependency is gone and current research state now comes from
  `PROGRESS.md`.

The third command returned these current-policy, historical, or test-command hits:

- `AGENTS.md:178,181,183-184,227,287` â€” retain. These are canonical test commands, connector
  instructions, and the new researcher sweep exclusion.
- `docs/tasks/README.md:61,63,107,124,127,129,140,142,147,156,161,178-179,189,193,200-201,230,232`
  â€” retain. These define impact declarations, durable amendments, the historical rationale,
  canonical verification and expected-file/researcher boundaries.
- `docs/AGENT_ARCHITECTURE.md:22,29,76,86,112` â€” retain. These are historical sweep evidence,
  auditor duties, expected-file isolation, and researcher routing.
- `.codex/agents/orchestrator.toml:73,95-97,108,113,169,173` â€” retain. These implement impact
  sweeps, consolidated amendments, expected-file ownership, researcher routing, and verification
  reuse.
- `.codex/agents/implementer.toml:20,46-47,52-53`, `.codex/agents/reviewer.toml:22-23,26`,
  `.codex/agents/spec-auditor.toml:33-35`, `.codex/agents/spec-writer.toml:36-37`, and
  `.codex/agents/researcher.toml:8` â€” retain. These are the matching role duties and historical
  sweep checks; no contract contradicts the owner policy.

The contradiction command in criterion 11 exited 1 with no matches. All remaining numbered
CONTEXT current-state hits are explicitly deferred to Task 020; Task 021 owns Task 009 closure.
No live instruction contradicts universal merge approval, explicit push authorization, canonical
reviewer selection, verification reuse, expected-file write isolation, or the researcher boundary.

### Implementation verification (2026-09-11)

- `uv run python scripts/check_docs.py` exited 0 with the single line
  `Documentation checks passed.`
- `uv run pytest` exited 0: `128 passed in 42.32s`.
- `uv run ruff check .` exited 0: `All checks passed!`
- Both canonical commands ran after the final substantive change. Subsequent edits only record
  this evidence and completion status. Task 018 adds an executable checker and tests, so it is
  ineligible for the future documentation-only one-run shortcut.
- No path outside **Files expected to change** changed. `pyproject.toml` and `uv.lock` are
  unchanged. No dependency was added and no proxy test was introduced.

### Review amendment and rework cycle 1 (2026-09-11)

The human resolved the first dual-review disagreement in favor of the stricter rule: all task
work, including documentation, must use a task branch; the sole direct-to-`main` exception is the
local task-file-only blocker commit. Criterion 2 and the AGENTS Git policy are affected. The
absolute rule now sits outside the grammatically conditional â€œwithout being askedâ€ list while
merge and push remain separately authorized.

The agreed checker finding affects criteria 12-14: semantic validation must inspect the intended
`Scope` â†’ `Pre-approval impact sweep` structure and behaviorally reject incomplete core-file
dispositions, missing additional-dependent evidence, and missing hit-disposition evidence. The
checker remains mechanical: it validates bounded placement and disposition vocabulary without
claiming to understand the prose. Three focused tests were added without loosening the original
eight.

Criterion 15 and the post-edit record are also affected: the dependent inventory is six existing
agent TOMLs, not seven, and all exact search line references must describe the final diff. The
added consolidated sweep terms are `task branch`, `direct to main`, `pre-approval`, `disposition`,
`additional dependents`, `hit dispositions`, and `six .codex agents`.

The consolidated rework resweep returned:

- `AGENTS.md:322`, `docs/tasks/README.md:72,94,207`, and
  `.codex/agents/implementer.toml:57` â€” retain as the absolute task-branch rule, branch-visibility
  explanation, and implementer stop instruction. No `direct to main` wording remains; the sole
  exception is explicitly local and task-file-only.
- `scripts/check_docs.py:90,92,103,113-114,160,162,175,184,188,190` â€” retain as the bounded
  extraction and actionable failure reasons for additional dependents, hit dispositions, and
  core/task included-or-excluded evidence inside the pre-approval subsection.
- `tests/test_doc_checks.py:31,39,41,173,177,184,189,197` â€” retain as the valid fixture and three
  new negative behavioral assertions. Each negative assertion names the offending task path and
  the specific missing disposition evidence.
- `.codex/agents/orchestrator.toml:75` and `.codex/agents/spec-writer.toml:46` â€” retain as current
  impact-audit and additional-dependent duties.
- `PROGRESS.md:1066,1088,1091` â€” retain as criterion-2 and strengthened-checker evidence; the
  completion entry is append-only.
- `docs/tasks/018-documentation-fast-lane.md:9-10,63,84-85,178,253,259,267-268,274,277-278,302,328-329,406,456`
  â€” retain. These hits are the expanded metadata, original and post-edit sweep records, durable
  review amendment and its self-referential evidence record, approved policy text, and acceptance
  criteria. The corrected line 84 says six existing TOMLs. No hit describes an unapproved
  merge/push or a seventh TOML; the report's own occurrences do not require recursive resweeps.

No hit requires a product decision or another wording substitution.

### 1. Universal Git authority

Reconcile all live policy to these rules:

- Every merge into `main`, including ordinary documentation and low-risk work, requires explicit
  human approval in the current session.
- Every push of `main` or a named branch requires explicit user authorization in the current
  session.
- The user may grant merge and push together explicitly; otherwise neither permission implies the
  other. A PR is optional.
- All task work uses a task branch. The sole direct-local-`main` exception is the task-file-only
  blocker commit; it still cannot be pushed without authorization.

### 2. Canonical high-risk trigger list

`docs/tasks/README.md` is the canonical owner. The following list must be copied verbatim inside
clearly marked `CANONICAL HIGH-RISK LIST` blocks in `AGENTS.md`,
`docs/AGENT_ARCHITECTURE.md`, and `.codex/agents/orchestrator.toml`:

> A diff requires two independent reviewers if it:
>
> - changes `src/core/models.py`;
> - changes any file under `migrations/`;
> - changes `src/connectors/base.py`;
> - changes `.codex/agents/orchestrator.toml`;
> - changes `docs/AGENT_ARCHITECTURE.md`;
> - amends `docs/DECISIONS.md`; or
> - changes any numerical threshold, confidence value, or scoring weight in any path.

The list selects one versus two reviewers only. Every diff still stops for human merge approval.
Reviewer disagreement on any criterion remains a hard blocker.

### 3. Impact sweeps and durable amendments

For tasks numbered 018 onward, add `**Documentation impact:** none | structural | semantic` to the
required metadata. A semantic task also declares search terms (including known synonyms), gives an
included/excluded-with-reason disposition for `PRD.md`, `docs/DECISIONS.md`, the current-state
block of `PROGRESS.md`, `docs/CONTEXT.md`, and its own task file, lists additional dependents, and
records every pre-Gate-1 hit with a disposition. Structural tasks declare affected paths; `none`
requires only the classification. The spec writer performs this; the auditor fails an incomplete
declaration. The classification itself is reviewed, not inferred by code.

Genuinely identical or irrelevant hits may share one disposition only when that entry explicitly
enumerates every grouped file and line; an unnumbered “other matches are fine” bucket is not a
complete sweep.

Any user/chat change to scope, terminology, an interpretation, or a criterion is copied into the
task artifact before implementation begins/resumes and before review. Record its date, durable
wording or faithful decision summary, affected scope/criteria, and changed sweep terms.

For terminology changes, collect all known synonyms and hits into one amendment pass. Apply only
mechanically equivalent wording substitutions without escalation; a different product meaning is
a blocker. Record one complete cross-document resweep before resuming, rather than one blocker per
wording occurrence.

### 4. Canonical verification for documentation-only tasks

When the final diff changes nothing under `src/`, `tests/`, `migrations/`, or `config/` and adds no
executable tooling, the implementer runs `uv run pytest` and `uv run ruff check .` once after the
last substantive change. The Task session in `PROGRESS.md` records the exact commands, exit codes,
test count/concise output, and that the run covered the final substantive diff. Reviewer and
orchestrator reuse it while the diff remains relevantly unchanged.

Run both again and replace the evidence, recording why, if: relevant content changed after the
run; evidence is missing or stale; either command failed; or a reviewer identifies a concrete
verification gap. Editing only the evidence record does not invalidate it. Non-documentation tasks
retain the normal verification behavior. Task 018 adds executable tooling/tests, so it is not
itself eligible for this fast lane.

### 5. Review and researcher routing

Ordinary documentation-only work gets one independent pre-merge reviewer. Diffs matching the
canonical high-risk list get two reviewers with independent context. All reviewed work then stops
for human merge approval.

Do not dispatch the researcher for ordinary documentation editing, repository terminology sweeps,
or policy changes. Use it only for external web research, source audits, back-tests, dossier
assembly, or fetching external artifacts.

### 6. Dependency-free checker

Add `scripts/check_docs.py` using only the standard library and `docs/doc-checks.json` as bounded
configuration. With no arguments it must:

- validate required task metadata and section presence/order for Task 018 onward, including
  `## Interpretations` immediately after `## Intent`;
- validate the impact declarations in Scope item 3 without inferring their semantic category;
- validate repository-relative Markdown links in configured Markdown paths, including file
  existence and explicit heading fragments;
- compare the three marked high-risk mirrors with the canonical block in
  `docs/tasks/README.md`;
- reject only exact retired phrases in explicitly configured paths; and
- emit actionable path/reason errors with non-zero status, or one concise success line.

Document that the checker cannot judge semantic consistency or context-valid historical wording.
Add focused behavioral tests using temporary fixture trees. Add no dependency.

## Out of scope

- Current-state ownership/content migration; Task 020 owns it.
- Closing or rewriting Task 009; Task 021 owns its status correction.
- Product requirements, ADR content, source priorities, thresholds, weights, application code,
  models, migrations, connectors, or fixtures.
- A general Markdown parser, semantic classifier, spelling/style linter, or retroactive repair of
  Tasks 005–017.
- External research or artifact fetching.
- Requiring a pull request; the Git authorization gates do not mandate one.

## Acceptance criteria

1. `AGENTS.md`, `docs/tasks/README.md`, `docs/AGENT_ARCHITECTURE.md`, and
   `.codex/agents/orchestrator.toml` each state that every merge requires explicit human approval
   and every push requires explicit user authorization in the current session; they state that one
   permission does not imply the other unless both are granted explicitly together.
2. `AGENTS.md` requires task branches for all task work and permits direct local `main` commits
   only for a task-file-only blocker record. `docs/tasks/README.md` and the implementer/orchestrator
   TOMLs require asking before pushing that blocker commit and reporting that it is not remotely
   visible until authorized.
3. The seven bullets in Scope item 2 appear verbatim, in the same order, inside marked
   `CANONICAL HIGH-RISK LIST` blocks in `docs/tasks/README.md` (owner), `AGENTS.md`,
   `docs/AGENT_ARCHITECTURE.md`, and `.codex/agents/orchestrator.toml`. The documentation checker
   compares the three mirrors to the owner, and its passing output proves equality.
4. The convention/architecture state that ordinary documentation gets one reviewer, canonical
   high-risk diffs get two, disagreement is a hard blocker, and every diff then stops for human
   merge approval. Task 018 is classified high risk because it changes both exact paths
   `.codex/agents/orchestrator.toml` and `docs/AGENT_ARCHITECTURE.md`.
5. `docs/AGENT_ARCHITECTURE.md`, `docs/tasks/README.md`, and
   `.codex/agents/implementer.toml` give the implementer task-scoped write authority only over an
   approved **Files expected to change** list. The Task 018 bootstrap paragraph remains in this
   task and explicitly authorizes every expected path without authorizing merge or push.
6. The task convention requires `## Interpretations` immediately after `## Intent`; the stale
   mismatch note is absent from `docs/CONTEXT.md`, `docs/AGENT_ARCHITECTURE.md`, and
   `.codex/agents/spec-writer.toml`. The orchestrator/spec-writer TOMLs still require reading
   CONTEXT section 3 but no longer claim that it identifies unreconciled prediction-era PRD prose.
7. For Task 018 onward, the convention defines `none`, `structural`, and `semantic` documentation
   impact and every semantic requirement in Scope item 3. The spec-writer and spec-auditor TOMLs
   respectively require performing and auditing it.
8. The task convention and orchestrator TOML require durable recording of user/chat amendments and
   one consolidated terminology resweep before implementation/resumption and review, permit only
   mechanically equivalent wording fixes without escalation, and retain product-meaning choices as
   blockers.
9. The documentation-only verification policy contains the owner, timing, exact evidence fields,
   reuse rule, four rerun triggers, evidence-only exception, and non-documentation exclusion from
   Scope item 4. Matching duties appear in implementer, reviewer, and orchestrator TOMLs.
10. `AGENTS.md`, `docs/AGENT_ARCHITECTURE.md`, and the orchestrator/researcher TOMLs exclude the
    researcher from ordinary documentation and name the five external uses in Scope item 5.
    `.codex/agents/researcher.toml` no longer points to `docs/CONTEXT.md` section 7 and instead
    obtains current research state from `PROGRESS.md`.
11. `.codex/agents/orchestrator.toml` contains no live automatic-merge outcome at its former Stage
    5 or final-report locations, including former lines 170, 227–228, and 235. Across live policy
    files, `rg -n -i "merge(s|d)? autonomously|push(es|ed|ing)? without (asking|approval|authorization|waiting)|pushing is not optional|everything else merges" AGENTS.md docs/tasks/README.md docs/AGENT_ARCHITECTURE.md .codex/agents`
    returns no contradiction.
12. `scripts/check_docs.py` imports only standard-library modules.
    `uv run python scripts/check_docs.py` exits 0 with one concise success line, using
    `docs/doc-checks.json` to bound the minimum task number, Markdown paths, mirror paths/markers,
    and retired phrase/path pairs.
13. `tests/test_doc_checks.py` behaviorally proves: valid fixtures pass; missing/out-of-order
    sections fail; missing semantic sweep metadata fails; nonexistent internal paths fail;
    nonexistent explicit heading fragments fail; a changed high-risk mirror fails; and a retired
    phrase fails only inside its configured paths. Every failure assertion checks the offending
    path and reason, not only the exit code.
14. The checker/convention say they do not infer semantic classification, judge prose consistency,
    or ban unconfigured/context-valid historical terms. Neither `pyproject.toml` nor `uv.lock`
    changes.
15. This task contains a post-edit rerun of all three pre-approval search commands with every
    remaining hit disposed. No live instruction contradicts universal merge approval, explicit
    push authorization, canonical reviewer selection, verification reuse, expected-file write
    isolation, or the researcher boundary. Deferred current-state hits point to Task 020.
16. `uv run pytest` and `uv run ruff check .` pass after the final substantive change. Task 018’s
    evidence states that its executable checker/tests make it ineligible for the future
    documentation-only one-run shortcut.
17. `PROGRESS.md` contains a Task 018 session entry with criterion-level evidence, command results,
    undeclared-file accounting, and unfinished work. This task file is committed at status
    `complete` only after every criterion passes.

## Files expected to change

```
AGENTS.md
.codex/agents/implementer.toml
.codex/agents/orchestrator.toml
.codex/agents/researcher.toml
.codex/agents/reviewer.toml
.codex/agents/spec-auditor.toml
.codex/agents/spec-writer.toml
docs/AGENT_ARCHITECTURE.md
docs/CONTEXT.md
docs/doc-checks.json
docs/tasks/018-documentation-fast-lane.md
docs/tasks/README.md
PROGRESS.md
scripts/check_docs.py
tests/test_doc_checks.py
```

## Risks

- **Bootstrap escape.** The Task 018 write exception is limited to the expected list and does not
  authorize Git integration or remote mutation.
- **Four drifting high-risk lists.** The README owns one exact block and the checker compares every
  mirror; prose summaries must not create a fifth variant.
- **A faster false green.** Stale or incomplete evidence triggers a replacement run; the shortcut
  removes repetition, not verification.
- **Permission ambiguity.** Merge and push may be approved together only when the user says both.
- **Automation overreach.** Exact, bounded rules are mechanical; semantic consistency remains a
  spec/audit/review responsibility.
- **Incomplete sweep repair.** The post-edit sweep must cover full files, including the
  orchestrator final-report tail and all numbered CONTEXT references.

## Blockers and questions

*(none at creation)*
