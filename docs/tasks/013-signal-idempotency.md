# 013 — Signal idempotency across runs

**Status:** complete
**Branch:** task/013-signal-idempotency
**Depends on:** 011 merged.

---

## Intent

Task 011's completion report disclosed that re-running the ingestion command appends a second
full set of signals. `raw_doc` deduplicates by content hash; `signal` has no equivalent
protection.

This contradicts `PRD.md` section 10, which states that re-running the pipeline over the same
raw documents must produce identical output and that content hashing enforces it. Content
hashing enforces it for raw documents only. The PRD sentence is wrong.

The consequence scales badly. The pipeline is specified to run weekly. An unchanged BIRAC
source would emit 102 new signals every week — 5,304 duplicate rows after a year from one
connector. The review queue would show each awardee 52 times, and the corroboration component
of the scoring model, which counts distinct source families, would be computing over duplicated
evidence.

---

## Scope

Skip parsing entirely when a raw document has already been parsed by the same extractor
version.

The reasoning is that `raw_doc` deduplication already proves the bytes are identical. If the
bytes and the extractor version are both unchanged, the resulting signals are necessarily
identical, so re-parsing produces nothing new. One query answers it.

1. Before calling `parse()`, the orchestrator reads `connector.extractor_version` (a class
   attribute) and checks whether signals already exist for
   `(raw_doc_id, extractor_version)`. If so, it skips that document and records the skip.
2. Skips are reported in the run summary — skipped documents are not failures and must not
   touch `source.health_status` or `consecutive_failures`.
3. `PRD.md` section 10's idempotency bullet is corrected to describe what actually enforces it.

This preserves ADR-001. Nothing is updated or deleted; a document is simply not re-parsed.

### A related gap, deliberately not fixed here

ADR-001 says a parser is corrected by emitting new signals with a bumped `extractor_version`
and **superseding** the old facts. Nothing implements supersession — there is no column for it
and no query that distinguishes current from stale signals.

That is latent today because no `extractor_version` has ever been bumped. It becomes live the
moment one is, and this task makes it more visible: after a bump, the skip no longer applies
and both old and new signals exist for the same document with no way to tell which is current.

Record it, do not fix it, and add the constraint below to `PROGRESS.md` open questions:

> **Do not bump any `extractor_version` until supersession exists.** Doing so silently doubles
> the signals for every affected document.

---

## Out of scope

- Implementing supersession. Separate task, and it needs a schema decision.
- Any `UPDATE` or `DELETE` of existing signals. ADR-001 stands.
- Deduplicating the 102 signals currently in Neon, if a duplicate set exists from testing.
  Report whether one does; cleaning it is a separate operational step.
- Resolution, scoring, the review UI.

---

## Acceptance criteria

1. The orchestrator skips `parse()` for a `raw_doc` that already has signals at the same
   `extractor_version`. Quote the check.

2. **The test this task exists for.** Running the pipeline twice over the same fixtures yields
   102 signals, not 204. Assert the exact count after each run.

3. A skipped document does not set `health_status = 'failed'`, does not increment
   `consecutive_failures`, and does not clear `last_success_at`. A skip is a successful run
   with nothing to do. Assert all three.

4. A test proves that changing `extractor_version` causes the document to be parsed again,
   demonstrating the skip is keyed on version and not on `raw_doc_id` alone.

4a. A test asserts that every `Signal` returned by `parse()` carries an `extractor_version`
    equal to the connector's declared class attribute. Without this drift guard, the attribute
    and parser constant can diverge, the skip keys on a version no signal carries, and
    idempotency silently stops working while every other test stays green.

5. `run_connectors()` returns `RunSummary`, and the CLI reports parsed and skipped separately
   from it. Assert the returned values in a test, not just printed output.

6. **Against Neon**, run the CLI twice and report `signal` row counts after each. State whether
   duplicate signals already exist in the database from task 011's testing, and if so how many.
   Do not delete them — report only.

7. `PRD.md` section 10's idempotency bullet is replaced with:

   > **Idempotency:** re-running the pipeline over unchanged sources must add nothing. Two
   > mechanisms enforce this: content hashing deduplicates `raw_doc`, and the orchestrator
   > skips parsing any raw document already parsed at the current `extractor_version`. Neither
   > alone is sufficient — content hashing does not prevent a second parse of the same bytes.

8. `PROGRESS.md` open questions gains the supersession constraint quoted in scope above, worded
   so a future session cannot miss it.

8a. **ADR-021** — `extractor_version` is declared connector metadata, not solely an artifact of
    parsing. Reason: the orchestrator must know a document's parse version before deciding to
    parse it, and a value reachable only through `parse()` cannot inform whether to call
    `parse()`. State reversal conditions.

