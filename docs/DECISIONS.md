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
objects. They never access the database and never set `signal.company_id`; the orchestrator
persists results and the Resolve layer assigns canonical entities.

**Reason:** Pure parsers are deterministic and golden-testable, while centralized persistence
keeps source failures isolated. Entity identity requires evidence across sources and therefore
cannot be decided correctly inside one connector.

**To reverse:** A new boundary must retain pure replayable parsing, cross-source resolution,
per-source failure isolation, and full provenance without connector-owned persistence or
identity guesses.

## ADR-006: Unresolved signals retain a nullable company identifier

**Decision:** Keep `signal.company_id` nullable until entity resolution runs.

**Reason:** Signals can exist before a company is known, and some belong initially to a person
or ambiguous applicant. Premature attachment would turn an uncertain match into a stored fact.

**To reverse:** Every source must provide a canonical company identifier at extraction time, or
the schema must gain a more general unresolved-entity representation preserving uncertainty.

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
rows cannot be deleted. `signal.company_id` is the single permitted signal mutation and is
owned exclusively by `resolve/`, which may assign or revise the canonical company link without
rewriting the sourced fact.

**Reason:** A blanket signal update prohibition would prevent entity resolution even though
the unresolved signal must exist before its company is known. Restricting mutation to the
resolution-owned foreign key preserves auditable source facts while keeping re-resolution
possible.

**To reverse:** Replace `signal.company_id` mutation with a separately versioned resolution
association or another auditable identity-assignment mechanism, migrate existing assignments
without losing their history, and update the Resolve boundary before tightening the trigger to
reject every signal update.
