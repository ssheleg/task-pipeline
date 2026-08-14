# Companions — what's built in, what's optional, what to install

**The pipeline's doctrine is entirely built into this skill.** Stages 0, 2, 3, 4, 5,
6 and 10 run from `references/*.md` — no companion plugin, no resolution step, no
fallback path, no version skew, and no failure mode where a stage can't run because
something isn't installed.

What remains is a short list of **optional** companions that make individual stages
better, plus one that is required only for user-facing work.

## Contents

- Built in — nothing to install
- The matrix
- Optional bridge — substituting an external skill set
- Preflight (emit before stage 0)
- Is this skill itself current?
- Credit
- Hand-off the other direction

## Built in — nothing to install

| Stage | Doctrine |
|---|---|
| 0 Knowledge harvest (pre-grill) | `references/knowledge-sources.md` |
| 0 + 9 + any settled decision — the documentation system | `references/documentation.md` |
| 6–10 + any check you write — gates | `references/gates.md` |
| any agent-time enforcement — hooks | `references/hooks.md` |
| 0 + 9 The code graph (the tool is optional; the doctrine ships) | `references/knowledge-graph.md` |
| 0 Intake grill | `references/grill.md` |
| 2 Brainstorm | `references/brainstorm.md` |
| 2 Decompose (platforms only) | `references/decomposition.md` |
| 3 Spec | `references/spec.md` |
| 4 Plan | `references/planning.md` |
| 5 Build (isolation, subagents, fix loop) | `references/build.md` + `references/review.md` |
| 5–6 TDD + suite gate | `references/tdd.md` |
| 10 Acceptance (REQ close-out) | `references/acceptance.md` |
| 10 Retrospective (the run's last act: stamp, prune, entry) | `references/retrospective.md` |
| 10 + any audit (finding what's missing) | `references/audit.md` |
| any repeating loop | `references/loop-guard.md` |

## The matrix

| Skill / tool | Needed for | Required? | Install |
|---|---|---|---|
| **super-ux** (`ux-foundation`, `ux-flows`, `ux-scenarios`, `ux-audit`, `/ux`, `/ux-lint` — **and the copy half**: `copywriting`, `brand-voice`, `/brand-init`, `/copy`, `/brand-lint`, plus `/vision`) | stage 3 — the **UX track** *and* the **COPY track**. This row named six surfaces until 2026-08-10 while super-ux shipped eight skills and fifteen commands: the whole brand-and-copy half was invisible to this pipeline, so a run built scenarios and screens and then wrote the interface strings by taste | **Required for any user-facing task** | `/plugin marketplace add ssheleg/super-ux` → `/plugin install super-ux@super-ux` (or `npx skills add ssheleg/super-ux`) |
| **sheleg-design** (`/sheleg-design`) | stage 3 — the **VISUAL track**: tokens and themes, typography and rhythm, motion and how it degrades to rest, the visual language a brand is recognised by. It answers *how it looks*, which no other companion here answers — `super-ux` decides what the interface must do, `copywriting` how it sounds. Before 2026-08-10 this skill appeared once in the whole bundle, as a name in a list | **Recommended** on any task with a visual surface; never a gate. Absent → the run says the visual layer shipped **undesigned**, which is the honest name for picking values at the keyboard | `/plugin marketplace add ssheleg/sheleg-design` → `/plugin install sheleg-design@sheleg-design-skill` |
| **context7** (MCP — call tools fully qualified: `context7:resolve-library-id`, `context7:query-docs`) | stage 1 docs study | Recommended (web-search fallback) | connect the context7 MCP server |
| **Figma** (MCP) | stage 3 UX track, when the project designs visually — super-ux mirrors each `SCR-` screen/state into a frame | Optional, **UI + Figma-on only**. Absent → super-ux degrades to text-only *by itself and never blocks*, so shipping a UI feature with no mockups becomes a silent scope call — which is why the stage-0 sweep decides it | connect the Figma MCP server (`/mcp`, or your claude.ai connectors) |
| **[obsidian-wiki](https://github.com/ar9av/obsidian-wiki)** (`wiki-query`, `wiki-update`) | **stage 0 harvest** (query what's already known) **+ stage 9 sync** | **Recommended** — never a gate; absent → harvest runs on repo docs alone | `pip install obsidian-wiki` → `obsidian-wiki setup --vault /path/to/your/vault` |
| **[graphify](https://github.com/Graphify-Labs/graphify)** (`/graphify`, `graphify query`, `graphify affected`, `graphify god-nodes`) | **stage 0 harvest** (reach: what calls this, what breaks if it moves) **+ stage 9 refresh + the graph↔docs divergence check** ([`knowledge-graph.md`](knowledge-graph.md)) | **Recommended** — never a gate; absent → the harvest greps instead, and the divergence axis is unavailable | `uv tool install graphifyy` → `graphify install` → `/graphify .` |
| **playwright** (CLI — `playwright-cli open`, `snapshot`, `click`, `type`, and the two this pipeline actually asks for: `console` and `requests`; or MCP — `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_console_messages`, `browser_network_requests`) | **stages 5–6 on any project with a web front end**, and **stage 8** on a deployed target — the same job as the row below: open the surface, snapshot it, read the console and the network log. Its own difference is **cost per look**: the CLI is a shell command whose upstream states it *"avoid[s] loading large tool schemas and verbose accessibility trees into the model context"*, and both channels snapshot the **accessibility tree rather than pixels**, so a look costs a page of text and no vision model | **Recommended** — never a gate; absent → say the surface was verified **by reading the diff** and treat that as the weaker claim it is | CLI: `npm install -D @playwright/cli@latest` → `npx playwright-cli --help` (or `-g` for the global binary; `playwright-cli install --skills` adds its agent skills). MCP: `claude mcp add playwright npx @playwright/mcp@latest` |
| **chrome-devtools** (MCP — `list_pages`, `navigate_page`, `take_snapshot`, `take_screenshot`, `evaluate_script`, `list_console_messages`, `list_network_requests`, `lighthouse_audit`, `performance_start_trace`, `take_heapsnapshot`) | **stages 5–6 on any project with a web front end** — verify the **rendered** surface rather than the diff: computed layout, console errors, failed requests. **Stage 8** on a deployed web target: load the page and read what the browser did, not what the deploy said. Its own difference is **reach past the page**: `lighthouse_audit`, performance traces and heap snapshots have no equivalent in the row above, and `seo-aeo-audit` builds on the first of them | **Recommended** — never a gate; absent → say the surface was verified **by reading the diff** and treat that as the weaker claim it is | `/plugin install chrome-devtools-mcp@claude-plugins-official` (or connect the MCP server directly) |
| **[agent-sync](https://github.com/ssheleg/agent-sync)** (`/agent-sync`, **≥ 1.3.0** — `finish` did not exist before it, so an older install turns the stage-10 close-out into a command that is not there) | **guarded registers** — a lease before writing one, `reserve` before minting an id, `reconcile`/`record` for intent vs as-built, and `finish` for the stage-10 multi-repository close-out ([`documentation.md`](documentation.md)) | **Recommended** — never a gate. Absent → the run is **`ungated`** and must say so out loud; the discipline still applies, only the arbitration is missing | `npx sshlg-skills install` |
| ~~superpowers~~ | — | **Not a dependency.** Stages 2/4/5/6 run on the built-in doctrine above. See *Optional bridge* | — |
| ~~grill-me / grilling~~ | — | **Not a dependency.** The stage-0 grill is built in (`references/grill.md`) | — |

## Optional bridge — substituting an external skill set

An operator who already runs an equivalent skill set may map it onto stages 2/4/5/6
in their `pipeline.json` → `skills[]`, e.g. `superpowers:brainstorming`,
`superpowers:writing-plans`, `superpowers:using-git-worktrees`,
`superpowers:subagent-driven-development`, `superpowers:test-driven-development`.

Rules for that bridge:

- **It is a substitution, never a requirement.** Nothing detects it, nothing
  recommends it, nothing waits for it, and its absence is never an error.
- **The gates still govern.** Whatever runs a stage, `stages.md` decides when the
  stage is done.
- **Never mix providers inside one stage** — either the built-in doctrine runs it or
  the substitute does; interleaving two review loops produces neither.

## Preflight (emit before stage 0)

Detect the optional companions and print ONE block — companions **plus the model
decision** (`model-tiering.md`), so the operator arms the whole run in a single
exchange:

```
Pipeline companions (stage doctrine is built in — nothing to install for it):
  ✗ super-ux           — this task looks user-facing; required for the UX track,
                         and it also owns the COPY track (copywriting, brand-voice):
                           /plugin marketplace add ssheleg/super-ux
                           /plugin install super-ux@super-ux
  ✗ sheleg-design      — this task has a visual surface; it owns the VISUAL track:
                         tokens, themes, typography, rhythm, motion and its rest state:
                           /plugin marketplace add ssheleg/sheleg-design
                           /plugin install sheleg-design@sheleg-design-skill
                         (running without it — the visual layer ships undesigned,
                          and the close-out says so in those words)
  ✓ context7           — ready
  ✗ Figma MCP          — this task is user-facing and the project designs in Figma
                         (docs/ux/foundation.md → Design tooling). Without it the
                         UX chain still runs, text-only — no mockups this run:
                           connect the Figma MCP via /mcp
                         (say "text-only is fine" and I'll record that instead)
  ✗ obsidian-wiki      — recommended: stage 0 queries it before grilling you,
                         stage 9 syncs back what this run learned:
                           pip install obsidian-wiki
                           obsidian-wiki setup --vault /path/to/your/vault
                         (running without it — the harvest uses repo docs only)
  ✗ agent-sync         — recommended: guarded registers, id reservation before
                         minting, intent-vs-as-built reconcile, and the stage-10
                         multi-repository close-out:
                           npx sshlg-skills install
                         (running without it — the doc track still applies, the
                          run is recorded `ungated`, and that is said out loud)
  ✗ graphify           — recommended: stage 0 asks it what reaches what,
                         stage 9 refreshes it beside the docs and the wiki:
                           uv tool install graphifyy
                           graphify install
                           /graphify .        (once, in this project)
                         (running without it — no reach queries, no graph↔docs
                          divergence check)
  ✗ playwright         — recommended when this project has a web front end.
                         One of TWO channels that do the same look; either is
                         enough, and a project that already runs Playwright has
                         this one for free:
                           npm install -D @playwright/cli@latest   (then npx playwright-cli)
                           claude mcp add playwright npx @playwright/mcp@latest
                         (running without it — see the line below; without BOTH,
                          the surface is verified by reading the diff)
  ✗ chrome-devtools    — recommended when this project has a web front end:
                         stages 5-6 check the RENDERED surface instead of the
                         diff, stage 8 reads what the browser did after a deploy.
                         The other channel; it alone reaches lighthouse_audit,
                         performance traces and heap snapshots:
                           /plugin install chrome-devtools-mcp@claude-plugins-official
                         (running without it — the surface is verified by reading
                          the diff, and the close-out says so in those words)

🧠 Model for this run: recommended <top tier available>. You're on <current>.
   /model <id> to switch, or "keep current", or name per-stage overrides.

⚠  This skill's own behaviour is unverified: evals/RESULTS.md records <N> blind
   run(s) on <M> model(s). Its triggering and its stage compliance are authored,
   not measured. Nothing here is blocked by that — you are told because a skill
   that never says so is one you would assume had been tested.

Install the ✗ items you want, answer the model line, then say "continue".
```

Rules:

- Only flag **super-ux** when the task implies a UI (the stage-0 grill decides;
  when unsure, flag it — a false positive costs one install). It arms **two** tracks,
  not one: the UX chain and the copy layer.
- **sheleg-design**: flag it when the task has a **visual** surface — a page, a screen,
  a themed component, a landing, a dashboard. Detect via a resolving `/sheleg-design`.
  **A CLI, a library, a backend service or an internal script does not flag it**, and
  neither does a purely structural change to an existing screen: choosing a palette for
  a log parser is how a recommendation is taught to be noise, and this bundle already
  spent a rule learning that about the browser. Absent → the run continues and says the
  visual layer shipped **undesigned**; that is a weaker claim and the close-out records
  it as one, exactly as it does for a surface verified by reading the diff.
- **obsidian-wiki**: detect via `~/.obsidian-wiki/config` or a resolving
  `wiki-query`/`wiki-update`. Present → say `✓ ready` and use it in the harvest.
  Absent → print the two install lines **once** and continue; never ask twice in a
  run and never block a stage on it ([`knowledge-sources.md`](knowledge-sources.md)).
- **The browser channels — `playwright` and `chrome-devtools`, one rule for both.**
  Flag them only when the project **has a web front end** — an `index.html`, a
  `package.json` naming a browser framework, a `docs/ux/screens.md`, or a deploy target
  that serves pages. **A CLI, a library or a backend service does not flag either** —
  offering a browser to a project with no browser is how a recommendation is taught to
  be noise. Detect `playwright` via a resolving `playwright-cli` binary, a
  `@playwright/cli` or `@playwright/mcp` dependency, a `playwright.config.*`, or
  `mcp__playwright__browser_navigate`; detect `chrome-devtools` via a resolving
  `mcp__chrome-devtools__list_pages` (either one under whatever prefix the host uses).
  Present → `✓ ready`. Absent → print its install lines **once** and continue; neither
  is a gate.
- **They are two channels for one look, and the run needs one of them, not both.**
  Both open the page, snapshot it and read the console and the network log, so **stop
  at the first one that answers** — running the same look twice is a cost with no
  second fact. Where neither is present, say the surface was verified **by reading the
  diff**; where both are, the tie-breakers are stated rather than left to taste:
  **`playwright` when the project already runs it**, or when context budget is tight —
  its own upstream sells the CLI on not loading large tool schemas and verbose
  accessibility trees into the model context. **`chrome-devtools` when the question is
  past the page** — a Lighthouse category, a performance trace, a heap snapshot; the
  Playwright channel has no equivalent for any of the three. Neither is *the better
  browser*, and a run that ranks them has invented a fact this matrix does not carry.
- **graphify**: detect via `graphify-out/graph.json` (built → `✓ ready`, query it in
  the harvest) or a resolving `graphify` binary with no `graphify-out/` (installed,
  not built → offer the one-line `/graphify .`). Absent → print the install lines
  **once** and continue. Same law as the wiki: recommended, never a gate, never
  asked twice ([`knowledge-graph.md`](knowledge-graph.md)).
- **Figma MCP**: flag it only when the task is user-facing **and** the project
  designs visually — read `docs/ux/foundation.md` → *Design tooling* first; no
  record yet means the choice itself is a stage-0 question (super-ux's default is
  on). Detect the official Figma MCP tools; **how** frames get built, named and
  linted is entirely super-ux's — its own `figma-integration.md` and
  `figma-structure.md` own that — while this preflight only decides whether the run
  has the capability
  and, if not, what ships instead. That last part is the point: super-ux recommends
  the MCP and then *continues text-only on its own*, so without a recorded answer
  the run silently narrows from "designed" to "described". The sweep row is
  `3 Design surface` ([`grill.md`](grill.md) → *The autonomy sweep*).
- **agent-sync**: detect via a resolving `/agent-sync` or a `.claude/agent-sync.json`
  in the project. Present → take a lease before writing a guarded register and
  reserve ids before minting them. Absent → print the line **once**, continue, and
  **record the run as `ungated`** — never describe the project as protected
  ([`documentation.md`](documentation.md) → *Registers are shared state*).
- **The behaviour line prints whenever `evals/RESULTS.md` records no blind run**, and
  disappears the moment one is recorded — it is a state of the evidence, not a warning
  and not a ratchet. This bundle asks every project it touches for evidence rather than
  assertion, and until 2026-08-10 it made the opposite claim about itself by saying
  nothing: **one self-observed run by the author, zero blind runs on zero models**, with
  a preflight that reported companion availability in detail and its own confidence not
  at all. A skill silent about its own evidence is read as tested.
- **Never gate any stage on an install** except the stage-3 UX track on a UI task.
- Optional tools missing → state the fallback, don't block.
- Re-detect after the operator installs; don't assume.
- The model answer goes into the brief. Don't ask again per stage
  (`model-tiering.md` → *Mechanic*).

## Is this skill itself current?

Preflight's other question, asked once beside the companion block. A pipeline running
on a stale copy of its own doctrine repeats a class of failure that was already fixed
upstream — and nothing in a run would ever reveal it.

```bash
npx --yes sshlg-skills@latest list      # what the current release of each member is
```

Compare it with what is installed. Behind → offer the **launcher**, never the bare
per-skill form:

```bash
npx --yes sshlg-skills@latest update
```

The launcher moves the whole family, updates plugins and agent copies together, and
prunes the plain `~/.claude/skills/<name>/` copies that otherwise shadow a plugin and
serve the version they were copied from, forever. A bare `npx skills update <name>`
re-creates exactly that shadow.

**Three staleness signals worth naming**, because none of them is a version number:

| Signal | What it means |
|---|---|
| A standing instruction that has not fired in five run stamps, or in sixty days | the rule was situational; the prune retires it ([`retrospective.md`](retrospective.md)) |
| A doc map older than the project's last release | the regime was decided for a project that has since changed shape — `setup` offers the entry audit ([`setup.md`](setup.md)) |
| A ratchet whose count has not moved in months | either the backlog is genuinely frozen, or nobody is looking at the number printed beside every verdict |

Recommend once, then continue. **Never a gate** — a run blocked on its own updater is
a run that cannot ship a fix to the updater.

## Credit

The built-in doctrine is **ported, not depended on**:

- The stage-0 grill is adapted from Matt Pocock's `grilling` / `grill-with-docs`
  skills (MIT, https://github.com/mattpocock/skills).
- Stages 2–6 are adapted from the `brainstorming`, `writing-plans`,
  `using-git-worktrees`, `subagent-driven-development`, `test-driven-development`
  and `requesting-code-review` skills in obra/superpowers (MIT,
  https://github.com/obra/superpowers).

Both notices live in the repo `LICENSE` → *Third-party*.

## Hand-off the other direction

super-ux's `/ux` menu can hand off *to* this pipeline (its "execute autonomously"
action). When entered that way the UX chain already exists — see `stages.md` → 0
*Entry-from-super-ux short-circuit*: verify, don't rebuild.
