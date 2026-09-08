# Operating manual: running this project with Codex

Written for someone who hasn't used an agentic coding tool before. Verified against Codex CLI
as of September 2026, but these tools move fast — if a flag doesn't exist, check
`codex --help` rather than assuming this doc is right.

---

## The one mental shift

If you've used ChatGPT, your instinct is: paste files into the chat, ask for code, copy the
answer out. **Codex doesn't work that way and fighting this will cost you weeks.**

Codex reads your repository directly. You don't attach files, you *commit* them. It runs
commands, edits files in place, and runs your tests. Your job shifts from "write the code" to
"write the spec, then verify the work."

The practical consequence: **set up the repo before you open Codex.** Everything you want it
to know has to exist as a file on disk first.

---

## Step 1 — install

```bash
node --version            # need 18 or higher
npm install -g @openai/codex
codex                     # first launch opens a browser to sign in with ChatGPT
codex --version
```

Authenticating through ChatGPT rather than an API key is the easier path and gives you the
current models.

### Which Codex surface to use

There are several (CLI, desktop app, IDE extension, cloud tasks, Chrome extension). For this
project:

- **CLI is your primary tool.** It can run your tests, which is the entire point. A surface
  that can't run `uv run pytest` can't verify its own parser.
- **Desktop app is worth having alongside** if you aren't comfortable reading diffs in a
  terminal. It gives visual diff review, which is where most of your actual work happens.
- **Ignore cloud tasks and the IDE extension for now.** More surfaces means more places to
  lose track of state, and state management is the hard part of this project.

---

## Step 2 — build the repo before you prompt anything

```bash
mkdir india-sourcing && cd india-sourcing
git init
mkdir -p config docs fixtures_inbox
```

Place the files:

```
india-sourcing/
├── AGENTS.md                  # auto-loaded by Codex every session. 8.8 KiB.
├── PROGRESS.md                # session state. You and Codex both maintain this.
├── PRD.md                     # read on demand, not auto-loaded
├── config/
│   └── sources.yaml
├── docs/
│   ├── DECISIONS.md           # start empty
│   └── CODEX_KICKOFF.md       # your playbook, not Codex's
└── fixtures_inbox/            # fetched PDFs land here before being placed properly
```

**AGENTS.md must sit at the git root.** That's the anchor for Codex's discovery: it loads
`~/.codex/AGENTS.md` if you have a global one, then walks from the git root down to your
current directory, merging what it finds. Put it anywhere else and it silently won't load.

**Do not merge PRD.md into AGENTS.md.** There's a 32 KiB cap on the instruction chain, and
more importantly AGENTS.md costs context on *every single turn*. AGENTS.md is rules Codex
needs constantly. PRD.md is reference material it reads when relevant. Keeping them separate
is why AGENTS.md is 8.8 KiB and has room to grow.

Then commit the spec before any code exists:

```bash
git add -A && git commit -m "Spec: PRD, agent instructions, verified source registry"
```

This gives you a baseline. Every later diff is code measured against a stated intent.

---

## Step 3 — confirm Codex actually read your instructions

```bash
codex --print-instructions
```

This dumps the merged instruction chain it loaded. You should see your AGENTS.md content. If
you don't, you're either not at the git root or the file is misnamed.

Do this once now and again any time Codex starts behaving as if the rules don't exist.

Skip `/init`. It scaffolds a generic starter AGENTS.md, and yours is better.

---

## Step 4 — set sandbox and approval mode

This is the setting that protects you while you're still learning what Codex does.

```bash
codex --sandbox workspace-write --ask-for-approval on-request
```

- `workspace-write` — it can only write inside the repo directory
- `on-request` — it asks before running shell commands, so you see each one

Start here. Watch what it wants to run for the first few sessions. Loosen only once the
commands stop surprising you.

**Never use a full-auto or bypass mode on this project.** It runs network fetches, database
migrations, and eventually a paid API. Those are exactly the categories where an unattended
mistake costs money or corrupts data.

---

## Step 5 — your actual first prompt

Do **not** make the first prompt a build task. Make it a comprehension check. If Codex has
misunderstood the spec, you want to find out for free, before there's code to unpick.

Launch `codex` in the repo, then send:

> Read these files in full before doing anything: AGENTS.md, PRD.md, config/sources.yaml.
>
> Then answer, in under 250 words and writing no code:
>
> 1. In one sentence, what does this system do and what is its commercial edge?
> 2. Name the six pipeline layers in order.
> 3. List the data-model invariants you are forbidden from breaking.
> 4. Why is `signal.company_id` nullable?
> 5. What is the rule about golden fixtures, and what happens if you ignore it?
> 6. Which sources in sources.yaml are marked red, and why must you not build on each?
>
> If anything in those documents is contradictory or unclear, say so now.

Read the answer carefully. What you're checking:

| If it gets this wrong | The problem is |
|---|---|
| The commercial edge | Your positioning isn't written clearly enough to build against |
| Nullable `company_id` | It will guess at entity resolution inside connectors |
| The fixture rule | It will write parsers against imagined layouts |
| Anything marked red | It will burn a week on InPASS |

Fix the documents, not the prompt. A doc that Codex misreads is a doc your future self will
misread too.

Question 6 is a deliberate trap for a subtle failure: models often claim to have read a file
they only skimmed. A wrong answer here means it didn't actually load sources.yaml, and you
should re-prompt rather than proceed.

---

## Step 6 — then work through the kickoff prompts

`docs/CODEX_KICKOFF.md` has prompts 1 through 6 in order. Send them one at a time.

