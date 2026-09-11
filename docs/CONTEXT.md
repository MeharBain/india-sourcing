# CONTEXT — read this first

Orientation for anyone, human or agent, arriving at this repository. Written 2026-09-11.

**This document is an index plus the things recorded nowhere else.** It deliberately does not
restate the PRD or the ADRs. Duplicated content drifts, and then there are two answers.

## Where truth lives

| Question | Authoritative file |
|---|---|
| What is the product, what are the sources, how is scoring meant to work | `PRD.md` |
| Why is anything the way it is | `docs/DECISIONS.md` — 22 ADRs. Read before proposing a structural change. |
| What has been built, what is next, what is blocked | `PROGRESS.md` |
| Rules code must obey | `AGENTS.md` |
| How work is specified and reviewed | `docs/tasks/README.md` |
| What a surfaced company row must carry | `docs/SHORTLIST_SCHEMA.md` |
| What the research actually found | `docs/FEASIBILITY_TEST.md` |
| Which sources exist and how hard they are | `config/sources.yaml` |
| How the agents divide work | `docs/AGENT_ARCHITECTURE.md` |

**When this file and any of those disagree, they win.** This one goes stale; they are maintained.

---

## 1. What the product is

A deal sourcer for Indian deeptech. It surfaces companies with credible technical validation
that private capital has not yet reached, and presents enough evidence per company for a human
to decide whether to take a meeting.

**It does not predict funding events.** A company living on non-dilutive grants with no
institutional equity is the target, not a false positive. This was a correction to an earlier
framing — see ADR-016.

v1 scope is bio and medtech only (ADR-014). The architecture stays sector-agnostic.

---

## 2. What exists and works

One connector end to end, with real data in Postgres (Neon).

- **Storage layer** — polite fetching, per-domain rate limiting, robots handling, SHA-256
  content addressing, deduplication. Offline ingestion path for committed fixtures.
- **Provenance** — enforced in CI. A signal's source URL and retrieval time are reachable via
  `signal.raw_doc_id`, never duplicated onto the signal.
- **Connector contract** — ABC, non-instantiating registry, orchestrator with per-source failure
  isolation and typed health columns. Parser purity enforced by test.
- **BIRAC BIG connector** — parses BIG-21 and BIG-24 PDFs. **102 real signals in Neon.**
- **Classification** — five applicant classes with confidence. Shape-based inference is recorded
  as low-confidence, never as fact.
- **Idempotency** — re-running adds nothing. Skip keyed on `(raw_doc_id, extractor_version)`.
- **Minimal resolution** — 65 companies, 25 persons, 25 watchlist rows, 12 signals awaiting
  human classification.

Roughly 117 tests. Migration head as of writing: `9d6f1e2a4b80`.

**Nothing renders any of this.** There is no surface. That is the largest gap.

---

## 3. What is stale or contradictory RIGHT NOW

The most important section. An agent that reads the PRD without this will build the wrong thing.

### A dangling task reference

Task 008's blocker resolution defers live listing-page discovery to "task 010". Task 010 turned
out to be classification confidence. **Discovery transport has no task number and is not
scheduled.** `discover()` currently reads URLs from `config/sources.yaml` and makes no network
call.

The recorded leaning: the listing page should become a `RawDoc` like any other fetched document
rather than a database-free side channel, because provenance for *how a URL was discovered* is
real provenance, and `big.php` changing shape is exactly the failure the immutable raw layer
exists to catch. That implies two-phase discovery and a `Connector` ABC change, which is why it
is a task and not an aside.

### Supersession does not exist

ADR-001 says a parser is corrected by bumping `extractor_version` and *superseding* old facts.
Nothing implements supersession — no column, no query distinguishing current from stale.

**Do not bump any `extractor_version` until it exists.** Doing so doubles the signals for every
affected document with no way to tell which set is current.

### Two proxy tests are presented by their names as behavioural

`tests/test_migration_protections.py` asserts the migration *defines* the immutability triggers,
not that they fire. The task-006 CHECK constraint test runs against in-memory SQLite while
production is Postgres. Both had real behaviour confirmed manually against Neon, once,
unrepeatably. They need an integration suite excluded from the default run, once CI exists.

### PRD section 13's broader build plan remains deferred

Task 017 reconciled the completed feasibility back-test and the Phase 5–6 completion gates, but
the broader phase plan predates the implemented sequence and remains deferred. Do not treat it
as the current project schedule.

---

## 4. Failure patterns specific to this project

Each of these happened. They are why the review machinery looks the way it does.

**An amendment applied in one place with dependents left stale.** Three separate blockers.
Exact-text edits verify what they name and are blind to what depends on it. Hence the sweep
requirement in `docs/tasks/README.md` — and note that a term list can itself be too narrow, which
caused the third one.

