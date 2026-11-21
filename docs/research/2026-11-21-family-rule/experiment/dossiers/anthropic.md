# Research: the validator's route and verdict format

Question: Which route should the spec protocol use to call a validator of another model family, and how should the call ask for a machine-readable verdict?
Tier: M
Author: withheld/deep

## Findings

1. **Why the validator should be another family.** LLM judges show position, verbosity and self-enhancement biases. GPT-4 favors itself with a 10% higher win rate, and Claude-v1 with a 25% higher win rate. The same study says it "cannot determine whether the models exhibit a self-enhancement bias" [B5]. A later abstract reports three things [B6]:
   - evaluators score their own outputs higher than humans rate them;
   - models recognize their own text with non-trivial accuracy;
   - self-recognition and self-preference correlate linearly, which the authors suggest is causal.

   Together these support a cross-family validator. The evidence for self-preference is suggestive, not settled.

2. **One aggregator route exists.** OpenRouter takes `POST https://openrouter.ai/api/v1/chat/completions` with `Authorization: Bearer` and a vendor-prefixed `model` plus `messages` [A1].
   - It normalizes the request and response schema across models and providers, including `finish_reason`.
   - It returns `choices[]` and `usage`, with `prompt_tokens`, `completion_tokens`, `total_tokens` and `cost` [A1].
   - The catalogue lists `moonshotai/kimi-k3.1-pro`, `google/gemini-4-argon`, `z-ai/glm-5.3` and `deepseek/deepseek-v4.1-flash` as present, read 2026-11-21 [M1].

3. **Silent ignoring is the main hazard on OpenRouter.**
   - Unsupported parameters are ignored [A1].
   - `provider.require_parameters` defaults to false. Its definition is "Only use providers that support all parameters in your request" (verbatim) [B3].
   - Without it, a provider lacking a parameter ignores it and the request proceeds. This point comes from a page summary, not a verbatim quote [B3].

4. **Structured output on OpenRouter is uneven.** `json_schema` is supported by select models only [B2].
   - Support is set per endpoint, not just per model, and changes over time [B2].
   - Some providers treat the schema only as a strong hint, so exact compliance is not guaranteed [B2].
   - `require_parameters: true` routes the request only to endpoints that support the schema [B2].

5. **Schema adherence needs strict structured outputs.** JSON mode guarantees valid JSON but not adherence to a schema. Only `json_schema` with `strict: true` guarantees adherence [B1].

   Even then, the application must still handle:
   - refusals;
   - incomplete responses;
   - API errors;
   - business rules that a schema cannot express [B1].

   Only the first 100000 of about 151840 characters of this source were read [B1].

6. **Repair has limits.** OpenRouter's opt-in Response Healing plugin repairs malformed JSON in non-streaming `json_schema` or `json_object` requests: brackets, commas, quotes, fences and preceding prose. It cannot repair output truncated by the token limit [B4].

7. **Direct vendor routes are uneven.**

   | Vendor | Base URL | Structured output | Caveat |
   |---|---|---|---|
   | Gemini [A2] | `.../v1beta/openai/` | Supported | Still in beta; Gemini-specific options go in `extra_body` |
   | Anthropic [A3] | `https://api.anthropic.com/v1/` | `response_format` accepts only `json_schema` with `strict: true` | Meant for testing and comparison, not production; `n` must be 1; many fields ignored |
   | DeepSeek [A4] | `https://api.deepseek.com` | Source states no structured-output support | OpenAI/Anthropic-compatible format; body is `model`, `messages`, `stream` |
   | Moonshot [A5] | `https://api.moonshot.ai/v1` | `text`, `json_object` and `json_schema` | Returns `reasoning_content` and `usage`; does not claim full compatibility |

## Options

1. **OpenRouter as the single route, with strict schema enforcement.**
   - Send `response_format` = `json_schema` with `strict: true` and `provider.require_parameters: true`.
   - The verdict schema is `verdict` ∈ {`agree`, `partial`, `disagree`} plus `evidence`.
   - Parse `choices[0].message.content` locally and validate it against the schema.
   - Handle refusals, a truncation `finish_reason` and HTTP errors as failed validations.
   - Basis: [A1][B1][B2][B3][M1].
2. **Direct vendor endpoints, one adapter per family.** Call Gemini [A2], DeepSeek [A4] or Moonshot [A5] on their own OpenAI-compatible base URLs, each with its own key. Use structured output where the vendor documents it.
3. **JSON mode or prompt-only JSON, made robust by repair.** Ask for `json_object`, or instruct JSON in the prompt. Optionally enable Response Healing, then parse leniently [B1][B4].

## Recommendation

Option 1.

- **One request shape covers all families.** A single standard-library HTTP call (one URL, one Bearer key, one normalized response with `usage.cost`) reaches validators from several families other than the author's. The candidate ids are confirmed present [A1][M1].
- **It closes the silent-ignore hole.** `require_parameters: true` stops the schema being dropped without notice. Without it, a validator could return free text while the request still appears to succeed [A1][B2][B3].
- **It is the only mode that promises schema adherence.** Strict `json_schema` gives that guarantee; JSON mode does not [B1].
- **Local checks stay mandatory.** Some endpoints treat the schema as a hint [B2], and refusals and truncation remain possible [B1]. The script must therefore parse locally, check the verdict against the allowed values, and require non-empty evidence. A missing or invalid verdict counts as "no verdict", never as `agree`.
- **Response Healing is optional.** It may be enabled, but it is not relied on, because it cannot fix truncation [B4].
- **Why not Option 2.** It multiplies adapters and keys, rests on a beta endpoint [A2], and includes a vendor that does not claim full compatibility [A5]. It is kept only as a fallback if a needed model is missing from OpenRouter.

## What would refute it

Run a fixed probe: one known spec claim, N = 10 calls per model id from [M1], each through OpenRouter with strict `json_schema` and `require_parameters: true`.

The recommendation is refuted for practical use if any of these happens:

- the calls for a needed cross-family model are routinely rejected for lack of a supporting endpoint;
- returned content fails local parsing or schema validation in more than an occasional call;
- the call silently returns non-JSON despite `require_parameters`.

A further check: send the same request without `require_parameters` to an endpoint that lacks schema support. If the schema is not ignored there, the claimed hazard from [B3], which rests on a summary, is overstated, though that would not by itself overturn the route.

## Rejected

- **Anthropic's OpenAI-compatibility endpoint** as the validator route. The vendor describes it as not a long-term or production-ready solution [A3].
- **JSON mode alone.** It guarantees valid JSON but not the verdict schema [B1].
- **Relying on Response Healing for correctness.** It cannot repair truncated output [B4] and does not enforce the schema.
- **Treating cross-family validation as a guarantee of unbiased judgment.** [B5] could not determine whether self-enhancement bias exists, and [B6] is read from the abstract only.

## Validation

| validator | family | verdict | note |
|---|---|---|---|
