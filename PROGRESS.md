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
6. **Do not bump any `extractor_version` until supersession exists.** Doing so silently doubles
   the signals for every affected document.

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

---

## 2026-09-10 — task 010 confidence-bearing applicant classification

**Branch / commits:** task/010-classification-confidence, this commit
**Prompt used:** `docs/tasks/010-classification-confidence.md`

**Changed**
- Changed the BIRAC applicant classifier to return class and confidence together, retaining
  the task-008 name-shape rule and all five ADR-012 classes.
- Loaded validated classification confidences from `config/scoring.yaml` before parser entry
  so the parser receives configuration without performing configuration I/O, and propagated
  the result to `Signal.confidence`.
- Configured explicit-marker confidence at 0.95, shape inference at 0.50, ambiguity at 0.30,
  and the human-review threshold at 0.70.
- Added `Shri` and `Smt` to the explicit honorific pattern required by the specification and
  bumped the extractor version from `birac-big-v1` to `birac-big-v2`.
- Added ADR-019, confidence regression and distribution coverage, and confidence values to
  the ten hand-verified BIG-21 golden rows. No other field in that golden file changed.
- Reused the existing constrained `Signal.confidence` column; no model or migration change was
  necessary.

**Tests proving it**
- Test-first focused run after updating tests and the golden expectation: 10 failed, 19 passed.
  Failures showed the old bare-string classifier signature and uniform confidence of 1.0.
- `test_applicant_classification_uses_configured_confidence_for_each_basis` covers private
  limited, LLP, OPC, honorific person, shape-only person, and ambiguity bases.
- `test_unknown_business_words_remain_low_confidence_person_inferences` proves that stripped
  `Inger Therapeutics` and `Leofelis Instruments` remain person-shaped but receive only 0.50.
- `test_cohort_class_and_confidence_distributions_are_stable` preserves both 51-row class
  distributions and verifies confidence counts and review-threshold routing.
- Pre-change `uv run pytest` — 73 passed. Post-change `uv run pytest` — 83 passed.
- `uv run ruff check .` — all checks passed.

**Cohort distributions**
- BIG-21 classes: ambiguous 2, company LLP 2, company private limited 32, person 15. Confidence:
  0.30 = 2, 0.50 = 8, 0.95 = 41; 10 signals fall below the 0.70 review threshold.
- BIG-24 classes: ambiguous 2, company LLP 2, company OPC 1, company private limited 28,
  person 18. Confidence: 0.30 = 2, 0.95 = 49; 2 signals fall below the threshold.

**Unfinished**
- The review queue consumer is intentionally out of scope; this task makes its threshold and
  low-confidence inputs explicit and testable.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- ADR-019: classification by name shape is recorded as low-confidence inference, never as
  fact, because a confident company-as-person error would silently corrupt the incorporation
  watchlist.

---

## 2026-09-10 — task 012 non-instantiating connector registration

**Branch / commits:** task/012-non-instantiating-registry, this commit
**Prompt used:** `docs/tasks/012-non-instantiating-registry.md`

**Changed**
- Changed connector discovery and `REGISTERED_CONNECTORS` to hold concrete connector classes,
  preserving class-level empty-key and duplicate-key validation without calling constructors.
- Moved connector construction into the orchestrator's guarded per-source run, after resolving
  the source row by the connector class's key, so construction failures update source health
  and do not prevent healthy connectors from running.
- Updated cross-connector contracts to instantiate at test execution time and retained the
  real BIRAC BIG fixture assertion for all 102 signals.
- Added ADR-020 and strengthened AGENTS.md rule 5 to make non-instantiating registration and
  construction-time failure isolation explicit repository invariants.
- No database model or migration changed; the task changes object lifecycle around the
  existing task-006 source-health columns.

**Tests proving it**
- Pre-change `uv run pytest` — 83 passed. Pre-change `uv run ruff check .` — all checks passed.
- Test-first focused run — 9 failed and 4 passed. The failures proved constructors still ran
  during discovery/import and the orchestrator had not yet adopted connector classes.
