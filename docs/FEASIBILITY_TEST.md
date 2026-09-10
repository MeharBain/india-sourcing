# Phase 0 feasibility test: lead-time validation

**Status:** partially run 2026-09-01. Protocol corrected after first three checks exposed
design flaws. Frame incomplete (11 of 20 candidates identified, 1 fully checked).

**The question:** do BIRAC, DST, incubator and patent records reveal Indian deeptech
companies 9 to 18 months before they raise institutional capital? If yes, the tracker has a
business. If no, it does not, and no amount of engineering fixes that.

---

## Corrections to the original protocol

The original spec said "20 Indian deeptech companies that raised a seed round in the last 18
months." Three flaws surfaced immediately.

### 1. "Seed round" does not mean "early-stage company"

**Case that exposed it — Bioscan Research.** Raised $1M "seed" in July 2026. Also: founded
2013 (Inc42, Crunchbase, CB Insights) or incorporated 2017 (press releases), ₹13.4 Cr revenue
in FY25, 19 employees, and prior backing from MedTech Innovator Asia Pacific, WE Hub, the
Startup India CRPF Grand Challenge, Qualcomm Design in India Challenge and Zone Startups
India.

A nine-to-thirteen-year-old company with ₹13 Cr revenue is not a pre-seed opportunity. It
would score as a detection *success* — it appears in challenge and accelerator records going
back years — while being worthless to the fund. Companies like this inflate the hit rate with
false comfort.

**Fix: mandatory inclusion filter.**

| Criterion | Threshold |
|---|---|
| Incorporated | Within 5 years of the round date |
| Prior institutional equity | None before this round (grants, challenges and accelerators are fine and expected) |
| Revenue at round | Under ₹3 Cr, or undisclosed and plausibly pre-revenue |
| Round size | Under $3M |
| Sector | Deeptech: bio, medtech, defence, space, materials, semiconductors, robotics, climate hardware. **Exclude** fintech, SaaS, consumer, D2C, and "AI" that is an application wrapper |

Record every rejected company and the reason. The rejection rate is itself a finding: if
most Indian "seed" deeptech rounds fail these filters, the addressable pre-seed population is
smaller than the headline deal count suggests, which matters for market sizing.

### 2. Founding date is ambiguous, so lead time needs a fixed denominator

Bioscan is 2013 or 2017 depending on source. Press-reported founding dates are unreliable.

**Fix:** lead time is measured as `round_announcement_date − earliest_dated_alt_data_signal`.
Use MCA incorporation date only as a sanity check on the age filter, never as the signal date.
If a signal cannot be dated, it does not count as a signal.

### 3. Knowing a company was incubated proves nothing about timing

Funding coverage routinely states incubation status. BAAS Technologies is described as
incubated by SINE IIT Bombay, ARAI-AMTIF and AIC-JKLU in its own pre-seed announcement.
InspeCity is described as IIT-Bombay-incubated in its round coverage.

That is not lead time. That is the press telling you something at the moment of the round —
exactly when it has no value. The real question is whether the company was **publicly
discoverable on the source at time T minus 12 months.**

**Fix: Wayback Machine is mandatory, not optional.** For every incubator-portfolio or
grantee-list hit, retrieve dated snapshots from `web.archive.org` of that specific page and
find the earliest snapshot containing the company. A hit with no dated snapshot is recorded as
**undated** and excluded from the lead-time median.

This is the step that makes the test slow and the reason it is not a two-day task done
rigorously. Budget four to five days.

---

## Per-company method

For each company passing the filter, work through in this order and record dates:

1. **Round date and size** — from funding press. This is T₀.
2. **BIRAC** — search the BIG awardee PDFs (BIG-16 through BIG-24 on birac.nic.in) for the
   company name *and* each founder name individually. Founders appear as individuals in
   roughly 35% of BIG entries, so a company-name-only search will miss them.
3. **Incubator portfolio** — identify the likely institution from founder background, then
   check that incubator's portfolio page. Then **Wayback that page** and find the earliest
   snapshot listing them.
4. **DST NIDHI** — check the PRAYAS compendium PDFs and the relevant PRAYAS Centre. Low
   expected hit rate; there is no central grantee list.
5. **Patents** — search the company and each founder as applicant or inventor. Record the
   **filing date**, not the publication date. Remember publication lags filing by 18 months,
   so a patent visible today was filed a year and a half ago.
6. **iDEX / state schemes** — only for defence and hardware.

**Record the earliest dated signal across all sources.** Lead time in months is
T₀ minus that date.

