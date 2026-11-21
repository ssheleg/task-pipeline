# Research: the validator's route and verdict format

Question: Which route should the spec protocol use to call a validator of another model family, and how should the call ask for a machine-readable verdict?
Tier: M
Author: withheld/deep

## Findings

- **Cross-family requirement**: Evaluators recognize their own text and score their own outputs higher than humans rate them, with a linear correlation between self-recognition and self-preference [B6]. Earlier evaluation observed GPT-4 and Claude-v1 favoring their own outputs by 10% and 25% respectively, though that study could not determine whether the models exhibited a self-enhancement bias [B5].
- **Unified vs. direct routing**: OpenRouter provides a single endpoint (`POST https://openrouter.ai/api/v1/chat/completions` with `Authorization: Bearer`) that accepts vendor-prefixed `model` names and `messages`, normalizing the request/response schema (`choices[]`, `finish_reason`, and `usage` with token counts and cost) across models and providers [A1]. It currently serves the host model map's check and volume models (`moonshotai/kimi-k3.1-pro`, `google/gemini-4-argon`, `z-ai/glm-5.3`, `deepseek/deepseek-v4.1-flash`) [M1].
- **Direct vendor endpoints**: Calling vendors directly requires distinct base URLs and carries compatibility caveats: Gemini's OpenAI compatibility (`https://generativelanguage.googleapis.com/v1beta/openai/`) is still in beta [A2]; Anthropic's (`https://api.anthropic.com/v1/`) is intended for testing/comparison rather than long-term or production use and ignores many fields [A3]; Moonshot (`https://api.moonshot.ai/v1`) does not claim full compatibility [A5]; DeepSeek (`https://api.deepseek.com`) documents `model`, `messages`, and `stream` [A4].
- **Verdict format and schema enforcement**: JSON mode (`json_object`) guarantees valid JSON but not schema adherence; only Structured Outputs (`response_format` with `json_schema` and `strict: true`) ensure schema adherence [B1]. Even with `json_schema`, the caller must handle refusals, incomplete responses, API errors, and business rules the schema cannot express [B1].
- **Provider routing and healing on OpenRouter**: By default, OpenRouter's `provider.require_parameters` is `false`, meaning providers that lack support for a parameter ignore it and proceed [A1, B3]. Support for `response_format` `json_schema` varies per endpoint and over time, and some providers treat the schema only as a strong hint [B2]. Setting `provider.require_parameters: true` routes requests only to endpoints that support all requested parameters [B2, B3]. For non-streaming `json_schema` or `json_object` requests, OpenRouter's opt-in Response Healing plugin repairs malformed JSON (brackets, commas, quotes, fences, preceding prose), though it cannot fix output truncated by token limits [B4].

## Options

1. **OpenRouter route + `json_schema` (`strict: true`) + `require_parameters: true` + Response Healing + client-side validation**: Send a non-streaming `POST` to `https://openrouter.ai/api/v1/chat/completions` [A1, B4] using a vendor-prefixed model from a different family [A1, B6, M1]. Request `response_format` of `json_schema` (`strict: true`) [B1, B2], set `provider.require_parameters: true` [B2, B3], enable the Response Healing plugin [B4], and validate the parsed JSON in the script against the verdict schema and business rules [B1, B2].
2. **Direct vendor OpenAI-compatible endpoints + `json_schema` (`strict: true`)**: Configure per-vendor base URLs and Bearer keys for Gemini, Anthropic, DeepSeek, and Moonshot [A2, A3, A4, A5], requesting `response_format` with `json_schema` (`strict: true`) [A3, A5, B1] and reading `choices[0].message.content` [A3, A5].
3. **OpenRouter route + `json_object` mode**: Call OpenRouter [A1] with `response_format` set to `json_object` [B1, B4] without `json_schema` or `require_parameters`, relying on prompt instructions and client-side validation.

## Recommendation

Pick **Option 1**.

Using OpenRouter (`POST https://openrouter.ai/api/v1/chat/completions`) lets a standard-library HTTP script reach all required check and volume model families (`moonshotai/kimi-k3.1-pro`, `google/gemini-4-argon`, `z-ai/glm-5.3`, `deepseek/deepseek-v4.1-flash`) through a single URL, credential, and normalized response format (`choices[]`, `finish_reason`, `usage`) [A1, M1]. To ask for a machine-readable verdict, the call should specify `response_format` with `json_schema` (`strict: true`) because `json_object` does not ensure schema adherence [B1]. Because OpenRouter ignores unsupported parameters by default [A1, B3] and `json_schema` support is per-endpoint [B2], the request must set `provider.require_parameters: true` so it only routes to supporting endpoints [B2, B3]. Because some providers still treat the schema as a strong hint rather than a strict guarantee [B2], and because applications must always handle refusals, incomplete outputs, and business rules [B1], the call should enable the opt-in Response Healing plugin (for non-streaming repair of fences, prose, or syntax errors) [B4] and enforce strict schema and business-rule validation in the Python script after parsing [B1, B2].

## What would refute it

A live test calling `https://openrouter.ai/api/v1/chat/completions` with `response_format` (`json_schema`, `strict: true`) and `provider.require_parameters: true` across the target cross-family validator models in the catalogue (`moonshotai/kimi-k3.1-pro`, `google/gemini-4-argon`, `z-ai/glm-5.3`, `deepseek/deepseek-v4.1-flash`) [M1] fails to find any supporting endpoint (returning routing errors for the required validator families) or produces unparseable/non-compliant verdicts at a rate that prevents automated validation even with Response Healing enabled [B2, B3, B4].

## Rejected

- **Option 2 (Direct vendor OpenAI-compatible endpoints)**: Rejected because Anthropic documents its compatibility endpoint as not production-ready or a long-term solution [A3], Gemini's compatibility layer is still in beta [A2], Moonshot does not claim full compatibility [A5], and DeepSeek's quick-start does not document `response_format` `json_schema` [A4].
- **Option 3 (`json_object` mode or omitting `require_parameters: true`)**: Rejected because `json_object` only guarantees valid JSON, not adherence to the verdict schema [B1], and omitting `provider.require_parameters: true` on OpenRouter allows providers that lack `json_schema` support to silently ignore the parameter [A1, B2, B3].

## Validation

| validator | family | verdict | note |
|---|---|---|---|
