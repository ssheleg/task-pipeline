# Exact-main release gate after PR112 squash

The chained full release gate on accepted main 4d750573ce53ea4c7ffa2bde192ee35b59acefa7
failed before any tag. [Receipt](failed.json) and [complete compressed log](failed.log.gz)
retain the failure: all 438 planted guards and 15 properties passed, then documentation
validation rejected six historical bare source references that are no longer ancestors
after the normal squash. Existing branch-local document checks did not prove a future
squash commit's ancestry. No test or guard is weakened.

The correction converts only those six citations to immutable commit-addressed GitHub
links. Historical results keep their actual source; no result is rewritten as a pass.
Runtime, tests, workflows, versions and npm payload are unchanged. Validate documentation,
review this bounded diff, integrate through genuine required checks, then repeat the
full local suite on the new accepted main before the annotated 1.94.0 tag. An equal
payload or prior hosted pass does not substitute for that exact-main gate.

Independent recovery_audit review mechanically verified the six substitutions,
resolved all six exact GitHub sources, and matched the retained full log hash.
Focused `npm run test:docs` passed after correction. The full accepted-main gate
remains required; only link readability changed after that review.