---

## Worked case 1 — Innovodigm (medtech, passes filter)

The first company checked end to end. **n=1, so this proves nothing on its own**, but it
already challenges the source ranking in the PRD.

**Profile.** Kolkata-based, deep-tech spin-off from IIT Kharagpur's Microelectronics and MEMS
Lab. Developing India's first Microneedle Array Patch — a skin-dissolvable, painless,
waste-free vaccine delivery system whose thermostabilised vaccines stay viable up to 120 days
at 40°C, removing cold-chain dependency. Founders Jhimli Manna (materials scientist at the
MEMS Lab) and Ayan Chatterjee (then a research scholar), with lab head Tarun Kanti
Bhattacharya as advisor.

**Filter:** PASSES. Founded 2020, round ₹5.5 Cr (~$635K), no prior institutional equity,
pre-revenue, medtech.

**T₀ = 24 June 2025.** ₹5.5 Cr seed led by IAN Group (₹4.5 Cr) with PadUp Ventures.

**Signals found, by date:**

| Date | Signal | Source | Detectable when? |
|---|---|---|---|
| Pre-2020 | Manna's academic publications on microneedles and thermostable vaccines; Google Scholar lists her as IIT Kgp scientist | Google Scholar / journals | **Immediately on publication** |
| 2020 | Technology developed at MEMS Lab during COVID; company founded | Institutional / press, retrospective | Not contemporaneously |
| 2023 | **Patent filed** for the technology | IITM Shaastra reporting | **Only ~2024–25**, after the 18-month s.11A publication lag |
| 2025 | Top 2 Technology, Nano Electronics Showcase (MeitY); G20 Summit honours | MeitY / press | Same year as round — no lead |
| Jun 2025 | Seed round | Funding press | T₀ |

**Lead times:**

- Patent *filing* to round: ~18–30 months. Looks excellent.
- Patent *publication* to round: ~0–12 months. **Marginal.** The statutory lag ate most of it,
  exactly as predicted.
- Academic publication record to round: **several years.** Longest lead by far.

### What this case suggests

1. **No BIRAC hit.** The single strongest assumed source in the PRD did not surface this
   company at all. If that repeats, the whole BIRAC-first fan-out order is wrong.
2. **No incubator portfolio hit found.** It is an IIT Kharagpur spinout with its R&D lab still
   at IIT KGP, but no STEP or SIIC portfolio listing surfaced. Institutional affiliation is
   not the same as being on a scrapeable portfolio page.
3. **The earliest signal was academic, not governmental.** A named scientist at a named
   institutional lab, publishing on the exact technology, before incorporation. That is the
   arXiv/affiliation-change source currently sitting in **Tier 3** of `sources.yaml`.
4. **A directorship-network signal exists.** Google Scholar lists Manna as "Founder Director
   UniAm Pvt.Ltd" alongside Innovodigm. A second directorship is precisely what MCA DIN
   name-lookup would surface, and it corroborates founder identity across entities.
5. **Founding date conflicts again.** Press says 2020, Tracxn says 2018. Second instance of
   this in two companies checked. Treat press-reported founding dates as unusable.

### Provisional implication for source priority

If further cases follow this pattern, the ranking inverts: **academic publication and lab
affiliation become Tier 1**, patents remain a corroborating depth signal weakened by the
publication lag, and BIRAC becomes one high-precision source among several rather than the
spine. Do not act on n=1 — but check the academic-publication signal explicitly for every
remaining company, which the original protocol did not require.

**Protocol amendment:** add a mandatory step 2b — search Google Scholar and journal databases
for each founder name, and record the earliest dated publication on the company's core
technology, plus the institutional affiliation on it.

---

## Worked case 2 — Ayati Devices, and the finding that changes the product

**Profile.** Bengaluru/Mumbai medtech, diabetic foot and peripheral vascular diagnostics.
Products: Vibrasense (vibration perception threshold), Vibrasense+T, Vasosense, Angiocam
(real-time tissue perfusion imaging), PODIA Trolley. Founded by Nishant Kathpal and Pankaj
Inchulkar.

**Alt-data signals — all of them present, all of them easy:**

- **BIRAC BIG grant awardee.** Stated plainly on the company's own trade profile: awarded the
  BIRAC BIG Grant by the Government of India.
- **Incubated at SINE, IIT Bombay**, as part of the institute's translational research
  programme.
- **Also virtually incubated at CoE-IoT & AI Gurugram**, a joint initiative of MeitY, the
  Government of Haryana and NASSCOM.
