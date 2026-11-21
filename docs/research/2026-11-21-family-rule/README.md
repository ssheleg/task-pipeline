# Research: does a validator of the author's family miss more or favour its own text?

Question: Should `research validate` keep refusing a validator of the author's model family, or record it with a warning?
Tier: M
Author: anthropic/deep

Backlog B-176, after B-175 hit its ceiling [M1]. One scout of the working tier with web
search found C1 to C4; the decider (deep tier) wrote the experiment, committed it with its
decision rule before the run (`f17d94a`), and reads it here. Raw replies, plants, keywords
and the three written dossiers are in `experiment/`.

## Findings

- **The literature measures preference, not missed errors.** Self-enhancement was seen in
  pairwise judging (GPT-4 +10%, Claude-v1 +25%) but not confirmed as bias by its authors [B5];
  self-recognition correlates with self-preference [B6]. Wataoka et al. find the bias strongest
  in GPT-4 (0.749) and near zero for most judges, and trace it to low perplexity, "not whether
  the response is their own" [C2]. Against an evaluator-quality baseline only 51% of earlier
  self-preference findings stay significant [C4]. A panel of disjoint families shows "less
  intra-model bias", without a number in the abstract [C1]. A model fixes an error it is told
  came from outside and misses the same error presented as its own (64.5% blind spot) [C3];
  that is self-correction, not a judge of the same family.
- **Part A: eight quiet plants, three runs a cell at temperature 0.7, 81 calls [M2].** Caught
  (a verdict other than `agree` and a plant keyword): anthropic/claude-sonnet-5.5, the author's
  family, 24 of 24; moonshotai/kimi-k3.1-pro 18 of 24; google/gemini-4-argon 12 of 24. Gemini
  named the plant in 23 of 24 replies but kept `agree` in 11 of them. Kimi missed the
  threshold raised to "all twelve" in 3 of 3 runs. On the control the author's family returned
  `partial` once in three runs, the others never.
- **Part B: each family wrote the same dossier, author withheld, 27 judgements [M2].** The
  author's family judging its own family's dossier: 0 of 3 `agree`, mean 7.0 gaps, against 3 of 3
  on each of the other two (6 of 6) and 6.5 gaps. Kimi on Kimi's text: 3 of 3 `agree`, 0.67 gaps, against 0.833 and
  2.5 on the others, which meets the preference rule (an own-text `agree` rate higher by 1/3
  or more, or a mean gap count lower by 1 or more; `experiment/run.py`). Gemini: 3 of 3 and 0 gaps on its own
  against 0.833 and 0.83, under both margins, so it does not meet the rule. The anthropic dossier drew the fewest `agree` from every judge
  (Kimi 2 of 3, Gemini 2 of 3), so its harsher verdicts may be about that text, not its family.
- **Parse failures: 0 in 125 validator calls** (B-175's 15, this run's 108, the first two).
  One Kimi reply stopped with `finish_reason: error` mid-JSON: a provider error, counted apart.

## Options

1. Keep the refusal: a validator of the author's family is never called or recorded.
2. Record it with a warning, and keep the tier's minimum of validators of other families.
3. Drop the family condition altogether: any validator counts toward the minimum.

## Recommendation

Option 2. The decision rule fixed before the run says the refusal becomes a warning when the
author's family neither misses more plants nor prefers its own text [M2]; it caught the most
plants (24 of 24 against 18 and 12) and judged its own family's text the hardest [M2]. The
tier's minimum still counts only other families, because the one judge that met the
preference rule was of another family (Kimi on Kimi) [M2], panels of disjoint families carry
less intra-model bias [C1], and the bias the literature finds varies by model [C2][C4]: a
family is no guarantee either way, and diversity is the cheap hedge. A same-family row is
recorded with its family, so a reader sees it.

Read beside it: a validator's `agree` is not clean while its gaps name a defect. Gemini kept
`agree` over a named plant 11 times [M2]; the decider answers every gap, whatever the verdict.

## What would refute it

1. The next five dossiers with a same-family validator recorded: if it returns `agree` where
   a validator of another family returns `disagree` with a defect the decider confirms, and the same-family reply names that
   defect nowhere (neither in evidence nor in gaps), two times or more, the refusal comes back.
2. A rerun of Part A with plants written by another family: if the author's family then
   catches 3 or more fewer of 24 than each other family, the refusal comes back.

## Rejected

- Option 1: it refuses the validator that caught the most plants [M2], on a preference effect
  whose size the literature leaves uncertain [B5][C4].
- Option 3: one judge of another family preferred its own text [M2] and disjoint panels carry
  less intra-model bias [C1]; counting the author's family toward the minimum gives up the
  hedge for nothing measured.
- Reading Part B as anthropic's leniency or harshness by family: every judge agreed least with
  the anthropic dossier [M2], so text quality and family are confounded at n = 3.

## Validation

| validator | family | verdict | note |
|---|---|---|---|
| moonshotai/kimi-k3.1-pro | moonshotai | agree | M2 supports the recommendation under the rule committed before the run: the author's family caught 24/24 plants versus 18/24 and 12/24 for the other families, and its own-family judgements were harshe; validation/moonshotai-kimi-k3-1-pro.json |
| google/gemini-4-argon | google | agree | The recommendation for Option 2 follows directly from the pre-registered decision rule and empirical findings in [M2], where the author's family (anthropic) caught 24/24 planted defects (compared to 1; validation/google-gemini-4-argon.json |

## Changes after validation

Both validators read the version before these changes. Taken from moonshotai, by the decider:

- Part B's comparison says 3 of 3 on each other dossier (6 of 6), not an ambiguous 3 of 3.
- The preference rule is quoted where Kimi meets it and Gemini does not, with both margins.
- Refutation 1 counts a miss only when the same-family reply names the defect nowhere: an
  `agree` that names it in its gaps is not a miss, as the Recommendation itself says.
- Not changed: n = 3 per cell and the confound of text and family are already stated as limits
  in Findings and Rejected; the decision is the narrow one the rule fixed in advance.
