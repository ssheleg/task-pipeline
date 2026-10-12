#!/usr/bin/env bash
# name: Negative self-test (the seeded gate must stay portable)
set -eu
rm -rf /tmp/portable-copy-2 && cp -R . /tmp/portable-copy-2
python3 - <<'EOF'
p = "/tmp/portable-copy-2/plugins/task-pipeline/skills/task-pipeline/templates/docgate.sh"
t = open(p, encoding="utf-8").read()
# Build the construct at runtime — spelling it here would trip the
# workflow's own portability guard on this very file.
bad = "s" + "ed -" + "i 's/a/b/' /dev/null"
# plant in CODE, not in a comment: the guard reads code only
assert "set -u" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("set -u", "set -u\n" + bad, 1))
EOF
if python3 /tmp/portable-copy-2/test/validate.py; then
  echo "ERROR: validator passed a gate using an in-place stream edit — on BSD it silently edits nothing and reads as a guard that failed to fire"
  exit 1
else
  echo "OK: validator rejects non-portable constructs in the seeded gate"
fi