- **Incorporated 9 February 2019** — a precise date, registry-derived.
- Regulatory clearances across CDSCO, US FDA, CE Mark, Sri Lanka, Malaysia, UAE. Over 10,000
  devices in 30+ countries, 1M+ screenings claimed. A published clinical study of 562 type-2
  diabetes patients comparing Vibrasense against conventional biothesiometry and nerve
  conduction studies.

**T₀ = August 2026.** ₹15 Cr Pre-Series A led by Inflexor Ventures, explicitly described as
**the company's first institutional investment**.

**Lead time from incorporation to first institutional round: 7.5 years.**

### The structural finding

Three cases, one pattern:

| Company | Incorporated | First institutional round | Gap |
|---|---|---|---|
| Innovodigm | 2020 | Jun 2025 | ~5 years |
| Ayati Devices | Feb 2019 | Aug 2026 | **7.5 years** |
| Bioscan Research | 2013 / 2017 | Jul 2026 | **9–13 years** |

**Indian deeptech bio and medtech companies survive on grants, incubators and revenue for
five to thirteen years before taking their first institutional cheque.**

This is the most important thing found in this exercise, and it breaks a core assumption in
the PRD.

### What breaks

**The 9-to-18-month lead-time thesis is wrong.** Not too optimistic — wrong in magnitude and
direction. A BIRAC BIG awardee does not raise seed 12 to 18 months later. They raise five to
eight years later, if ever.

**The timing component of the scoring model is inverted.** PRD section 8 currently scores
12–20 months since the funding-clock signal at 15 points (peak window) and 30+ months at 2
points (stale). On this evidence a company four years past its BIG grant may be at exactly
the right moment, and the 12–20 month band may be far too early. The curve needs rebuilding
from data, and until then the timing component should be disabled rather than left
backwards.

**The inclusion filter I wrote two hours ago is also wrong.** It excludes on age over 5 years,
which would have rejected Ayati — a textbook case of exactly the company this tracker should
find. Age is a red herring. Indian deeptech is simply slow.

**Corrected filter:** the criterion is **first institutional equity round**, at any company
age. Drop the age test. Relax the revenue test substantially. Keep round size under $3M and
the sector test.

### What this is good news for

The lead time is *enormous*, not marginal. Ayati was publicly identifiable as a
BIRAC-funded, SINE-incubated diabetic-foot diagnostics company for something like six years
before Inflexor wrote the first institutional cheque. No competitor is watching that long.
Detection is not the hard problem.

### What this is bad news for

**Precision collapses.** If the gap is five to eight years, then at any moment the watchlist
holds five to eight cohorts of BIG awardees simultaneously, the overwhelming majority of whom
will never raise institutionally. The base-rate problem is far worse than the PRD assumed,
and "when" becomes almost unanswerable from grant data alone.

This shifts what the product actually is. Not "catch them 12–18 months out" — that window
doesn't exist. Instead: **maintain a persistent watchlist of grant-validated deeptech
companies and detect the transition to institutional-readiness.** The signals that matter for
timing are therefore not the grant at all, but the later ones: regulatory clearances arriving,
first clinical study published, distributor networks appearing, headcount inflecting, revenue
starting. Those are EPFO, regulatory databases and clinical-trial registries — currently
Tier 3 or absent from `sources.yaml`.

**Open question this raises, and it is now the most important one:** what fraction of BIRAC
BIG awardees ever raise institutional capital? If it is 5%, a BIG-driven tracker produces
twenty false positives per hit and the digest is unusable without a strong readiness signal.
That is a precision test, and it runs in the opposite direction to this one — start from a BIG
cohort and follow it forward. **It should be run before any further build.**

---

## Precision test — what fraction of BIG grantees ever raise?

Run 2026-09-01. **No independent evaluation of BIG outcomes exists.** Every number below is
self-reported by BIG Partners in promotional material, so treat all of it as an **upper
bound** — partners have every incentive to present favourably.

### The numbers found

**C-CAMP** (Bangalore, the largest and probably strongest BIG Partner):
- Supported **over 150 startups** through the BIG scheme
- **Over 50 startups have received follow-on funding, including private investment**, totalling
  more than ₹500 crore
- Over 75 patents filed; more than 15 healthcare/life-sciences products

→ Implies roughly a **33% follow-on rate**.

**Venture Center** (Pune, BIG Impact report Dec 2022):
- **50+ grantees have raised more than ₹160 Cr** in follow-on funding
- Of 67 closed projects, **75% of grantees have commercial products**
- Denominator not stated in available material

