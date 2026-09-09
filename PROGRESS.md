# PROGRESS

## Current position

The repository has its project scaffold, hosted-Postgres schema and initial migration,
immutable raw-document storage and provenance enforcement, and the connector contract,
registry, and failure-isolating orchestrator. No concrete connector is registered yet. The
next task is the first real BIRAC BIG connector, which is blocked until the real BIG-24 and
BIG-21 PDFs and hand-verified expected JSON fixtures are committed; live fetching also remains
disabled until a real contact address is configured locally. The former 9-to-18-month product
bet is now rejected: three cases show five to thirteen years from incorporation to first
institutional round. What remains contested is the small evidence base, the estimated 10–20%
institutional-raise rate for BIG grantees, and which later signals can support a reliable
readiness ranking.

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
| Lead-time test: 15+/20 with meaningful lead | complete | n=3 found a five-to-thirteen-year gap from incorporation to first institutional round; detection has ample lead but readiness ranking is the constraint. |
| Readiness model validated against first institutional equity rounds | not started | The former timing component is disabled at weight 0 until this is built from data. |
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
5. Trigger behavior is currently verified only by manual Neon runs because `pytest-socket`
   blocks database access. Add a separate integration test suite, excluded from the default
   test run, when CI is set up.

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

---

## 2026-09-09 — task 03 storage layer (blocked before implementation)

**Branch / commits:** task/03-storage, no commit
**Prompt used:** kickoff prompt 3

**Changed**
- Confirmed `task/02-schema`, `main`, and `origin/main` already pointed to `5847055`; the
  requested merge and push were therefore no-ops, then created `task/03-storage`.
- Added test-first coverage for HTTP rate limiting, robots.txt enforcement, User-Agent
  identity, retry behavior, 4xx handling, content hashing, raw-document persistence,
  deduplication, and complete signal provenance.
- Added `config/http.toml` with HTTP policy settings and the clearly marked placeholder
  contact address `SET_ME@example.invalid`.
- Reserved ignored runtime storage at `data/raw_docs/`; committed connector fixtures remain
  unaffected and tracked.
- Added an empty connector registration surface so the contract test passes trivially until
  prompt 4 implements connector discovery.

**Tests proving it**
- None yet. `uv run pytest tests/test_storage.py tests/test_provenance.py
  tests/test_contracts.py` could not execute because PowerShell could not find `uv`.

**Unfinished**
- All implementation in `src/core/storage.py` and `src/core/provenance.py`.
- Running the new focused tests and the required full `uv run pytest` suite.
- Reviewing and proposing the completed staged set for approval before commit.
- Blocker: install `uv` or make the existing executable available on `PATH`, then resume this
  task. Per `AGENTS.md`, work stopped when the canonical test command failed to execute.

**Assumptions I had to make because the spec didn't say**
- `source_url` and `retrieved_at` will live in a reserved `_provenance` object inside
  `signal.payload`, because the approved schema stores those values on `raw_doc` and adding
  new `signal` columns would require an unrequested migration and architectural approval.
- Raw document runtime bytes will live under `data/raw_docs/` in the repository working tree,
  addressed by SHA-256, while golden connector fixtures remain under their tracked connector
  directories.
- The HTTP contact address belongs in a dedicated `config/http.toml`; TOML avoids adding a
  YAML parser dependency because Python 3.12 includes `tomllib`.
- Until prompt 4 defines connector discovery, registered connectors are represented by an
  empty `REGISTERED_CONNECTORS` tuple; future registrations will expose offline
  `contract_signals()` fixtures to the cross-connector contract test.
- Content-hash uniqueness remains global, matching the schema's existing unique constraint,
  rather than being scoped per source or URL.

**Decisions promoted to docs/DECISIONS.md**
- None.

---

## 2026-09-09 — task 03 storage layer resumed and completed

**Branch / commits:** task/03-storage, this commit
**Prompt used:** kickoff prompt 3, corrected provenance contract

