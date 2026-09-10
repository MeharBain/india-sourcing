# 019 — Repository-grounded business advisor

**Status:** blocked
**Branch:** task/019-business-advisor-agent
**Depends on:** 018 merged
**Documentation impact:** semantic
**Sweep terms:** `business-advisor`; `business advisor`; `next best step`;
`best next upgrade`; `best next feature`; `product decisions`; `Six agents`;
`Six agents per cycle`; `No agent in this roster`; `` `/agent` ``; `write isolation`;
`memory`; `next task`; `whole system`; `invoke`; `delegate`; `handoff`

---

## Intent

Add a project-scoped, explicitly invoked business-advisor agent that reconstructs the latest
repository state, compares the next immediate step, the best upgrade to existing work, and the
best new feature, then recommends one overall priority with an orchestrator-ready prompt. This
gives the human a durable, evidence-grounded decision brief after a completed task without
granting any agent product authority or starting another delivery cycle automatically.

## Interpretations

- **Durable memory.** “Remember everything / know the last thing done” means reconstruct current
  state on every invocation from repository artifacts, primarily `PROGRESS.md` plus task status
  and git history/status as corroboration; there is no hidden cross-session model memory or new
  state store. The alternative would create an unverifiable second source of project truth.
- **Invocation timing.** “After the last task has been carried out” means the human explicitly
  invokes the advisor after a completed cycle. There is no event hook or automatic post-merge
  spawn in scope. The alternative would add automation the request does not define or authorize.
- **Advice, not authority.** “Give all business decisions” means recommendation and advice, not
  authority: the human retains every product decision and must explicitly approve before giving
  the generated prompt to the orchestrator. The alternative would contradict the architecture's
  product-escalation boundary.
- **Three distinct lanes.** A next step may be any immediate action, including research,
  documentation, repair, or a feature; an upgrade improves an existing capability or process; a
  feature adds a new product capability. All three are reported even if one action could fit
  multiple lanes, and any overlap is disclosed. The alternative would make the three requested
  comparisons labels for the same recommendation.
- **One priority and one handoff.** The advisor selects one overall priority from the three and
  generates one bounded orchestrator-ready feature-request prompt for that choice. The alternative
  would produce three competing prompts and leave prioritization to the human.
- **How it is invoked.** Invocation is a direct root-agent request naming the custom agent,
  consistent with Codex custom-subagent behavior. `/agent` is for inspecting or switching agent
  threads, not the prescribed invocation. An exact copyable invocation sentence will live in an
  inspectable repository document.
- **Evidence standard.** Recommendations cite repository evidence, distinguish facts from
  judgement and unknowns, account for open blockers and deferrals and the current product framing,
  and state why the chosen priority outranks the alternatives. When the evidence says research or
  a human decision is needed, the advisor says so rather than fabricating an implementation-ready
  feature.
- **Orchestrator boundary.** No change to `.codex/agents/orchestrator.toml` is required. The
  handoff is a prompt the human can review and submit separately, preserving the existing human
  product gate.
- **Task 018 sequencing.** Task 019 is not implemented until Task 018 is merged. Task 018 owns the
  earlier number and changes overlapping governance files, so this task builds on its durable
  amendment, review, verification, merge, and push policies instead of racing or restating them.
  The alternative would create conflicting edits and two versions of the workflow rules.
- **Existing operating guide.** `docs/SETUP_GUIDE.md` currently calls `PROGRESS.md` the memory,
  provides a root prompt that asks for the next task, and calls that prompt plus the completion
  prompt “the whole system.” Reconcile that live guidance to the explicit advisor-then-human-
  approval flow while retaining `PROGRESS.md` as durable repository truth. Leaving it unchanged
  would give the user two contradictory invocation paths; deleting its session-maintenance
  guidance would discard useful operating instructions.

## Scope

This is one repository-agent concern. Add the advisor's read-only contract and reconcile the
agent roster and invocation boundary around it; do not change the application pipeline.

### Pre-approval impact sweep

This semantic specification was prepared against the Task-018 core set before Gate 1:

- **Terms:** the `Sweep terms` metadata above, including the distinct recommendation lanes, agent
  roster/count language, product-decision authority, invocation syntax, and write isolation.
- **`PRD.md`: included and unchanged.** It has no sweep-term hit. It remains mandatory input to
  the advisor because it owns product requirements, but this task does not change those
  requirements.
- **`docs/DECISIONS.md`: included and unchanged.** It has no sweep-term hit and no ADR governs a
  read-only advisory role. Existing ADRs constrain recommendations and remain authoritative.
