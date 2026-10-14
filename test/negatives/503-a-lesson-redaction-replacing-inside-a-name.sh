#!/usr/bin/env bash
# name: Negative self-test (a lesson redaction replacing inside a name)
set -eu
rm -rf /tmp/r13-redact-whole-copy && cp -R . /tmp/r13-redact-whole-copy
python3 - <<'EOF'
# Round 13, N2: redaction replaces whole path components only. Replace every occurrence.
p = "/tmp/r13-redact-whole-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        text = re.sub(r"(?<![\\w.~/-])" + re.escape(path) + r"(?![\\w.~-])", lambda _m: name, text)\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        text = text.replace(path, name)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-redact-whole-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-redact-whole-copy
  echo "ERROR: lessons_test passed a path replaced inside a longer name"
  exit 1
else
  rm -rf /tmp/r13-redact-whole-copy
  echo "OK: lessons_test correctly FAILs — only whole path components are replaced"
fi
