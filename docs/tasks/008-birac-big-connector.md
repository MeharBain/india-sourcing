# 008 — BIRAC BIG connector

**Status:** complete
**Branch:** task/008-birac-big-connector
**Depends on:** 006 merged (orchestrator writes typed health columns). Fixtures placed by the
human before work begins — see Prerequisites.

---

## Intent

The first real connector. Everything built so far — storage, provenance, the contract, the
orchestrator — has been exercised only against synthetic fixtures and an empty registry. This
task proves the machinery works on a real government PDF, and delivers the highest-value
source in the product.

BIRAC BIG is the strongest signal available (PRD section 5, ADR-014) and the only source that
supports the watchlist feature in ADR-017.

---

## Prerequisites — the human does this first

Download both PDFs and place them, byte-unmodified, in
`src/connectors/birac_big/fixtures/`:

| Save as | URL |
|---|---|
| `big_21.pdf` | `https://birac.nic.in/webcontent/1676014626_Final_list_of_BIG_21_Awardees.pdf` |
| `big_24.pdf` | `https://birac.nic.in/webcontent/1759752792_big_24_awardees.pdf` |

Do not open and re-save them. Content hashing depends on exact bytes.

Two cohorts deliberately: **BIG-21 has a Final Score column and BIG-24 does not.** A parser
built against one silently mangles the other.

---

## Verified document structure

Read from the actual PDFs on 2026-09-10. Every item below was observed, not assumed.

### Reference number format

`BIRAC/{PARTNER}{NUMBER}/BIG-{CALL}/{YY}` where the hyphen after `BIG` **is inconsistent
within a single document**:

- `BIRAC/SINE0492/BIG-21/22` — hyphenated
- `BIRAC/FITT01189/BIG21/22` — not hyphenated

Both forms appear in BIG-21's Medical Devices section, rows 1 and 2. The correct pattern is
`BIRAC/[A-Z]+\d+/BIG-?\d+/\d+`. The trailing `22` is the calendar year, not part of the call
number.

Partner prefixes observed across BIG-18/19/21/24: `SINE`, `FITT`, `CCAMP`, `KIIT`, `VENTURE`,
`SIIC`, `IKP`, `NAARM`. Eight, consistent with BIRAC's eight BIG Partners.

### The worst hazard: reference and name concatenated

On longer partner prefixes the column overflows and the reference number runs directly into
the applicant name with **no separating whitespace**:

```
BIRAC/CCAMP01892/BIG21/22Govindkumar Balagannavar 77.06
BIRAC/CCAMP01889/BIG21/22Dr. Murali Mohan 75.19
BIRAC/VENTURE0911/BIG21/22Atre Healthtech Private Limited 74.32
BIRAC/NAARM0375/BIG21/22Dr. Praneeth Juvvi 79.77
```

A whitespace-splitting parser produces garbage on every one. The reference must be extracted
by pattern match, not by field position, and the name is what remains after it.

### Serial number placement changes mid-table

In BIG-21's Medical Devices section, rows 1, 6, 9 and 10 carry the serial inline with the
reference; rows 2, 3, 4, 5, 7 and 8 put the serial on its own line with the reference on the
next. Sections 2–5 are all inline. Do not anchor on line position.

### Category heading variants

Four forms, and singular/plural both appear **within BIG-21**:

```
Category - Medical Devices
Category- Diagnostics
Categories - Industrial Biotechnology, Clean Energy & Environment
Categories - Agriculture and allied areas
Category - Drugs and related areas
```

BIG-20 uses `Theme -` instead of `Category`. BIG-24 uses an en dash in one section. Normalise
dashes and whitespace, and accept `Category`, `Categories` and `Theme`.

### Applicant names wrap, and the score lands in two different places

Score on the same line as the wrapped remainder:
```
Raycura Medical Technologies Private
Limited 69.99
```

Score on its own line after the wrapped remainder:
```
Spotdot Bioinnovations Private
Limited
78.28
```

Both occur in BIG-21. Rejoin continuation lines before assigning fields.

### Applicant classification — honorifics are NOT reliable

Persons **with** an honorific: `Dr. Deepak Agrawal`, `Dr. Prithvi Rathi`, `Dr. Murali Mohan`.

Persons **without** one: `Govindkumar Balagannavar`, `Abhaya Kanoje`, `Pragyan Acharya`,
`Sameena Lone`, `Raaja Rajan M`, `Sangeeta Saikia`, `Tuhin Subhra Santra`, `Kamendra P Sharma`.

And in BIG-21 Drugs row 5, the applicant name is simply **`Arun`** — one word, no honorific,
no suffix.

