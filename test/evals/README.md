# Evaluations for task-pipeline

These files describe behavior to measure with the pack installed. They are not
unit tests and CI does not pretend that schema validity is model quality.

| File | Holds |
|---|---|
| `triggers.json` | positive requests and close negative cases, split before tuning |
| `scenarios.json` | three end-to-end behaviors scored line by line |
| `RESULTS.md` | dated model runs, or an explicit statement that none exist |

Validate the data and the validator's planted defect:

```bash
python3 test/evals_validate.py
python3 test/evals_validate.py --self-test
```

To measure triggers, ask each query in a fresh session three times and record
whether the intended skill loaded. To measure scenarios, record each expected
line as pass or fail. Always record the model, pack version and other installed
skills; coexistence changes routing.

