# AGENTS.md

Instructions for AI coding agents working in this repository. Read this fully before
writing code. If a task conflicts with anything here, stop and ask rather than improvising.

---

## What this project is

A pipeline that detects Indian pre-seed deeptech companies from public government grant
lists, institutional incubator pages, patent filings and corporate registry data. It
produces a scored weekly shortlist and a review queue.

See `PRD.md` for product context and `docs/DECISIONS.md` for the reasoning behind
architectural choices. Read `docs/DECISIONS.md` before proposing a structural change.

---

## Repository layout

```
config/
  sources.yaml          source registry: URLs, cadence, licence, difficulty
  scoring.yaml          scoring weights, thresholds, suppressors
src/
  core/
    models.py           SQLModel table definitions
    provenance.py       provenance helpers, enforced everywhere
    storage.py          raw_doc read/write, content hashing
  connectors/
    base.py             Connector ABC. Do not modify without discussion.
    birac_big/
      __init__.py
      connector.py
      parser.py
      fixtures/
        2024-cohort.pdf         saved raw input
        2024-cohort.expected.json   expected parser output
      test_parser.py
    dst_nidhi_sss/
    mca_master/
    ...
  extract/
    deterministic.py    regex and table parsers
    llm.py              LLM extraction, cached by content hash
  resolve/
    normalize.py
    blocking.py
    features.py
    decide.py
  score/
    compute.py
  surfaces/
    digest.py
    app.py              Streamlit review queue
migrations/             Alembic
tests/
docs/
  DECISIONS.md
```

One directory per connector. Never put two sources in one connector module.

---

## The connector contract

Every connector subclasses `Connector` and implements exactly this interface:

```python
class Connector(ABC):
    key: str                      # matches a key in config/sources.yaml
    cadence: Cadence

    @abstractmethod
    def discover(self) -> Iterable[FetchTarget]:
        """Yield URLs to fetch. No parsing, no network writes to DB."""

    @abstractmethod
    def parse(self, doc: RawDoc) -> Iterable[Signal]:
        """Pure function. RawDoc in, Signals out. No network. No DB. No I/O."""
```

Hard rules:

1. **`parse()` is pure.** No network calls, no database access, no filesystem writes, no
   clock reads. Given the same `RawDoc` it must return identical `Signal` objects forever.
   This is what makes golden tests possible and re-parsing cheap.
2. **Connectors never write to the database.** They return `Signal` objects. The pipeline
   orchestrator persists them. A connector that imports a session object is wrong.
3. **Connectors never set `company_id`.** Entity resolution owns that. A connector that
   guesses which company a signal belongs to is wrong.
4. **Every `Signal` carries provenance.** `raw_doc_id`, `source_id`, `event_date`,
   `extractor_version`, `confidence`. There is a CI test that fails the build if any signal
   is missing these. Do not work around it.
5. **Fail loudly per-source, never globally.** A broken connector must not stop the run.
   Catch at the orchestrator boundary, record the failure in `source.health_status`, continue.
6. **Rate limit.** One request per two seconds per domain, via the shared fetch helper. Do
   not use `requests` or raw `httpx` directly; use `core.storage.fetch()`.

---

## The golden fixture rule

**No parser ships without a golden fixture.** This is the most important rule in this file.

To add or change a parser:

1. Save the real raw input into `fixtures/` (the actual PDF or HTML, unmodified).
2. Write the expected output as `<name>.expected.json`.
3. Write the test that parses the fixture and asserts equality against the expected JSON.
4. Only then write or modify the parser.

Write the test first. Government sites change their layout without warning; the fixture is
how you find out that happened, rather than silently ingesting garbage for three months.

If a fixture is too large to commit (over 5MB), store the hash and a fetch script, and note
it in the connector README.

---

## LLM usage rules

LLMs are used for two things only: extracting structured fields from unstructured documents,
and classifying (tech domain, thesis fit).

1. **The model never invents a fact.** Extraction prompts must require that every returned
   field be quotable from the input. Any field the model cannot ground gets returned as null
   with a reason, not guessed.
2. **Every LLM-derived field carries a confidence score and a source span.**
3. **All LLM calls are cached** by `(content_hash, extractor_version, prompt_version)`.
   Re-running the pipeline must not re-bill.
4. **Never call an LLM in a test.** Tests use recorded responses in
   `fixtures/llm/`. A test that hits the API is a broken test.
5. **Never use an LLM in the blocking stage of entity resolution.** Blocking is
   deterministic and runs over N² candidate pairs. LLMs only adjudicate the ambiguous band
   after blocking has narrowed it.
6. **Never use an LLM to compute a score.** Scoring is deterministic from
   `config/scoring.yaml`. The only LLM contribution is the thesis-fit multiplier, and that
   is a separate, logged, overridable value.

