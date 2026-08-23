# The probe catalogue

What to run, chosen by what the discovery phase found. Every entry is a probe in
the sense `SKILL.md` defines: it declares what it needs, and a need that is not
met makes it **blind with a reason**, never absent and never clean.

`scripts/audit.py` ships the mechanical ones. This file is the larger catalogue
— what to add for a project shape the script does not cover, and what a person
runs by hand once the script has printed where it could not look.

## Contents

- How to read this file
- Universal — every project, whatever it is
- By language and package manager
- By shape: a published package
- By shape: a deployed service
- By shape: a monorepo or a submodule tree
- By shape: a public web surface
- Production evidence through connected MCP servers
- Adding a probe
- What deliberately has no probe

## How to read this file

Each table row is `probe · needs · what it answers · what its absence means`.
The fourth column is the one that matters: **a probe worth adding is one whose
silence would otherwise be read as health.**

Two rules bind every row, and both come from defects this family has shipped:

- **Read committed state.** `git ls-files`, `git show <ref>:<path>`. A probe
  that walks the working tree reports build residue and local scratch as project
  state, and its finding cannot be reproduced from a clone.
- **A command that printed nothing has not answered.** Check the exit code *and*
  that the output is non-empty and shaped as expected. An empty result and a
  broken invocation are the same characters.

## Universal — every project, whatever it is

| Probe | Needs | Answers | Silence would mean |
|---|---|---|---|
| `secrets-tree` | git | is a credential committed? | "no secrets" when nobody looked |
| `secrets-history` | git | is one still reachable in history? | a rotated-looking repo that is not |
| `worktree` | git | does the tree disagree with HEAD? | a finding no clone can reproduce |
| `gitignore-secrets` | git | is a credential-shaped file tracked? | `.env` in the repo, unnoticed |
| `docs-present` | — | is there an entry point for a reader? | the entry point is a person |
| `ci-present` | — | does anything run the checks? | "the tests pass" — on whose machine? |
| `test-command` | — | does the project's own test command exist and run? | a suite nobody can invoke |
| `dependency-age` | manager | how far behind are the pinned deps? | quiet rot |
| `licence` | git | is there one, and do the deps agree with it? | a distribution problem found by a lawyer |

**`test-command` is worth writing by hand for any project the script cannot
guess.** Run the project's *own* documented command, read its output, and quote
it. `npm test` exiting 0 while printing `FAIL: 2 guards did not fire` has
happened in this family — a wrapper's exit status is not the suite's verdict.

## By language and package manager

| Stack | Probes worth running | Note |
|---|---|---|
| node / npm | `npm audit --json`, `npm outdated --json`, `npm ls --all` for phantom deps, `npm pack --dry-run` to see what actually ships | `files` in `package.json` decides the tarball; compare it against what the README claims ships |
| python | `pip-audit` or `uv pip list --outdated`, import-time side effects, `pyproject` vs `requirements` drift | two dependency files that disagree is the *two copies* problem: one of them is what installs |
| go | `go vet ./...`, `govulncheck`, `go mod tidy -diff` | a dirty `go.sum` after tidy is a real finding |
| rust | `cargo audit`, `cargo tree --duplicates` | duplicate transitive versions bloat and diverge |
| php / composer | `composer audit`, `composer outdated --direct` | |
| java | `mvn versions:display-dependency-updates`, `gradle dependencies` | |

**Whatever the stack: run the analyser the ecosystem already ships before
writing one.** A hand-rolled check competing with `cargo audit` will be wrong in
a way nobody notices.

## By shape: a published package

This is where the sharpest findings live, because the repository cannot see
them.

| Probe | Needs | Answers |
|---|---|---|
| `published-version` | registry, network | does the registry serve what the manifest claims? |
| `channel-divergence` | git (+ registry) | do the channels that share a version share a tree? |
| `tarball-contents` | registry, network | does the published artefact contain what it should — and nothing it should not? |
| `install-smoke` | network | does a clean install from the registry actually run? |
| `adoption` | network | downloads: is this in production at all? |
| `release-reliability` | gh | what share of *release* runs failed, and was a failure noticed? |

**`channel-divergence` is the reason this section exists**, and its trap is in
`SKILL.md`: compare the pair that can disagree — the tag against the branch tip
— not the registry against the tag, which agree by construction.

**`tarball-contents` catches the other direction.** A `files` allowlist that is
too wide ships tests, fixtures and sometimes `.env.example`; one too narrow ships
a package that cannot run. `npm pack --dry-run` prints the list.

