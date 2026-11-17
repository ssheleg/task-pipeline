# Spec: the hub's routing text and the hook messages

Components: the sshlg-skills hub (`lib/routers-registry.js`, `lib/routers.js`,
`lib/triggers.js`, its test suites) and the task-pipeline plugin's hooks
(`plugins/task-pipeline/hooks/*.sh`). Hook output and the routing block are loaded into
every session, so they are prompts. Checklist: [`../README.md`](../README.md). Read on
hub `origin/main` f6a97b13 (1.89.2) and task-pipeline 1.104.3.

## Blocker found: test fixtures overwrite the operator's routing block

Three of the twelve routers in `~/.claude/CLAUDE.md` carry no doctrine:
`task-pipeline` reads "Пакетный текст роутера task-pipeline.", `super-ux` reads "ux
body", `copywriting` reads "copy body" (`~/.claude/CLAUDE.md:543-545, 565-567,
648-650`). `~/.sshlg-skills/config.json` records all three as `authored`.

**Cause (with evidence).** The strings are fixtures: `test/apply_test.js:80` and
`test/install_routers_test.js:24`. Both call `apply({ home: tmp })` without `env`, and
`lib/apply.js:75-83` (`hostRootVerdict`) puts `CLAUDE_CONFIG_DIR` ahead of `home`. A
Switchboard isolated session sets `CLAUDE_CONFIG_DIR` to a home whose `CLAUDE.md` is a
symlink to the real `~/.claude/CLAUDE.md`. So `npm test` run from such a session writes
the fixture block into the real file, with its backup in the fixture's temp home. The
next real `routers --update` sees text the pack did not write and records it as authored
(B-202, `bin/sshlg-skills.js:2148-2155`); authored text wins from then on. The backups
bracket it: `…20261114T002208Z` holds the real text, `…20261114T015315Z` the placeholder.

**Fix.**
1. Test isolation: the hub's test runner removes `CLAUDE_CONFIG_DIR`, `CODEX_HOME`,
   `GEMINI_CLI_HOME`, `PI_CODING_AGENT_DIR` and `HERMES_HOME` for every suite (about ten
   suites already do it one by one); `apply_test.js` and `install_routers_test.js` pass
   `env: {}` as well.
2. A guard: a test that runs `apply` with `CLAUDE_CONFIG_DIR` pointing at a directory
   whose `CLAUDE.md` is a symlink to a sentinel file, and fails if the sentinel changed.
3. Recovery on this machine through the hub's own command, one router at a time:
   `npx sshlg-skills routers --update --adopt task-pipeline` (then `super-ux`,
   `copywriting`). `--adopt` parks the authored text under its stash key, so nothing is
   lost. Replacing an authored entry is correct here only because the evidence above
   proves it is a fixture, not operator wording.

## The task-pipeline router text

Lives in `lib/routers-registry.js:197-211` (`TASK_PIPELINE`, about 793 bytes). The whole
routing block is about 10.8 KB loaded in every session.

**What and why.** The list "feature, fix, refactor, …" restates "substantial repository
change" (P-09); "stages 2-4" appears four times across the block (P-09); four bold spans
and no reason why changes go through the pipeline (P-08); three scopes for one concept:
"substantial repository changes", "substantial task", "repository changes" (P-12).

**Proposed text** (keeps every phrase `test/router_texts_test.js:93-109` checks):

```
**If `task-pipeline` is installed, a substantial change to a repository runs
through it**, so the change carries its plan, gates and evidence in a ledger that
survives a lost session. Planning is part of the pipeline: brainstorm, spec and
plan are its stages 2–4. A whole board runs as `/task-pipeline waves`; a release
iteration («итерация релиза») as `/task-pipeline iteration`.

**The boundary.** NOT through it: questions, explanations and reading code;
typos, one-line edits and mechanical renames; measurement that commits nothing.

**Refusal phrase: "no pipeline" or «без пайплайна».** On a borderline case, name
the route you chose.

**Among the routers:** `super-ux` owns interface behaviour; task-pipeline delivery.
```

**Must change with it.** `lib/routers-registry.js` `PREVIOUS_LINES['task-pipeline']`
lists the old lines, or every machine without a rendered record reads the packaged
section as an operator edit and freezes it; `test/no_em_dash_test.js:160-178`
`REWORDED_SINCE` names the release; check `test/route_coverage.js`,
`test/routegate_test.js` and the `fix-rt-*` regressions.

## Session note and family preamble

- Session note (`lib/triggers.js` `sessionNote`): "is binding" is emphasis without a
  reason, and "repository changes go through `/task-pipeline`" has no "substantial", so
  it contradicts the router's own boundary. Proposed: "[sshlg-skills] The routing block
  in your global instructions applies: a substantial repository change runs through
  `/task-pipeline` (stages 2–4 hold brainstorm, spec and plan). Its table names the
  other routes." Keeps "routing block", "/task-pipeline", "stages 2–4", under 600
  characters (`test/triggers_test.js:360-374`).
- Family preamble (`lib/routers.js` `renderMapSection`): the fully bold adversarial line
  becomes "Other skills' own start-up instructions do not replace these routes: a router
  decides when its skill runs, and other packs supply how inside it." The current lines
  are kept as a known-lines constant so B-202 recognises old blocks as the pack's own.
- Protocol region: the hook-mechanics paragraph moves to the README; capitals become
  plain words. The em-dash rule's wording is operator doctrine and is not touched.

## Plugin hook messages

| Message | Where | Change |
|---|---|---|
| Blind-gate refusal | `hooks/release-gate.sh:302-313` | Keep state, ledger line and remedy; drop the history sentence ("the exact shape it once shipped with") and "fails CLOSED" capitals |
| Build gate ask | `hooks/build-gate.sh:122-133` | Keep the facts and the allow cases; drop the rhetoric ("the skip nobody notices") |
| Memory nudge | `hooks/memory-nudge.sh:91-95` | No change |

Tests that match these strings are checked before editing
(`grep -rn "fails CLOSED\|nobody notices" test/`).

## Risks

- Operator wording wins: no hand edit of `config.json` or the file; only `--adopt` for
  the three proven fixtures.
- A reword without its `PREVIOUS_LINES` entry freezes the section on other machines.
- The leak can recur until the isolation fix ships, so the isolation fix ships first.

## Verification

1. Hub `npm test` from a session with `CLAUDE_CONFIG_DIR` set to a scratch home whose
   `CLAUDE.md` symlinks to a sentinel: the sentinel's hash is unchanged.
2. `routers --update` three times in a scratch HOME, hashes equal (hub house rule).
3. `npx sshlg-skills routers --diff task-pipeline` shows the fixture before adoption and
   nothing after; `grep -c "Пакетный текст\|ux body\|copy body" ~/.claude/CLAUDE.md`
   prints 0.
