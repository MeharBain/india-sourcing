# PRD: India Pre-Seed Sourcing Tracker

**Status:** Draft v0.2
**Owner:** TBD
**Last updated:** 2026-09-09

---

## 1. What this is

A sourcing system that detects Indian deeptech companies at pre-seed stage by monitoring
non-obvious public sources: government grant programmes, institutional incubators, patent
filings and corporate registry data. It surfaces a ranked weekly shortlist and a review
queue rather than a searchable database.

The product bet is **lead time**, and the measured lead time is far longer than first
assumed. Incumbents cover companies after incorporation, after a website, after press.
Grant and incubator records make Indian deeptech companies visible **five to thirteen
years** before their first institutional round — see `docs/FEASIBILITY_TEST.md`. Detection
is therefore not the hard problem. Ranking is: at any moment roughly eight BIRAC BIG
cohorts are simultaneously live, and only an estimated 10–20% of grantees ever raise
institutional equity. The product's value is in identifying which of a persistent
watchlist are approaching a raise.

**Non-goal:** being a comprehensive Indian startup database. That market is taken and the
buyer already pays for it.

---

## 2. Positioning

| Player | Covers | Gap we exploit |
|---|---|---|
| Tracxn, Venture Intelligence | Post-incorporation Indian startups, funding rounds | Weak before first round; lag on grant-stage |
| Harmonic, Specter, SourceScrub | Global alt-data pre-seed sourcing | Thin India coverage; no government grant or Indian patent layer |
| Incubator newsletters, LinkedIn | Anecdotal, per-institution | No aggregation, no scoring, no dedup |

Positioning statement: *the India layer nobody has built, because it is PDF-heavy,
fragmented and unglamorous.* The difficulty of the work is the moat.

### Candidate buyers (beyond own use)

- Indian early-stage funds (pre-seed and seed) — primary
- Global funds building an India thesis — high willingness to pay, no local network
- Accelerators and incubators wanting to see peer-institution pipelines
- Corporate VC and R&D scouting arms in pharma, chem, defence
- Government agencies themselves. BIRAC and DST have limited visibility into what happened
  to their own grantees downstream. This is worth exploring as a design partner channel.

---

## 3. Core principles (non-negotiable)

1. **Provenance on every field.** Source URL, retrieval timestamp, raw snapshot reference.
   No field exists without it. This is a sales feature, not just hygiene.
2. **Corroboration beats volume.** A company appearing in two independent source families
   is worth more than the sum of both. Scoring reflects this explicitly.
3. **Broad collection, narrow promotion.** Everything enters the graph. Only corroborated,
   in-window entities reach the digest.
4. **Shared graph, tenant-scoped workflow.** Company and signal data is shared. Scores,
   notes, status and review events are per-tenant. `tenant_id` present from migration one.
5. **Human-in-the-loop entity resolution.** Auto-merge above threshold, review queue below.
   Never attempt full automation.
6. **LLMs extract and classify; they never invent.** Any field an LLM produced carries a
   confidence value and a pointer to the source span.

---

## 3a. Pipeline layers

Six layers, strictly separated. The separation exists because parsers get rewritten many
times and re-scraping government sites each time is neither polite nor fast.

| # | Layer | Module | Responsibility |
|---|---|---|---|
| L0 | **Collect** | `connectors/` + `core/storage.py` | Discover URLs, fetch politely, persist raw bytes verbatim with a content hash |
| L1 | **Extract** | `extract/` | Raw document to typed `Signal` records. Deterministic parsers where layout is stable, LLM extraction where it isn't |
| L2 | **Resolve** | `resolve/` | Attach signals to canonical `Company` or `Person`. Blocking, feature scoring, auto-merge above threshold, review queue below |
| L3 | **Enrich** | `enrich/` | Add what the source didn't carry: MCA director lookup, website fetch, patent family expansion. **Gated and budgeted** — never runs over the whole graph |
| L4 | **Score** | `score/` | Deterministic scoring from `config/scoring.yaml`, plus the LLM thesis-fit multiplier and hard suppressors |
| L5 | **Surface** | `surfaces/` | Weekly digest and review queue app |

