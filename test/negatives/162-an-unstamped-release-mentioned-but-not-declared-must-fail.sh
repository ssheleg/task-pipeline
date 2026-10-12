#!/usr/bin/env bash
# name: Negative self-test (an unstamped release MENTIONED but not declared must fail)
set -eu
rm -rf /tmp/gapmention && cp -R . /tmp/gapmention
# dormant-when: `git tag -l` returns nothing inside the copy, so the trailing
#   set cannot be computed and the release-gap guard itself declines to look.
#   MEASURED 2026-08-31 and stated because the obvious cause is wrong: through
#   `test/negatives.py` this never fires, because the runner reconstructs a real
#   `.git` in its snapshot even from a submodule pointer, and CI checks out with
#   `fetch-depth: 0`, which fetches tags. It fires where the step is run on its
#   own against a checkout whose `.git` is a pointer file, or on a tagless
#   fetch. Cost: in that shape the release-gap check is unprobed and says so,
#   rather than an environment answering for the guard.
set +e
python3 test/plant_gap_mention.py /tmp/gapmention
EOF_RC=$?
if [ "$EOF_RC" = "9" ]; then
  exit 0
elif [ "$EOF_RC" != "0" ]; then
  echo "PLANT FAILED TO RUN (exit $EOF_RC)"; exit 1
fi
if python3 /tmp/gapmention/test/validate.py; then
  echo "ERROR: a release merely MENTIONED in the gap section was accepted as declared"
  exit 1
else
  echo "OK: validator FAILs — a mention is not a declaration, only a bold one is"
fi
