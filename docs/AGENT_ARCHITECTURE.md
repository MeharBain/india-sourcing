# Agent architecture

Draft 2026-09-10. Designed against Codex CLI's `.codex/agents/*.toml` subagent primitives.

Governing principle: **the orchestrator carries process, never judgement.** Every mechanism
below exists to preserve two properties that made the pre-orchestrator workflow work.

1. **The reviewer is never the author.** Different context, no access to the author's reasoning.
2. **Product decisions escalate to the human.** Process decisions do not.

The orchestrator runs the cycle with two human gates: spec approval before any code exists, and
merge approval on high-risk changes only. Everything between is unattended. The two properties
above are what keep that safe. Neither is negotiable — remove either and the structure becomes a
fluent way to produce work nobody chose.

---

## Why those two properties matter

Of the last five blockers raised on this project, three were Codex catching defects in
Claude-authored task specifications — a contradictory status vocabulary, an acceptance criterion
that was unimplementable given the connector contract, and a sweep term list too narrow for the
change it was policing. None would have been caught by the author re-reading their own spec.

The defects found in the other direction split by kind:

| Defect | How it was found | Automatable? |
|---|---|---|
| Dangling references after a doc edit | Term sweep | **Yes** |
| Acceptance criteria silently unmet | Criterion-by-criterion check | **Yes** |
| `health_status` JSON in a VARCHAR column | Memory of an earlier task's schema plus one phrase in a report | Partly |
| `_BUSINESS_WORDS` denylist unsafe to generalise | Knowing Indian deeptech naming conventions | **No** |
| A grant-funded company is the target, not a false positive | Product owner correction | **No** |

The mechanical half is what this architecture automates. The rest still needs a human, and the
architecture's job is to make sure it reaches one.

---

## Roster

Six agents. Codex defaults to `agents.max_threads = 6` and `agents.max_depth = 1`, so this fits
without configuration changes. Most run sequentially; only implementers fan out.

### `orchestrator`

Reads `PROGRESS.md`, `docs/DECISIONS.md` and `docs/tasks/`. Dispatches, collates, classifies
escalations. **Writes nothing outside `PROGRESS.md`.**

Hard constraints:

- **Never reviews work it dispatched.** Review goes to `reviewer`, always.
- **Never resolves a product question.** See the escalation boundary below.
- **Never writes code, specs, or ADRs.** It routes.
- Caps fan-out at three concurrent implementers. OpenAI's own team found engineers manage three
  to five agent sessions before context-switching costs dominate; the reviewing human is the
  bottleneck, not the model.

### `spec-writer`

Authors `docs/tasks/NNN-slug.md` per `docs/tasks/README.md`. Write access limited to
`docs/tasks/`.

### `spec-auditor`

**The most valuable addition, and the one with no analogue in the old workflow.** Reads a
finished spec before any implementation and checks it against itself:

- Do any two criteria contradict? (Task 006's blocker: criterion 1 required `healthy`/`failed`,
  criteria 4 and 6 required `ok`/`failing`.)
- Is every criterion verifiable from a cheap artifact? (`docs/tasks/README.md` verifiability rule.)
- Is every criterion implementable given the current contracts? (Task 013's blocker:
  `extractor_version` was not reachable before `parse()`.)
- Does the files-expected list include everything the criteria require, including the task file
  itself? (Task 009 forbade committing its own spec.)
- If the spec removes or renames a concept, does it sweep for dependents? (Tasks 007 and 017.)

Read-only sandbox. Reports; does not edit. Two of this project's blockers and one silent defect
would have been caught here, before an implementer wasted a cycle.

### `implementer`

Code work against one task spec. Writes to `src/`, `tests/`, `migrations/`, `config/`. One task
per agent, one branch per agent, git worktree for isolation.

Inherits every rule in `AGENTS.md` — golden fixtures, no silent exception swallowing, blocker
protocol, no threshold widening.

### `reviewer`

Reads **only** the task spec and the diff. Reports met / not met / partially met per criterion
with evidence.

**Critical: the reviewer is not given the implementer's completion report.** A self-report
generated from a wrong assumption reads as convincing to anyone sharing that assumption. The
orchestrator passes the spec path and the branch, nothing else.

Read-only sandbox — it cannot fix what it finds, which keeps findings visible instead of quietly
absorbed.

### `researcher`

Holds its own `mcp_servers` block with web access. The other agents stay code-only.

Does source audits, back-tests, dossier assembly. Writes only to `docs/research/`. **Cannot
write to `src/`, `tests/` or `migrations/`** — research must never silently become
implementation.

This agent is how fixtures get fetched. Codex's default sandbox cannot reach `birac.nic.in`;
this one can, and it commits fetched artifacts for implementers to work from locally.

---

## The escalation boundary

The single most important rule. An orchestrator that resolves product questions produces a
plausible product nobody chose.

**Process — orchestrator may resolve:**

- Naming, file placement, which module something belongs in
- Test structure, fixture organisation
- Sequencing between tasks with no product consequence
- Anything already settled in `docs/DECISIONS.md`
- Wording substitutions where the replacement is mechanical

**Product — orchestrator must escalate:**

- What a field *means* (task 013: is `event_date` the award year or the publication date?)
- What counts as a target versus a false positive
- Scope: what the product does and does not do
- Any trade-off between coverage and precision
- Anything that would need a new ADR, or would contradict an existing one
- Anything where two defensible answers exist and the choice reflects preference