**`release-reliability` is the closest thing a package has to a production
log.** A library never phones home, so the only observable failure signal is the
release pipeline. Measure the *release* workflow specifically — an overall
success rate is dominated by cheap validation runs and hides it.

## By shape: a deployed service

| Probe | Needs | Answers |
|---|---|---|
| `telemetry-present` | — | can anyone see a failure that happens to a user? |
| `health-endpoint` | network | does the deployed thing answer, and with what? |
| `deployed-version` | network | does what is running match what is tagged? |
| `migration-drift` | db access | are there migrations the deployed schema does not have? |
| `config-surface` | — | which env vars are required, and which are documented? |

**`deployed-version` is `channel-divergence` for services**, and it fails the
same way: a health endpoint reporting a version string proves a string.

**`config-surface` is almost always a finding.** Collect every `env` reference
in the code, compare against `.env.example` and the README. The difference is
what a new deployment will discover at runtime.

## By shape: a monorepo or a submodule tree

| Probe | Needs | Answers |
|---|---|---|
| `pointer-freshness` | git | does the parent point at a commit the child still has? |
| `pin-vs-release` | git, network | is the pinned commit the released one, by **tree** and not by version string? |
| `cross-package-drift` | — | do two packages state the same fact differently? |
| `workspace-orphans` | manager | is a package in the tree and in no workspace list? |

**A parent records a submodule as a pointer to one commit, and moving the
submodule does not move the pointer.** Work can be committed, pushed and green
while a clone of the parent gets the commit before it — and neither repository
looks wrong alone. Require `git submodule status` with no line starting `+`.

## By shape: a public web surface

| Probe | Needs | Answers |
|---|---|---|
| `robots-and-sitemap` | network | can a crawler reach what the product wants read? |
| `render-without-js` | network | is the answer extractable without running scripts? |
| `heading-and-schema` | network | one question per page, one answer, marked up |
| `link-rot` | network | do the addresses the site publishes still resolve? |

Depth beyond this is `seo-aeo-audit`'s ground, and an audit that reproduces it
badly is worse than one that names the boundary and points.

## Production evidence through connected MCP servers

Where the project uses a service **and** its MCP server is connected in this
session, read it. Where it is not, the probe is `blind` with that as the reason
— and that sentence belongs in the report.

| Source | Read | Never read |
|---|---|---|
| error tracker | issue counts by class, first/last seen, release correlation, regression flags | stack traces, request bodies, user identifiers |
| analytics | funnel steps, retention curves, conversion rates as numbers | individual sessions or user paths |
| hosting / edge | error rates, deploy history, rollback events | request logs |
| database | row counts, table sizes, migration state, index health | rows |
| CI / VCS | run history, failure rates, open issues and their age | — |

**The right-hand column is the contract, not a suggestion.** The report carries
aggregates and pointers; a reader who needs the trace opens the tracker. A report
holding raw bodies is one nobody can forward, and a report nobody forwards is
written once.

**Ask before assuming a service is unused.** A project with no Sentry dependency
in its manifest may still run one at the platform layer. Absence of a dependency
is evidence about the manifest, not about production.

## Adding a probe

```python
@probe("my-probe", "prod", needs=("gh", "network"))
def _p_mine(ctx):
    rc, out, err = ctx.sh("gh", "api", "repos/:owner/:repo/releases")
    if classify_output(rc, out, err) == "blind":
        return Result("blind", "gh returned nothing: %s" % (err or rc))
    ...
    return Result("clean", "12 releases, newest 3 days old")
```

Four rules, each of which has a defect behind it:

1. **Declare every need.** A probe that shells out to find out cannot explain
   why it was skipped, and the report loses the reason.
2. **Assert the input arrived.** A component that never received its input fails
   *open*, and from outside it is indistinguishable from one that approved.
3. **Never let a probe take the run down.** It may raise; the registry converts
   that to `blind`. It must not `sys.exit`.
4. **Exclude the audit's own output.** A probe reading `docs/audit/` measures
   the instrument. Caught by the three-run fixture, not by reading.

## What deliberately has no probe

- **Whether the code is good.** Style, architecture and taste are readings, and
  a script that scores them produces a number nobody can argue with.
- **Whether a finding matters.** Severity and effort are the operator's, priced
  with the project's own formula.
- **Anything that writes.** Not a fix, not an issue, not a board row. The audit
  proposes; a separate act accepts.
- **Anything requiring a credential the operator has not already connected.**
  An audit that asks for a new secret to run is a supply-chain risk wearing a
  clipboard.