**Changed**
- Implemented polite outbound HTTP with a shared per-domain two-second rate limiter,
  robots.txt enforcement, configured User-Agent identity, retry/backoff behavior, and clear
  failures for unsafe HTTP configuration or unsuccessful requests.
- Kept `SET_ME@example.invalid` as the committed contact default and made live fetches fail
  before network access until a real local contact address is configured.
- Implemented SHA-256-addressed raw byte storage and globally deduplicated `raw_doc`
  persistence using the schema's unique content hash.
- Implemented signal construction that requires all five direct provenance columns and
  rejects underscore-prefixed payload keys at any nesting level.
- Corrected the contract tests so URL and retrieval time resolve through `signal.raw_doc_id`
  to authoritative `raw_doc.url` and `raw_doc.fetched_at`; neither value is copied into the
  signal payload.

**Tests proving it**
- `tests/test_storage.py` — exercises per-domain limiting, robots allow/deny behavior,
  configured User-Agent identity, 5xx and transport retries, non-retried 4xx responses,
  placeholder-contact refusal, exact content hashing, disk persistence, and row deduplication.
- `tests/test_provenance.py` — exercises direct provenance enforcement, source-only payloads,
  reserved-key rejection, and raw-document provenance resolution.
- `tests/test_contracts.py` — applies reachable-provenance checks to every registered
  connector and passes with the current empty registry.
- `uv run pytest` — 43 passed.
- `uv run ruff check .` — all checks passed.

**Unfinished**
- Configure a real contact address locally before any live fetch.
- Review, stage, and commit the task after human approval.

**Assumptions I had to make because the spec didn't say**
- A missing robots.txt response represented by a 4xx other than 401 or 403 allows fetching;
  401 and 403 deny fetching, while server and transport failures fail loudly after retries.
- Content-addressed files use the full SHA-256 hex digest as the filename directly under
  `data/raw_docs/`.
- Connector contract fixtures will expose `contract_raw_docs()` alongside
  `contract_signals()` when connector registration is implemented in prompt 4.

**Decisions promoted to docs/DECISIONS.md**
- None. The corrected reachable-provenance contract is recorded in `AGENTS.md` and
  `docs/CODEX_KICKOFF.md` and does not change the approved schema.

---

## 2026-09-09 — task 04 connector contract

**Branch / commits:** task/04-connector-contract, this commit
**Prompt used:** kickoff prompt 4

**Changed**
- Recorded the v1 bio and medtech scope sequence while preserving a sector-agnostic
  architecture.
- Implemented the exact connector ABC, URL fetch targets, and automatic discovery of concrete
  connector subclasses.
- Implemented orchestration through the shared storage fetcher, detached raw-document handoff
  to pure parsers, centralized signal persistence, and per-connector failure isolation.
- Stored structured source health with a consecutive-failure count, diagnostic exception
  details, and reset-on-success behavior.

**Tests proving it**
- `tests/test_orchestrator.py::test_registry_discovers_concrete_connector_subclasses` — a
  concrete connector in a synthetic package is found and instantiated automatically.
- `tests/test_orchestrator.py::test_discover_failure_does_not_stop_other_connectors_and_records_health`
  — a discovery exception records failed health while the next connector persists its signal.
- `tests/test_orchestrator.py::test_parse_failure_does_not_stop_other_connectors_and_records_health`
  — a parse exception records failed health while the next connector persists its signal.
- `tests/test_orchestrator.py::test_three_consecutive_failures_are_distinguishable_from_one`
  — structured health preserves consecutive failure counts of one and three distinctly.
- `tests/test_contracts.py::test_parse_purity_boundary_rejects_network_database_and_clock_reads`
  — parser execution rejects explicit network, session, and clock probes.
- `uv run pytest` — 50 passed.
- `uv run ruff check .` — all checks passed.

**Unfinished**
- The connector registry remains empty until prompt 5 supplies the first real connector.

**Assumptions I had to make because the spec didn't say**
- `source.health_status` stores compact JSON so status, consecutive failure count, exception
  type, and message remain distinguishable without an unrequested schema change; a successful
  run resets the count to zero.
