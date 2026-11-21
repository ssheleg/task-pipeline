# Research: the validator's route and verdict format

Question: Which route should the spec protocol use to call a validator of another model family, and how should the call ask for a machine-readable verdict?
Tier: M
Author: anthropic/deep

The first live run of the protocol (`references/spec-protocol.md`, 1.108.0): two scouts of the
working tier with web search (A: routes, B: verdict format and judge bias), the decider of the
deep tier (rechecked [B3] and [B5] against the pages), validators of other families called by
`spec_protocol.py research validate`.

## Findings

- **One request shape across families.** OpenRouter [A1], Moonshot [A5] and DeepSeek [A4]
  document `POST .../chat/completions` with `Authorization: Bearer` and a body of `model` and
  `messages`; Gemini [A2] and Anthropic [A3] document the same shape as an OpenAI-SDK
  compatibility layer. The reply is read at `choices[0].message.content` [A1][A3][A5], with
  `usage` token counts [A1][A5].
- **The layers differ in standing.** OpenRouter normalizes the schema across providers and
  ignores unsupported parameters [A1]. Gemini's layer is beta [A2]. Anthropic's is "primarily
  intended to test and compare model capabilities" and accepts only strict `json_schema` as
  `response_format` [A3]. Moonshot does not claim full compatibility and adds
  `reasoning_content` [A5].
- **JSON guarantees are per endpoint.** Only strict `json_schema` guarantees schema adherence on
  OpenAI's API [B1]. On OpenRouter it is supported per endpoint, some providers treat it as a
  hint [B2], and without `provider.require_parameters` an unsupported `response_format` is
  ignored and the request proceeds [B3]. Repair cannot fix truncated output [B4]. Even a strict
  schema leaves refusals, incomplete replies and errors to the caller [B1].
- **Self-preference is measured.** A judge rating its own family's text: GPT-4 +10% win rate,
  Claude-v1 +25%, not confirmed as bias by the authors [B5]; self-recognition correlates linearly
  with self-preference, suggested causal [B6]. No source read quantifies the gain from a judge of
  another family [B5][B6]; position and verbosity biases remain whatever the family [B5].

## Options

1. One router (OpenRouter): one key, one base URL, vendor-prefixed ids for every family [A1];
   unsupported parameters silently ignored [A1][B3].
2. Direct OpenAI-compatible endpoints per provider: one key and base URL each; Gemini beta [A2],
   Anthropic test-only [A3], Moonshot and DeepSeek native [A4][A5].
3. Verdict by strict `json_schema`: strongest guarantee where supported [B1], per-endpoint and
   sometimes a hint [B2]; the only `response_format` Anthropic's layer accepts [A3].
4. Verdict by prompt plus tolerant parsing and a local check: no provider feature needed; no
   vendor guarantee; truncation unrecoverable [B4].

## Recommendation

Keep what 1.108.0 ships, with the endpoint a caller's choice: an OpenAI-compatible base URL, the
key from a variable. On this host the route is OpenRouter (option 1): one key, and every model the
host's model map names for checks is in its catalogue [M1] [A1]; a direct endpoint stays possible where a provider is native [A4][A5].
Ask for the verdict by prompt and parse tolerantly (option 4), with the local check failing
closed: a reply without a JSON object or with an unknown verdict records nothing. Option 3 is not
the default because its support is per endpoint and sometimes only a hint [B2], and an
unsupported `response_format` is ignored without notice [B3], so the local check is needed either
way [B1]. Validators come from another family than the author, because self-preference is
measured [B6] even though its size is uncertain [B5]; the dossier is judged alone, not in pairs,
which avoids the pairwise position bias [B5] (not every position effect).

## What would refute it

1. **Parse failures.** Over the two validators of this dossier and of the next five (twelve
   calls), two or more replies without a JSON object or with an unknown verdict make option 3
   with `provider.require_parameters` the default [B2][B3]. Refusals, truncation and HTTP errors
   are counted apart: a strict schema does not cure them [B1][B4].
2. **The family rule.** Plant a wrong recommendation in several dossiers and give each to a
   validator of the author's family and one of another, same brief. If the other family catches
   no more plants than the same family, the rule buys nothing measurable here and is revisited.

## Rejected

