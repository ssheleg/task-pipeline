# Questions — <topic> (YYYY-MM-DD)

The single question queue of an iteration (`references/iteration.md` → *Question rounds —
asked in batches, never blocking*; `references/waves.md` → *The questions*). Every question
is first tried against the sources. One the sources answer is recorded under **Closed**, with
its citation, and never asked. The rest fall into three groups:
- **Operator** — ordered so prerequisite decisions come first;
- **Peers** — grouped by the repository or session that owns the answer;
- **Assumed** — taken on the recommendation because the answer is internal and reversible;
  the nodes resting on each are named, so a different answer re-plans exactly those.

An outward or irreversible act is never assumed. A round is called on the first of three
triggers: the whole frontier is blocked, five questions are open, a wave boundary.

**Counts:** <N closed from sources · N operator · N peers · N assumed>.

## Closed from the sources (not asked)

| # | Question (raised by) | Answer | Citation |
|---|---|---|---|
| C1 | <question> (<dossier or node>) | <answer> | <decision record, ADR, code at file:line, a peer's message> |

## Operator

| # | Blocks | Question | Recommended | Consequence of each answer | Reversible? |
|---|---|---|---|---|---|
| O1 | <node ids> | <question, answerable without context> | **<answer>** | (a) <…> (b) <…> | <yes / no> |

## Peers

| # | Blocks | Peer (repository / session) | Question | Recommended |
|---|---|---|---|---|
| P1 | <node ids> | <owner> | <question> | <answer> |

## Assumed

| # | Assumption | Taken from | Nodes resting on it |
|---|---|---|---|
| A1 | <the recommendation, as taken> | <O1 / P1> | <node ids> |

## Answers received

| # | From, when | Answer | Applied to |
|---|---|---|---|
| <O1> | <who, date> | <answer as given> | <nodes re-planned, or none> |