- **The current-state block of `PROGRESS.md`: included.** It has no sweep-term hit and its product
  summary is not reframed. The file receives only the Task 019 completion entry required by the
  task convention; Task 018 remains responsible for its own current-state consolidation.
- **`docs/CONTEXT.md`: included and unchanged.** Its references to agent architecture and product
  escalation remain correct; Task 018 owns any removal of duplicated current-state snapshots.
- **This task file: included.** Its interpretations, scope, criteria, and sweep vocabulary use the
  same advisor, lane, authority, invocation, roster, and isolation terms.
- **Additional dependents found:** `AGENTS.md`, `docs/AGENT_ARCHITECTURE.md`,
  `docs/SETUP_GUIDE.md`, `.codex/agents/spec-writer.toml`, and
  `.codex/agents/orchestrator.toml`. The first three need edits; the existing product-decision
  boundaries in the two TOMLs remain correct.

Pre-approval hits and dispositions in the repository before Task 018 or Task 019 implementation:

- `docs/AGENT_ARCHITECTURE.md:9` (`Product decisions`) — retain and reinforce it for the advisor;
  recommendations do not cross the human product gate.
- `docs/AGENT_ARCHITECTURE.md:42` (`Six agents`) — change the roster total to seven while making
  clear that the advisor is outside the six-role delivery cycle and is not an additional
  concurrently required role.
- `docs/AGENT_ARCHITECTURE.md:238` (`Write isolation`) — add the business advisor as read-only
  with no write root.
- `docs/AGENT_ARCHITECTURE.md:261` (`No agent in this roster`) — retain the domain-knowledge
  limitation and explicitly apply it to the advisor, which can expose an unknown or request
  research but cannot manufacture expertise absent from the repository.
- `docs/AGENT_ARCHITECTURE.md:269` (`Six agents per cycle`) — retain the delivery-cycle count but
  clarify that the explicitly invoked advisor runs before, not within, that cycle.
- `docs/CONTEXT.md:193` (`Product questions`) — correct as-is; it preserves human escalation.
- `.codex/agents/spec-writer.toml:56` and `.codex/agents/orchestrator.toml:226` (`product
  decisions`) — correct as-is; do not edit or weaken either boundary.
- `docs/SETUP_GUIDE.md:189` (`memory`) — retain the durable-repository meaning while clarifying
  that the advisor reconstructs state from it and corroborating artifacts rather than possessing
  hidden memory.
- `docs/SETUP_GUIDE.md:201` and `:207` (`next task`) — retain the stop-after-completion boundary,
  but replace the old direct next-task prompt with the exact advisor invocation and separate
  approved orchestrator handoff.
- `docs/SETUP_GUIDE.md:210` (`whole system`) — replace the now-incomplete two-prompt claim with the
  advisor, human approval, and orchestrator sequence without restating Task 018's merge, push, or
  verification policy.
- `business-advisor`, `business advisor`, the three recommendation-lane phrases, and the exact
  code token `` `/agent` `` have no pre-existing hit. The new role and invocation guidance will
  introduce their first live definitions.
- `AGENTS.md`, `PRD.md`, `docs/DECISIONS.md`, the current-state portion of `PROGRESS.md`, and this
  not-yet-created task had no pre-existing hit requiring another semantic disposition.

Because Task 018 changes overlapping governance files, its merge invalidates this captured hit
list as an implementation baseline. After Task 018 is merged and before Task 019 implementation,
the implementer records a fresh pre-edit semantic sweep over every metadata term and every
declared core/additional path, with a one-line disposition for every hit. After Task 019 edits,
the implementer records a post-edit pass over that same vocabulary and path set. Every remaining
hit is classified as current policy, historical/task evidence, or blocker.

### 1. Add the project-scoped advisor

Create `.codex/agents/business-advisor.toml` with the supported custom-agent fields `name`,
`description`, `sandbox_mode`, optional `model_reasoning_effort`, and `developer_instructions`.
Use `name = "business-advisor"` and `sandbox_mode = "read-only"`. The agent has no write root,
does not edit or commit files, does not call external research by default, and never dispatches
the orchestrator or another agent.

On every invocation, its instructions require it to read in full:

- `AGENTS.md`, `PRD.md`, `docs/DECISIONS.md`, `docs/tasks/README.md`,
  `docs/AGENT_ARCHITECTURE.md`, and `PROGRESS.md`;
- `docs/CONTEXT.md` for durable warnings and pointers, without treating it as current-state
  authority after Task 018;
- `docs/SHORTLIST_SCHEMA.md` and `docs/FEASIBILITY_TEST.md` for the current surface contract and
  research evidence; and