L3 Enrich is the layer most easily forgotten and the only one that costs money per call. It is
where the paid director API from `sources.yaml` lives, and where the watchlist (individual
grant awardees monitored for later incorporation) is evaluated. Do not collapse it into L1 or
L2.

---

## 4. Scope

### In scope for v1

- 8 to 12 source connectors (see tiering below)
- Raw document store with content hashing
- Extraction pipeline (deterministic parsers + LLM extraction for messy PDFs)
- Entity resolution with review queue
- MCA-backed canonical company identity
- Deterministic scoring model with config-driven weights
- Weekly digest (email or Slack)
- Review queue web app with labelled actions

### Out of scope for v1

- Multi-user auth and billing (schema-ready, not built)
- LinkedIn or any ToS-violating source
- Contact enrichment and outreach sequencing (Phase 6+)
- Real-time or daily refresh. Sources update monthly to quarterly; weekly batch is correct.
- Mobile app
- Any non-India geography

---

## 5. Data sources

**Tier 0 — spine.** Provides canonical identity. Build first.

| Source | What it gives | Format | Cadence |
|---|---|---|---|
| MCA company master data | CIN, incorporation date, directors (DIN), registered address, paid-up capital | Bulk download / portal | Monthly |

Every other source becomes an annotation on an MCA record. This solves roughly half of the
entity resolution problem for free.

**Correction after source audit (2026-09-01).** The spine is a *dual* spine, not a company
spine. Two findings force this:

1. A large minority of BIRAC BIG awardees are listed as **individual persons, not
   companies** and have not incorporated yet. Measured on the full BIG-24 list: about 18 of
   51 awardees, roughly 35%. NIDHI-PRAYAS accepts individual applicants too. So a
   large share of the highest-value signals cannot attach to any MCA record at the moment
   they arrive.
2. The free MCA bulk dataset **does not contain directors or DINs**. Director data requires
   either fragile portal scraping or a paid per-record API.

Consequences, reflected below and in section 7:

- `Person` is a first-class spine entity alongside `Company`, not a company attribute.
- Applicant type resolves to **five** classes, not two: private limited, LLP, OPC private
  limited, individual person, and ambiguous bare name with neither honorific nor legal suffix.
  The ambiguous class goes to review rather than being forced either way.
- Grant awardee lists can be **provisional**. BIG-24 is footnoted as subject to further due
  diligence and budget availability, so an announced awardee is not a funded awardee. Signals
  carry a `provisional` flag and are discounted in scoring until confirmed.
- A new pipeline stage, the **watchlist**: individual grant awardees with no company yet,
  monitored for a matching director appearing on a newly incorporated entity. A BIG awardee
  named as a person who incorporates fourteen months later is the single earliest signal in
  the system and is invisible to every incumbent.
- **Cost pattern:** free bulk spine plus *targeted* paid director enrichment, called only on
  entities above a score threshold or on the watchlist. Never enrich the whole graph. Hard
  monthly call budget in config.
- **Freshness risk:** the CDM portal bulk snapshot read "as on 30th June 2025" when checked
  on 2026-09-01. If that is genuinely the latest bulk release, new incorporations are not
  detectable from bulk at all and the watchlist needs the paid route. Verify first.

**Tier 1 — high signal, low volume.** Highest value per row.

| Source | Signal | Notes |
|---|---|---|
| BIRAC BIG grantees | Strongest Indian bio pre-seed signal. Technical founder, validated, predictable funding clock. | Administered via partner incubators (C-CAMP, IKP, Venture Center, FITT). Lists are scattered across partners, not centralised. |
| BIRAC SEED / LEAP / PACE | Later-stage BIRAC support | Company already past ignition |
| DST NIDHI-SSS (Seed Support) | Incubator-disbursed seed capital | Only NIDHI variant that reliably implies "will raise" |
| iDEX / SPRINT winners | Defence deeptech | Small lists, very high hit rate |
| Technology Innovation Hubs (NM-ICPS) | 25 hubs at IITs/IISc funding startups (ARTPARK, C3iHub etc.) | Publish portfolios, structurally underused |
| TDB (Technology Development Board) | Commercialisation-stage support | Larger cheques, later stage |

**Tier 2 — corroborating.** Weak alone, valuable in combination.

