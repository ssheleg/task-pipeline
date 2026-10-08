# The browser — how the look is actually taken, and how a suite is run beside it

[`companion-skills.md`](companion-skills.md) decides **which** channel a project has
and how to install it. This file is **how to use one**: the model both channels share,
the commands the look is made of, and the three different things people mean when they
say *"tested in a browser"*.

Stages 5, 6 and 8 ([`stages.md`](stages.md)) and [`tdd.md`](tdd.md) demand a look at the
rendered surface. Until this file existed, they demanded it and named no mechanism —
which is how a run says *I checked the browser* and means *I ran the unit tests*.

> **Every command and flag below was read from the tool's own `--help`**, not from a
> vendor page. Where the two disagreed, `--help` won and the page was wrong — see
> *Rationalizations*. Re-derive before quoting:
> `npx @playwright/cli@latest --help` and `npx @playwright/mcp@latest --help`.
>
> **Use the scoped name with `npx`.** `npx playwright-cli --help` fails outside a project
> that has already installed it (`could not determine executable to run`), and the bare
> `playwright-cli` on npm is **somebody else's package** — Microsoft's, deprecated in
> favour of this one. The binary is called `playwright-cli`; the package is
> `@playwright/cli`. Every `playwright-cli …` line below assumes it is installed and on
> PATH, which is what the matrix's install line does.

## Contents

- The one model: a tree, and a ref
- The look, as commands you can run
- Sessions, and why an agent needs them
- Reading a look vs gating on one
- "Tested in a browser" is three different claims
- The visual half — pixels against intent, under a contract
- Getting past a login, and past a backend
- When the look finds something: debugging the spec that missed it
- Evidence a reader can open
- What the channel can reach — the part a recommendation owes you
- Rationalizations

## The one model: a tree, and a ref

**Both channels drive the page through its accessibility tree, not its pixels.** You ask
for a snapshot, you get structured text — roles, names, and a **ref** per interactive
element (`e5`, `e12`) — and you act on the ref.

```
snapshot  ->  button "Checkout" [ref=e12]  ->  click e12
```

Three consequences the doctrine rests on:

- **A look costs a page of text and no vision model.** This is why the pipeline can ask
  for one at three stages without the cost being an argument. A `screenshot` exists in
  both channels and *is* pixels — in the functional look, take one for a human, not for
  you to read. Reading pixels against the design's intent is a different check with its
  own contract: *The visual half*, below.
- **The ref is a fact about the page as rendered**, so `click e12` after a snapshot is
  deterministic in a way a coordinate never is.
- **A ref that no longer resolves is a finding, not an error to retry past.** The element
  moved, or never rendered. That is exactly the class stage 6 says a green suite cannot
  see. Re-snapshot, read what changed, and report it — do not hunt for a selector that
  makes the command succeed.

Refs come from the **latest** snapshot. Act, then snapshot again before using a ref from
before the act.

## The look, as commands you can run

The pipeline asks for the same four things every time: **open it, snapshot it, read the
console, read the network.** In the CLI that is literally four commands:

```bash
playwright-cli open http://localhost:3000/checkout
playwright-cli snapshot
playwright-cli console warning     # min-level: only warnings and errors
playwright-cli requests            # then: request <n> for headers, body, response
```

The MCP is the same four moves under different names: `browser_navigate`,
`browser_snapshot`, `browser_console_messages`, `browser_network_requests`.

**Quote what you read, not that you looked.** *"Console clean, all requests fine"* is a
claim. *"`console warning` → empty; `requests` → no status ≥ 400"* is the same claim with
its command attached, and it is the one that belongs in a gate verdict.

**Do not quote the request count as the page's count.** `requests` hides successful static
resources by default and says so in its own footer (*"N static request(s) not shown"*);
`requests --static` includes them. Failures are listed either way — a 404'd stylesheet
appears without the flag — so *no status ≥ 400* is a safe claim and *14 requests* is not.

`chrome-devtools` takes the identical four moves — `navigate_page`, `take_snapshot`,
`list_console_messages`, `list_network_requests` — which is why the matrix ranks neither:
the look is the same look.

