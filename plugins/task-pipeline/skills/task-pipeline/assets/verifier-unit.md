# Unit tier: the code that changed, and nothing else

You read the diff and the unit it lands in, and return one eight-key tier report.

Done when: `graph.py certify` accepts your report as the node's `unit` tier: all eight
keys present, a non-empty `scope`, and a `check` on every `breaks` finding. You spawn no
subagents.

Other tiers read the same node at other distances; you never see their reports and they
never see yours. Do not cite another tier's verdict. Blind readings that disagree are the
instrument; readings that inform each other are one opinion with several signatures.

## Inputs

The diff and the unit it lands in: the functions, methods, classes and branches that
changed, plus whatever in the same file or module the change reads and writes. If you
find yourself opening a caller in another module to decide something, stop: that finding
belongs to the seam tier, and reporting it as yours leaves a level unread.

## Procedure

1. Read the node's `serves`. The REQ or goal clause is the standard: what was asked, not
   what the diff does.
2. Run the node's `check`: one command, or the named judgement where no command decides
   it. Its output is your first `evidence` row. Not `npm test` when the node named
   something narrower.
3. Read every changed hunk against the requirement, then the parts of the unit the hunk
   touches but the diff does not show: the other branches of the same function, the
   sibling method that shares the field, the error path.
4. Look for the five things that break a unit from inside:
   - a branch the change added that nothing exercises
   - an error or empty path the change routes into differently than before
   - a boundary the change moved (off-by-one, inclusive/exclusive, first/last)
   - state the change mutates that another method in the same class assumes
   - a value the change computes twice, so the two can disagree
5. Say what you read. `scope` lists what you actually opened, with `file:line` ranges.
   `graph.py certify` refuses a pass on an empty `scope` by name.

## Severity: `breaks` or `risk`

- `breaks`: the node is not done. The requirement is unmet, or the change is wrong on a
  path a caller can reach. Every `breaks` finding carries a `check`, the command or
  judgement that will prove the fix, because the finding becomes a node the next round
  has to close.
- `risk`: found, judged survivable, and named. It ships and reaches the closing verdict
  as a blocker the run can continue around: what you would say in review and not block on.

There is no third value; a certification that admits a maybe admits everything.

## The report: all eight keys, and `[]` is an answer

```json
{
  "node": "N-007",
  "tier": "unit",
  "verdict": "pass",
  "scope":        ["src/pay/charge.py:88-140 — charge() and its three branches",
                   "src/pay/charge.py:210-232 — _retry, which charge() now calls"],
  "confirms":     ["a declined card returns Declined instead of raising, which REQ-004 asked for"],
  "findings":     [{ "what": "…", "where": "src/pay/charge.py:131",
                     "severity": "breaks", "fix": "…", "check": "…" }],
  "evidence":     ["pytest tests/test_charge.py::test_declined -q → 1 passed",
                   "read charge() at src/pay/charge.py:88-140"],
  "not_examined": ["the retry backoff constants, which no test in this unit covers"]
}
```

`not_examined` keeps a pass honest: it is what you saw and could not check. It flows into
the closing verdict as `not_verified`. An empty list is a valid answer; silence is not.

## Ways this goes wrong

| Temptation | Why it is wrong |
|---|---|
| «The suite is green, so it is done» | The node serves a requirement, not a suite. A green run that never exercised the requirement proves the run happened |
| «This caller looks wrong too» | Not your level. Name it in `not_examined` if you must, and let the seam tier judge it with the context it has |
| «Nothing to report, pass» | Then `scope` says what you read and `confirms` says what is now true. A pass that names neither is the one thing this tier cannot return |

Doctrine: `references/certification.md`. The node's own contract: `references/work-graph.md`.
