# Design review: the interface, walked by its users, as a gate

Load this when a node's brief names a `surface_class` other than `none`, at stage 3 (before
build) and at stage 6 (after build), in a single run, a wave or a release iteration. The agent
is [`../../../agents/design-tester.md`](../../../agents/design-tester.md); its gate is
`scripts/design_gate.py`; its machine discipline is `scripts/resource_guard.py`; its browser is
[`browser.md`](browser.md) → *The tester's browser*.

## Contents

- When it is owed
- The test panel
- The two passes and their gates
- The budget, and where findings go
- Degradation

## When it is owed

Every node that changes what a user sees or does. On `flagship`, `product` and `ad` it is a
gate; on `internal` it is recommended and its report is checked for honesty, its coverage
reported. A recorded refusal (`Design review: declined: <reason>` in the brief) passes; an
unmentioned one does not. Waves and iterations owe it per UI node, never once per wave.

## The test panel

`docs/ux/test-panel.md`, owned by super-ux (`ux-foundation` → *The test panel*): ten portraits,
each with **basis** (`evidence RE-NN` or `hypothesis`), **situation**, **goals**, **features**,
**scenarios** (composite chains by `SCR-` id), **activation** (steps to first value, and where
it drops), **retention** (trigger → action → reward → what brings it back) and **needs**
(device, engine, locale, accessibility). The operator confirms it once; a later change of the
product revises it. `python3 scripts/design_gate.py panel docs/ux/test-panel.md` gates it.

A portrait marked `hypothesis` chooses what to test, never what to build: the super-ux rule
that a synthetic persona is never evidence still holds.

## The two passes and their gates

| Stage | Pass | Reads | Gate |
|---|---|---|---|
| 3, before build | D, design | Figma frames (Figma MCP) or, without Figma, the scenario's mockups | `design_gate.py report <r> --class <c> --panel docs/ux/test-panel.md --scope <ids> --require design` exits 0 |
| 6, after build | B, build | the running build in the recorded browser, each step captured, compared with its frame or mockup, the outcome read back | the same command with `--require build` exits 0, and `resource_guard.py verify` is clean |

The checklist every step answers: `frame`, `primary_action`, `controls`, `focus`, `states`,
`text_fit`, `outcome`: pass, fail, na or NOT_RUN with its reason. A failed item names its
finding; a `breaks` finding names its failed item. NOT_RUN is never PASS.

With Figma, pass D judges what the designer drew and pass B how it was built against it.
Without Figma, pass D judges the mockups and pass B the build against them.

## The budget, and where findings go

One pass D and one pass B per surface per round; a re-review reads only the steps the fix
touched; at most `run.finish.maxRounds` rounds ([`finish-line.md`](finish-line.md)). A finding
in the scope goes to the builder (pass D: the designer); outside it, to the board with its
evidence. The review never widens the iteration.

## Degradation

- **No panel**: NOT_RUN, and super-ux `ux-foundation` builds it; the gate does not pass on a
  missing panel.
- **No Figma and no mockup**: pass D reads the scenario text alone and says so in every row's
  `frame` (`scenario text only`); a gated class owes a mockup next round.
- **No browser channel**: pass B is NOT_RUN, the weaker claim recorded, never "tested".
- **A sign-in wall**: the human gate is named once, the steps behind it NOT_RUN, the rest run.