8b. `AGENTS.md`'s connector contract code block gains `extractor_version: str` beside `key` and
    `cadence`.

9. `uv run pytest` and `uv run ruff check .` pass. Report counts before and after.

10. `PROGRESS.md` session entry.

---

## Files expected to change

```
src/connectors/orchestrator.py    skip check and run summary
src/connectors/base.py            extractor_version connector metadata
src/connectors/birac_big/connector.py    BIRAC extractor version declaration
src/cli.py                        reports the returned run summary
tests/test_orchestrator.py        idempotency, version-bump, and skip-health coverage
PRD.md                            section 10 idempotency bullet
PROGRESS.md                       session entry and supersession constraint
AGENTS.md                         connector contract documentation
docs/DECISIONS.md                 ADR-021
```

---

## Risks

- **Keying the skip on `raw_doc_id` alone.** It would work today and silently prevent every
  future parser correction from ever taking effect. Criterion 4 exists to catch it.
- **Treating a skip as a failure.** Health status is how source liveness is judged; a source
  with nothing new is healthy, not broken. Criterion 3 asserts this.
- **Deleting duplicates to make a count come out right.** ADR-001 forbids deleting signals.
  Criterion 6 asks for a report, not a cleanup.
- **Fixing supersession while here.** It is genuinely tempting because the two are related, and
  it needs a schema decision that deserves its own review.

---

## Blockers and questions

### 2026-09-10 — current extractor version is not exposed before parsing

The required skip query needs the current `extractor_version` before `Connector.parse()` is
called. The connector contract exposes only `key`, `cadence`, `discover()` and `parse()` (plus
the contract-fixture methods); BIRAC's `EXTRACTOR_VERSION = "birac-big-v2"` lives in
`src/connectors/birac_big/parser.py` and reaches the orchestrator only inside the `Signal`
objects returned by `parse()`. Therefore the orchestrator cannot query
`(raw_doc_id, extractor_version)` while also skipping parsing entirely.

The available options are:

1. Add a required non-empty `extractor_version: str` class attribute to `Connector`, set it on
   every concrete connector, and let the orchestrator read it after construction but before
   parsing. This is the recommended option: extractor identity is connector metadata, is
   deterministic for the whole parser implementation today, and becomes directly available to
   the required query. It changes `src/connectors/base.py`, the BIRAC connector, test connectors,
   and likely registry/contract validation, all outside this task's expected files. `AGENTS.md`
   also says not to modify the connector interface without discussion.
2. Add a required method such as `extractor_version(doc: RawDoc) -> str`. This supports a
   document-dependent version but adds an unnecessary callable contract for the current global
   parser version and touches the same out-of-scope files.
3. Parse first, inspect returned signals, and discard them when that version already exists.
   This fails criterion 1's explicit requirement to skip `parse()` entirely.
4. Skip whenever any signal exists for `raw_doc_id`. This fails criterion 4 and would suppress
   all future parser corrections.

Please decide whether option 1 is approved and amend the task's scope/files accordingly, or
specify another source of pre-parse extractor-version metadata. The amendment should also state
whether the new run summary is a returned aggregate value (recommended, e.g. immutable
`RunSummary(documents_parsed, documents_skipped)`) or log/output-only reporting; the current
`run_connectors()` returns `None` and no summary contract exists.

### Decision — Claude, 2026-09-10

Option 1 approved. Correct blocker; criterion 1 was unimplementable as written. Specific shape:

`Connector` gains a class attribute `extractor_version: str`, declared alongside `key` and
`cadence`. This is additive metadata of exactly the same kind as the two already there, no
method signature changes.

`BiracBigConnector.extractor_version` is set from the existing `EXTRACTOR_VERSION` constant in
`parser.py`, not restated as a second literal. One source of truth.

Option 2 rejected. A callable where a constant suffices, to support document-dependent versions
no connector needs. `AGENTS.md` forbids abstraction layers for hypothetical cases and asks for
three concrete connectors before generalising. Add it when a second connector genuinely
requires it.

Option 3 rejected, as stated above — it defeats the purpose.

Run summary recommendation approved. `run_connectors()` returns a frozen dataclass
`RunSummary(documents_parsed, documents_skipped, signals_persisted, connectors_failed)`. The CLI
reports from it rather than counting separately.

Amendment sweep: `extractor_version` at original lines 37, 46, 50, 56, 74, 83 and 96 — all
remain correct; the concept is unchanged and only its source becomes explicit. `run summary` at
original lines 38, 86 and 111 — line 86 was amended above, while lines 38 and 111 are
unaffected.
