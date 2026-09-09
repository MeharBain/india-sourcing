# 005 — Product reconciliation with feasibility findings

**Status:** complete
**Branch:** task/005-product-reconciliation
**Depends on:** 004 (connector contract) merged first, to avoid a `PROGRESS.md` conflict.
Task 004 claims **ADR-014** for the bio/medtech v1 scope decision, so this task starts at
ADR-015. Verify 014 is present and is the scope ADR before appending.

---

## Intent

Between 2026-09-01 and 2026-09-09 a feasibility and precision investigation was run outside
the repository. Its findings invalidate the product's central quantitative assumption and two
concrete scoring rules that are currently committed. The repository is about to become the
sole source of truth, so those findings must land before the switch or they are lost.

The headline: **the lead-time thesis is wrong by roughly a factor of five.** The PRD claims
grant-stage signals appear 9 to 18 months before an institutional round. Measured, the gap
between incorporation and first institutional round is five to thirteen years.

This task is documentation only. No source code changes.

---

## Scope

Land the feasibility findings, correct the documents they invalidate, record the new
decisions as ADRs, and establish the `docs/tasks/` convention.

---

## Out of scope

- Any change under `src/`, `tests/`, `migrations/` or `config/`
- Rebuilding the scoring model. This task disables what is wrong; it does not design a
  replacement.
- Running or extending the feasibility test itself
- Touching `config/sources.yaml` tiering. The source-priority implications are real but need
  more than n=2 to act on.

---

## Acceptance criteria

1. `docs/FEASIBILITY_TEST.md` exists, committed verbatim from the content supplied with this
   task. Its first line is `# Phase 0 feasibility test: lead-time validation`.

2. `docs/tasks/README.md` exists, committed verbatim from the content supplied with this task.

3. `PRD.md` header shows `**Status:** Draft v0.2` and `**Last updated:** 2026-09-09`.

4. `PRD.md` section 1 no longer contains the string `9 to 18 months earlier`. The paragraph
   beginning "The product bet is" is replaced with exactly:

   > The product bet is **lead time**, and the measured lead time is far longer than first
   > assumed. Incumbents cover companies after incorporation, after a website, after press.
   > Grant and incubator records make Indian deeptech companies visible **five to thirteen
   > years** before their first institutional round — see `docs/FEASIBILITY_TEST.md`. Detection
   > is therefore not the hard problem. Ranking is: at any moment roughly eight BIRAC BIG
   > cohorts are simultaneously live, and only an estimated 10–20% of grantees ever raise
   > institutional equity. The product's value is in identifying which of a persistent
   > watchlist are approaching a raise.

5. `PRD.md` section 8, the **Component: timing** block, is replaced entirely with:

   > ### Component: readiness (max 15 pts) — DISABLED, weight 0
   >
   > This component previously scored months elapsed since the funding-clock signal, peaking at
   > 12–20 months. That curve was built on the assumption of a 9-to-18-month lead time and is
   > refuted by `docs/FEASIBILITY_TEST.md`. A company four years past its BIG grant may be at
   > exactly the right moment.
   >
   > **Weight is 0 until a readiness model is built from data.** Maximum achievable score is
   > therefore 85, not 100. Do not redistribute these points to other components; doing so
   > would silently inflate every score.
   >
   > The readiness signals to model, from worked case 2 in the feasibility document, are
   > regulatory clearances arriving (CDSCO, US FDA, CE), first published clinical study,
   > distributor or partner networks appearing, and headcount inflection. None are currently
   > in `config/sources.yaml` above Tier 3. Building this is a future task.

6. `PRD.md` section 8 **Suppressors (hard)** is replaced entirely with:

   > - Already raised institutional seed or later → suppress from digest, keep in graph
   > - No signal of any kind in the last 36 months → suppress
   > - Sole director, no team, and no signal in 36 months → suppress
   >
   > The former suppressor "incorporated over 4 years ago with no signal in the last 24
   > months" has been **removed**. It would have suppressed Ayati Devices, which raised its
   > first institutional round 7.5 years after incorporation and is the strongest validating
   > case found. Company age is not evidence of anything in Indian deeptech.

7. `PRD.md` section 12, the paragraph beginning "**The metric that matters", is replaced with:

   > **The metric that matters: precision on the readiness ranking.** Of the top 10 companies
   > surfaced in a weekly digest, how many raise institutional capital within 18 months?
   >
   > Lead time is no longer the headline metric. It is measured at five to thirteen years and
   > is not the constraint. Detection is solved; ranking is not.