- Concrete connector classes have no-argument constructors so automatic registry discovery can
  instantiate them.
- `FetchTarget` carries only a URL because the shared storage fetch contract currently accepts
  no target-specific request metadata.

**Decisions promoted to docs/DECISIONS.md**
- ADR-014: v1 focuses on bio and medtech because BIRAC BIG is the strongest available signal;
  broader deeptech sectors are sequenced after validation without changing the sector-agnostic
  architecture.

---

## 2026-09-10 — task 005 product reconciliation

**Branch / commits:** task/005-product-reconciliation, this commit
**Prompt used:** `docs/tasks/005-product-reconciliation.md`

**Changed**
- Committed the feasibility findings and established `docs/tasks/` as the task-specification
  convention.
- Reframed the product around readiness ranking after measured five-to-thirteen-year lead
  times, disabled the unsupported timing curve at weight 0, and removed company-age
  suppression.
- Recorded ADR-015 through ADR-018, marked the kickoff guide historical, added task workflow
  instructions, and refreshed the project position and gates.

**Tests proving it**
- `uv run pytest` — 50 passed, unchanged from task 004.
- `uv run ruff check .` — all checks passed.

**Unfinished**
- The readiness model remains intentionally unbuilt and disabled pending a data-backed future
  task.
- The first BIRAC BIG connector still needs committed real PDFs and hand-verified golden
  outputs before parser work can begin.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- ADR-015: measured lead time is five to thirteen years, not nine to eighteen months.
- ADR-016: readiness scoring stays at weight 0 until it can be fit from sufficient data.
- ADR-017: individual and faculty BIG awards create an incorporation watchlist with a known
  founder and 18-month window.
- ADR-018: validation-set inclusion follows first institutional equity, never company age.

---

## 2026-09-10 — task 007 dangling timing references

**Branch / commits:** task/007-dangling-timing-references, this commit
**Prompt used:** `docs/tasks/007-dangling-timing-references.md`

**Changed**
- Replaced the disabled timing component's dangling weekly-digest feature with an explicit
  deferral and documented the current 85-point achievable score.
- Aligned the Phase 5 completion condition, Phase 6 gate, and risk table with readiness-ranking
  precision while preserving the historical lead-time evidence.
- Recorded that task 005's exact-text acceptance criteria did not catch downstream references.
  Future specifications that remove or rename a concept should include a full-document
  consistency sweep, because named-section replacements alone cannot prove dependent prose is
  coherent.

**Tests proving it**
- Post-edit consistency searches covered every occurrence of `timing`, `lead time`,
  `lead-time`, `9 to 18`, `9-to-18`, and `months` in `PRD.md`; no uncovered item remained.
- `uv run pytest` — 50 passed.
- `uv run ruff check .` — all checks passed.

**Unfinished**
- The readiness model remains intentionally unbuilt and disabled pending a data-backed future
  task.
- The older section 13 build plan and section 12 supporting metrics were deliberately left for
  a separate task, as directed by the resolved task-007 blocker.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- None.

---

## 2026-09-10 — task 006 typed source health tracking

**Branch / commits:** task/006-source-health-columns, this commit
**Prompt used:** `docs/tasks/006-source-health-columns.md`

**Changed**
- Replaced JSON text in `source.health_status` with constrained status text, an integer
  consecutive-failure counter, and typed latest-failure details.
- Added the reversible `c4b9e2d7a106` migration and verified its upgrade, downgrade, and final
  upgrade against Neon.
- Updated connector orchestration to write the typed fields directly and removed JSON parsing,
  including `_failure_count` and its silent exception handler.
- Added database-backed tests for the three-failure escalation predicate, invalid-status CHECK
  rejection, and failure-counter reset after recovery.

**Tests proving it**
- Pre-change `uv run pytest` — 50 passed.
- Post-change `uv run pytest` — 53 passed.
- `uv run ruff check .` — all checks passed.
- `uv run alembic check` against Neon — no new upgrade operations detected.
- Neon round-trip — upgraded to `c4b9e2d7a106`, confirmed the four typed columns through
  `information_schema.columns`, downgraded to `f9fda2306f8a` and confirmed only
  `health_status` remained, then upgraded to head again.