| Source | Signal | Notes |
|---|---|---|
| PCT filings (WIPO Patentscope) | International ambition, real IP spend | Strongest patent variant |
| Indian patent filings | Technical depth, not stage | Patent Office Journal (weekly Friday PDF) is the richest free feed; Google Patents BigQuery for structured analysis. InPASS confirmed dead end: no API, no bulk export, ~1000-result cap |

**Correction after source audit (2026-09-01).** Indian applications publish under s.11A only
**18 months after filing or priority date**. Patents therefore cannot be the signal that
finds a company first, and the PRD originally overrated them. They are a depth and
credibility signal applied to companies surfaced by grant and incubator sources. The scoring
weights in section 8 already treat patent-only signals as weak; the reason is the statutory
lag, not merely ambiguity.
| Academic assignee + inventor→director link | Spinout detection | IIT/IISc/CSIR assignee, inventor later a director of a new company |
| DST NIDHI-PRAYAS | Prototype grant | Small, early, high volume |
| Institutional incubator residents | SINE, IITM IC, IIT-K SIIC, IIT-D FITT, IISc SID, C-CAMP, Venture Center, IKP, IIT-R TIDES, IIT-H i-TIC | Low signal per row, high volume, good for founder names |
| State schemes | Karnataka ELEVATE, Kerala KSUM, Telangana T-Hub/TASK, Gujarat iHub | Regionally uneven quality |
| Trademark filings (IP India) | Brand name registered before website exists | Very early, noisy |

**Tier 3 — later phases.**

| Source | Signal |
|---|---|
| EPFO establishment data | Monthly headcount for registered companies. Growth signal unavailable anywhere else at this stage. |
| arXiv / paper affiliation change | Author affiliation flips from institution to company name. Potentially the earliest possible signal, pre-incorporation. |
| Certificate Transparency logs (crt.sh) | New domains with SSL certs |
| 100X.VC, Antler, Axilor cohorts | Exclude list or co-invest list, depending on strategy |
| DPIIT / Startup India recognition | Attribute only. Never a promotion reason. |

**Explicitly excluded:** LinkedIn and any scraped personal contact data.

---

## 6. Data model

```
tenant              id, name, thesis_doc, weight_overrides jsonb

source              id, key, name, tier, category, cadence,
                    last_success_at, health_status

raw_doc             id, source_id, url, fetched_at, content_hash,
                    storage_path, http_status
                    -- immutable, never deleted, never re-fetched to re-parse

signal              id, company_id NULL, signal_type, source_id,
                    event_date, payload jsonb, raw_doc_id,
                    confidence, extractor_version, created_at
                    -- append-only fact table; the heart of the system
                    -- company_id stays NULL until resolution runs
                    -- signals are never mutated, only re-resolved

company             id, cin UNIQUE NULL, legal_name, display_name,
                    incorporation_date, state, city, website,
                    lifecycle_status, created_at, updated_at

company_alias       company_id, name, normalized_name, first_seen_source_id

person              id, din UNIQUE NULL, full_name, normalized_name

company_person      company_id, person_id, role, source_ref, confidence
                    -- role: founder | director | inventor | employee

resolution_candidate  signal_id, company_id, match_score, features jsonb,
                      decided_by, decided_at
                      -- the review queue for entity resolution

score               company_id, tenant_id, total, components jsonb,
                    model_version, computed_at

review_event        company_id, tenant_id, user_id, action, reason,
                    created_at
                    -- action: interesting | not_for_us | already_known | data_wrong
                    -- this is the training data. Treat it as a first-class asset.
```

### Key design decisions

- **`signal` is append-only.** Parsers change; facts don't. Re-run resolution over signals
  rather than mutating them.
- **`company_id` nullable on signal.** A patent filing exists before you know whose it is.
- **`raw_doc` immutability.** You will rewrite parsers ten times. Do not re-scrape
  government sites ten times to do it.
- **`review_event` is separate from `score`.** Scores get recomputed; human judgement does
  not get overwritten.

---

## 7. Entity resolution