- `docs/SETUP_GUIDE.md` for the user-facing operating and invocation flow; and
- the status metadata of all numbered task files, followed by the newest relevant completed,
  proposed, in progress, or blocked task files needed to explain sequencing.

It also inspects `git status` and recent `git log` read-only. It identifies the latest completed
work from agreement among `PROGRESS.md`, task status, and merge/commit history, never from the
highest task number alone. Uncommitted, proposed, accepted, in progress, blocked, and abandoned
work is not reported as completed. Any disagreement is shown as an unknown/conflict rather than
silently resolved.

### 2. Require one decision brief

The developer instructions require exactly one response with these headings, in this order:

1. `## Repository checkpoint`
2. `## Next best step`
3. `## Best next upgrade`
4. `## Best next feature`
5. `## Overall recommendation`
6. `## Orchestrator-ready prompt`
7. `## Human gate`

The repository checkpoint names the latest completed task/work and its corroborating commit or
merge, working-tree and pending-task state, the current product framing, built capabilities,
largest gaps, open blockers, and explicit deferrals. Each of the three recommendation lanes
contains `Recommendation`, `Facts and repository evidence`, `Judgement`, `Unknowns or blockers`,
`Expected business value`, and `Confidence`. Evidence cites file paths plus a heading, task ID,
ADR number, or commit; unsupported chat memory is not evidence.

The overall recommendation selects exactly one lane, discloses overlap, explains why it outranks
the other two now, and names what would change the ranking. It may select research or a decision
checkpoint when evidence is insufficient. It does not invent a product semantic, threshold,
weight, source permission, or implementation detail that the repository has not settled.

The orchestrator-ready section contains one copyable prompt for only the selected priority. The
prompt states the requested outcome, why it is next with repository evidence, bounded scope,
explicit out of scope, known constraints/blockers, and the observable success outcome. It asks
the orchestrator to apply the existing workflow; it does not pre-author a task specification,
claim human approval, assign a task number, or start work. If research or a human product decision
must precede implementation, the prompt requests that prerequisite honestly.

The human-gate section states that no work has been dispatched or approved and tells the human to
review the recommendation. Only after agreement does the human submit the single prompt in a new
root request naming the orchestrator.

### 3. Document the role and invocation

Update `docs/AGENT_ARCHITECTURE.md` to add the advisor to the roster, describe it as an explicit
pre-cycle advisory role, add its read-only/no-write-root row, and preserve the six-role delivery
cycle. Explain that it reconstructs state from durable repository truth, has no hidden memory,
does not replace domain expertise, never decides for the human, and never auto-dispatches.

Update `AGENTS.md` in the agent-dispatch section to distinguish an explicit business-advisor
request from a feature request that starts the orchestrator cycle. Reconcile
`docs/SETUP_GUIDE.md` step 7 so its current `PROGRESS.md` memory statement, old next-task root
prompt, and “whole system” claim describe this same durable-state and human-gated handoff. Do not
duplicate Task 018's workflow policies. All three documents contain these exact copyable
root-request sentences:

> Use the `business-advisor` agent to recommend the next project decision. Do not invoke the
> orchestrator or begin implementation.

> Use the `orchestrator` agent to carry out this approved request: [paste the advisor's
> Orchestrator-ready prompt here].

State next to them that `/agent` inspects or switches threads and is not the invocation mechanism.
The second sentence is used only after the human agrees with the recommendation; pasting or
generating the prompt alone is not approval.

### 4. Verify the functional agent configuration and record completion

Treat `.codex/agents/business-advisor.toml` as functional agent configuration, not as a
documentation-only fast-lane change. After the final substantive edit, run fresh normal full
verification: Task 018's documentation checker if the merged task supplies it, the complete
pytest suite, and Ruff. Do not reuse earlier command evidence under Task 018's documentation-only
rule. Record Task 019 in `PROGRESS.md`, including the advisor file, exact invocation, fresh
verification evidence, and that advice remains behind the human gate. Do not alter or restate
Task 018's merge/push authorization policy.

## Out of scope

- Implementing Task 019 before Task 018 is merged, editing Task 018, or duplicating/reversing its
  amendment, reviewer, verification, merge, or push policies.
- Editing `.codex/agents/orchestrator.toml` or automatically connecting the advisor to the
  orchestrator. If implementation appears to require either, stop and raise a blocker.
- Adding an event hook, scheduler, background monitor, persistent memory store, database table,
  or any state outside the existing repository artifacts.
- Letting the advisor approve product decisions, create task specifications, allocate task
  numbers, dispatch agents, implement changes, commit, merge, or push.
