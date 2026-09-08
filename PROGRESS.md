# PROGRESS

Session state for this project. Codex reads this at the start of every session and appends to
it at the end. Do not delete history — the log is the point.

Newest entries at the bottom.

---

## Current phase

**Phase 0 — feasibility and source audit.** No code yet.

## Next task

Lead-time feasibility test (see `docs/CODEX_KICKOFF.md`, Week 1 Days 1–2). Delegate to a
web-capable agent. Codex is not involved until Day 6.

## Gate status

| Gate | Status | Notes |
|---|---|---|
| Lead-time test: 15+/20 with meaningful lead | not started | Governs whether the project proceeds at all |
| Fixtures committed for BIG-24 and BIG-21 | not started | BIG-24 confirmed fetchable and text-extractable |
| MCA bulk snapshot freshness verified | not started | Read "as on 30 June 2025" on 2026-09-01. If genuinely stale, watchlist design changes. |
| Vertical slice usable on real data (Day 14) | not started | The real gate. Do not build more connectors before this. |

## Open questions blocking work

1. Is the MCA bulk release genuinely over a year stale, or is the CDM portal just showing an
   old snapshot while data.gov.in has something fresher?
2. Does `idex.gov.in` have any listing page for DISC/ADITI winners, or is it bulletins only?
3. Google Patents BigQuery: how good is IN assignee-name normalisation? Test with a known
   Indian startup assignee.
4. Does the `startupindia.gov.in` search pagination have a JSON endpoint behind it? Low
   priority.

## Assumptions not yet validated

- BIRAC content is licensed permissively enough for commercial reuse. Confirm site terms.
- Cohort-to-cohort BIG PDF layout variation is bounded to the hazards already catalogued in
  `config/sources.yaml`. Expect at least one surprise.

---

# Session log

## Template — copy this shape for every entry

```
## YYYY-MM-DD — <task id and short name>

**Branch / commits:** task/NN-name, <sha>
**Prompt used:** kickoff prompt N

**Changed**
- ...

**Tests proving it**
- `path/to/test.py::test_name` — what it actually asserts

**Unfinished**
- ...

**Assumptions I had to make because the spec didn't say**
- ...            <-- the most important field. Read this every time.

**Decisions promoted to docs/DECISIONS.md**
- ... or "none"
```

---

## 2026-09-01 — project initialised

**Branch / commits:** main, initial spec commit
**Prompt used:** none, human-authored

**Changed**
- `PRD.md`, `AGENTS.md`, `config/sources.yaml`, `docs/CODEX_KICKOFF.md`, `SETUP_GUIDE.md`
- No code.

**Tests proving it**
- None. Spec only.

**Unfinished**
- All of Phase 0.

**Assumptions I had to make because the spec didn't say**
- None; this is the spec.

**Decisions promoted to docs/DECISIONS.md**
- Append-only `signal` table; parsers corrected by version bump, never by mutation
- Immutable `raw_doc`; re-parsing must never require re-fetching
- Dual `Person` / `Company` spine, because ~35% of BIRAC BIG awardees are individuals
- `tenant_id` on workflow tables from migration one, despite a single tenant
- Connectors never touch the database and never set `company_id`
- Patents are a depth signal, not a detection signal, due to the 18-month s.11A lag

---

## 2026-09-01 — comprehension check (kickoff step 5)

**Branch / commits:** main
**Prompt used:** comprehension check, DAY_ONE.md step 10

**Changed**
- No code. Four spec defects found by Codex and corrected:
  1. **Six pipeline layers were never written down.** They existed only in conversation. Codex
     inferred a plausible but wrong six, splitting Collect into fetch/storage and **omitting
     Enrich entirely**. Added PRD section 3a naming all six with module paths.
  2. **LLM cache key contradiction.** `AGENTS.md` had
     `(content_hash, extractor_version, prompt_version)`; PRD omitted `prompt_version`.
     AGENTS.md was correct. PRD updated.
  3. **`tenant` listed as carrying `tenant_id`.** Incoherent — its own `id` is its identity.
     Fixed in `AGENTS.md` and kickoff prompt 2.
  4. **Comprehension question 6 implied one red source; there are two.** Question and
     expected-answer note corrected in `DAY_ONE.md` and `docs/SETUP_GUIDE.md`.

**Tests proving it**
- None. Spec only. Answers to Q3, Q4 and Q5 were correct and precise, so those invariants are
  landing as written.

**Unfinished**
- Phase 0 feasibility test not started.

**Assumptions I had to make because the spec didn't say**
- None taken; the point of this session was to surface where the spec forced Codex to assume.

**Decisions promoted to docs/DECISIONS.md**
- LLM cache key is `(content_hash, extractor_version, prompt_version)`. Prompt changes alter
  output even when parser code is unchanged, so the prompt version must be part of the key.
- L3 Enrich is a distinct layer and must not be collapsed into Extract or Resolve. It is the
  only layer that costs money per call and the only one that must be budget-gated.