The problem, concretely: `Bugworks Research India Pvt Ltd` (MCA) /
`Bugworks` (incubator page) / `BUGWORKS RESEARCH INDIA PRIVATE LIMITED` (patent assignee).
Plus South Indian naming conventions that break naive matchers: `S. Ramesh` vs
`Ramesh Subramanian` vs `Subramanian Ramesh`.

**Pipeline:**

1. **Normalise.** Strip legal suffixes (pvt ltd, private limited, llp, incorporated),
   lowercase, collapse whitespace, remove punctuation.
2. **Block.** Candidate pairs must share a normalised token prefix, a city, or a director
   name. Blocking is deterministic and cheap; never run an LLM at this stage.
3. **Feature-score candidate pairs.** Jaro-Winkler on normalised name, city match, director
   overlap, domain match, date proximity.
4. **Decide.** Above 0.92 auto-merge. Below 0.70 auto-reject. Between the two, LLM
   adjudication produces a recommendation, human confirms via the review queue.
5. **Log every decision** into `resolution_candidate`. Human decisions become the tuning
   set for the thresholds.

Person matching gets the same treatment with an additional initials-expansion step
(`S. Ramesh` is a candidate match for any `Ramesh` whose other name starts with S).

---

## 8. Scoring model v0

Score is 0 to 85 per tenant while the readiness component is disabled; the nominal range is
0 to 100 and will be restored when readiness is built. Weights live in `config/scoring.yaml`
so they can be tuned without a deploy.

### Component: source strength (max 35 pts)

Take the maximum across all signals, not the sum. Multiple weak signals should raise
corroboration, not source strength.

| Signal | Weight |
|---|---|
| BIRAC BIG grantee | 0.90 |
| DST NIDHI-SSS | 0.85 |
| iDEX / SPRINT winner | 0.85 |
| BIRAC SEED / LEAP | 0.75 |
| TIH-funded startup | 0.70 |
| Academic assignee + inventor→director link (spinout) | 0.60 |
| DST NIDHI-PRAYAS | 0.60 |
| PCT filing by company under 3 years old | 0.55 |
| State scheme winner | 0.55 |
| Institutional incubator resident | 0.50 |
| Indian patent filing by company under 3 years old | 0.35 |
| Incubator portfolio listing only | 0.25 |
| Trademark filing only | 0.15 |
| DPIIT recognition only | 0.10 |

### Component: corroboration (max 25 pts)

Count **distinct source families**, not distinct sources. Grant / patent / incubator /
registry / traction are five families. Two incubator listings is one family.

| Distinct families | Points |
|---|---|
| 1 | 0 |
| 2 | 12 |
| 3 | 20 |
| 4+ | 25 |

This is the single most important component. It is what makes the system better than
reading any one source directly.

### Component: readiness (max 15 pts) — DISABLED, weight 0

This component previously scored months elapsed since the funding-clock signal, peaking at
12–20 months. That curve was built on the assumption of a 9-to-18-month lead time and is
refuted by `docs/FEASIBILITY_TEST.md`. A company four years past its BIG grant may be at
exactly the right moment.

**Weight is 0 until a readiness model is built from data.** Maximum achievable score is
therefore 85, not 100. Do not redistribute these points to other components; doing so
would silently inflate every score.

The readiness signals to model, from worked case 2 in the feasibility document, are
regulatory clearances arriving (CDSCO, US FDA, CE), first published clinical study,
distributor or partner networks appearing, and headcount inflection. None are currently
in `config/sources.yaml` above Tier 3. Building this is a future task.

### Component: IP depth (max 10 pts)

PCT filing 10, granted Indian patent 7, filed Indian patent 4, none 0.

### Component: team (max 10 pts)

Derived from patent inventors and MCA directors. PhD, IIT/IISc/IIM affiliation, prior
founder or exit, second-time founder. Capped so a strong team can't carry a weak signal.

### Component: traction (max 5 pts)

EPFO headcount delta, live website, first non-founder job posting, DPIIT recognition.

### Multiplier: thesis fit (0.0 to 1.0)

LLM classification of the company's one-line description against the tenant's written
thesis document. Applied as a multiplier to the total, not a component. A perfect-signal
company outside the thesis should score low, not medium.

### Suppressors (hard)

- Already raised institutional seed or later → suppress from digest, keep in graph
- No signal of any kind in the last 36 months → suppress
- Sole director, no team, and no signal in 36 months → suppress