### Why 33% is too generous

1. **"Follow-on funding, including private investment" is not institutional equity.** It
   plausibly includes further BIRAC schemes (SEED, LEAP, BIPP), CSR grants, state schemes and
   angel money. Venture Center's own page notes it works with 20+ CSR grantors and runs
   multiple fellowship, grant and seed programmes — all of which would count.
2. **C-CAMP is the best case, not the average.** Bangalore location, strongest network,
   largest throughput. The other seven partners will be worse.
3. **Self-reported and undated.** No cohort-level breakdown, so mature and recent cohorts
   cannot be separated.

**Working estimate: 10–20% of BIG grantees ever raise institutional equity.** Possibly lower.
This is an estimate, not a finding. Revisit if better data appears.

### What that means — the volume math

- BIG runs two calls a year (1 January and 1 July), open ~45 days
- BIG-24 had 51 awardees; assume ~100 awardees per year
- Given the 5-to-8-year gap to first institutional round, roughly **8 cohorts are
  simultaneously live** on the watchlist
- Steady-state watchlist: **~800 entities**
- At a 15% eventual institutional-raise rate: ~120 will eventually raise, spread over years
- Implies roughly **15–20 institutional rounds per year emerging from the BIG pool**

**Verdict, and it beats the 5% worst case:** 15–20 qualified opportunities a year from a
single source is real deal flow for a fund doing four to six deals annually. The pool is
navigable.

**But only with a readiness ranking.** An 800-row undifferentiated watchlist is useless. The
product's value is entirely in ranking *which* of the 800 are approaching a raise — the
readiness-signal problem from worked case 2, not the grant signal itself.

### The strongest finding of the whole exercise

From BIRAC's scheme guidelines and partner FAQs:

- **Faculty applicants must create a startup within the 18-month BIG term.** Those unwilling
  are directed to other BIRAC faculty schemes instead.
- **Employed applicants must undertake to terminate their employment** and go full-time if
  selected.
- **Individual applicants receive funds into a separate, dedicated, auditable no-lien
  account**, disbursed against milestones via the BIG Partner.

So an individual or faculty BIG awardee is under a **contractual obligation to incorporate
within 18 months of the award.**

This converts the watchlist from a guess into a near-deterministic prediction. For every
individual-type BIG awardee you know: a company will very likely be incorporated, within a
known 18-month window, under a known founder name.

Monitoring MCA new incorporations against that specific name list is high-yield, narrowly
scoped and cheap. **This is the most defensible feature in the product**, and it depends on
the Person spine and the watchlist table — both already built.

### Other scheme mechanics worth encoding

- ₹50 lakh over up to 18 months, four milestone instalments (max 30% / 30% / 30%, final
  5–10% on completion). A mid-term progress signal exists in principle.
- Scores in the awardee PDFs are the **geometric mean of individual TEP expert scores**.
  Where present, that is BIRAC's own quality ranking, free.
- Evaluation criteria: unmet need, value proposition, technical viability, team strength.
- **Grantees pay 5% royalty on net sales** until royalties equal the grant disbursed. BIRAC
  therefore holds commercialisation data on successful grantees; worth checking whether any
  is public.
- Currently 8 BIG Partners, a subset of BioNEST bio-incubators. Current BioNEST list at
  `birac.nic.in/bionest.php` — another meta-source.

### Ecosystem scale, for market sizing

India went from fewer than 50 biotech startups in 2012 to 6,300+ in 2022, and the India
BioEconomy Report 2026 puts the count at **11,855 biotechnology startups**, with the
BioEconomy above $195 billion and 4.8% of GDP. A BIG-grantee pool of ~800 live entities is a
highly selective ~7% slice of that population. Selectivity is the filter you are buying.

---

## Remaining frame candidates (bio/medtech)

Identified but not yet checked. Note the corrected filter — do not reject on age.

| Company | Round | Date | Notes |
|---|---|---|---|
| Lamark Biotech | $759K pre-Series A | ~Jul 2025 | Thermostable insulin. IAN Group, IAN Alpha Fund, BioAngels |
| BioDimension | ₹8 Cr | Jun 2026 | Bengaluru. IAN Angel Fund led |
| CrisprBits | $3M pre-Series A | — | **Check BIRAC first** — "CrisprBits Private Limited" appears as a company-type applicant in BIG cohort data |
| Perkant Tech | ₹6.6 Cr seed | — | Indore. YourNest, plus ₹1 Cr from Atal New India Challenge (NITI Aayog) *inside the round*. Founded 2020 |
| GrivaVision | TDB-backed | ~2026 | Cervical cancer screening. TDB is a Tier 1 source in sources.yaml |
| Plenome Technologies | ₹6.5 Cr seed | 2025 | IIT Madras SIE portfolio |



