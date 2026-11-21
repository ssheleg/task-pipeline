# Research: the validator's route and verdict format

Question: Which route should the spec protocol use to call a validator of another model family, and how should the call ask for a machine-readable verdict?
Tier: M
Author: withheld/deep

## Findings

- OpenRouter documents `POST https://openrouter.ai/api/v1/chat/completions` with Bearer authorization, a vendor-prefixed `model`, and `messages`. It normalizes response schemas and `finish_reason` across models and providers, but unsupported parameters may be ignored [A1].
- JSON mode alone ensures valid JSON, not schema adherence. Structured Outputs use `response_format` with `json_schema` and `strict: true`; applications must still handle refusals, incomplete responses, API errors, and business rules that the schema does not express [B1].
- On OpenRouter, structured-output support is endpoint-specific and changes over time. Some providers treat the schema only as a strong hint. Setting `provider.require_parameters: true` restricts routing to endpoints supporting the request parameters [B2]. It defaults to `false`; without it, a provider can ignore an unsupported parameter and proceed [B3].
- The 2026-11-21 catalogue snapshot contained `moonshotai/kimi-k3.1-pro`, `google/gemini-4-argon`, `z-ai/glm-5.3`, and `deepseek/deepseek-v4.1-flash` [M1]. This establishes presence at that time, not current structured-output support.
- Cross-family validation is consistent with the reported self-preference concerns, but does not guarantee impartiality. Zheng et al. report self-favoring win-rate examples while explicitly stating that their study cannot determine whether the models exhibit self-enhancement bias; Panickssery et al. report self-recognition and self-preference, with fine-tuning evidence suggesting a causal relationship [B5][B6].
- OpenRouter's optional Response Healing plugin can repair some malformed JSON in non-streaming structured-output requests, but cannot repair token-limit truncation [B4].

## Options

1. **OpenRouter with strict structured output.** Use the normalized chat-completions route, select a vendor-prefixed model from a different family than the author, request strict `json_schema`, and set `provider.require_parameters: true` [A1][B2][B3].
2. **Direct Gemini OpenAI-compatible REST.** Use `https://generativelanguage.googleapis.com/v1beta/openai/` with Bearer authorization and structured output. This supports chat completions and structured output, but the compatibility support is still beta [A2].
3. **Direct Moonshot/Kimi.** Use its Bearer-authenticated chat-completions API with `response_format` set to `json_schema`. It returns message content and token usage, but does not claim full compatibility [A5].
4. **Direct Anthropic OpenAI-compatible API.** Use `https://api.anthropic.com/v1/`, `n: 1`, and strict `json_schema`, reading `choices[0].message.content`. Anthropic describes this compatibility route primarily as a testing/comparison facility, not a generally production-ready long-term solution; many fields are ignored [A3].

## Recommendation

Choose **option 1**. It provides one normalized HTTP interface across providers and model families, while `require_parameters` prevents the normal default behavior of silently proceeding without requested parameters [A1][B2][B3]. The direct alternatives carry beta, compatibility, or production-readiness caveats [A2][A3][A5].

The script should use its standard-library HTTPS and JSON facilities, without a vendor SDK. It must explicitly check that the configured validator family differs from the author's. For a `deep`/DeepSeek author, a concrete example is `moonshotai/kimi-k3.1-pro`, whose catalogue presence was observed in M1; `deepseek/deepseek-v4.1-flash` would not satisfy that family separation [M1].

Send a non-streaming request to the OpenRouter endpoint with `Authorization: Bearer <key>` and a body such as:

```json
{
  "model": "moonshotai/kimi-k3.1-pro",
  "messages": [
    {
      "role": "system",
      "content": "Validate the supplied specification. Return only JSON matching the supplied schema. The verdict must be agree, partial, or disagree. Supply concrete evidence for the verdict."
    },
    {
      "role": "user",
      "content": "<specification and material to validate>"
    }
  ],
  "stream": false,
  "provider": {
    "require_parameters": true
  },
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "spec_validation_verdict",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "verdict": {
            "type": "string",
            "enum": ["agree", "partial", "disagree"]
          },
          "evidence": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "required": ["verdict", "evidence"],
        "additionalProperties": false
      }
    }
  }
}
```

Read the returned choice's message content and parse it as JSON. Because endpoint compliance is not uniformly guaranteed, apply a small standard-library check for the exact keys and types, the verdict enum, and at least one non-empty evidence string [B2]. Handle HTTP/API errors, refusals, incomplete or truncated responses, JSON parse failures, and schema or business-rule failures as validation errors—not as a `disagree` verdict [A1][B1][B4].

## What would refute it

Run a live conformance test for the selected model before deployment and whenever its model or endpoint configuration changes. Send non-streaming strict-schema requests with `provider.require_parameters: true`, using fixtures intended to produce all three verdicts and allowing sufficient output tokens. The test fails if no supporting endpoint is available, routing silently ignores the requested format, or repeated responses are truncated, non-JSON, schema-invalid, or lack usable evidence. Such a failure would refute OpenRouter as the default route **for that validator configuration**; catalogue presence alone would not be sufficient, and the protocol should select another model or a direct option rather than disable parameter enforcement [B2][B3][M1].

## Rejected

- **Prompt-only JSON or JSON mode alone:** neither establishes adherence to the verdict schema [B1].
- **OpenRouter with default parameter routing:** `require_parameters` defaults to `false`, allowing unsupported parameters to be ignored [B3].
- **Response Healing as a substitute for validation:** it is opt-in, limited to certain malformed-JSON repairs, and cannot fix truncation. Any repaired output would still require the same parsing and validation [B4].
- **DeepSeek as validator for a `deep`/DeepSeek author:** its documented API offers a compatible chat-completions route, but that choice would violate the different-family requirement [A4].
- **Treating cross-family selection as proof of unbiased judging:** the cited studies motivate caution but do not establish that every same-family judge is biased or that every cross-family judge is impartial [B5][B6].

## Validation

| validator | family | verdict | note |
|---|---|---|---|