**When uncertain, escalate.** A wrongly escalated process question costs one message. A silently
resolved product question costs a product.

Escalations surface to the human with: the question, the options, a recommendation with
reasoning, and what is blocked meanwhile. They are recorded in the task file's Blockers section
and in `PROGRESS.md` open questions — never only in chat.

---

## Dispatch cycle

Two human gates. Between them, the orchestrator runs unattended.

```
human names a feature
   ↓
STAGE 0  intake: interrogate the request for product ambiguity
         interpretations imply materially different specs? ──► ESCALATE
         minor choices? ──► record them, carry into the spec
   ↓
STAGE 1  spec-writer → spec-auditor
         FAIL twice? ──────────────────────────────────────► ESCALATE
   ↓
╔═══ GATE 1 — HUMAN APPROVES THE SPEC ═══════════════════════════════════╗
║  spec + audit verdict + every interpretation + every deferral          ║
╚════════════════════════════════════════════════════════════════════════╝
   ↓
STAGE 2  implementer                                  [worktree, own branch]
         product blocker? ────────────────────────────────► ESCALATE
   ↓
STAGE 3  reviewer — given only task path + branch              [read-only]
         two reviewers if schema / migration / ADR / threshold
         reviewers disagree? ─────────────────────────────► ESCALATE
   ↓
STAGE 4  orchestrator adjudicates + 13 quality gates
         gates fail twice? ───────────────────────────────► ESCALATE
   ↓
STAGE 5  high-risk paths? ──► GATE 2, human approves merge
         otherwise ─────────► merge autonomously
   ↓
ONE REPORT
```

### Gate 1 is the cheapest place to change direction

It sits after the audit and before any code exists. What matters is *how* the spec is
presented: interpretations and deferrals first, acceptance criteria after. A human skimming an
approval request needs the judgement calls at the top, not buried under a well-formatted spec —
the failure mode is approving an assumption without noticing it was made.

Hence the `## Interpretations` section, required in every spec, recording what was ambiguous,
what was chosen, and what the alternative would have produced. "None; the request was
unambiguous" is a valid entry. The heading is never omitted.

*(`docs/tasks/README.md` does not yet list this as a required section. Amending the convention
is a small outstanding task.)*

### Stage 0 still matters, but is no longer the sole guard

If the interpretations would produce specs differing in scope, data model or acceptance
criteria, the orchestrator escalates before writing anything. Writing first would waste a cycle
and risk the human approving an interpretation buried inside the spec.

For minor choices it records them and carries them to Gate 1. One interrupt, not two.

### Stage 4 is adjudication, not review

The orchestrator dispatched the work, so it cannot independently judge the code. It can verify
the *review* was done properly:

- Every criterion has an explicit verdict — a criterion with no verdict is unmet
- Every "met" cites evidence — an unevidenced "met" is an assertion
- The reviewer said what it could not verify
- Where reviewer and implementer disagree, **the reviewer is authoritative**, and the
  discrepancy is reported rather than reconciled

Then thirteen quality gates, all of which must pass. They encode every silent defect found on
this project: fixtures edited instead of code, thresholds widened, applied migrations edited,
ADRs left contradicted, JSON in a VARCHAR, exceptions swallowed, proxy tests presented as
coverage.

### Dual review and Gate 2 share one trigger list

`src/core/models.py`, anything under `migrations/`, `src/connectors/base.py`, the orchestrator,
an ADR amendment, or any threshold or weight.

Those changes get two reviewers with independent context, and **disagreement is a hard
blocker**. They also stop at Gate 2 for merge approval. Same list, same reason: they propagate,
and unwinding them costs more than a human reading one report.

Everything else merges autonomously. Corrections are fix-forward, so an ordinary change on main
is cheap to fix and expensive to sit on.

### Iteration limits

Two failed audits, or two failed rework cycles, and the orchestrator escalates rather than
trying again. A third attempt almost always means the spec is wrong rather than the
implementation, and without a limit the loop burns tokens indefinitely while looking like
progress.

---

## Write isolation

Prompting an agent not to write somewhere is not isolation. Enforce it.

| Agent | Sandbox | Write root |
|---|---|---|
| orchestrator | workspace-write | `PROGRESS.md` only |
| spec-writer | workspace-write | `docs/tasks/` |
| spec-auditor | **read-only** | none |
| implementer | workspace-write | `src/`, `tests/`, `migrations/`, `config/`, own task file |
| reviewer | **read-only** | none |
| researcher | workspace-write | `docs/research/` |

Concurrent implementers get git worktrees, so parallel branches cannot collide in a shared
working tree.

---

## What this does not fix

Stated plainly so it is not discovered later.

- **Domain-knowledge defects.** `_BUSINESS_WORDS` omitting *therapeutics* and *agroventures* was
  caught by knowing what Indian deeptech companies are called. No agent in this roster knows
  that.
- **Wrong product framing.** Sixteen tasks were built on the belief that the product predicts
  funding events. Every task was well-specified, reviewed and green. The framing was wrong, and
  only the product owner could say so.
- **Correct-but-pointless work.** The last four tasks before this were all corrections found by
  review. That loop can run indefinitely, because any codebase yields corrections forever. It
  feels like progress. Only the human deciding what to build next breaks it.
- **Token and review cost.** Six agents per cycle is more tokens and more output to read. Cap
  fan-out at what can actually be verified.

The architecture makes the mechanical half reliable. It does not make the judgement half
optional.
