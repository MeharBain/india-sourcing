# Architectural decisions

This document records architecture already fixed by the product specification. Each entry
also states what evidence or replacement guarantee would be required to revisit it.

## ADR-001: Signals are append-only

**Decision:** Treat `signal` as an append-only fact table. Correct a parser by emitting new
signals with a bumped `extractor_version` and superseding old facts, never by updating a
stored signal payload.

**Reason:** Parser behavior evolves, but historical facts and their provenance must remain
auditable. Append-only history also makes re-resolution reproducible.

**To reverse:** Adopt an equally auditable versioned-fact mechanism that preserves every prior
value and can reconstruct any past pipeline run deterministically.

## ADR-002: Raw documents are immutable

**Decision:** Store fetched raw documents verbatim as immutable records. Re-parsing reads the
stored snapshot and never requires another fetch.

**Reason:** Government sources change or disappear, while parsers will be rewritten. A stable
snapshot makes extraction repeatable without repeatedly burdening the source.

**To reverse:** A replacement store must guarantee durable, content-addressed, historically
retrievable snapshots with equivalent provenance and replay behavior.

## ADR-003: Person and Company form a dual spine

**Decision:** Model `Person` as a first-class canonical entity alongside `Company`, rather than
as a company attribute.

**Reason:** Roughly 35% of audited BIG-24 awardees are people who may not have incorporated.
Forcing those signals onto companies would discard the earliest and most differentiated leads.

**To reverse:** Show that person-level pre-incorporation signals are no longer material, or
adopt an entity model that preserves them and their later company transitions without loss.

## ADR-004: Tenant scoping applies only to workflow data

**Decision:** Keep the entity graph and source facts shared. Put `tenant_id` on tenant-specific
workflow tables such as `score`, `review_event`, and future notes or statuses, but not on shared
tables or on `tenant` itself.

**Reason:** Source truth is common across customers, while thesis weights and human judgments
belong to one tenant. Establishing this boundary in the first migration avoids a later split.

**To reverse:** Adopt fully isolated source graphs or one global workflow, with a migration and
access model that prevents cross-tenant leakage or data loss.

## ADR-005: Connectors do not own persistence or entity assignment

**Decision:** Connectors only discover fetch targets and transform a `RawDoc` into `Signal`
objects. They never access the database and never set `signal.company_id` or `signal.person_id`;
the orchestrator persists results and the Resolve layer assigns canonical entities.

**Reason:** Pure parsers are deterministic and golden-testable, while centralized persistence
keeps source failures isolated. Entity identity requires evidence across sources and therefore
cannot be decided correctly inside one connector.

**To reverse:** A new boundary must retain pure replayable parsing, cross-source resolution,
per-source failure isolation, and full provenance without connector-owned persistence or
identity guesses.

## ADR-006: Unresolved signals retain nullable entity identifiers

**Decision:** Keep `signal.company_id` and `signal.person_id` nullable until entity resolution
runs, and permit at most one to be non-null.

**Reason:** Signals can exist before either canonical entity is known, and some belong initially
to a person or ambiguous applicant. Premature or dual attachment would turn an uncertain match
into a stored fact.

**To reverse:** Every source must provide one canonical entity identifier at extraction time, or
the schema must gain a more general unresolved-entity representation preserving uncertainty and
exclusive assignment.

## ADR-007: Human review history is separate from computed scores

**Decision:** Store `review_event` independently from `score`, and never overwrite human review
events through automated recomputation.

**Reason:** Scores change as signals, weights, and model versions change; human judgments are
durable labeled data and must survive those recalculations.

**To reverse:** A replacement event or versioning model must preserve the complete human
decision history while allowing scores to be recomputed freely.

## ADR-008: Patents are a depth signal, not a detection signal

**Decision:** Use patents to corroborate technical depth and credibility for entities found
elsewhere, rather than as the primary early-detection feed.

**Reason:** Indian patent applications generally publish under Patents Act section 11A only 18
months after filing or priority, removing the lead-time advantage required for discovery.

**To reverse:** Publication law or data access must provide reliable, substantially earlier
visibility that demonstrably improves sourcing lead time.

## ADR-009: LLM extraction uses a three-part cache key

**Decision:** Cache every LLM extraction by
`(content_hash, extractor_version, prompt_version)`.

**Reason:** Input bytes, extraction code, and prompt text can independently change output.
Omitting any one makes cached results stale or makes reruns incur unnecessary cost.

**To reverse:** Replace it with another complete, deterministic identity for every input that
influences model output, with equivalent replay and billing guarantees.