- `test_registry_discovers_concrete_connector_subclasses`,
  `test_registry_rejects_empty_class_key_without_instantiating`, and
  `test_registry_rejects_duplicate_class_keys_without_instantiating` use constructors that
  raise if called, proving registration and key validation do not instantiate.
- `test_importing_registry_does_not_instantiate_connectors` patches the real
  `BiracBigConnector.__init__` to raise `RuntimeError("scoring config malformed")`, removes the
  package from `sys.modules`, and proves a fresh `src.connectors` import still succeeds.
- `test_construction_failure_does_not_stop_other_connectors_and_records_health` proves the
  healthy connector emits its signal while the failed source becomes `failed`, increments
  consecutive failures from 2 to 3, and stores the constructor error in `last_error`.
- Existing task-004 tests `test_discover_failure_does_not_stop_other_connectors_and_records_health`,
  `test_parse_failure_does_not_stop_other_connectors_and_records_health`, and
  `test_three_consecutive_failures_then_success_resets_source_health` now pass connector classes
  because `run_connectors()` owns construction. Their behavioral assertions were not weakened.
- Post-change `uv run pytest` — 87 passed. `uv run ruff check .` — all checks passed.

**Behavioural/proxy disclosure**
- These are direct unit and contract tests of registry import, connector lifecycle, and health
  mutation behavior; no proxy test was added.

**Unfinished**
- Merge and push are intentionally deferred for pre-merge review under the code-task policy.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- ADR-020: connector registration is non-instantiating, and construction occurs inside the
  orchestrator's per-source failure boundary.

---

## 2026-09-10 — task 011 offline ingestion

**Branch / commits:** task/011-offline-ingestion, this commit
**Prompt used:** `docs/tasks/011-offline-ingestion.md`

**Changed**
- Extracted `_persist_raw_doc()` in `src/core/storage.py` so HTTP fetching and local-byte
  ingestion share SHA-256 hashing, content-hash lookup, content-addressed storage, immutable
  `RawDoc` construction, and database persistence.
- Added `ingest_bytes()` for committed artifacts, carrying the authoritative origin URL and
  caller-supplied retrieval timestamp without opening the network.
- Added `python -m src.cli`, which loads the configured Neon URL without printing it, seeds
  the BIRAC source and default tenant, maps the connector's configured URLs to the two committed
  PDFs, runs only `BiracBigConnector` through the orchestrator, and reports created-row and
  source-health counts.
- Added `category: government_grant` to the BIRAC source registry entry because the database
  requires `source.category`; keeping the value in `sources.yaml` avoids a second source of
  truth in the CLI.

**Tests and live run proving it**
- Pre-change `uv run pytest` — 87 passed. Pre-change `uv run ruff check .` — all checks passed.
- The test-first focused run failed during collection because `ingest_bytes` did not exist.
  After implementation, `tests/test_storage.py::test_ingest_bytes_persists_local_fixture_once_with_remote_provenance`
  passes and proves two calls over the same small local file create one row and one stored blob
  while retaining the remote URL and supplied timestamp. The global socket blocker makes this
  a behavioural offline test, not a proxy.
- `uv run alembic current` reported `c4b9e2d7a106 (head)` before ingestion.
- `uv run python -m src.cli` reported 2 `raw_doc` rows created, 102 `signal` rows created,
  `birac_big health_status: healthy`, and `birac_big consecutive_failures: 0`.
- Re-ingesting the already stored BIG-21 bytes twice against Neon left the source-scoped
  `raw_doc` count at 2 after each call and returned the same row ID both times.