Generic startup aggregators (ProjectStartups, GrowthList, OpenVC) are dominated by US
companies and stale rounds. What produced usable Indian bio/medtech results:

- **BioSpectrum India** (`biospectrumindia.com`) — dedicated Indian bio and pharma trade
  publication, with sector and state tagging. Best single frame source found.
- **Entrackr, IndianStartupNews, StartupTalky daily roundups** — Indian-specific, dated.
- **Investor sites directly** — Endiya Partners, pi Ventures, Unicorn India Ventures,
  IAN Group, PadUp Ventures. Note IAN and PadUp both appear in the Innovodigm round and are
  under-represented in the original frame plan.
- **IITM Shaastra** and equivalent institutional magazines — carry technical detail and
  dates that funding press omits, including the patent filing year in this case.

Do **not** build the frame from C-CAMP, IKP or Venture Center portfolio pages. Sampling from
an incubator's portfolio guarantees an incubator hit and destroys the test.

---

## Frame progress (bio/medtech v1)

| # | Company | Round | Date | Filter | Checked? |
|---|---|---|---|---|---|
| 1 | Innovodigm | ₹5.5 Cr seed | Jun 2025 | PASS | **Complete** — see above |
| 2 | Bioscan Research | $1M seed | Jul 2026 | FAIL — age, revenue | Rejected |
| 3 | Mave Health | ₹6 Cr pre-seed | Apr 2024 | FAIL — window, and healthtech not deeptech | Rejected |
| 4 | Plenome Technologies | ₹6.5 Cr seed | 2025 | Check | No |
| — | *Target: 12 passing companies* | | | | **1 of 12** |



Built from deeptech-specialist seed investors and institutional incubator portfolios, with no
reference to grant data, to avoid selecting for the answer.

| # | Company | Round | Date | Sector | Passes filter? | Notes |
|---|---|---|---|---|---|---|
| 1 | Bioscan Research | $1M seed | Jul 2026 | Medtech | **NO** | Founded 2013/2017, ₹13.4 Cr revenue. Rejected on age and revenue. Rejection is the finding. |
| 2 | BAAS Technologies | ₹5 Cr pre-seed | Jul 2026 | Spacetech | Likely yes | Founded 2024. SINE IIT Bombay, ARAI-AMTIF, AIC-JKLU. Short window by construction — only ~2 yrs exists |
| 3 | Inbound Aerospace | >$1M pre-seed | 2025 | Spacetech | Likely yes | IIT Madras incubated, Speciale + Piper Serica |
| 4 | Plenome Technologies | ₹6.5 Cr seed | 2025 | Healthcare | Check | IIT Madras SIE portfolio |
| 5 | Susstains Engineering | ₹1.5 Cr seed | 2025 | Sustainability | Check | IIT Madras SIE portfolio |
| 6 | Green Aadhaar | ₹50 L seed | 2025 | Sustainability | Check | IIT Madras SIE portfolio |
| 7 | H2LooP | Seed | ~2026 | Novel energy | Check | Speciale Invest first-time investment |
| 8 | Unmanned | Seed | Sep 2025 | Defencetech | Check | Speciale + Accel |
| 9 | InspeCity | ₹100 Cr | Aug 2026 | Spacetech | **NO** | Round too large; founded 2022. Useful as a lead-time case study, not a frame member |
| 10 | Grow Your Farm | ₹32 L seed | 2025 | Agritech | Check | IIT Madras SIE. Agritech may fail sector filter |
| 11 | Urban Matrix | ₹6 Cr | 2023 | Dronetech | **NO** | Outside 18-month window |

**Frame gaps to fill (target 20 passing companies):** bio and pharma are badly
under-represented, which is a problem because BIRAC is the strongest expected source. Work
the portfolios of pi Ventures, Endiya Partners, IvyCap, Inflexor, YourNest, 100X.VC and
Unicorn India Ventures, plus C-CAMP, IKP Knowledge Park and Venture Center portfolio pages
for companies that subsequently raised.

---

## Decision rule

Computed only over companies passing the filter, using dated signals only.

| Result | Action |
|---|---|
| 15+ of 20 with 9+ months dated lead | Premise validated. Proceed as planned. |
| 8–14 | Proceed, but cut the source list to whichever sources actually produced the hits. Re-rank the connector fan-out order accordingly. |
| Under 8 | **Stop.** Reconsider before building further. The infrastructure built so far (storage, provenance, schema) is largely reusable for a different sourcing thesis. |

