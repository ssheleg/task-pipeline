#!/usr/bin/env bash
# name: Negative self-test (a lesson redaction replacing a relative name)
set -eu
rm -rf /tmp/r13-redact-abs-copy && cp -R . /tmp/r13-redact-abs-copy
python3 - <<'EOF'
# Round 13, N2: only absolute paths with a real name are redacted. Redact any key.
p = "/tmp/r13-redact-abs-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        if not os.path.isabs(path) or path == "/" or name in ("", ".", ".."):\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        if path == "/":\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-redact-abs-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-redact-abs-copy
  echo "ERROR: lessons_test passed a root given as . rewriting messages"
  exit 1
else
  rm -rf /tmp/r13-redact-abs-copy
  echo "OK: lessons_test correctly FAILs — only absolute paths are redacted"
fi