- Database provenance was checked with:

  ```sql
  SELECT count(*) AS signals,
         count(*) FILTER (WHERE r.id IS NULL) AS unresolved_raw_doc_id,
         count(*) FILTER (WHERE r.url IS NULL OR r.fetched_at IS NULL)
             AS null_raw_provenance,
         count(*) FILTER (WHERE r.url NOT LIKE 'https://birac.nic.in/%')
             AS non_birac_urls,
         count(*) FILTER (WHERE s.company_id IS NOT NULL) AS assigned_company_ids
  FROM signal s
  LEFT JOIN raw_doc r ON r.id = s.raw_doc_id
  WHERE s.source_id = (SELECT id FROM source WHERE key = 'birac_big');
  ```

  The result was `(102, 0, 0, 0, 0)`. Grouping the same join by URL returned the two configured
  BIRAC HTTPS URLs with 51 signals each and non-null timezone-aware retrieval timestamps.
- `SELECT signal_type, count(*), min(confidence), max(confidence) FROM signal WHERE source_id =
  (SELECT id FROM source WHERE key = 'birac_big') GROUP BY signal_type` returned: ambiguous
  `(4, 0.30, 0.30)`, company LLP `(4, 0.95, 0.95)`, company OPC `(1, 0.95, 0.95)`, company
  private limited `(60, 0.95, 0.95)`, and person `(33, 0.50, 0.95)`. These totals and ranges
  match task 010's combined cohort distributions.
- `SELECT count(*) FROM signal WHERE source_id = (SELECT id FROM source WHERE key =
  'birac_big') AND confidence < 0.70` returned `12`.

**Criterion 9 schema findings**
- Source seeding exposed one configuration gap: `source.category` is non-null but BIRAC had no
  corresponding registry value. `government_grant` is now explicit in `sources.yaml`; no
  schema change was needed. The remaining source fields came directly from the registry.
- Tenant seeding needed an operational identity even though source ingestion is tenant-neutral.
  The command uses the explicit default name `India sourcing`; `thesis_doc` naturally remains
  null, while SQLModel supplies the required JSONB `weight_overrides` as `{}`. Neon stored all
  three values with their declared types.
- No column proved unusable as typed. The one semantic compromise is `raw_doc.http_status`:
  local ingestion performs no HTTP request, but the non-null integer records `200` for these
  committed fixtures, consistently with their existing connector contract rows and their
  origin as successfully downloaded artifacts. A future non-HTTP raw-document source would
  require a separately specified schema decision; this task does not introduce one.
- The existing `raw_doc_immutable` and `signal_append_only` triggers were present for both
  `UPDATE` and `DELETE` in `information_schema.triggers`. They did not interfere because this
  path only inserts raw documents and signals; all 104 inserts committed successfully. No
  update/delete workaround was attempted.
- These findings concern explicit seed metadata and offline HTTP semantics, not an inability
  of the current schema to represent the requested BIRAC run, so no structural blocker or ADR
  was raised.

**Behavioural/proxy disclosure**
- The local fixture test directly executes hashing, deduplication, storage and `RawDoc`
  construction with sockets blocked. It does not exercise PostgreSQL JSONB, foreign keys,
  server defaults, or triggers. The Neon run proved those production-schema behaviours, the
  end-to-end orchestrator write, and reachable database provenance.

**Unfinished**
- Live discovery, entity resolution, scoring, and the review UI remain intentionally out of
  scope. The CLI is safe for the requested first run; re-running the whole command would append
  another signal version because signal-run idempotency was not part of this task.

**Assumptions I had to make because the spec didn't say**
- The single initial tenant is named `India sourcing` and starts without a thesis document or
  weight overrides.
- `government_grant` is the source-level category for BIRAC BIG.
- HTTP 200 is the appropriate stored status for the already downloaded fixture bytes.

**Decisions promoted to docs/DECISIONS.md**
- None. No data-model invariant changed.

---

## 2026-09-10 — task 013 signal idempotency

**Branch / commits:** `main` blocker commit `7e32be5`; `task/013-signal-idempotency`, this commit
**Prompt used:** `docs/tasks/013-signal-idempotency.md`, including the approved blocker amendment