## Sessions, and why an agent needs them

**The CLI keeps a browser alive between commands.** That is the whole reason the four
commands above compose: `snapshot` sees the page `open` navigated to, and `click e12`
acts on the element that snapshot named. A tool that launched a browser per invocation
would lose the page, and every ref with it.

| Need | Command |
|---|---|
| Two surfaces at once without shared cookies | `playwright-cli -s=checkout open …` and `-s=admin open …` |
| See what is still running | `playwright-cli list` |
| Tidy up at the end of a stage | `playwright-cli close-all` |
| A stale or zombie process after a crash | `playwright-cli kill-all` |

**A run that opened a browser closes it**, the same rule the pipeline applies to every
other resource it starts ([`residue.md`](residue.md)). `list` before you claim the
environment is clean — the reply is the evidence, not the `close-all` you typed.

## Reading a look vs gating on one

Two global flags change what the output is for:

- **`--json`** — the full response as JSON. This is what a script parses, and therefore
  what a *check* can be built on.
- **`--raw`** — the result value alone, no status wrapper. For one value in a shell
  variable.

Default output is for a reader. If you find yourself regexing the default output in a
gate, you wanted `--json`; a check that parses prose breaks on the release that reworded
it ([`gates.md`](gates.md)).

## "Tested in a browser" is three different claims

Keeping these apart is the entire point of the stage-6 pair, and conflating them is the
commonest way a run reports a green it does not have.

| | What it is | What it proves | Where it counts |
|---|---|---|---|
| **The look** | an agent driving a page: open, snapshot, console, network | that this surface renders, right now, and what the browser said while it did | the **functional look**, stage 6 — recommended, never a gate. Its **visual half** is a gate on a `flagship`, `product` or `ad` surface — *The visual half*, below |
| **The spec suite** | `playwright test` — the **test runner** | that the assertions someone wrote still hold, on the paths someone thought to write | the **suite** half of the stage-6 gate, counted with every other test |
| **The library** | `require('playwright')` — `chromium`/`firefox`/`webkit`, `devices`, `request`, `selectors` | whatever your own script asserts; it is an automation API, not a test framework | wherever the project already runs it |

The library and the runner are **separate APIs** — a script built on `chromium.launch()`
has no `expect`, no fixtures, no reporter, and no retry. Choosing the library where a
runner was wanted is how a project ends up with a bespoke half-runner nobody trusts.

The minimal library shape, for reading a script that already exists:

```js
const { chromium } = require('playwright');
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('http://example.com');
await browser.close();
```

**A green spec suite never discharges the look.** It asserts what was written down; the
console error nobody asserted on is precisely what the look is for. This is `DEC-0004`
and it is the reason both halves exist.

