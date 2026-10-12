#!/usr/bin/env bash
# name: Negative self-test (a seeded template may not carry a relative link)
set -eu
rm -rf /tmp/tpl-copy && cp -R . /tmp/tpl-copy
python3 - <<'EOF'
p = "/tmp/tpl-copy/plugins/task-pipeline/skills/task-pipeline/templates/brief.md"
t = open(p, encoding="utf-8").read()
assert "# Task brief" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(
    t.replace("# Task brief",
              "See [`audit.md`](../references/audit.md).\n\n# Task brief", 1))
EOF
if python3 /tmp/tpl-copy/test/validate.py; then
  echo "ERROR: validator passed a template carrying a relative link — it resolves from templates/ and from nowhere the file is ever actually read"
  exit 1
else
  echo "OK: a seeded template is self-contained"
fi