Also record, separately from the headline number:

- **Median lead time** across hits. This is the figure for a future sales deck.
- **Which source produced the earliest signal**, per company. This determines connector
  priority and is arguably more actionable than the hit rate itself.
- **Hit rate for individual-person signals** — founders appearing in a grant list before any
  company existed. This is the differentiated watchlist feature; if it never fires, the
  Person spine is over-engineered.
- **Filter rejection rate.** If most Indian deeptech "seed" rounds fail the inclusion
  criteria, the real pre-seed population is much smaller than headline deal counts imply.

---

## Known biases in this frame

State them in any writeup rather than pretending they aren't there.

- **Investor-portfolio sourcing over-samples institutionally incubated companies.** Speciale
  Invest and IIT Madras SIE both skew toward companies already inside the system this tracker
  monitors. That inflates the hit rate. A properly unbiased frame would sample from *all*
  Indian deeptech rounds, including those from founders with no institutional affiliation.
- **Survivorship.** Companies that took a BIG grant and never raised are invisible here. The
  test measures recall, not precision. A source can have perfect recall and still be useless
  if it also surfaces 500 grantees who never raise. Precision needs a separate test.
- **Publication lag on patents** means recent-filing signals are structurally undetectable
  today, so patent lead time will be understated for the newest companies.

---

# Back-test: BIG-21 cohort outcomes

Started 2026-09-10. **In progress — 2 of 51 checked.** BIG-21 awarded 2022, so four years of
runway. BIG-24 (2024) is too recent to be informative; BIG-18 and BIG-19 (both 2021) are the
natural extension if the signal looks strong.

Direction is correct: start from the awardee list, follow forward to outcomes. This measures
**precision** — what fraction of grantees raise — which is the opposite of the lead-time test
above and the question that decides whether a digest is worth opening.

## Checked

### 1. Theranautilus Private Limited — HIT

`BIRAC/CCAMP01937/BIG-21/22`, score 73.19, Medical Devices. C-CAMP partner.

IISc spin-off founded 2020 by Prof. Ambarish Ghosh, Dr Debayan Dasgupta and Dr Peddi Shanmukh
Srinivas. Magnetically-controlled nanorobots for dental hypersensitivity.

**Raised $1.2M seed led by pi Ventures, November 2024**, at a ₹60 Cr valuation, with Golden
Sparrow Ventures and angels including Tracxn's Abhishek Goyal and Groww's Lalit Keshre. Five
patents secured. Human trials planned 2025.

**BIG award (2022) → institutional seed (Nov 2024) = ~2.5 years.**

### 2. Raycura Medical Technologies Private Limited — PARTIAL / grant treadmill

`BIRAC/SINE0489/BIG-21/22`, score 69.99, Medical Devices. SINE IIT Bombay partner.

Nagpur-based, founders Rohan Deshpande and Ayush Gaikwad. Product BETTER, a rehabilitation
device for stroke and paralysis recovery.

**No institutional equity round found.** In January 2026 it won IIT Bombay TIH's ATMAN 3.0
accelerator and was recommended for up to ₹1 Cr of seed support, subject to evaluation. That is
government money under NM-ICPS, not private capital.

**Four years post-BIG, still non-dilutive.** This is the category that makes precision the
binding constraint.

---

## Findings so far

### The BIG→raise gap is much shorter than the incorporation→raise gap

Theranautilus: BIG 2022 → seed Nov 2024, **2.5 years**. The lead-time test above measured
*incorporation* → first institutional round and found 5–13 years. Those are different
quantities and the tracker cares about the **grant→raise** interval, since the grant is what it
observes.

Implication for the readiness model: the window after a BIG award may be far tighter than
ADR-015 implies. Do not rebuild the timing curve on either number until more of this cohort is
checked — but note that ADR-015's 5–13 year figure answers a question the product does not
actually ask.

### Two distinct outcome classes, not a binary

Not raised / raised is the wrong frame. There are at least three:

1. **Raised institutional equity** (Theranautilus)
2. **Grant treadmill** — alive, progressing, winning further government programmes, no private
   capital (Raycura)
3. **Dormant or dead** — none confirmed yet

Class 2 is the precision problem in concrete form. Raycura looks *successful* by every
government metric and would score well on any grant-and-incubator-based model. The readiness
model must separate class 1 from class 2, and grant wins cannot be the discriminator, because
class 2 is defined by accumulating them.