The former suppressor "incorporated over 4 years ago with no signal in the last 24
months" has been **removed**. It would have suppressed Ayati Devices, which raised its
first institutional round 7.5 years after incorporation and is the strongest validating
case found. Company age is not evidence of anything in Indian deeptech.

---

## 9. Surfaces

### Weekly digest

Delivered Monday morning. Email or Slack. Fixed structure:

- **New this week** (5 to 10 companies). One line each: company, one-sentence description,
  strongest signal with date, score, why-now sentence.
- **Entering the window.** *Deferred.* This section was defined by the timing component,
  which is disabled at weight 0 (see section 8). It cannot be built until a readiness model
  exists. Do not implement a placeholder that silently returns nothing.
- **Movers.** Companies whose score changed materially, and the specific signal that caused it.
- **Needs review.** Count of pending entity-resolution decisions, linked.
- **Source health.** Any connector that failed. Non-negotiable; a silently broken scraper
  is worse than no scraper.

Every company name links to its detail view. Every claim links to its source.

### Review queue app

Three views:

1. **Triage.** One company at a time. Description, all signals with dates and source links,
   score breakdown, founders. Four actions: interesting, not for us, already known,
   data is wrong. Keyboard-driven.
2. **Resolution queue.** Candidate merge pairs with feature scores and both raw sources
   side by side. Merge, reject, or defer.
3. **Company detail.** Full signal timeline, provenance for every field, score history.

The four triage actions are the labelled dataset. Do not collapse them into a single
"seen" flag.

---

## 10. Non-functional requirements

- **Cadence:** weekly full pipeline run. Sources update monthly to quarterly; anything
  faster is wasted compute and rate-limit risk.
- **Source health monitoring:** every connector reports success/failure per run. Three
  consecutive failures escalates to the digest and to a direct alert.
- **Idempotency:** re-running the pipeline over unchanged sources must add nothing. Two
  mechanisms enforce this: content hashing deduplicates `raw_doc`, and the orchestrator
  skips parsing any raw document already parsed at the current `extractor_version`. Neither
  alone is sufficient — content hashing does not prevent a second parse of the same bytes.
- **Politeness:** respect robots.txt, rate-limit to one request per two seconds per domain,
  identify with a real user agent and contact address.
- **Cost ceiling:** LLM spend under $50/month at v1 volumes. Achieved by using
  deterministic parsers wherever format is stable and caching all extraction by
  `(raw_doc.content_hash, extractor_version, prompt_version)`. All three matter: changing the prompt changes the output even when parser code is untouched.

---

## 11. Legal and compliance

- **Government data:** generally reusable under GODL-India, including commercially, with
  attribution. **Verify per source** during Phase 0 rather than assuming. Record the
  licence terms in `sources.yaml`.
- **DPDP Act 2023:** applies to founders' personal data. Business contact information used
  for B2B sourcing is defensible. A scraped personal-email database is not. Decide this
  deliberately.
- **LinkedIn and equivalents:** excluded. Reselling data derived from a ToS-violating scrape
  is a materially different risk from using it privately.
- **Attribution:** the digest and app must display source attribution. This is both a
  licence requirement and a trust feature.

---

## 12. Success metrics

**The metric that matters: precision on the readiness ranking.** Of the top 10 companies
surfaced in a weekly digest, how many raise institutional capital within 18 months?

Lead time is no longer the headline metric. It is measured at five to thirteen years and
is not the constraint. Detection is solved; ranking is not.

Supporting metrics:

- **Recall on the golden set.** Of 50 known Indian deeptech seed rounds from the last 18
  months, how many did the system surface before the round, and how early?
- **Precision@10 on the weekly digest.** Of the top 10 surfaced, how many get marked
  "interesting" by a human?
- **Resolution accuracy.** Rate of human overrides on auto-merges. Above 5% means the
  threshold is too loose.
- **Source liveness.** Percentage of connectors succeeding on their expected cadence.

---

## 13. Build sequence

### Phase 0 — feasibility and source audit (week 1). Do not skip.

Two deliverables, both manual:

