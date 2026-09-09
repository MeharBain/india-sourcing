# 010 — Confidence-bearing applicant classification

**Status:** complete
**Branch:** task/010-classification-confidence
**Depends on:** 008 merged.

---

## Intent

Task 008's classifier is correct on all 102 rows of both fixtures. It is nevertheless unsafe to
generalise, and task 008's own completion report says so.

`_classify_applicant` returns `person` whenever a name has two to four alphabetic tokens, no
hyphen, and no word from a twelve-entry `_BUSINESS_WORDS` set. That set omits `therapeutics`,
`instruments`, `foods`, `devices`, `systems`, `pharma`, `agroventures` and every other business
word nobody has thought of yet. BIG-21 contains Inger Therapeutics, Leofelis Instruments,
Famnutra Millet Foods and Gohemp Agroventures; they classify correctly today only because they
carry `Private Limited`. A company without a legal suffix and without a listed business word
becomes a `person`.

**The direction of that error is what matters.** Under ADR-017, an individual awardee enters
the watchlist as someone contractually obliged to incorporate within eighteen months. A company
misfiled as a person corrupts the watchlist — the product's most defensible feature — and does
so silently, because a confident misclassification never reaches human review. The failure is
undiscoverable by using the product.

A denylist of business words is structurally a guess about the world's vocabulary. The fix is
not a longer list.

---

## Scope

Stop treating classification as a binary decision. The `Signal` model already carries a
`confidence` float; use it.

Keep all five classes from ADR-012 — no new class, no ADR change. What changes is that a
classification reached by name *shape* is recorded as low-confidence and routed to review,
while one reached by an explicit legal suffix or honorific is high-confidence.

| Basis | Class | Confidence |
|---|---|---|
| OPC / LLP / Private Limited variant present | respective company class | 0.95 |
| Honorific present (`Mr`, `Ms`, `Mrs`, `Dr`, `Prof`, `Shri`, `Smt`, with or without a full stop) | `person` | 0.95 |
| Conservative name shape only, no explicit marker | `person` | **0.50** |
| No signal in either direction | `ambiguous` | 0.30 |

The existing shape rule is **retained**, including the token-count gate. It is a reasonable
prior and it was right 102 times. It simply stops being asserted as fact.

Anything below a configured review threshold routes to human review. Default threshold 0.70,
in `config/scoring.yaml` — not hardcoded.

This resolves the spec conflict honestly. Task 008 said "do not infer person-ness from word
count"; the implementation does, and the reason it is now acceptable is that the inference is
labelled as an inference rather than removed.

---

## Out of scope

- Adding words to `_BUSINESS_WORDS`. That is the fix this task rejects.
- A sixth applicant class. ADR-012's five stand.
- The review queue UI. This task makes items reviewable; it does not build the surface.
- Changing `confidence` semantics for any other signal type.
- Re-parsing or re-scoring anything.

---

## Acceptance criteria

1. `_classify_applicant` returns a `(class, confidence)` pair, or equivalent, rather than a
   bare string. Every call site updated.

2. Confidences are exactly as tabulated above and are read from configuration, not literals in
   `parser.py`. State where they live.

3. `config/scoring.yaml` gains a `review_confidence_threshold`, default `0.70`, with a comment
   explaining that signals below it require human confirmation before use in the watchlist.

4. A test asserts the four confidence tiers using a name for each basis, including at least one
   honorific person and one shape-only person, showing they receive different confidences
   despite sharing the class `person`.

5. **The regression test this task exists for.** A test asserts that a two-token name whose
   business word is absent from `_BUSINESS_WORDS` — use `Inger Therapeutics` and
   `Leofelis Instruments`, with legal suffixes stripped — is classified `person` at confidence
   0.50 and **not** at high confidence. The test's docstring states that these are in fact
   companies, that the classifier cannot know this, and that the low confidence is what
   prevents the error from becoming a silent watchlist entry.

6. Class distributions for both fixtures are unchanged from task 008 — 51 rows each, same
   counts per class. Report them. **A changed distribution means the shape rule was altered,
   which this task does not ask for.**

7. Confidence distributions are reported for both cohorts: how many rows at each tier, and how
   many fall below the review threshold.

8. `big_21.expected.json`'s ten hand-verified rows still pass unmodified except for added
   confidence values. Report exactly what changed in that file and why.

9. The purity boundary and all task-008 invariants still pass.

10. `uv run pytest` and `uv run ruff check .` pass. Report counts before and after.

11. `PROGRESS.md` session entry. A new ADR is warranted here — propose it as **ADR-019:
    classification by name shape is recorded as low-confidence inference, never as fact**,
    with the watchlist-corruption reasoning. Write it.

---

## Files expected to change

```
src/connectors/birac_big/parser.py
src/connectors/birac_big/fixtures/big_21.expected.json    confidence values added
src/connectors/birac_big/test_parser.py
config/scoring.yaml                                        review_confidence_threshold
docs/DECISIONS.md                                          ADR-019
PROGRESS.md
```

---

## Risks

- **Lengthening `_BUSINESS_WORDS` instead.** It will look like the obvious fix and it makes the
  classifier feel better while leaving the failure mode exactly where it was. Criterion 5 is
  written to fail if this is attempted.
- **Changing the shape rule.** Not asked for. It was right 102 times. Criterion 6 detects any
  change to it.
- **Treating confidence as decoration.** If nothing consumes the threshold, this task has moved
  the problem rather than solved it. The consumer is the review queue, built next; criterion 3
  exists so the threshold is configured and discoverable when that task starts.
- **Assuming empirical success settles it.** The classifier is correct on every row we have.
  That is exactly what a silent failure looks like before it fires.

---

## Blockers and questions

*(none at creation)*