### New readiness-signal source: Technology Innovation Hub accelerators

IIT Bombay's TIH runs **ATMAN**, an eight-week accelerator for hardware-heavy healthtech. ATMAN
3.0 took 173 applicants, accelerated 13, and recommended 6 for up to ₹1 Cr each on Demo Day
(January 2026). Coverage frames these programmes explicitly as validating technology *before*
private capital enters.

That is a selection event with a published shortlist, a published winner list, and a stated
position immediately upstream of institutional rounds. `config/sources.yaml` lists Technology
Innovation Hubs in Tier 1 but records nothing about their accelerator programmes. Worth
promoting and specifying properly.

Caveat from Raycura: winning ATMAN is *not* evidence of imminent private capital. It may equally
mark the grant treadmill. Which of the two it predicts is answerable only from a larger sample.

### Methodological trap: aggregator "institutional investors" includes government

Tracxn reports Raycura as having raised over 3 rounds with 3 institutional investors. The only
funding traceable is BIRAC and TIH money. **Round counts and investor counts in aggregator
profiles cannot be used as evidence of private backing.** Every outcome must be confirmed
against a named private investor and a dated announcement.

This matters beyond the back-test: any future automated outcome-tracking must not treat
aggregator round counts as a raise signal.

---

## Remaining

49 of 51 BIG-21 awardees unchecked. Eight remaining in Medical Devices: Magnimous Info Tech,
Dr Deepak Agrawal, Imrobonix, FeetWings, SunQulp Tech, Dr Prithvi Rathi, Dverse Technologies,
Babycue. Then Diagnostics (9), Industrial Biotechnology (9), Agriculture (14), Drugs (9).

Record for each: outcome class (1/2/3), named private investor and date if class 1, and any
publicly observable event in the 12 months before the raise. That last column is the readiness
model.

## Batch 2 — Medical Devices continued (4 of 51 checked)

### 3. Magnimous Info Tech Private Limited — NO PUBLIC OUTCOME FOUND

`BIRAC/SINE0492/BIG-21/22`, score **77.86 — the highest in the Medical Devices cohort**. SINE
IIT Bombay partner.

No funding announcement, no product news, no press. Absence of search results is not proof of
failure, so this is recorded as *not found* rather than class 3. Needs an MCA status check to
distinguish dormant from quietly operating.

### 4. Imrobonix Private Limited — CLASS 2, award treadmill

`BIRAC/FITT01170/BIG-21/22`, score 72.21. FITT IIT Delhi partner.

Incorporated **3 January 2022**, ROC Chennai, registered in Tenkasi/Tirunelveli, Tamil Nadu.
Founded by Iyyappan Madasamy; LinkedIn dates activity from 2020, so incorporation postdates
founding as usual. Product SurgiKot, a thumb/joystick-controlled handheld robotic surgical
device for laparoscopy.

Active and visible: StartupTN and AIC Anna University ecosystem, and in **June 2026** it won the
TT Jagannathan Safety Through Innovation Award at Startup Singam Season 2. A Crunchbase profile
exists with no funding recorded.

Four years post-BIG, collecting awards, no private capital traceable. Same shape as Raycura.

---

## Finding: BIRAC's own expert score does not predict institutional raise

| Awardee | TEP score | Outcome |
|---|---|---|
| Magnimous Info Tech | **77.86** (highest) | Nothing found |
| Theranautilus | 73.19 | **Raised $1.2M seed** |
| Imrobonix | 72.21 | Award treadmill |
| Raycura | 69.99 | Grant treadmill |

The single company that raised sits **third of four** on BIRAC's score, and the top-scoring
awardee has no traceable outcome at all.

n=4, so this is an observation and not a result. But it matters because `PRD.md` and
`config/sources.yaml` both record the Final Score column as "BIRAC's own quality ranking, free"
— implying it is a usable input. On this evidence it may rank technical merit at the proposal
stage while carrying no information about fundability, which is a different question assessed
years earlier by a panel judging science rather than commercial trajectory.

**Do not build the score into the scoring model** until the full cohort is checked. If the
pattern holds, it belongs in the payload as provenance, not as a component weight.

## Finding: SINE now runs its own VC fund

SINE self-reports 245 startups incubated, $942M raised collectively, $3.56Bn aggregate
valuation, and an 80% survival rate against a claimed 20% industry average. It has launched the
**Y Point Venture Capital Fund at roughly ₹250 Cr**, investing in ventures from IIT Bombay and
other research institutions.