## ADR-010: Enrich is a distinct, budget-gated pipeline layer

**Decision:** Keep L3 Enrich separate from Extract and Resolve, and run it only for watchlisted
or threshold-qualified entities under a hard budget.

**Reason:** Enrichment adds facts absent from source documents and is the only layer with paid
per-record calls. Running it over the graph or hiding it in another stage obscures cost and
side effects.

**To reverse:** Enrichment must become cost-free and side-effect-free, or another explicit
boundary must provide the same gating, accounting, and observability.

## ADR-011: Grant awardee announcements may be provisional

**Decision:** Represent provisional status on grant signals and discount provisional awards
until funding is confirmed.

**Reason:** Lists such as BIG-24 state that awards remain subject to due diligence and budget
availability. Treating announcement as disbursement would overstate evidence and scores.

**To reverse:** Sources must publish only confirmed funded awards, or a reliable confirmation
feed must reconcile announcements before signals enter the graph.

## ADR-012: Applicant type has five classes

**Decision:** Resolve applicants conservatively as private limited company, LLP, OPC private
limited company, honorific-identified individual person, or ambiguous bare name. Route the
ambiguous class to review rather than forcing it into person or company.

**Reason:** Real grant lists mix legal entities, people, and bare names without reliable type
markers. A binary classifier would create false canonical entities and contaminate resolution.

**To reverse:** Sources must provide authoritative entity types and identifiers for every
applicant, or a validated classifier must eliminate ambiguity without reducing accuracy.

## ADR-013: Signal facts are immutable while resolution remains mutable

**Decision:** Enforce `raw_doc` immutability and `signal` append-only behavior with database
triggers. Every signal fact and provenance column is immutable after insertion, and signal
rows cannot be deleted. `signal.company_id` and `signal.person_id` are the two permitted signal
mutations and are owned exclusively by `resolve/`, which may assign or revise one canonical
entity link without rewriting the sourced fact.

**Reason:** A blanket signal update prohibition would prevent entity resolution even though
the unresolved signal must exist before its company or person is known. Restricting mutation to
the two mutually exclusive, resolution-owned foreign keys preserves auditable source facts while
keeping re-resolution possible.

**To reverse:** Replace `signal.company_id` and `signal.person_id` mutation with a separately
versioned resolution association or another auditable identity-assignment mechanism, migrate
existing assignments without losing their history, and update the Resolve boundary before
tightening the trigger to reject every signal update.

## ADR-014: V1 focuses on bio and medtech

**Decision:** Narrow v1 source coverage and thesis validation to bio and medtech. Defer
defence, space, materials, and semiconductor coverage until the bio thesis is validated,
while keeping the architecture sector-agnostic so those sectors can be added later without a
redesign.

**Reason:** BIRAC BIG is the strongest available early-stage signal and is specific to
biotechnology. A positive feasibility result in the sector with the best signal would justify
further build and later expansion; attempting broad deeptech coverage before that result would
spend effort on weaker signals without first validating the product premise.

**To reverse:** Validate the bio and medtech thesis with the agreed feasibility evidence, or
produce equivalent evidence that another sector's sources offer a stronger reason to change
the sequencing. Reversal changes source priority, not the sector-agnostic architecture.

## ADR-015: Lead time is five to thirteen years

**Decision:** Treat the observed lead time from incorporation to first institutional round as
five to thirteen years, not nine to eighteen months.

**Reason:** The feasibility cases span Innovodigm at approximately five years, Ayati Devices
at 7.5 years, and Bioscan Research at approximately nine to thirteen years. The evidence
invalidates the former short-window product assumption even though the sample remains small.

**To reverse:** Produce a larger, date-grounded validation set showing that first institutional
rounds consistently occur on a materially shorter timeline for the in-scope companies.

## ADR-016: Readiness scoring is retired

**Decision:** Retire the former timing component at weight 0 rather than re-tuning it. The
maximum achievable score remains 85, and the unused 15 points are not redistributed. Evidence
assembly replaces funding-event prediction as the product's ranking problem.

**Reason:** The component was first disabled because three observed cases are insufficient to
fit a readiness curve, and a wrong curve is worse than none. Redistributing the points would
also inflate every score and break comparability with earlier results. The later product
reframe established the deeper reason for retiring it: predicting a funding event is not the
product's job. Regulatory, clinical, distribution, team and traction evidence belongs in the
company dossier described by `docs/SHORTLIST_SCHEMA.md`, not in a timing curve.