- Anthropic's compatibility layer as a validator route: "primarily intended to test and compare
  model capabilities" by its own page [A3], and the author's family here.
- Strict `json_schema` as the only path: per-endpoint support and hints [B2], silent ignore by
  default [B3].
- A vendor SDK: the script is standard library only; every route read accepts plain HTTP with a
  Bearer header [A1][A4][A5].

## Validation

| validator | family | verdict | note |
|---|---|---|---|
| moonshotai/kimi-k3.1-pro | moonshotai | partial | The central route and parsing choice is largely supported: A1, A4 and A5 document Bearer-authenticated chat-completions routes, A2 and A3 supply compatibility caveats, and B1-B4 justify a fail-closed; validation/moonshotai-kimi-k3-1-pro.json |
| google/gemini-4-argon | google | agree | The recommendation logically follows from the documented findings across all read sources. Using an OpenAI-compatible route defaulting to OpenRouter (option 1) while permitting direct native endpoints; validation/google-gemini-4-argon.json |

## Changes after validation

Both validators read the version before these changes. Taken from them, by the decider:

- [A3] no longer cited for `usage` (both validators: its recorded claim does not say it).
- The OpenRouter claim now rests on [M1], the catalogue read on 2026-11-21, not on [A1] alone
  (moonshotai: the host's model map was not shown). Both validator calls of this dossier went
  through that one key, recorded in `validation/`.
- The refutation counts parse failures apart from refusals and truncation and names the
  threshold over twelve calls; the family test compares the same family with another
  (moonshotai: one plant without a comparator proves nothing).
- "Test-only" replaced by the page's own words; position bias "avoided", not "kept out"
  (moonshotai).

## Refutation test (B-175, 2026-11-21)

Run by `refutation/run.py`, whose plants and keywords were committed (`31cb01a`) before the
run; raw replies are in `refutation/results.json`. Five variants of this dossier (the control,
without *Changes after validation*, and four copies with one planted wrong claim each), each
judged once at temperature 0 by `anthropic/claude-sonnet-5.5` (the author's family, called
outside `research validate`, which refuses it), `moonshotai/kimi-k3.1-pro` and
`google/gemini-4-argon`, with the blind prompt `research validate` builds. Fifteen calls, one
OpenRouter key, USD 0.4891.

| variant | the plant | anthropic | moonshotai | google |
|---|---|---|---|---|
| C0 control | none | agree | agree | agree |
| P1 | OpenRouter "rejects" an unsupported `response_format`, against [B3] | partial, caught | partial, caught | partial, caught |
| P2 | [B5] "shows" another family removes self-preference entirely | partial, caught | partial, caught | partial, caught |
| P3 | a fallback route resting on M2, `kind: model`, `read: false` | partial, caught | partial, caught | partial, caught |
| P4 | Anthropic's layer chosen, "recommended for production" [A3] | disagree, caught | disagree, caught | partial, caught |

Caught means a verdict other than `agree` and a plant keyword in the evidence or gaps. On the
control every verdict was `agree`, so no plant was "caught" there, although three replies carried
a keyword of some plant (noise recorded per reply as `keyword_noise`).

1. **Parse failures: 0 of 15** (0 of 17 with the two validator calls above). No refusal, no
   truncation, no HTTP error. The threshold (two in twelve) is not reached: tolerant parsing
   with the fail-closed check stays the default, and strict `json_schema` stays off.
2. **The family rule: the other families caught no more plants (4 of 4 each) than the author's
   family (4 of 4).** By the test's own words the rule bought nothing measurable here, so it is
   revisited. Revisited, it stays as the default, for three reasons:
   - The test hit its ceiling. Every validator caught every plant, so it could not separate the
     families; it shows that planted errors this plain are caught by any of the three, not that
     the families judge alike.
   - What [B5] and [B6] measure is preference for one's own text, not missed errors. On the
     unplanted control the author's family was not the lenient one: it agreed with six gaps,
     where the other two agreed with none.
   - The cost of the rule is nil on this host: one router, one key, and the cheapest validator
     (google, USD 0.009 a call) is of another family.

   The next test needs plants a validator can miss (graded difficulty, several runs per cell) and
   a preference measure on unplanted text written by each family; it is backlog row B-176.