- Changing `PRD.md`, `docs/DECISIONS.md`, `docs/CONTEXT.md`, `docs/tasks/README.md`, product scope,
  source priority, shortlist/scoring semantics, thresholds, or weights.
- Editing application code, tests, migrations, `config/`, fixtures, or external research
  artifacts.

## Acceptance criteria

1. `.codex/agents/business-advisor.toml` exists and parses with Python 3.12 `tomllib`. A reported
   parse command proves `name == "business-advisor"`, `sandbox_mode == "read-only"`, and
   non-empty string values for `description` and `developer_instructions`. Separately, an exact
   set comparison proves its top-level keys are precisely `name`, `description`, `sandbox_mode`,
   `model_reasoning_effort`, and `developer_instructions`, with that set cited to the supported
   custom-agent schema or the merged repository convention; `tomllib` parsing alone is not
   presented as proof that a key is supported.
2. A quoted excerpt from the advisor's `developer_instructions` requires no writes, commits,
   dispatches, automatic orchestrator invocation, or external research by default. The TOML has
   `sandbox_mode = "read-only"`, and the architecture write-isolation table gives the advisor no
   write root.
3. The advisor instructions list every mandatory repository read in Scope item 1, require all
   numbered task statuses plus relevant task bodies, and require read-only `git status` and recent
   `git log`. A quoted instruction also says there is no hidden cross-session memory or separate
   state store.
4. The advisor instructions define latest-completed identification from `PROGRESS.md`, task
   status, and git history together; explicitly reject highest-task-number inference and all six
   non-complete statuses named in Scope item 1; and require any disagreement to appear in
   `## Repository checkpoint` as an unknown/conflict.
5. The literal seven output headings in Scope item 2 occur once and in order in the advisor
   instructions. Each recommendation lane requires all six named fields, repository citations,
   and overlap disclosure; the checkpoint requires the latest completed work, pending/worktree
   state, current framing, capabilities, gaps, blockers, and deferrals.
6. The advisor instructions require `## Overall recommendation` to select exactly one of the
   three lanes, explain why it outranks both alternatives, name ranking-changing evidence, and
   permit a research or human-decision prerequisite rather than fabricated certainty.
7. `## Orchestrator-ready prompt` is specified as one bounded, copyable prompt containing the six
   elements in Scope item 2. The instructions prohibit three competing prompts, a pre-written
   task specification or task number, a claim of approval, dispatch, and implementation; an
   unresolved research or decision prerequisite remains explicit in the prompt.
8. `AGENTS.md`, `docs/AGENT_ARCHITECTURE.md`, and the advisor instructions preserve human product
   authority: facts, judgement, and unknowns are distinguished; current framing, ADRs, blockers,
   and deferrals constrain recommendations; and no prompt is submitted until the human approves
   it. Quote one confirming excerpt from each file in the completion report.
9. `AGENTS.md`, `docs/AGENT_ARCHITECTURE.md`, and `docs/SETUP_GUIDE.md` contain both exact
   invocation sentences from Scope item 3 and state that the first is a direct root-agent
   request. All three say `/agent` is only for thread inspection/switching and that the second
   sentence is used in a separate root request only after human agreement. SETUP guide step 7
   still identifies `PROGRESS.md` as durable session truth but no longer presents the old direct
   next-task prompt and completion prompt as “the whole system.”
10. `docs/AGENT_ARCHITECTURE.md` describes seven registered project roles and six delivery-cycle
    roles, adds the advisor to the roster and write-isolation table, and does not imply all seven
    must run concurrently. Its limitation section says the advisor cannot supply domain knowledge
    absent from repository evidence. No existing role is removed.
11. `.codex/agents/orchestrator.toml` is byte-unchanged, and no hook, scheduler, memory/state file,
    application code, test, migration, `config/`, fixture, ADR, or product-document change appears
    in `git diff --name-only` for Task 019. Name-only evidence is paired with exact parsed-TOML
    assertions that the advisor has only criterion 1's five keys, has no `mcp_servers` or key
    containing `hook`, `schedule`, `trigger`, or `state`, uses the read-only sandbox, and includes
    explicit developer-instruction prohibitions on persistent state, agent dispatch, automatic
    orchestrator invocation, and implementation. The allowed Markdown files contain guidance,
    not an executable hook or dispatch configuration.