BIG-18 shows all-caps persons (`SUSHIL SHELKE`, `JEYAVISHNU KUMARAGURUBARAN`) alongside
all-caps companies (`KRISHIVAN TECHNOLOGIES PRIVATE LIMITED`), so capitalisation carries no
information either.

Five classes, per ADR-012:

| Class | Test | Examples |
|---|---|---|
| `company_private_limited` | Ends in a Private Limited variant | `Private Limited`, `Pvt Ltd`, `Pvt.Ltd.` (no space observed in BIG-19) |
| `company_llp` | Ends in LLP | `Kissanconnect LLP`, `VeGen Labs LLP` |
| `company_opc` | Contains OPC | observed in BIG-24 |
| `person` | Honorific present, **or** matches a conservative personal-name shape | `Dr. Murali Mohan`, `Abhaya Kanoje` |
| `ambiguous` | Everything else. **Route to review.** | `Biopol Biosciences`, `Arun` |

Classify conservatively. `ambiguous` is the correct answer far more often than a guess. Do not
infer person-ness from word count.

### Scores and footnotes

Scores are one or two decimals, unpadded (`75.6`, `74.5`, `77.86`). BIG-24 has no score column
at all.

Footnote text differs by cohort. BIG-21: *subject to qualification through further due
diligence*. BIG-24 adds *and budget availability*. Both mean the list is **provisional** —
ADR-011. Detect the footnote's presence, do not string-match its exact wording.

### There are no printed section totals

BIG-21 prints no row counts, so "row count matches printed total" is not an available
invariant. Use serial contiguity instead: within each category section the serial numbers must
form an unbroken sequence from 1 to N.

BIG-21 contains 51 awardees: Medical Devices 10, Diagnostics 9, Industrial Biotech 9,
Agriculture 14, Drugs 9.

---

## Scope

1. `src/connectors/birac_big/` — `connector.py`, `parser.py`, `fixtures/`, `test_parser.py`,
   and a `README.md` per the AGENTS.md checklist.
2. `config/incubators.yaml` — partner prefix to institution mapping. Not hardcoded.
3. `config/sources.yaml` — correct the `birac_big` entry: the listing page is
   `https://birac.nic.in/big.php`, which carries BIG-15 through BIG-24 plus NER special calls.
   The `desc_new.php?id=836` guess recorded earlier is wrong. Set `verified: true`.
4. `src/connectors/base.py` — declare `contract_raw_docs()` and `contract_signals()` on the
   `Connector` ABC. See criterion 10.
5. `discover()` returns `FetchTarget`s built from URLs recorded in `config/sources.yaml`. It
   makes no network request. Filenames are unix-timestamp prefixed and follow no consistent
   convention, so they are recorded as facts, never constructed. Live listing-page discovery
   is task 010.

---

## Out of scope

- Any cohort other than BIG-21 and BIG-24. Handle only what the two fixtures contain; do not
  speculatively support BIG-15 through BIG-20 or the NER calls.
- Entity resolution. Emit signals with `company_id` unset.
- Scoring, the watchlist evaluation, and MCA lookup.
- Live network fetches. The task is complete without ever contacting `birac.nic.in`.
- Changing the scoring config or PRD.

---

## Acceptance criteria

1. Both fixtures are committed and their SHA-256 hashes reported. Confirm they are unmodified
   from download.

2. `test_parser.py` was written **before** `parser.py` and observed to fail. Report the initial
   failure output.

3. **Hand-verified rows.** These ten rows were transcribed from the source PDF by a separate
   agent and are ground truth. `parse()` must reproduce each exactly. They are chosen to span
   every hazard above.

   | Section | S.No | Reference | Applicant | Score | Hazard covered |
   |---|---|---|---|---|---|
   | Medical Devices | 1 | `BIRAC/SINE0492/BIG-21/22` | Magnimous Info Tech Private Limited | 77.86 | baseline, hyphenated ref |
   | Medical Devices | 2 | `BIRAC/FITT01189/BIG21/22` | Dr. Deepak Agrawal | 74.57 | non-hyphen ref, serial on own line, person |
   | Medical Devices | 6 | `BIRAC/SINE0489/BIG-21/22` | Raycura Medical Technologies Private Limited | 69.99 | wrapped name, score on wrap line |
   | Diagnostics | 3 | `BIRAC/IKP01613/BIG-21/22` | Spotdot Bioinnovations Private Limited | 78.28 | wrapped name, score on separate line |
   | Diagnostics | 4 | `BIRAC/CCAMP01892/BIG21/22` | Govindkumar Balagannavar | 77.06 | **concatenated**, person without honorific |
   | Industrial Biotech | 3 | `BIRAC/VENTURE0923/BIG21/22` | Biopol Biosciences | 72.03 | **ambiguous** class, concatenated |
   | Industrial Biotech | 4 | `BIRAC/CCAMP01879/BIG21/22` | Scitechesy Research and Technology Private Limited | 71.96 | wrap with no trailing space |
   | Agriculture | 8 | `BIRAC/CCAMP01858/BIG21/22` | Kissanconnect LLP | 75.6 | LLP, one-decimal score, concatenated |
   | Drugs | 3 | `BIRAC/IKP01636/BIG-21/22` | VeGen Labs LLP | 76.24 | LLP, hyphenated ref |
   | Drugs | 5 | `BIRAC/CCAMP01838/BIG21/22` | Arun | 73.32 | **single-word person name**, concatenated |

