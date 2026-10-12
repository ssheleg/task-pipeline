#!/usr/bin/env bash
# name: Property check (a portable example command in shipped doctrine is not this repo's script)
set -eu
rm -rf /tmp/gloss3-copy && cp -R . /tmp/gloss3-copy
python3 - <<'EOF'
# `references/planning.md` names `npm run lint:paths` as an example of a HOST
# project's command. Refusing that would teach the doctrine to stop naming
# commands at all — measured on the check's first run, which reported four.
p = "/tmp/gloss3-copy/plugins/task-pipeline/skills/task-pipeline/references/planning.md"
t = open(p, encoding="utf-8").read()
assert "npm run lint:paths" in t, "PLANT DID NOT LAND: the portable example is gone"
EOF
if python3 /tmp/gloss3-copy/test/validate.py >/dev/null; then
  echo "OK: shipped doctrine may name a host project's command"
else
  echo "ERROR: the existence check reached into portable doctrine"
  exit 1
fi