**Changed**
- Added approved class-level `Connector.extractor_version` metadata and bound
  `BiracBigConnector.extractor_version` to the parser's existing `EXTRACTOR_VERSION` constant.
- Added a pre-parse `(raw_doc_id, extractor_version)` existence check. Previously parsed
  documents are skipped without mutating source health; a new version parses and appends new
  signals without updating or deleting old facts.
- Made `run_connectors()` return the frozen `RunSummary(documents_parsed, documents_skipped,
  signals_persisted, connectors_failed)` and changed the offline CLI to report those values
  instead of independently counting signals.
- Corrected the PRD idempotency guarantee, added ADR-021, documented the connector attribute in
  `AGENTS.md`, and added the supersession constraint to the open questions above.
- Preserved the original blocker and appended Claude's decision. The amendment sweep covered
  every `extractor_version` and run-summary occurrence recorded in the decision; the concept
  stayed unchanged and only its pre-parse source became explicit.

**Tests proving it**
- Test-first focused collection failed because `RunSummary` did not exist. After implementation,
  the focused orchestrator and contract suite passes 17 tests.
- `test_running_real_birac_fixtures_twice_keeps_exactly_102_signals` runs both committed PDFs:
  the first summary is `(2 parsed, 0 skipped, 102 persisted, 0 failed)` and the second is
  `(0 parsed, 2 skipped, 0 persisted, 0 failed)`, with 102 signals after each run.
- `test_skipped_document_is_successful_without_losing_source_health` proves `parse()` is not
  called and an all-skipped run preserves `health_status`, `consecutive_failures`, and
  `last_success_at` exactly.
- `test_new_extractor_version_parses_an_already_processed_document` proves changing from
  `test-v1` to `test-v2` parses the same raw document again and persists the new-version signal.
- `test_every_registered_connector_emits_its_declared_extractor_version` is the automatic drift
  guard: all 102 real BIRAC signals equal their connector's declared version.
- The construction-failure isolation test now also asserts summary values, including one
  connector failure alongside one successfully persisted signal.
- Pre-change `uv run pytest` — 88 passed. Post-change `uv run pytest` — 92 passed.
- `uv run ruff check .` — all checks passed before and after.

**Neon idempotency run**
- Before the final runs, Neon held 102 `birac-big-v2` signals and zero duplicate rows beyond a
  first occurrence when grouped by raw document, version, type, event date, payload and
  confidence. Task 011 testing had not created a duplicate set.
- First final-code CLI run: 0 raw documents created, 0 documents parsed, 2 skipped, 0 signals
  persisted, 0 connectors failed; the SQL count afterwards remained 102 with zero duplicates.
- Second final-code CLI run reported the same summary; the SQL count again remained 102 with
  zero duplicates. No signal or raw-document rows were updated or deleted.

**Behavioural/proxy disclosure**
- The orchestrator tests are behavioral: they run the real committed BIRAC fixtures through
  parsing and persistence doubles with network blocked. The Neon CLI runs directly proved the
  production PostgreSQL existence query and end-to-end skip behavior. No proxy test was added.

**Unfinished**
- Signal supersession remains deliberately unimplemented. Do not bump a production extractor
  version until a separate reviewed schema design can distinguish current from stale signals.

**Assumptions I had to make because the spec didn't say**
- None after the blocker decision.

**Decisions promoted to docs/DECISIONS.md**
- ADR-021: extractor version is connector metadata available before parsing, and emitted
  signals must carry the same identity.

---

## 2026-09-10 — task 015 classification review schema

**Branch / commits:** `task/015-classification-review-schema`, this commit
**Prompt used:** `docs/tasks/015-classification-review-schema.md`

**Changed**
- Added the global, signal-scoped `ClassificationReview` model with one unique review per
  signal, pending/resolved/undecidable workflow states, the two specified review reasons, and
  ADR-012's five applicant classes.
- Added migration `5a3e7b1c9d02` on top of prior head `c4b9e2d7a106`; neither existing migration
  was edited.