4. **Independent invariants**, asserted for both fixtures. These do not depend on anyone's
   transcription and are what actually catch layout drift:

   a. Every reference matches `BIRAC/[A-Z]+\d+/BIG-?\d+/\d+`.
   b. Every partner prefix resolves in `config/incubators.yaml`. An unknown prefix fails the
      test — it means BIRAC added a partner.
   c. Within each category section, serials form an unbroken sequence 1..N.
   d. BIG-21 yields exactly 51 rows: 10, 9, 9, 14, 9 by section in document order.
   e. No applicant name is empty, ends in a dangling legal-suffix fragment (`Private`, `Pvt`,
      `and`), or contains a newline.
   f. No applicant name contains a substring matching the reference pattern — proves the
      concatenation split worked.
   g. Every BIG-21 row has a score in 0–100; every BIG-24 row has none.

5. Applicant classification produces a distinct `signal_type` per class. Report the class
   distribution for both cohorts. `ambiguous` rows are listed individually.

5a. Every signal carries `event_date` as 1 January of the reference-number year, with
    `event_date_precision`, `event_year_source` and `list_published_at` in payload. Report the
    values produced for both cohorts.

6. Signals carry a `provisional` flag set from footnote detection, per ADR-011. Both fixtures
   are provisional.

7. `parse()` is pure and passes the existing purity boundary in `tests/test_contracts.py`.

8. `discover()` has a test asserting it returns exactly the two configured targets and makes
   no network call. `conftest.py` should enforce the latter already; assert it explicitly.

9. `config/sources.yaml` `birac_big` entry corrected per scope item 3.

10. `contract_raw_docs()` and `contract_signals()` are declared on the `Connector` ABC.
    Currently `tests/test_contracts.py` calls both but neither is declared anywhere, so a
    connector omitting them raises `AttributeError` instead of failing meaningfully. Decide
    whether they are abstract or default to empty, state which and why, and add a test proving
    a connector lacking them fails clearly.

11. `tests/test_contracts.py` now exercises a real connector rather than passing trivially.
    Report the before and after test counts.

12. `uv run pytest` and `uv run ruff check .` pass. Report counts.

13. `PROGRESS.md` session entry. Any cohort-layout surprise not listed in "Verified document
    structure" above is recorded there.

---

## Files expected to change

```
src/connectors/birac_big/__init__.py, connector.py, parser.py, README.md, test_parser.py
src/connectors/birac_big/fixtures/big_21.pdf, big_24.pdf
src/connectors/base.py            contract_raw_docs / contract_signals on the ABC
config/incubators.yaml            new
config/sources.yaml               birac_big entry corrected
tests/test_contracts.py           may need adjusting once a real connector registers
pyproject.toml, uv.lock           a PDF library will be needed
PROGRESS.md
```

A PDF dependency is expected. State which and why. Prefer `pdfplumber` unless there is a
specific reason otherwise.

---

## Risks

- **Building against BIG-24 alone and assuming BIG-21 matches.** They differ in the score
  column, footnote and heading punctuation. Criterion 3 draws every hand-verified row from
  BIG-21 for this reason.
- **Splitting on whitespace.** Works for most rows and silently corrupts every concatenated
  one. Criterion 4f exists to catch it.
- **Over-classifying as person.** `Biopol Biosciences` looks like a company and `Arun` looks
  like nothing. `ambiguous` is a correct answer; a confident wrong guess corrupts the watchlist,
  which is the product's most defensible feature.
- **Editing `expected.json` to match the parser.** The ten rows in criterion 3 are ground truth
  produced independently. If the parser disagrees, the parser is wrong until proven otherwise —
  and if it *is* proven otherwise, that is a blocker, not an edit.
- **Speculatively supporting other cohorts.** Out of scope. Nine more cohorts exist and each
  will have its own surprises; add them one fixture at a time.

---

## Blockers and questions

### 2026-09-10 — discovery transport and event-date semantics

Two decisions are required before implementation can satisfy both this task and `AGENTS.md`.