1. **Lead-time feasibility test.** Take 20 Indian deeptech companies that raised seed in the
   last 18 months. Manually check whether each appears earlier in BIRAC, DST, incubator or
   patent records, and by how many months. Record results in a spreadsheet.
   - 15+ of 20 with meaningful lead time → premise validated, proceed
   - 8 to 14 → proceed but narrow the source set to what actually hit
   - Under 8 → stop and rethink. The premise is weaker than it looks and this is a cheap
     place to discover that.
2. **Source availability audit** → `sources.yaml`. For each of ~25 candidate sources:
   URL, format (HTML/PDF/API/bulk), auth or CAPTCHA barrier, update cadence, robots and
   ToS position, licence terms, estimated rows per year, scrape difficulty 1 to 5.
   Kill or defer anything red.

### Phase 1 — vertical slice (weeks 2–3)

Postgres schema, raw doc store, **one** connector end to end (BIRAC BIG, since it's the
highest-value source and PDF-heavy enough to prove the hard path), extraction, manual
company creation, one review screen. No entity resolution yet.

Done when: a BIRAC PDF becomes a reviewable company record with working provenance links.

The point of this phase is to discover the schema is wrong. Discovering that after twelve
connectors is expensive; after one it's an afternoon.

### Phase 2 — identity and resolution (weeks 4–5)

MCA spine connector. Normalisation, blocking, feature scoring, thresholds, resolution
review queue. This is the hardest part of the system. Doing it early rather than late is
the single biggest determinant of whether the project works.

Done when: three sources naming the same company collapse to one record, with the
disagreements visible.

### Phase 3 — connector fan-out (weeks 6–7)

8 to 10 additional connectors. This is the phase to parallelise heavily with Codex, because
each connector is bounded, independently testable, and has a sibling to copy.

Done when: `sources.yaml` Tier 1 is fully covered and all connectors are green.

### Phase 4 — scoring and digest (week 8)

Scoring model from config, suppressors, weekly digest generation, source health reporting.

Done when: a digest lands in your inbox on Monday without you doing anything.

### Phase 5 — validation and tuning (weeks 9–10)

Build the 50-company golden set properly. Back-test. Measure lead time and recall. Tune
weights against results, not intuition.

Done when: you have a defensible precision figure for the readiness ranking — of the top 10
surfaced, how many raised institutional capital within 18 months.

### Phase 6+ — productisation

Auth, tenancy activation, billing, contact discovery, outreach drafting, CRM export.
Not before Phase 5 produces a defensible precision figure for the readiness ranking.

---

## 14. Risks and open questions

| Risk | Severity | Mitigation |
|---|---|---|
| Lead-time premise did not hold as stated | Resolved | Measured at 5–13 years, not 9–18 months. Product reframed around readiness ranking. See ADR-015 and `docs/FEASIBILITY_TEST.md` |
| Readiness ranking cannot be modelled | Fatal | Detection is solved; if readiness cannot be predicted the digest is unrankable. Open — no mitigation yet |
| Source availability worse than assumed (CAPTCHAs, logins, no bulk access) | High | Phase 0 audit; design for PDF-first from the start |
| Entity resolution quality caps everything downstream | High | Phase 2 early, human-in-loop, log all decisions |
| Buyer market is small (~100–200 Indian funds who'd pay) | Medium | Explore adjacent buyers: global funds, corporates, agencies |
| Government sites break silently | Medium | Source health in the digest, escalation on 3 failures |
| Incumbent adds this layer | Medium | The moat is the unglamorous PDF work; they've had years and haven't |
| LLM extraction hallucinating facts | Medium | Provenance enforced in CI; confidence thresholds; deterministic parsers preferred |

### Open questions

- Is MCA bulk data actually accessible at the granularity needed, or is it portal-only
  lookup? Determines whether the spine strategy works as designed.
- Do BIRAC BIG cohort lists exist in one place, or must they be assembled from each partner
  incubator separately?
- Google Patents BigQuery vs Lens.org vs EPFO OPS for Indian patent coverage. Which has the
  best IN assignee data and at what cost?
- Should DPIIT recognition be a connector at all, given the signal-to-noise ratio?
- Single-tenant-in-multi-tenant-schema, or genuinely activate tenancy in Phase 1?