**The claims are a contract, not prose** (PXS-05.01): `templates/browser-claims.json`
links each REQ/scenario id to the STATE it was verified in and the KIND of check
(this table's own look/suite/library split), and `python3 test/browser_claims_test.py`
validates a filled copy with stdlib only — a visual PASS needs its artifact, captured
in the claim's own state (the initial screenshot closes nothing about opened/error);
a suite PASS closes no look claim; a toggle owes its full cycle; no browser channel
is NOT_RUN with the reason.

## The visual half — pixels against intent, under a contract

Everything above reads the **accessibility tree**: it proves the surface renders and the
browser stayed quiet. It cannot say whether the surface looks like what was designed —
the wrong weight on a heading, a card that lost its spacing at 200 % text, a dark theme
that drops a border, a frame that drifted from the Figma it was built from. That is a
different question, and asking it of a snapshot is how a run reports *it looks right*
having read no pixels at all. The **functional look** and the **visual half** are two
checks; neither discharges the other.

**When it runs, and when it gates — by the brief's `surface_class`**
([`stages.md`](stages.md) → stage 0, *The surface class*):

| Class | Visual half at stages 5–6 | Human pass at stage 10 |
|---|---|---|
| `flagship` | **gate** — full matrix, pairwise across every axis, judge items per the full rubric | **gate** — the approved contact sheet |
| `product` | **gate** — every state, the mandatory pairs; pairwise holes reported | **gate** — the approved contact sheet |
| `ad` | **gate** — the ad rubric profile and the safe zones | **gate** — the approved contact sheet |
| `internal` | recommended — the project linter is the floor; a sheet, if made, is checked for honesty | the functional look closes it |

It gates only where the stage-3 VISUAL track ran. A recorded refusal (*«без дизайна»*,
`Mode: declined`) turns the visual half into the functional look plus the linter, said in
the close-out — the same rule as every other refusal in the pipeline.

**The checks run cheapest first, and the person last:**

1. **Deterministic.** The project linter — `python3 scripts/visual_gate.py lint <dir>`,
   which runs sheleg-design's `--lint` where it is installed and answers **NOT_RUN (exit 3)**
   where it is not — plus axe or Lighthouse, the token check, the type checker. An S1
   finding blocks, whatever anyone says about the picture later. **With Figma on, the
   token check includes the drift probe**: `python3 scripts/visual_gate.py tokens
   --figma <variables.json> --css <tokens.css>` compares the variable names exported
   from the file (the JSON `get_variable_defs` returns, or the REST export) with the
   custom properties the pack's token file declares. It names each variable with no
   property, each property with no variable, and each variable whose WEB code syntax
   is not the property the file actually declares. A name maps by kebab-case
   (`Color/Text Muted` → `--color-text-muted`) unless code syntax says otherwise.
   Exit `0` PASS · `1` FAIL · `2` unreadable · `3` NOT_RUN. No export is NOT_RUN,
   never PASS: save the export beside the frames and run again, or record the probe
   as not run.
2. **Regression** against the approved baseline, where one exists (`toHaveScreenshot`, or
   the platform's snapshot test).
3. **The matrix.** One frame per `SCR-NN` state the screen map lists (default, loading,
   empty, error, offline, long-content, keyboard-up, first-run — the ones that apply),
   across viewport × theme × text size × locale: **pairwise coverage** — every value of one
   axis meets every value of every other in some frame — plus the **mandatory pairs**
   (dark × large text, RTL × narrow). Never the full cross product: every state at every
   combination of every axis value is hundreds of frames, and nobody reads them. Seed the
   worst-case data first (`break-ui`, [`companion-skills.md`](companion-skills.md) →
   *Visual lanes*) so the frames show long names and empty lists, not the demo account.
4. **Each frame carries its capture record** — revision, route, state, viewport, locale,
   theme, motion, captured-at, source — and is disqualified, not passed, when it is blank,
   stale, of the wrong route or state, or taken before the fonts rendered. This is
   sheleg-design's visual-review contract; the pipeline only refuses a frame without it.
   Where a Figma frame or an approved baseline exists, the frame is **diffed against it**,
   and a failing diff is never a PASS the run writes: either the build drifted, or the
   person approves a new baseline.
5. **The rubric**, read by a judge that is not the agent that built the surface: a
   checklist per task, never a single score; pairwise only against the approved
   reference and in both orders; three samples, and disagreement is `uncertain`, which
   goes to the person rather than to a coin. **A judge item (J) is `NOT_ASSESSED` until a
   labelled set exists and the judge's agreement with it is measured** — a verdict from an
   uncalibrated judge is a guess with a format. A gate item (G) is deterministic and the
   judge never overrides its FAIL. Every FAIL is a triple: *region → defect → fix*.
6. **One human pass** over the contact sheet. Approval makes its frames the next baseline.

**The contact sheet is the one surface the person reviews**, and its data is
`templates/browser-claims.json` — the same file, **not a second schema**. A look row
that carries `axes` is a frame: `axes{viewport,theme,text,locale}`, `capture{revision,
route,motion,captured_at,source}`, `figma_frame`, `baseline`, `diff`, `rubric[]`. The file
names its `surface`, `revision`, `review_rounds`, `approved_by` and `approved_at`. The
viewing page is a self-contained local HTML beside the frames — a full document, `<meta
charset="utf-8">`, no CDN. **Frames and the HTML stay out of git; the JSON goes in.**

```bash
python3 scripts/visual_gate.py sheet design/review/contact-sheet.json \
    --class product --artifact-root design/review --states SCR-01/default,SCR-01/empty
# stage 10 adds --require-approval
```

Exit `0` PASS · `1` FAIL · `2` unreadable · `3` NOT_RUN — a frame that did not run makes
the whole verdict NOT_RUN, never PASS. **On a gated class NOT_RUN stops the stage and
asks**: connect a capture channel, or the operator accepts the surface as `unverified`,
recorded in the brief and named in the close-out. It is never reported around, which is
the failure `DEC-0004` kept the functional look ungated to avoid; `DEC-0006` gates the
visual half on these classes and keeps that exit open in words.

**Two rules keep the loop from becoming the work** ([`loop-guard.md`](loop-guard.md) →
*The re-render loop*): a re-render budget of **one, two at most**, after which a failing
item goes to the person as `unresolved`; and **only external, specific feedback** starts a
round — a linter line, a diff, an audit item, a triple — never "look again". Each return
from the person adds one to `review_rounds` and one `review:` line to the run ledger, so the
number of passes a surface took is measured, not remembered.

**Native surfaces are not web surfaces.** A web render styled as a phone is a mockup. A
native screen's frames come from a simulator or a device (XCUITest snapshots, Compose
screenshot tests) and its accessibility from the platform's own audit; with neither, the
native rows stay `NOT_RUN`, said in words.

## Getting past a login, and past a backend

A surface behind auth is the usual reason a run skips the look. Both channels solve it,
and neither needs a password in a transcript.

**Storage state — log in once, replay it.**

```bash
mkdir -p .auth                                  # state-save does not create it
playwright-cli open https://app.example.com/login
#  … sign in by hand, or drive the form …
playwright-cli state-save .auth/state.json      # cookies + localStorage
playwright-cli state-load .auth/state.json      # every later look starts signed in
```

The MCP takes the same file at startup: `--storage-state <path>`. Point the spec suite
at it too and the suite and the look agree about who is signed in.
**The state file is a credential.** It goes where credentials go, never into the
repository.

**Routes — make the backend say what you need it to.**

```bash
playwright-cli route '**/api/quote' --status 500   # then look at the error state
playwright-cli route-list
playwright-cli unroute '**/api/quote'
```

This is how a failure path gets a look at all. `route` is also the honest way to check
that a 404'd bundle or a 500'd call *renders* as something a user can act on — which no
unit test with a mocked fetch will ever tell you.

Storage families exist per layer when you need to reach past the whole state file:
`cookie-list|get|set|delete|clear`, and the same verbs for `localstorage-` and
`sessionstorage-`.

## When the look finds something: debugging the spec that missed it

The look found a defect the suite did not. Stage 6 says fix it here — and the fix has two
halves: the code, and the assertion that should have caught it.

```bash
playwright-cli generate-locator e12     # a locator for the element the look found
playwright-cli highlight e12            # show it on the page (--hide to clear)
```

Drop that locator into a new spec, then drive the spec itself:

```bash
playwright-cli pause-at src/checkout.spec.ts:42   # run up to this line and stop
playwright-cli snapshot                            # the page as the test sees it there
playwright-cli step-over
playwright-cli resume
```

That loop is what turns *"the look caught it"* into *"the suite catches it next time"* —
which is the only reason the look's finding stops recurring. `run-code` and `eval` are
there for the case a question is faster answered in the page than through a command.

## Evidence a reader can open

A verdict that says *the surface renders* is worth what its attachment is worth.

| Artefact | Command | Use it for |
|---|---|---|
| Screenshot | `screenshot [ref]` | one state, for a human |
| Trace | `tracing-start` … `tracing-stop` | a failure someone else has to reproduce |
| Video | `video-start [file]`, `video-chapter <title>`, `video-stop` | a flow, or a regression that only appears in motion |
| PDF | `pdf` | a printable surface that is itself the deliverable |

`video-show-actions` annotates each action on the page with a callout naming it, which is
what makes a recording readable by someone who did not run it.

The MCP's equivalents are `browser_take_screenshot`, `browser_start_tracing` /
`browser_stop_tracing`, `browser_start_video` / `browser_stop_video`, `browser_pdf_save`,
written under `--output-dir` — **and all but the screenshot are behind `--caps`.** See
below: the tool list you read about is not the tool list you get.

**Attach the artefact or drop the claim.** A trace nobody can open is prose.

## What the channel can reach — the part a recommendation owes you

This bundle recommends handing an agent a real browser. That is a wider capability than
anything else in the matrix, and the boundary is worth stating rather than discovering.

- **The MCP restricts file access to the workspace roots** (cwd when no roots are
  configured) and blocks navigation to `file://` by default. `--allow-unrestricted-file-access`
  removes both. Read that flag as what it says.
- **`--allowed-origins` / `--blocked-origins` are not a security boundary**, and upstream
  says so in its own help: they do not survive redirects. Do not use them as one.
- **`--isolated` keeps the profile in memory**, so nothing persists past the session —
  the right default for a look at someone else's site. The opposite is deliberate and
  spelled differently per channel: `--user-data-dir <path>` on the MCP,
  `open --persistent` (or `open --profile <path>`) on the CLI.
- **`--secrets <path>`** exists so a credential reaches the browser without reaching the
  transcript. Use it rather than typing the password into a `fill`.
- **`--extension` / `attach`** connect to a browser **you are already using**, with your
  sessions in it. That is occasionally exactly what you want and is never the default
  for an unattended run.

**The MCP's tool list is capability-gated, and the default is the small one.** Asking
the running server rather than a page: **24 tools by default, 42 with
`--caps vision,pdf,devtools`.** Tracing, video and PDF — `browser_start_tracing`,
`browser_start_video`, `browser_video_chapter`, `browser_pdf_save` — are **not present**
until `--caps` names them, and neither are the coordinate-mouse tools. A doctrine that
sends an agent to `browser_start_tracing` on a default server sends it to a tool that is
not there, and the agent concludes the doctrine is stale rather than the server narrow.
Re-derive rather than trust this paragraph: start the server and call `tools/list`.

Both counts above were measured on `@playwright/mcp` 0.0.79 by listing the server's own
tools. The vendor page current at the time listed tool groups this version does not ship
at all — routes, cookies and localStorage among them — which is why the CLI is what this
file names for state and mocking.

The MCP runs **headed** by default; the CLI is headless unless you pass `open --headed`.
On a CI box, headed is the failure you will spend an hour on.

## Rationalizations

| The excuse | Why it fails |
|---|---|
| *"`playwright test` is green, the surface is checked."* | The suite asserts what someone wrote down. `DEC-0004`: it is the coverage half, never the look. |
| *"I took a screenshot, so I looked."* | A screenshot is pixels you did not read. The functional look is `snapshot` + `console` + `requests`, and the verdict quotes them; reading the pixels is the visual half, with a capture record per frame and a matrix behind it. |
| *"The snapshot is clean, so it looks right."* | The tree says the heading exists, not that it rendered at the right weight, in the dark theme, at 200 % text. That is the visual half's question, and on a flagship, product or ad surface it is a gate. |
| *"The judge said it looks great."* | An uncalibrated judge's J items are `NOT_ASSESSED`, and no judge overrides a deterministic FAIL. A verdict needs a checklist, a reference, both orders and three samples. |
| *"The click failed, I'll find a better selector."* | A ref that stopped resolving **is the finding**. Re-snapshot and report what moved. |
| *"The docs say the CLI has no `tracing`."* | A vendor page is a claim; `--help` is the tool. This file was written against `--help` **because** a page-derived claim shipped here and was wrong. |
| *"The tool list is in the docs."* | The page listed tools this version does not ship, and omitted that tracing, video and PDF need `--caps`. Ask the server: 24 tools default, 42 with all caps. |
| *"It's behind a login, so the look isn't possible."* | `state-save` / `state-load`, or `--storage-state`. Auth is a solved step, not an exemption. |
| *"No browser channel is installed, so the step doesn't apply."* | The step still applies; the claim weakens. Say *verified by reading the diff* and let the close-out record it as the weaker claim it is. |
| *"I closed the browser."* | `list` is the evidence. The command you typed is not the state you left ([`residue.md`](residue.md)). |