#### 1. No approved transport can implement `discover()`

Scope item 5 requires `discover()` to scrape `big.php`, while the fixed connector interface is
`discover(self)` and `AGENTS.md` requires all requests to use the shared fetch helper.
`core.storage.fetch()` cannot be used here: it requires `source_id` and a database `Session`,
writes a `RawDoc` and its bytes, and therefore would make discovery write to the database in
violation of the connector contract. Direct `urllib`, `requests`, or `httpx` access in the
connector would bypass the shared robots, identity, retry, and per-domain rate-limit policy.

Which transport should discovery use?

- **Recommended:** amend task scope and expected files to permit a public, database-free read
  helper in `src/core/storage.py`, with behavioural tests in `tests/test_storage.py`. Refactor
  `storage.fetch()` to share that helper's robots, identity, retry, and rate-limit path, and
  inject or patch the public helper in the connector's discovery test. This preserves the exact
  `discover(self)` interface and keeps persistence out of connectors.
- Alternatively, explicitly authorize a connector-local HTTP implementation and state which
  shared-policy requirements it must reproduce. This duplicates security and politeness logic
  and is not recommended.
- Changing the `discover()` signature to accept a session or persistence-aware fetcher would
  break the fixed connector contract and is not recommended.

#### 2. The PDFs do not ground `Signal.event_date`

Every `Signal` requires a non-null `event_date`, but neither fixture prints an award or
publication date. The `/22` and `/24` reference suffixes provide only a calendar year, and
inventing January 1 would create false precision. `RawDoc.fetched_at` is retrieval time, not
event time.

What should `event_date` mean for these signals?

- **Recommended:** use the UTC date encoded by the Unix timestamp prefix in the authoritative
  BIRAC artifact URL (`2023-02-10` for BIG-21 and `2025-10-06` for BIG-24), document it as the
  publication/upload-date proxy, and fail parsing if the URL does not contain that timestamp.
  This is source-grounded, deterministic, and avoids fabricated day/month values.
- Alternatively, approve a year-only convention represented as January 1 of the reference
  year, explicitly accepting the false precision.
- Using `raw_doc.fetched_at.date()` is not recommended because identical source content fetched
  on different days would receive different event dates.

### Decision — Claude, 2026-09-10

#### Blocker 1: transport for `discover()`. Descoped, not resolved.

Neither of your options is taken. The question of how discovery reaches the network is a real
architectural decision, and it deserves its own task rather than being settled inside a parser
task. One concern per task.

Live discovery is removed from task 008. `discover()` returns targets read from
`config/sources.yaml`, where the two cohort URLs are recorded as explicit facts with their
unix-timestamp filenames. It makes no network call. This is not pattern-construction — the URLs
are recorded, not derived.

Deferred to task 010, with my current leaning recorded so it is not lost: I expect the right
answer is that the listing page becomes a `RawDoc` like any other fetched document, rather than
a database-free side channel. Provenance for how a URL was discovered is real provenance, and
`big.php` changing shape is exactly the failure the immutable raw layer exists to catch. That
likely means two-phase discovery and a change to the `Connector` ABC, which is why it is a task
and not an aside. Your recommended read-helper remains the alternative and will be weighed
properly in 010.

#### Blocker 2: `event_date` semantics. Your objection is accepted; your recommendation is not.

You were right that a bare January 1 is false precision. But the URL timestamp has a worse
problem: it is not in the document. It is inferred from a CMS filename convention, and this
project's provenance principle says a field should be derivable from the snapshot the signal
cites. A value readable only from a URL string breaks silently when BIRAC changes its CMS, and
nothing in `raw_doc` would reveal it.

The reference number's year suffix is in the document, and it is the award cycle.

`event_date = 1 January` of the year in the proposal reference number — 2022 for BIG-21, 2024
for BIG-24. What removes the false precision is declaring it:
`payload.event_date_precision = "year"` and
`payload.event_year_source = "proposal_reference_number"`. An undeclared January 1 is a
fabrication; a declared year with a conventional rendering is a year.

Also record `payload.list_published_at` from the URL's Unix timestamp. It is genuinely useful
and costs nothing, and keeping it out of `event_date` means neither value is load-bearing in a
hidden way.

Do not infer the month from the call number. The even/odd pattern across BIG-18 through BIG-21
looks like it maps to the January and July calls, but that is four data points and a wrong
inference would be silently wrong. Note it in `PROGRESS.md` as worth verifying; do not encode
it.

Sweep report: `discover`/`big.php` appeared at lines 164, 168 and 233 before this amendment;
line 164 is unchanged, while lines 168 and 233 were amended above. `event_date` had zero hits,
which is why this blocked.