- After the pre-merge specification correction, renamed examination metadata to `reviewed_by`
  and `reviewed_at`. Enforced three explicit states: pending has no decision or review metadata;
  resolved has a class and both review fields; undecidable has both review fields but no class.
- Added ADR-022 documenting global tenant scope, override-without-mutation behavior, and reversal
  conditions.

**Tests proving it**
- Test-first focused collection failed because `ClassificationReview` did not yet exist. After
  the original implementation and amendment, `tests/test_models.py` passes 21 tests.
- `test_classification_review_schema_matches_contract` asserts the exact columns, nullability,
  signal foreign key, pending default, four named CHECKs, no `tenant_id`, and unique signal key.
- `test_classification_review_checks_reject_invalid_rows` covers bad status, reason and resolved
  class. `test_classification_review_accepts_each_valid_state` accepts pending, resolved and
  undecidable rows. `test_classification_review_rejects_inconsistent_states` rejects an
  undecidable row without `reviewed_by`, a pending row with `reviewed_by`, and a resolved row
  without `resolved_class`.
- `test_classification_review_signal_id_is_unique` proves a second review for one signal is
  rejected.
- `test_postgres_json_fields_use_jsonb` remains unchanged and still enumerates exactly four JSONB
  columns.
- Pre-change `uv run pytest` — 92 passed. Post-amendment `uv run pytest` — 103 passed.
- `uv run ruff check .` — all checks passed before and after.
- `uv run alembic check` against the final Neon head — no new upgrade operations detected.

**Neon migration round-trip**
- Before editing the unmerged migration, Neon was downgraded from `5a3e7b1c9d02` to
  `c4b9e2d7a106` and `information_schema.tables` confirmed the old table was gone. The migration
  was then amended in place as directed.
- `alembic upgrade head` applied the amended `5a3e7b1c9d02`. `information_schema` showed the nine
  specified columns including timezone-aware `reviewed_at` and `created_at`, the four named
  CHECKs, signal foreign key, primary key, and `uq_classification_review_signal_id`. The
  three-clause state expression matched the specification and the row count was zero.
- `alembic downgrade -1` again returned to `c4b9e2d7a106`; `information_schema.tables` returned
  zero matching tables. The final upgrade restored `5a3e7b1c9d02 (head)`.
- Transactional Neon probes accepted pending, resolved and undecidable states. They rejected the
  three vocabulary violations, an undecidable row without `reviewed_by`, a pending row with
  `reviewed_by`, a resolved row without `resolved_class`, and a duplicate signal. Every probe
  rolled back and the final row count remained zero.

**Behavioural/proxy disclosure**
- Default-suite constraint tests execute behaviorally on SQLite, so they are a proxy for the
  production PostgreSQL dialect. The named Postgres constraints were also exercised directly on
  Neon inside rolled-back transactions, proving real rejection behavior without populating the
  table.

**Unfinished**
- Populating classification reviews and reading resolved overrides remain intentionally deferred
  to task 014. `src/resolve/` is unchanged.

**Assumptions I had to make because the spec didn't say**
- None.

**Decisions promoted to docs/DECISIONS.md**
- ADR-022: signal classification review is global, signal-scoped, and overrides rather than
  mutates the parser's original classification.

---

## 2026-09-10 — task 014 minimal entity resolution

**Branch / commits:** `task/014-minimal-resolution`, this commit
**Prompt used:** `docs/tasks/014-minimal-resolution.md`, including the criterion 7 amendment

**Changed**
- Implemented punctuation-insensitive, casefolded exact-name normalization with repeated removal
  of private-limited, Pvt Ltd, LLP and OPC legal suffixes, including compound OPC Private Limited.
- Added a deterministic resolution pass over persisted signals. Company classes create or reuse a
  company and alias; confident people create or reuse a person and a signal-linked watchlist row.
- Added classification-review routing and overrides. New ambiguous and below-threshold signals
  get one pending review; existing pending and undecidable reviews create nothing; resolved
  reviews replace the parser class for resolution.
