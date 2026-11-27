---
report:
  id: task-pipeline/2026-11-27-harness-gates-shape
  kind: review
  status: active
  date: 2026-11-27
  valid_until: 2026-12-07
  owner: task-pipeline
  supersedes: none
---

# Can task-pipeline's release gate read `harness-gates/1`? The answer to board request 78454944

## The question

fabric-agent-contract asked (board request 78454944, 2026-11-27): does the shape of
`catalogue/harness-gates.json` (`harness-gates/1`, DEC-0198, draft PR
[#365](https://github.com/passioncode-ai/fabric-agent-contract/pull/365)) suit a
mechanical reader in task-pipeline's release stage (fields `id`, `command`, `blocks`,
`status`/`row`, `runBy`)? Without an answer by 2026-12-02 the shape merges as is on
2026-12-03 and freezes on 2026-12-04. Running the gates is task-pipeline's row by
2026-12-07; they close ST-05 findings TP-1 (HG-07), TP-2 (HG-01) and TP-3 (HG-03).

## Sources read

- `catalogue/harness-gates.json` and `schemas/harness-gates.schema.json` at the head of
  branch `agent/st-shapes-20261127` (PR #365), read 2026-11-27.
- `docs/specification/release-proof.md` on that branch, section *harness gates* and
  `FAC-SEM-193` (RP-6).
- `src/validate-cli.ts` usage text on that branch: exit `0` no blocking problem, `1` a
  problem, `2` a usage error; `--kind source-package` exits `0` with a note when the
  folder holds no `fabric.package.json`.
- `package.json` on that branch: `pin:check`, `validate` and `privacy:check` scripts
  exist; the four test files named by HG-01, HG-07, HG-09 and HG-06 exist.
- ST-05 report `docs/reports/2026-11-27-st05-audit/README.md` on fabric-agent-contract
  `main`, lines 111-113 (TP-1, TP-2, TP-3).
- This repository: `references/gates.md` (*Progressive arming*, *False success*,
  *Anatomy of a project gate*) and `references/stage-07-lint-deploy.md`.

## Verdict

The shape is a sound base and may merge on 2026-12-03. Stable ids, the `blocks`
boolean, `status` with `row` exclusive under RP-6, `runBy` naming
`task-pipeline-release` and an integer `revision` are what a reader filters and
reports on. Four gaps stop the release stage from running the list **mechanically**.
Two of them need a field, and because every gate object is `additionalProperties:
false`, a field added after the freeze breaks every reader that validates revision 1;
so they belong in the shape **before 2026-12-04**.

### Needed before the freeze (new optional fields)

1. **`command` is prose, not a command.** HG-02 joins two commands with "and"; HG-03
   and HG-07 say "pnpm validate on ... a captured answer; the live probe is the
   adapter's check_service"; HG-06 ("a runner-run/1 row per runner ...") and HG-08
   ("the adapter's upgrade drill") name no command at all. A reader has to guess
   the arguments, which is a deploy from inference (`stage-07-lint-deploy.md`), or
   copy an id-to-command table into task-pipeline, which makes two lists of one
   thing. Proposal: keep `command` as the human line and add **`run`**, an array of
   argv arrays executed in order, each required to exit `0`, with placeholders from a
   closed set (for example `{checkout}`, `{contract}`, `{capture}`). A gate proved by
   records (HG-06) gets a command that checks the records, so every `exists` gate has
   the same shape. A gate whose input is captured from a live service names the
   capturing command first (the adapter's `check_service`, writing into `{capture}`).
2. **No applicability.** HG-03, HG-07 and HG-10 concern a service or a compact MCP
   surface; many integrated projects have neither. Without a predicate the reader
   cannot tell "not applicable" from "could not run", and `gates.md` requires the two
   to print differently (`dormant` and `skip`). Proposal: **`appliesTo`**, a closed
   enum (for example `any`, `service`, `mcp`, `compact-mcp`, `runners`) with the
   artefact each one looks for written in the spec, so the reader prints
   `dormant: HG-03 (no service descriptor)` instead of a silent pass.

### Needed in the spec text (no field)

3. **What `status: row` with `blocks: true` does.** HG-08 is both. Read literally,
   every release stops on a check nobody can run until CT-381 lands. Recommended
   rule: a `row` gate is reported as `pending: HG-08 (CT-381)` and does not stop a
   release; `blocks` takes effect when the gate becomes `exists`.
4. **A blocking gate that applies but cannot run stops the release.** For example the
   adapter or `pnpm` is missing, or `pnpm validate` exits `2`. Exit `2` is a usage
   error, not a pass, and a reader that maps "non-zero but not 1" to `skip` would let
   a broken invocation through. Also state which contract revision the reader uses
   (recommended: the contract at the version the project's `fabric-contract.lock.json`
   pins, printed with `revision` in the release evidence).

## What task-pipeline does next

The release stage (stage 7) reads `harness-gates/1`, filters `runBy` for
`task-pipeline-release`, runs each `exists` gate that applies through its `run`,
prints `ok`, `ERR`, `dormant` or `pending` per gate with the catalogue revision, and
stops on a blocking `ERR`. That closes TP-1, TP-2 and TP-3 by 2026-12-07. If the
fields above do not land, the fallback is a reader that hard-codes the argv per gate
id and checks on every run that the catalogue's ids and `command` lines still match
its table, so a drift fails loudly rather than running an old command.