- A rolled-back Neon insert confirmed `ck_source_health_status` rejects an unexpected value.

**Unfinished**
- Digest and direct-alert escalation remain intentionally out of scope; the required SQL
  predicate is now expressible and tested.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- None.

---

## 2026-09-10 — task 009 process fixes to the task convention

**Branch / commits:** task/009-task-convention-fixes, this commit
**Prompt used:** `docs/tasks/009-task-convention-fixes.md`

**Changed**
- Made pushing the task-only blocker commit an explicit, mandatory blocker-protocol step.
- Required every specification amendment to include and report a whole-file sweep for the
  changed terms.
- Distinguished proxy tests from behavioural coverage and required completion reports to say
  what each proxy proves, what it does not prove, and how real behaviour was verified.

**Tests proving it**
- Exact-text and section-order checks cover every task-009 wording requirement.
- `git diff --name-only` lists only `docs/tasks/README.md` and `PROGRESS.md` among tracked
  changes.
- `uv run pytest` — 53 passed.
- `uv run ruff check .` — all checks passed.

**Unfinished**
- A repeatable Postgres integration suite remains intentionally out of scope until CI exists.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- None.

---

## 2026-09-10 — task 008 BIRAC BIG connector

**Branch / commits:** task/008-birac-big-connector, this commit
**Prompt used:** `docs/tasks/008-birac-big-connector.md`

**Changed**
- Added the first real connector with committed BIG-21 and BIG-24 PDFs, golden summaries,
  table-layout invariants, five applicant signal types, provisional flags, and complete signal
  provenance.
- Recorded the authoritative listing URL and two explicit artifact URLs in `sources.yaml`, and
  added the eight observed BIRAC partner prefixes to `incubators.yaml`.
- Made offline discovery return only configured artifact URLs; live listing-page discovery and
  its provenance are deferred to task 010.
- Declared `contract_raw_docs()` and `contract_signals()` abstract. Abstract methods were chosen
  instead of empty defaults so a registered connector cannot silently evade contract coverage;
  omission now fails clearly at instantiation.
- Added `pdfplumber` for real PDF text/table geometry and `PyYAML` for authoritative source and
  incubator configuration rather than hardcoding either mapping.

**Tests proving it**
- Parser tests were written before parser implementation. The meaningful initial run stopped
  during collection with `ImportError: cannot import name 'BiracBigConnector'`; after
  implementation, the focused suite passes.
- Real-fixture tests verify both SHA-256 hashes, all ten hand-transcribed rows, reference and
  partner invariants, per-category serial continuity, BIG-21 section counts, complete names,
  score presence by cohort, classification, provisional status, event-date precision, schema
  conformance, and exact configured discovery targets.
- `tests/test_contracts.py` now parses 102 signals from the real connector inside the purity
  boundary and verifies reachable provenance; missing contract fixtures raise at instantiation.
- Pre-change `uv run pytest` — 53 passed. Post-change `uv run pytest` — 73 passed.
- `uv run ruff check .` — all checks passed.

**Behavioural/proxy disclosure**
- PDF tests execute the real committed snapshots through `pdfplumber`; they prove parser
  behaviour for BIG-21 and BIG-24 rather than a source-text proxy.
- The discovery test proves that `discover()` returns exactly the two configured URLs and opens
  no socket. It does not prove live `big.php` availability or layout compatibility; live
  listing discovery was removed from this task and deferred to task 010.

**Cohort-layout surprises**
- None beyond the verified document structure. `pdfplumber` exposes some non-hyphenated BIG-21
  references as `BIG-` followed by a line break; the parser removes that layout hyphen as
  required by the hand-verified references.
- The apparent even/odd BIG call-number pattern may correspond to January/July calls and is
  worth verifying with more cohorts. It is not encoded in event dates or payloads.

**Unfinished**
- Task 010 must decide and implement provenance-preserving live listing discovery.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- None.