**Structured data in a column that cannot hold it.** Source health was serialised as JSON into a
VARCHAR, with a `try/except` returning 0 on a parse failure — silently resetting the escalation
counter the field existed to drive. Nothing failed. The string round-tripped fine.

**A heuristic that is empirically perfect and structurally unsound.** The applicant classifier
is correct on all 102 rows and relies on a twelve-word business-word denylist. It omits
*therapeutics*, *instruments*, *foods*, *devices*, *agroventures*. A suffix-less company with an
unlisted business word classifies as a **person**, and that corrupts the watchlist invisibly,
because a confident misclassification never reaches review. Mitigated by confidence, not fixed.
**It is not safe to generalise to more cohorts as written.**

**Green tests over the wrong product.** Sixteen tasks were specified, reviewed and passing on a
framing that turned out to be wrong. Every task was well-executed. Only a human could see it.

**Corrections becoming the work.** Four consecutive tasks were defects found by review. That
loop never exhausts, because any codebase yields corrections forever, and it feels like progress
throughout. Only deciding what to build next breaks it.

---

## 5. Domain facts that are easy to get wrong

Hard-won. Getting any of these wrong produces plausible, confident, wrong output.

**BIG award year ≠ publication date.** The reference number's year suffix is the award cycle;
the PDF appears months to a year later. BIG-21 is `/22` and was published February 2023.
`event_date` is 1 January of the reference year with `event_date_precision: "year"`;
`list_published_at` records the publication timestamp separately.

**Patent publication lags filing by 18 months** under s.11A. Patents cannot be the signal that
finds a company first. They are depth and credibility on companies found elsewhere.

**~35% of BIG awardees are individuals, not companies** — measured on BIG-24. They have not
incorporated. BIRAC contractually obliges faculty and individual awardees to incorporate within
the 18-month grant term, which makes the watchlist a near-deterministic prediction.

**Common Indian names are frequently unresolvable.** "Dr. Deepak Agrawal" returns at least four
distinct people. A third of the highest-value signal is name-only. An individual whose name has
not been resolved to a specific person **must not reach a shortlist**.

**Honorific usage varies by cohort.** All 18 of BIG-24's persons carry honorifics; BIG-21 splits
7 honorific / 8 shape-only. So the risky inference path fires unevenly — 20% of BIG-21 needs
review versus 4% of BIG-24. Do not read a clean BIG-24 run as evidence the classifier is safe.

**Aggregator round counts include government money.** Tracxn reported one company as three
rounds with three institutional investors; the only traceable funding was BIRAC and a government
innovation hub. Confirm private capital with a **named private investor and a dated
announcement**, never a round count.

**Incorporation date ≠ founding date.** Every company checked showed a gap, sometimes years,
sometimes disagreeing between sources. State which one is being reported.

**BIRAC's own panel score does not predict outcomes.** The highest scorer in the BIG-21 medical
devices cohort has no traceable outcome; the only awardee found to have raised scored third of
four. n=4. Keep the score as dossier evidence, not as a model input.

**Time from BIG award to institutional round is years, not months.** One confirmed case at 2.5
years; incorporation-to-first-round measured at 5 to 13 years across three companies. Most
grantees never raise institutionally — best estimate 10–20%, from partner self-reports that are
promotional and undated.

---

## 6. What no agent here knows

Stated plainly so it is not discovered late.

- **Domain judgement.** The classifier flaw was caught by knowing what Indian deeptech companies
  are called. Nothing in this repository encodes that.
- **Whether the framing is right.** Sixteen well-executed tasks were built on a wrong one.
- **Whether the current work is worth doing.** Correction loops are indefinitely self-sustaining
  and indistinguishable from progress from the inside.
- **What "investable" means.** "Raised" is publicly observable; investable is not. The back-test
  can measure whether a dossier assembles, never whether the company was worth the meeting.

The agent architecture makes the mechanical half reliable. It does not make the judgement half
optional. Product questions escalate — see the boundary in `docs/AGENT_ARCHITECTURE.md`.

---

## 7. Research state

Two exercises, both partial, both in `docs/FEASIBILITY_TEST.md`.

**Lead-time test** — 3 companies traced backwards from a funding round. Found the 5-to-13-year
gap that invalidated the original thesis.

**BIG-21 back-test** — **4 of 51 awardees checked.** One raised institutional equity, two are on
a grant treadmill, one has no traceable outcome. Outcomes are three classes, not two, and the
grant treadmill is the interesting one: alive, progressing, accumulating further government
programmes, no private capital. Under the current framing those are targets, not errors.

The unanswered question that matters most is in `docs/SHORTLIST_SCHEMA.md`: **what fraction of
~800 live watchlist entities would pass the shortlist gate?** If it is half, there is no
shortlist. Answerable by applying the gate to all 51 BIG-21 awardees.

Requires web access, so the `researcher` agent, not an implementer.