Competitive implication worth recording: the incubator best positioned to see its own portfolio
early now has capital to act on it. For SINE-incubated companies specifically, a tracker
watching the same signals is downstream of an insider with a fund. That does not apply to
BIRAC's other seven partners, but it is a reason to weight partner identity rather than treat
all eight as equivalent.

## Running tally — 4 of 51

| Class | Count |
|---|---|
| 1 — raised institutional equity | 1 |
| 2 — grant/award treadmill | 2 |
| 3 — dormant or dead | 0 confirmed |
| Not found | 1 |

Too early for a rate. Note that class 2 is currently double class 1, and that class 2 companies
are the ones a grant-signal-driven digest would surface most confidently.

---

## REFRAME 2026-09-10: the product is a deal sourcer, not a funding predictor

Product owner correction, and it invalidates how this back-test was being scored.

Classes 1 and 2 were framed as hit and false positive. That is backwards. A company with
credible technical validation and **no** private capital is the target, not the error. A tracker
that only surfaced companies which had already raised would be Tracxn with a lag.

**Revised definition.** The product surfaces deeptech companies with credible technical
validation that private capital has not yet reached, and presents enough evidence per company
for a human to decide whether to take a meeting. It does not predict funding events.

**What survives the reframe.** The ranking problem. ~800 live BIG-grantee entities at steady
state, and a four-year-old with no website, one founder and no patents is not the same
proposition as an eighteen-month-old with five patents and a working device. Both are "grants,
no VC." The discriminator stops being *probability of raising* and becomes *strength of the
investment case* — which is assembling evidence rather than predicting an event, and is a far
more tractable problem. This is why the readiness model felt intractable: it was the wrong task.

**What this back-test can and cannot measure.** "Raised" is publicly observable; "investable" is
not. So outcome-tracing cannot measure the thing that matters. What it *can* measure is whether
the sources assemble a complete enough dossier per company to support the decision. That is the
revised purpose from here.

**Consequence for the BIRAC score finding above.** Less damaging than stated. If the score is
not being used to predict raises, a panel score ranking technical merit remains a legitimate
input to an investment case. Keep it; do not weight it as a raise predictor.

---

## CRITICAL FINDING: individual awardees are frequently unresolvable by name

Attempted dossier: **Dr. Deepak Agrawal**, `BIRAC/FITT01189/BIG21/22`, score 74.57, Medical
Devices, FITT (IIT Delhi) partner.

Search returns at least four distinct people of that name:

- Deepak Agrawal — IIM Bangalore, Faridabad, "Stealth Startup"
- Deepak Agrawal — IIT Bombay, Computational Technology and Medicine Lab, Cambridge-educated
- Prof Deepak Agrawal — AIIMS New Delhi, professor of neurosurgery, describes himself as a
  medical device co-inventor, Wikipedia entry, born 1970
- Deepak Agrawal — AI and data analytics, unrelated

The AIIMS neurosurgeon is the most plausible match: Delhi, medical devices, inventor, and
AIIMS–IIT Delhi collaboration is routine. **Plausible is not resolved.** Assigning the wrong
person to a watchlist entry is worse than leaving it blank.

### Why this matters more than any other finding

Roughly **35% of BIG awardees are individuals** (measured on BIG-24). ADR-017 makes the
individual-awardee watchlist the product's most defensible feature, on the basis that BIRAC
contractually obliges faculty and individual awardees to incorporate within the 18-month grant
term — giving a known founder name, a known window, and a predictable MCA incorporation event.

That only works if the name resolves to a person. For common Indian names it does not.

### What actually disambiguates

1. **The BIG partner prefix**, which the task-008 parser already extracts. `FITT` narrows to
   IIT Delhi's orbit — institution and geography. Real information, insufficient alone.
2. **MCA DIN lookup by director name**, returning the full directorship network. This is the
   disambiguator, and it is the paid API flagged in `config/sources.yaml` as the keystone for
   `mca_director_lookup`. That entry was written on reasoning; it is now concretely justified.
3. **Google Scholar / institutional affiliation**, which worked for Innovodigm's Jhimli Manna
   because the technology was distinctive. Weaker for common names.

### Consequence

Individual awardees are **not shortlist-ready without enrichment**. They should enter the graph
and the watchlist, but must not reach a shortlist until a name is resolved to a specific person
with a DIN or an unambiguous institutional affiliation.

This is a third, independent argument for the low-confidence design in task 010 and ADR-019 —
arrived at from name ambiguity rather than from classification uncertainty.
