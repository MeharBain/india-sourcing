# Shortlist schema — what a sourced company row must carry

Draft 2026-09-10. Derived from dossiers attempted during the BIG-21 back-test, not designed in
the abstract. Every field below was either obtainable for a real company or conspicuously
missing.

**Purpose.** The output is a shortlist a human works through to decide whether to take a
meeting. Gaps are tolerable; misleading confidence is not. This is not a predictor of funding
events — see the reframe in `FEASIBILITY_TEST.md`.

---

## Field groups

### Identity — blocks shortlisting if absent

| Field | Source | Notes from the back-test |
|---|---|---|
| Canonical name | BIRAC list, MCA | Wrapped and concatenated in PDFs; task 008 handles it |
| CIN | MCA | Imrobonix resolved to CIN, ROC Chennai, Tenkasi |
| Incorporation date | MCA | **Not the founding date.** Imrobonix incorporated Jan 2022, active from 2020. Every company checked showed a gap |
| MCA status | MCA | The only way to separate *dormant* from *quietly operating*. Magnimous is unresolvable without it |
| Applicant class + confidence | Parser, ADR-012/019 | Below-threshold rows must not reach a shortlist |

**Hard rule:** an individual awardee whose name has not been resolved to a specific person
(DIN, or unambiguous institutional affiliation) does not appear on a shortlist. See the
Deepak Agrawal finding — four candidate people, no resolution.

### What they are building

| Field | Source | Notes |
|---|---|---|
| One-line description | Website, incubator page, press | Obtainable for every company checked so far |
| Product name | Same | Raycura → BETTER; Imrobonix → SurgiKot; distinctive and searchable |
| Maturity | Inferred, must be evidenced | concept / prototype / animal or bench validated / clinical / regulatory cleared / commercial |
| Website live | HTTP check | Cheap, and a dead site is a strong negative |

Maturity is the highest-value field and the least structured. Theranautilus was "extensively
tested in animals, human trials planned 2025" — evidenced. Do not infer maturity from grant
stage.

### Founders

| Field | Source | Notes |
|---|---|---|
| Names | BIRAC list, MCA directors | |
| PhD / faculty | Scholar, institutional pages | Theranautilus: a physicist who worked at Harvard, plus a dentist and an engineer |
| Institution | BIG partner prefix, Scholar | `CCAMP`→C-CAMP, `SINE`→IIT Bombay, `FITT`→IIT Delhi. Free from the reference number |
| Still academically affiliated | Scholar, lab pages | Innovodigm's Jhimli Manna listed as IIT Kgp scientist *and* founder |
| Prior companies | MCA DIN network | Manna is also Founder Director of a second company. Only DIN lookup surfaces this |
| Earliest publication on the core tech | Scholar | Innovodigm's longest lead signal by years |

### IP

| Field | Source | Notes |
|---|---|---|
| Patents filed / granted | Patent Office Journal, Google Patents | Theranautilus: five patents. Meaningful differentiator |
| PCT vs India-only | WIPO | International filing implies real spend |
| Filing dates | Journal | **Filing, not publication.** 18-month s.11A lag; Innovodigm filed 2023, visible ~2024–25 |

### Validation

| Field | Source | Notes |
|---|---|---|
| Grants: scheme, date, amount | BIRAC, DST, TDB | BIG = ₹50L over 18 months |
| BIG panel score | BIRAC PDF | Keep as evidence. **Not** a raise predictor — Magnimous scored highest and has no traceable outcome |
| Incubator / partner | Reference prefix | |
| Accelerator selections | TIH, ATMAN, state programmes | ATMAN 3.0: 173 applicants → 13 → 6 funded. Raycura won it |
| Regulatory clearances | CDSCO, FDA, CE | Ayati had CDSCO, FDA, CE across 30+ countries |
| Clinical studies | Trial registries, journals | Ayati: published study, 562 patients |
| Awards | Press | Imrobonix: Startup Singam 2026. Weak alone |

### Traction

| Field | Source | Notes |
|---|---|---|
| Headcount and trend | EPFO | Bioscan showed 19 employees. Currently Tier 3 in sources.yaml |
| Revenue signal | MCA filings, press | Bioscan ₹13.4 Cr FY25 |
| Deployments / partners | Press, website | Ayati: 10,000+ devices, 30+ countries |
| Hiring | Job boards | First non-founder hire is a real inflection |

### Capital — the sharpest filter

| Field | Source | Notes |
|---|---|---|
| Institutional equity raised | Funding press | **Must be a named private investor with a dated announcement** |
| Non-dilutive total | Grant records | |
| Actively raising | Press, accelerator demo days | Highest-value single field |
| Incubator's own fund exposure | Incubator news | SINE's Y Point fund, ~₹250 Cr, sees its portfolio first |

**Aggregator trap:** Tracxn reported Raycura as 3 rounds / 3 institutional investors. The only
traceable money is BIRAC and TIH. Aggregator round and investor counts include government
bodies and **cannot** be used as evidence of private backing.

---

## Shortlist gate

A row reaches a shortlist only when:

1. Identity is resolved — CIN, or a person resolved to a DIN
2. A one-line description exists and is evidenced, not inferred
3. At least one validation signal beyond the grant itself
4. Capital status is known — specifically that no institutional equity is recorded

Everything else is enrichment that improves ranking without gating.

---

## Open questions

- What ranks two companies that both pass the gate? Probably IP depth plus product maturity
  plus founder credential, but this needs the rest of the back-test.
- Does "actively raising" have any reliable public signal, or is it only visible through
  accelerator demo days and conversation?
- Is EPFO headcount actually retrievable per company at this scale, or only in aggregate?
- What fraction of the ~800 live watchlist entities would pass the gate? If it is 400 the
  shortlist is not a shortlist.