12. After Task 018 merges and before Task 019 implementation, the task file records a fresh
    pre-edit semantic sweep covering every metadata term, including `memory`, `next task`, `whole
    system`, `invoke`, `delegate`, and `handoff`, and every core/additional path including
    `docs/SETUP_GUIDE.md`. A post-edit sweep covers the same vocabulary and paths. Both record each
    hit's disposition; the final pass leaves no unqualified six-agent roster claim, false hidden-
    memory claim, obsolete whole-system/next-task invocation, advisor authority or auto-dispatch
    claim, or use of `/agent` as the prescribed invocation mechanism.
13. After the final substantive change, a fresh `uv run python scripts/check_docs.py` runs and
    exits 0 if merged Task 018 supplies that checker; if Task 018 is marked complete but the
    checker is absent, implementation stops as a blocker. Fresh `uv run pytest` and
    `uv run ruff check .` runs each exit 0. Completion reporting records the exact commands, exit
    codes, concise outputs/test count, and confirms they cover the final substantive diff; no
    earlier or documentation-fast-lane evidence is reused.
14. `PROGRESS.md` contains a Task 019 completion entry naming the advisor, the latest-state
    reconstruction sources, both exact invocation sentences, verification results, and the human
    approval boundary. This task file is included in the committed changes and reaches
    `Status: complete` only after every criterion passes.

## Files expected to change

```
.codex/agents/business-advisor.toml
AGENTS.md
docs/AGENT_ARCHITECTURE.md
docs/SETUP_GUIDE.md
docs/tasks/019-business-advisor-agent.md
PROGRESS.md
```

## Risks

- **Confusing advice with authority.** A fluent recommendation can look approved. The output and
  invocation flow repeat the human gate and prohibit dispatch.
- **False memory.** `PROGRESS.md`, a task status, and git history can disagree. The advisor must
  expose that conflict instead of selecting whichever source supports a cleaner narrative.
- **Calling proposed work complete.** Task numbers are not completion order. The explicit status
  and history reconciliation prevents the highest number from becoming a false latest task.
- **Three labels for one idea.** Step, upgrade, and feature can overlap. Distinct definitions and
  overlap disclosure keep the comparison honest.
- **Fabricated certainty.** Repository evidence may not support an implementation choice. The
  advisor may recommend research or a human decision and must preserve unknowns in its handoff.
- **Stale product framing.** The PRD still contains a deferred broader phase plan. The advisor must
  use the current evidence-assembly framing and cannot treat section 13 as the live schedule.
- **Workflow collision.** Task 018 changes the same governance files. The explicit dependency and
  deferral prevent Task 019 from implementing against superseded policies.
- **Roster-count drift.** Adding a seventh registered role while leaving an unqualified
  “Six agents” statement would make the architecture self-contradictory.

## Blockers and questions

*(none at creation; implementation is deferred until Task 018 is merged)*

### Specification amendment — 2026-09-11 first audit

The first spec audit failed because `docs/SETUP_GUIDE.md` was an unaccounted semantic dependent,
the initial sweep omitted its `memory`, `next task`, and `whole system` vocabulary, and the task
incorrectly classified runnable agent TOML as eligible for Task 018's documentation-only evidence
reuse. This amendment adds the guide to Scope, criteria, and expected files; expands the sweep and
requires a fresh baseline after Task 018 merges; makes normal full verification mandatory;
tightens schema and no-hidden-automation evidence; and normalizes the canonical `in progress`
status. Criteria 1, 9, and 11–13 and Scope items 1, 3, and 4 are affected. Re-audit is required
before Gate 1 approval.

### Blocker — 2026-09-11 second audit reached the hard limit

The second spec audit also returned FAIL, so the architecture's two-FAIL hard limit is reached.
Stage 1 must stop; human direction and a restarted Stage 1 audit cycle are required before this
task can return to proposed status or proceed to Gate 1.

The unresolved findings are:

1. Scope calls `model_reasoning_effort` optional, while criteria 1 and 11 require an exact
   five-key TOML set that includes it. Two coherent options remain: make the field mandatory and
   specify its explicit value, or allow an exact four-key/five-key alternative depending on
   whether the optional field is present. The specification does not choose between them.
2. Concurrent Task 020 now owns current-state consolidation, so Task 019's statement assigning
   that work to Task 018 is false. Two coherent options remain: add `current state` and
   `current-state` to the semantic sweep, disposition Task 020, and add `020 merged` as a
   dependency; or keep Task 019 independent of Task 020 and specify compatibility with either
   pre- or post-consolidation repository state. The specification does not choose between them.
3. Criterion 11 excludes a `product-document` change without defining which paths that term
   covers, so its name-only verification is not independently checkable until the paths are
   enumerated or the term is replaced with a defined file set.

No criterion or Scope language has been corrected after the second FAIL; this entry records the
blocker only.
