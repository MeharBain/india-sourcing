# 012 — Non-instantiating connector registration

**Status:** complete
**Branch:** task/012-non-instantiating-registry
**Depends on:** 010 merged.

**Execution order: this runs before task 011.** Task numbers are monotonic, not an execution
sequence. Task 011 is the first real exercise of the orchestrator's failure boundary, so the
boundary should be correct first.

---

## Intent

`AGENTS.md` rule 5 requires failing loudly per-source and never globally. Connector
registration currently violates it.

`src/connectors/__init__.py` builds `REGISTERED_CONNECTORS = discover_connectors()` at import
time, and `discover_connectors()` instantiates every concrete connector class.
`BiracBigConnector.__init__` reads and validates `scoring.yaml`. So a YAML syntax error, a
missing key, or an out-of-range confidence value raises during **import of
`src.connectors`** — before the orchestrator's per-connector `try` exists.

The consequence is precise: the `source` row is never resolved, no health failure is recorded,
`consecutive_failures` never increments, and the escalation predicate built in task 006 can
never fire. One malformed config file takes down every connector, including the healthy ones,
and leaves no trace in the database explaining why.

By contrast `sources.yaml` is read inside `discover()`, which already runs within the guarded
boundary. The two configs currently have different blast radii for no principled reason.

---

## Scope

Registration yields connector **classes**; the orchestrator constructs instances inside its
per-connector failure boundary.

1. `discover_connectors()` returns `tuple[type[Connector], ...]` rather than instances. Key
   uniqueness and non-emptiness are still validated — `key` is a class attribute, so this needs
   no instantiation.
2. The orchestrator constructs each connector inside its existing `try`. A construction failure
   resolves the `source` row by the **class-level** `key`, records the failure through the
   task-006 typed columns, and continues to the next connector.
3. Call sites updated: `tests/test_contracts.py` instantiates before calling
   `contract_raw_docs()` and `contract_signals()`; `tests/test_orchestrator.py`'s registry test
   still reads `.key` off the class.

Do **not** move configuration loading into `parse()`. Parser purity is not negotiable and
Codex was right to reject that route.

---

## Out of scope

- Changing the `Connector` ABC method signatures. `discover()` and `parse()` are unchanged.
- Lazy or cached config loading inside the connector. Eager validation in `__init__` is correct
  behaviour once construction happens in the right place.
- Any change to `birac_big` beyond what call-site updates require.
- Ingestion, the review UI, resolution, scoring.

---

## Acceptance criteria

1. `discover_connectors()` returns connector classes. `REGISTERED_CONNECTORS` holds classes.
   State the new type annotation.

2. Duplicate-key and empty-key validation still happens at discovery, without instantiating.
   The existing error messages naming both colliding classes are preserved — show them.

3. The orchestrator constructs each connector inside its per-connector `try`. Quote the code.

4. **The test this task exists for.** A connector whose `__init__` raises does not prevent other
   connectors from running, and its failure is recorded on its `source` row with
   `health_status = 'failed'`, `consecutive_failures` incremented, and `last_error` populated.
   Assert all four.

5. A test proves that importing `src.connectors` succeeds even when a connector's constructor
   would raise. This is the regression that closes the reported bug — state explicitly how it
   simulates a broken constructor.

6. `tests/test_contracts.py` still exercises the real `birac_big` connector and its 102 signals.
   Report the count to confirm nothing was lost in the call-site change.

7. Existing task-004 failure-isolation tests pass. If any needed changing, say which and why —
   a test changing to accommodate a structural fix deserves scrutiny.

8. **ADR-020** in `docs/DECISIONS.md`: connector registration is non-instantiating, and
   construction occurs inside the orchestrator's per-source failure boundary. Reason: eager
   construction at import time places connector-specific I/O outside the isolation boundary and
   converts a single malformed config into a total pipeline failure with no database record.
   State what would be required to reverse it.

9. `AGENTS.md` rule 5 gains one sentence: connector **construction**, not merely `discover()`
   and `parse()`, happens inside the orchestrator's failure boundary; registration must not
   instantiate.

10. `uv run pytest` and `uv run ruff check .` pass. Report counts before and after.

11. `PROGRESS.md` session entry.

---

## Files expected to change

```
src/connectors/base.py            discover_connectors returns classes
src/connectors/__init__.py        REGISTERED_CONNECTORS holds classes
src/connectors/orchestrator.py    construction moved inside the try
tests/test_contracts.py           instantiate before calling contract fixtures
tests/test_orchestrator.py        registry and construction-failure coverage
AGENTS.md                         rule 5 sentence
docs/DECISIONS.md                 ADR-020
PROGRESS.md
```

---

## Risks

- **Instantiating somewhere else at import time.** If `tests/test_contracts.py` or any module
  builds instances at import, the bug moves rather than closes. Criterion 5 is the check.
- **Losing the duplicate-key guard.** It currently runs during instantiation. Class attributes
  make it equally checkable, but it is easy to drop while refactoring. Criterion 2 exists for
  this.
- **Weakening a task-004 isolation test to fit.** Criterion 7 asks for any such change to be
  declared.
- **Treating this as theoretical.** The trigger is one malformed line in `scoring.yaml`, a file
  a human will hand-edit to tune weights. It is among the more likely failures in the system,
  and its current blast radius is total.