---

## Data model invariants

Violating these requires a `docs/DECISIONS.md` entry and explicit approval.

- `raw_doc` is **immutable**. Never update, never delete. Re-fetching produces a new row.
- `signal` is **append-only**. Parsers get corrected by writing new signals with a bumped
  `extractor_version` and marking the old ones superseded. Never `UPDATE` a signal's payload.
- `signal.company_id` is nullable and only written by `resolve/`.
- `review_event` is **never overwritten by automated processes**. Scores recompute; human
  judgement does not.
- Every **tenant-scoped** table (`score`, `review_event`, and any future notes or status
  table) carries `tenant_id`, even while
  there is one tenant. Do not "simplify" this away.
- `company.cin` is the canonical identifier where present. Prefer it over name matching
  everywhere.

---

## Testing

- `pytest`. Run `make test` before proposing any change as complete.
- Every connector needs: a parser golden test, a `discover()` test with a mocked fetch, and
  a schema-conformance test asserting all returned signals validate.
- Contract tests in `tests/test_contracts.py` run against every registered connector
  automatically. If you add a connector correctly, it is picked up with no test changes.
  If it fails there, the connector is wrong, not the test.
- Entity resolution has a labelled test set in `tests/fixtures/resolution_pairs.json`.
  Changes to `resolve/` must not regress accuracy on it. Report before and after numbers.
- No network access in any test. `conftest.py` blocks it.

---

## Forbidden patterns

Do not:

- Import a DB session inside `connectors/`
- Call `requests` or `httpx` directly outside `core/storage.py`
- Add a source to `sources.yaml` without the licence and ToS fields filled in
- Scrape LinkedIn or any source excluded in `PRD.md` section 5
- Add a field to any model without provenance
- Widen an entity-resolution threshold to make a test pass
- Add a new dependency without noting why in the PR description
- Create abstraction layers for hypothetical future sources. Three concrete connectors
  before any generalisation.
- Silently swallow an exception. Log it, record source health, re-raise or continue
  explicitly.

---

## How to add a new connector

1. Confirm the source exists in `config/sources.yaml` with licence and cadence filled in.
   If not, that comes first.
2. `cp -r src/connectors/birac_big src/connectors/<new_key>` as the reference implementation.
3. Save a real raw document into `fixtures/`.
4. Hand-write the `.expected.json`.
5. Write `test_parser.py` and confirm it fails.
6. Implement `parse()` until the test passes.
7. Implement `discover()`.
8. Run `make test`. The contract tests will pick up the new connector automatically.
9. Add a one-paragraph README in the connector directory: what the source is, where the
   list lives, what breaks when they redesign the page.

---

## Git operations

You run git in this repository. The human does not. Accordingly:

**You may:** `status`, `diff`, `log`, `add`, `commit`, `branch`, `checkout -b`, `merge`
(fast-forward or a normal merge commit), `push` to a named branch, `remote -v`, `remote add`.

**You must never, without being asked in that specific session:**

- `push --force` or `push --force-with-lease` to any branch
- `rebase`, `commit --amend`, `reset --hard`, `filter-branch`, or anything else that rewrites
  history that has already been pushed
- Delete a branch that has not been merged
- `git add .env`, any file containing a key or token, or anything matched by `.gitignore`.
  If `git status` shows a credential-bearing file as untracked, add it to `.gitignore` and say
  so rather than committing it.
- Commit directly to `main` when the change is code. Documentation and `PROGRESS.md` updates
  on `main` are fine; code goes on a `task/NN-name` branch.

**Before every commit:** run `git status` and `git diff --staged`, and state in your reply
what you are about to commit and why. If the staged set includes anything you did not
intentionally change, stop and report it instead of committing.

**Commit message format:** a short imperative subject line under 72 characters, then a blank
line, then a body explaining *why* if the reason is not obvious from the diff.

**If there is no remote configured,** report that and ask before creating one. Do not guess a
repository URL.

---

## Commit and PR conventions

- One connector or one concern per PR. A PR touching four connectors and the schema will be
  rejected.
- PR description states: what changed, what test proves it, what could break.
- Schema changes require an Alembic migration in the same PR, and a `docs/DECISIONS.md`
  entry if an invariant moved.
- Bump `extractor_version` on any parser logic change. This is how cached extraction knows
  to re-run.

---

## When to stop and ask

Stop and ask rather than proceeding if:

- A source requires authentication, CAPTCHA solving, or appears to prohibit automated access
- A change would require mutating `signal` or `raw_doc`
- Entity resolution accuracy on the labelled set drops
- A task implies scraping personal contact data
- The right implementation seems to require breaking one of the invariants above