**One task per session.** After each prompt completes and you've committed, start a fresh
session (`/new`, or quit and relaunch). This is the single most important habit.

Why: context degrades as a session grows. A session that scaffolded the repo, then wrote the
models, then wrote a parser will have pushed the AGENTS.md rules far enough back that they
stop influencing behaviour. You get a parser that ignores the fixture rule, and it looks
completely reasonable. Fresh session per task means AGENTS.md is always near the front.

Branch per task, so a bad session costs nothing:

```bash
git checkout -b task/02-schema
# ... work, review, test ...
git add -A && git commit -m "Schema + initial migration"
git checkout main && git merge task/02-schema
```

---

## Step 7 — how to maintain progress across sessions

Since each session starts blank, `PROGRESS.md` is the memory. It is the answer to "how do I
keep context."

**Close every session with this prompt:**

> Append a session entry to PROGRESS.md following the existing format. Record: what you
> changed, which tests prove it, what is unfinished, and every assumption you had to make
> because the spec didn't say.
>
> If you made a decision that future sessions must not silently reverse, also add an entry to
> docs/DECISIONS.md.
>
> Then stop. Do not start the next task.

**Open every session with this prompt:**

> Read AGENTS.md, PROGRESS.md and docs/DECISIONS.md.
>
> Tell me what the next task is according to PROGRESS.md, and any open assumptions from the
> last session that I need to resolve first. Wait for my confirmation before starting.

That pair is the whole system. The "assumptions I had to make" line is doing most of the
work — it surfaces the places where Codex quietly filled a gap in your spec, which is where
almost all silent divergence comes from.

Commit PROGRESS.md every time. Its history becomes a build log you can actually search.

---

## Step 8 — how to review when you aren't a strong coder

This is the part people skip, and it's what determines whether the project works.

**Read the tests, not the implementation.** Tests state intent in near-plain language. If
`test_parser.py` asserts that BIG-24 yields 51 rows across four categories, and it passes, you
have learned something real. You do not need to understand the PDF-parsing code to know that.

**Run the thing.** `uv run pytest` is necessary but not sufficient. Actually run the connector
against the real PDF and read twenty output rows with your own eyes. Tests confirm the code
does what the test says. Only looking at output confirms the test says the right thing.

**Ask Codex to critique itself,** in a fresh session so it isn't defending its own work:

> Read the diff on branch task/05-birac-connector. Where is this most likely to be wrong?
> What did the author assume that the PRD doesn't actually state? What would break if BIRAC
> changed the PDF layout next cohort?

**Red flags that mean stop and look closely:**

- "I've simplified this for now" or "as a placeholder"
- A threshold was changed and a test now passes
- A test was deleted or its assertion loosened
- A new dependency appeared without explanation
- More than one connector was touched in one task
- An `expected.json` file was edited rather than the parser

The last one is the dangerous one. Editing the fixture to match the parser inverts the entire
point of the fixture, and it looks like progress.

---

## Step 9 — project-specific guardrails

**Network.** Codex's sandbox has restricted egress and won't reach `birac.nic.in` or
`mcacdm.nic.in`. Fetch artifacts with a web-capable agent, drop them in `fixtures_inbox/`,
then commit them. Codex works from the local copy. Don't waste a session debugging this as
though it were a code problem.

**Database.** Point Codex at a local Postgres or SQLite for development. Never give it
connection details for anything you'd mind losing. Migrations are the highest-risk thing it
writes.

**Paid API keys.** The director-lookup API from `sources.yaml` costs money per record. Keep
the key in `.env`, gitignore it, and don't put a live key in the environment until you have
personally reviewed the call-gating logic and the monthly budget cap. An enrichment loop
without a gate is the failure mode that produces a surprise bill.

**The threshold rule.** AGENTS.md forbids widening an entity-resolution threshold to make a
test pass. Restating it here because it's the rule most likely to be broken helpfully. If
resolution accuracy drops, that's information, not an obstacle.

---

## Common first-timer mistakes

| Mistake | What happens | Fix |
|---|---|---|
| Pasting docs into the prompt instead of committing them | Codex loses them next session | Commit; reference by path |
| One long session for everything | Rules stop being followed halfway | New session per task |
| Accepting work you didn't run | Green tests, broken output | Run it, read 20 rows |
| Letting it build 5 connectors before the review app | Schema is wrong, all 5 need rework | Enforce the step-6 gate |
| Not committing between tasks | Can't isolate what broke | Branch and commit per task |
| Merging PRD into AGENTS.md | Burns context every turn, may hit 32 KiB | Keep separate |
| Asking "does this look right?" | It will say yes | Ask "where is this most likely wrong?" |
| Trusting a self-reported summary | It skimmed | Ask a question only a reader could answer |

---

## First two weeks, condensed

| When | What | Codex involved? |
|---|---|---|
| Days 1–2 | Lead-time feasibility test | Web agent, not Codex |
| Days 3–5 | Fetch fixtures, commit them, verify sources.yaml flags | Web agent, not Codex |
| Day 6 | Install, repo setup, comprehension check (step 5) | Yes |
| Day 7 | Prompt 1, scaffold. Review layout. | Yes |
| Days 8–9 | Prompt 2, schema. Prompt 3, storage. Read storage line by line. | Yes |
| Day 10 | Prompt 4, connector contract. Review hardest. | Yes |
| Days 11–13 | Prompt 5, BIRAC connector. Two cohort fixtures. | Yes |
| Day 14 | Prompt 6, review app. **Then use it for an hour on real data.** | Yes |

Day 14 is the real gate. If the schema can't support the workflow, you find out with one
connector built instead of ten.
