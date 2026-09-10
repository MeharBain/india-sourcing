# 011 — Offline ingestion: first end-to-end pipeline run

**Status:** complete
**Branch:** task/011-offline-ingestion
**Depends on:** 010 merged, **and 012 merged**. Task 012 corrects the orchestrator's failure
boundary so that connector construction happens inside it. This task is the first real exercise
of that boundary, so it must run against the corrected version.

---

## Intent

Every layer now exists — storage, provenance, the connector contract, the orchestrator, a real
parser — and **not one real signal has ever been written to the database.** Everything has been
proven against synthetic fixtures inside a network-blocked test suite.

This task runs the pipeline end to end for the first time and persists the 102 real BIRAC
signals to Neon. It is the last step before a human can look at real data, and it is the point
at which schema problems that only appear under real load become visible.

It is deliberately offline: the fixtures are already committed, so no network is required and
the live-discovery question deferred to a later task stays deferred.

---

## Scope

A command that loads committed fixture bytes into `raw_doc` and runs the orchestrator over
them, without network access.

The gap is narrow: `storage.fetch()` is the only path that creates a `raw_doc`, and it fetches
over HTTP. A committed fixture needs the same treatment — hashed, written to the raw store,
recorded with provenance — from local bytes.

1. `src/core/storage.py` gains a function that ingests local bytes as a `raw_doc`, given a
   source, a URL to record as the origin, and a retrieval timestamp. It shares the hashing,
   deduplication and storage-path logic with `fetch()` rather than duplicating it. **`fetch()`
   itself is not modified beyond extracting shared internals.**
2. A CLI entry point that seeds `source` and `tenant` rows, ingests both BIRAC fixtures, runs
   the orchestrator, and reports what was written.
3. The recorded origin URL for each fixture is its real BIRAC URL from `config/sources.yaml`,
   not a file path. Provenance must point where the document actually came from.

---

## Out of scope

- Any network access. The task completes without contacting `birac.nic.in`.
- Live discovery — still deferred.
- Entity resolution. Signals persist with `company_id` NULL, as designed.
- The review UI. Next task.
- Scoring.
- Any change to the parser or classifier.

---

## Acceptance criteria

1. The ingestion function is in `src/core/storage.py` and shares hashing, deduplication and
   storage-path logic with `fetch()`. Quote the shared internals to show they are not
   duplicated.

2. Re-running ingestion over the same fixture bytes creates no second `raw_doc`, exercising the
   existing content-hash deduplication. Prove it by running twice and reporting row counts.

3. The command runs against Neon and reports: `raw_doc` rows created, `signal` rows created,
   and the `source.health_status` and `consecutive_failures` for `birac_big` afterwards.

4. **102 signals are persisted** — 51 from each cohort. Report the actual count. Any shortfall
   is a finding, not a rounding error.

5. Every persisted signal satisfies the provenance contract against the database, not against
   an in-memory fixture: `raw_doc_id` resolves to a row with non-null `url` and `fetched_at`,
   and the recorded `url` is the BIRAC URL rather than a local path. Verify with SQL and show
   the query.

6. `source.health_status` is `'healthy'` and `consecutive_failures` is `0` after a successful
   run. This is the first time the task-006 columns are written by anything other than a test.

7. Report the SQL result of `SELECT signal_type, count(*), min(confidence), max(confidence)
   FROM signal GROUP BY signal_type` and confirm it matches task 010's reported distributions.
   A mismatch means something was lost between parsing and persistence.

8. Report the count of signals below `review_confidence_threshold`. This is the review queue's
   future workload; the expected figure is 12 across both cohorts.

9. **Report anything the schema made awkward.** This is the first real write path and the
   purpose of running it now. Specifically address: whether `tenant` and `source` seeding needed
   values the schema does not naturally supply, whether any column proved unusable as typed, and
   whether the append-only triggers interfered. Findings go in `PROGRESS.md` and, if
   structural, are raised as blockers rather than worked around.

10. A test covers the ingestion function using a small local fixture and no network. Per the
    proxy-test convention, state whether it is behavioural or a proxy and what the Neon run
    proved that the test does not.

11. `uv run pytest` and `uv run ruff check .` pass. Report counts before and after.

12. `PROGRESS.md` session entry, including the criterion 9 findings.

---

## Files expected to change

```
src/core/storage.py          ingestion function, shared internals extracted
src/cli.py or equivalent     entry point (state where you put it and why)
tests/test_storage.py        ingestion coverage
PROGRESS.md
```

If a new dependency is needed for the CLI, say which and why. `argparse` is in the standard
library and is sufficient.

---

## Risks

- **Duplicating `fetch()` instead of sharing it.** Two code paths that both write `raw_doc`
  will drift, and the second one will be the one that forgets a provenance field. Criterion 1
  asks for the shared internals to be shown.
- **Recording a file path as the origin URL.** Provenance is the product's core claim. A
  `raw_doc` whose `url` is `fixtures/big_21.pdf` is not provenance, and it would silently
  survive every existing test.
- **Working around a schema problem instead of reporting it.** Criterion 9 is the reason this
  task runs before the review UI. A schema that cannot express what is needed is a finding
  worth more than a completed task.
- **Treating a shortfall in the signal count as acceptable.** 102 is exact. If 98 arrive, four
  signals were lost silently, and that is a parser or orchestrator defect.

---

## Blockers and questions

*(none at creation)*