- Added `python -m src.cli resolve`, which reads the existing configured review threshold and
  reports rows created by the pass.
- The pass loads existing reviews before processing and checks by `signal_id`, so reruns skip
  review insertion rather than raising the unique constraint.

**Tests proving it**
- Pre-change `uv run pytest` — 103 passed. The test-first focused run failed at collection because
  `resolve_signals` did not exist. Post-change `uv run pytest` — 113 passed.
- `test_normalize_name_strips_legal_suffixes_and_punctuation` covers Private Limited, Pvt Ltd,
  `Pvt.Ltd.`, LLP, OPC, compound OPC Private Limited, casefolding, whitespace and punctuation.
- `test_resolution_creates_entities_watchlist_and_cross_cohort_match` covers company creation,
  person plus watchlist creation, two cohorts matching one normalized company, two review reasons,
  below-threshold non-creation, and a second pass creating nothing.
- `test_resolved_review_overrides_signal_type` gives a company-class signal a resolved `person`
  override and proves a person and watchlist—not a company—are created.
- `test_pending_and_undecidable_reviews_create_nothing_or_requeue` proves both states create no
  entity and neither adds another review across two passes.
- `uv run ruff check .` — all checks passed before and after.
- `AGENTS.md` names `tests/fixtures/resolution_pairs.json` for before/after accuracy reporting,
  but that path is absent from the repository. No labelled accuracy number could be run or
  invented; this task changes only exact matching and does not implement or widen a fuzzy
  threshold.

**Neon resolution run**
- Baseline counts `(company, person, alias, watchlist, classification_review, company_id set,
  company_id null)` were `(0, 0, 0, 0, 0, 0, 102)`.
- After the first pass they were `(65, 25, 65, 25, 12, 65, 37)`. The 12 reviews are all pending:
  4 `ambiguous_class` and 8 `low_confidence`. All 12 reviewed signals have neither a company link
  nor a watchlist row.
- A captured rerun considered all 102 signals and created zero companies, people, aliases,
  watchlist rows or classification reviews. Counts remained `(65, 25, 65, 25, 12, 65, 37)`.
- The 65 committed `signal.company_id` assignments prove the production append-only trigger
  permits ADR-013's resolution-owned mutation. `pg_get_triggerdef` confirms `company_id` is the
  only signal column omitted from the trigger's protected UPDATE column list.
- There were zero exact normalized-name matches across BIG-21 and BIG-24: zero companies and zero
  people appeared in both cohorts. With no matches, there was nothing to eyeball for over-match.

**Criterion 8 dual-spine finding**
- `watchlist.awarding_signal_id` was sufficient to reach every resolved person: all 25 confident
  person signals have exactly one watchlist row leading to a person. No required query was
  impossible.
- The asymmetry is materially awkward: `company_id IS NULL` reports 37 signals, but 25 are
  resolved people and only 12 are unresolved classifications. Company cohort queries join signal
  directly to company, while equivalent person queries must join signal → watchlist → person.
  Reporting unresolved signals therefore requires checking both spines, not just the nullable
  company foreign key.

**Behavioural/proxy disclosure**
- The synthetic tests exercise resolution behavior through an in-memory session double because
  the production JSONB schema is intentionally PostgreSQL-only and tests cannot use the network.
  The Neon runs directly proved PostgreSQL persistence, foreign keys, review uniqueness,
  resolution-owned signal updates, and whole-pass idempotency.

**Unfinished**
- Fuzzy matching, candidate scoring, LLM adjudication, watchlist monitoring, enrichment and UI
  remain intentionally out of scope. No parser, classifier or orchestrator changed.

**Assumptions I had to make because the spec didn't say**
- Newly resolved companies use `lifecycle_status = 'unknown'` because the award signals do not
  establish a current registry status and the column has no specified vocabulary.

**Decisions promoted to docs/DECISIONS.md**
- None. Task 015 and ADR-022 had already settled the classification-review design.