**To reverse:** Reverse the product decision and establish that funding-event prediction is a
required job, then build and validate an explicit model version on a sufficiently large set of
companies with known first institutional equity rounds. More data alone is not sufficient.

## ADR-017: Individual BIG awards predict incorporation

**Decision:** Treat individual and faculty BIRAC BIG awardees as a near-deterministic
incorporation watchlist with a known founder name and an 18-month window.

**Reason:** Individual and faculty awardees are contractually required to incorporate within
the 18-month BIG grant term. This makes targeted monitoring for the named founder's new company
the product's most defensible feature rather than a speculative identity guess.

**To reverse:** BIRAC must remove or materially weaken the incorporation obligation, or measured
awardee outcomes must show that it does not reliably predict incorporation within the term.

## ADR-018: Validation is anchored on first institutional equity

**Decision:** Determine inclusion in every validation set by whether the round is the company's
first institutional equity round, never by company age.

**Reason:** Age filters reject exactly the slow-maturing Indian deeptech companies the tracker
exists to find. Ayati Devices first raised institutional capital 7.5 years after incorporation
and would have been incorrectly excluded by the former five-year filter.

**To reverse:** Show that company age independently predicts an out-of-scope opportunity after
controlling for prior institutional equity, without excluding relevant slow-maturing companies.

## ADR-019: Classification by name shape is recorded as low-confidence inference, never as fact

**Decision:** Record applicant classification from a conservative personal-name shape at 0.50
confidence, never as fact. Explicit legal suffixes and honorifics carry 0.95 confidence, while
names with no signal in either direction remain ambiguous at 0.30. Signals below the configured
review threshold require human confirmation before watchlist use.

**Reason:** A denylist cannot enumerate every word used by a business. A company with a
person-shaped name can otherwise be misclassified confidently as an individual and silently
enter the incorporation watchlist established by ADR-017. Preserving the useful shape prior
while exposing its uncertainty routes that dangerous error to review instead of presenting it
as source fact.

**To reverse:** Replace name-shape inference with authoritative applicant types or a validated
classifier that demonstrably eliminates this company-as-person failure mode without reducing
coverage, and retain an auditable review path for remaining uncertainty.

## ADR-020: Connector registration is non-instantiating

**Decision:** Register connector classes without instantiating them. Construct each connector
inside the orchestrator's per-source failure boundary, after resolving its source row from the
class-level key.

**Reason:** Eager construction at import time places connector-specific I/O outside the
isolation boundary. A single malformed configuration can then cause a total pipeline failure
without recording the failure on its source row or allowing healthy connectors to run.

**To reverse:** Provide a replacement lifecycle that keeps all connector-specific
initialization failures inside a per-source boundary, records each failure against the correct
source row, and continues running healthy connectors before allowing registration to construct
instances again.

## ADR-021: Extractor version is connector metadata

**Decision:** Declare `extractor_version` on each connector as class-level metadata, while
requiring every emitted signal to carry the same value.

**Reason:** The orchestrator must know a raw document's current parse version before deciding
whether to parse it. A version reachable only through `parse()` cannot inform whether to call
`parse()`, so it cannot prevent duplicate signals from unchanged bytes and unchanged code.

**To reverse:** Replace the class attribute only with another deterministic version identity
that is available before parsing, supports the `(raw_doc_id, extractor_version)` idempotency
check, and guarantees that persisted signals carry the same identity.

## ADR-022: Signal classification review is global and signal-scoped

**Decision:** Record human applicant-type classification in one global
`classification_review` row per signal. A resolved review overrides `signal.signal_type` during
resolution without mutating the signal. Pending rows have not been examined; resolved and
undecidable rows both record who reviewed them and when, while only resolved rows carry a
`resolved_class` decision.

**Reason:** Whether a source applicant is a company, person, or ambiguous is shared entity-graph
truth rather than tenant-specific workflow judgement, so duplicating it per tenant could produce
contradictory canonical entities. Keeping the decision separate preserves ADR-001's append-only
signal history, retains what the parser originally said for audit and accuracy measurement, and
allows a human correction to apply to one row without pretending the parser changed globally.
Recording examination metadata for undecidable reviews distinguishes “looked but could not tell”
from “not yet reviewed” and preserves that judgement for later re-review and labelled-data use.

**To reverse:** Demonstrate that applicant classification legitimately differs by tenant, or
replace the review row with another auditable, signal-scoped and version-preserving decision
mechanism. Any replacement must migrate existing decisions without mutating sourced signal facts,
must distinguish pending review from a completed but undecidable outcome, and must prevent
different tenants from creating conflicting shared entities from the same signal.