8. `docs/DECISIONS.md` contains four new ADRs, numbered **015 through 018**, each following the
   existing Decision / Reason / To reverse structure:

   - **ADR-015:** Lead time from incorporation to first institutional round is 5–13 years, not
     9–18 months. Evidence: Innovodigm ~5y, Ayati Devices 7.5y, Bioscan Research 9–13y.
   - **ADR-016:** The timing component is disabled at weight 0 rather than re-tuned, because
     n=3 is insufficient to fit a curve and a wrong curve is worse than none. Maximum score
     becomes 85; points are not redistributed.
   - **ADR-017:** Individual and faculty BIRAC BIG awardees are under a contractual obligation
     to incorporate within the 18-month grant term. This makes the watchlist a
     near-deterministic prediction with a known window and a known founder name, and is the
     product's most defensible feature.
   - **ADR-018:** Inclusion in any validation set is determined by **first institutional
     equity round**, never by company age. Age filters reject exactly the companies the
     tracker exists to find.

9. `docs/CODEX_KICKOFF.md` has a new block immediately after its H1, reading exactly:

   > **HISTORICAL — superseded 2026-09-09.** The numbered prompts below describe tasks 001–004,
   > which are complete. They are retained as a record of how the project was bootstrapped.
   > **Tasks now live in `docs/tasks/`.** Do not take instructions from this file.

10. `AGENTS.md` has a new `## Tasks` section, placed immediately before `## Git operations`,
    reading exactly:

    > Work is specified in `docs/tasks/NNN-slug.md`. Read `docs/tasks/README.md` for the
    > convention before starting any task.
    >
    > - Implement against the task's acceptance criteria. Do not expand scope beyond them.
    > - Report against each criterion individually on completion: met, not met, or partially
    >   met, with specific evidence. Partially met is an acceptable answer.
    > - A product or architecture question known before you act is a **blocker**, not an
    >   assumption. Follow the blocker protocol in `docs/tasks/README.md`: append to the task
    >   file, set status blocked, commit the task file alone to `main`, and stop.
    > - `docs/CODEX_KICKOFF.md` is historical. Do not take instructions from it.

11. `PROGRESS.md` gains a `## Current position` block immediately below the `# PROGRESS`
    heading and above `## Current phase`, stating in plain prose: what is built, what the next
    task is, what is blocked, and what is contested. Written so a reader with no prior context
    can orient in under a minute.

12. `PROGRESS.md` gate table is updated: the lead-time gate is marked complete with the
    finding, and a new gate is added for the readiness model.

13. A session entry is appended to `PROGRESS.md` in the existing format.

14. `uv run pytest` still passes with the same count as before this task (no test changes
    expected), and `uv run ruff check .` passes.

---

## Files expected to change

```
docs/FEASIBILITY_TEST.md      new
docs/tasks/README.md          new
docs/tasks/005-product-reconciliation.md   new (this file)
PRD.md                        sections 1, 8, 12, header
docs/DECISIONS.md             ADR-015 to ADR-018 appended
docs/CODEX_KICKOFF.md         historical notice after H1
AGENTS.md                     new ## Tasks section
PROGRESS.md                   current position block, gate table, session entry
```

Nothing else. Any other file changing means something has gone wrong.

---

## Risks

- **Merge conflict in `PROGRESS.md`** if task 004 has not merged first. Sequence matters.
- **Over-correction.** The findings rest on n=3 for lead time and self-reported partner data
  for precision. The task deliberately disables rather than re-tunes. Codex should not attempt
  to fit a new curve, and criterion 5 exists to prevent that.
- **Silent point redistribution.** Setting timing to 0 leaves a 15-point hole. If anyone
  rebalances the remaining components to sum to 100, every historical score becomes
  incomparable. Criterion 5 forbids it explicitly.
- **`AGENTS.md` size.** It was 10.2 KiB before this task; Codex loads it every turn and the cap
  is 32 KiB. The new section is short. If AGENTS.md approaches 20 KiB, that is a signal to move
  reference material out.
- **Doc-only tasks feel low-stakes and get skimmed.** Two of these criteria remove rules that
  would actively suppress good companies. This is a correctness change wearing documentation
  clothing.
