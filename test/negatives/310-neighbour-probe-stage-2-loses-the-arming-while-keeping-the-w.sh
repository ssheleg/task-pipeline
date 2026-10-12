#!/usr/bin/env bash
# name: Negative self-test (neighbour probe — stage 2 loses the arming while keeping the word)
set -eu
rm -rf /tmp/nb03-copy && cp -R . /tmp/nb03-copy
python3 - <<'EOF'
p = "/tmp/nb03-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
clause = " \u2014 **and the loop's arming state is printed**:\n  armed with its queue and pacing, or not armed with the reason"
assert clause in t, "PLANT DID NOT LAND: nb03 gate clause"
t = t.replace(clause, "", 1)
# Plant the needle the predicate matches TODAY, next door. The first version
# planted the needles of two RETIRED predicates, which proved the old guards
# were neighbour-answerable and said nothing about this one — the doctrine's
# own step 2 failing on its first use.
needle = "A note for readers: the loop's arming state is printed by the harness, not by this stage."
t = t.replace("\n## 3 \u2014 Spec", "\n" + needle + "\n\n## 3 \u2014 Spec", 1)
assert needle in t, "PLANT DID NOT LAND: nb03 neighbour"
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/nb03-copy/test/validate.py 2>&1 | grep -q "the GATE does not require the loop's arming state"; then
  echo "OK: validator FAILs — a trailing note is not the gate's obligation"
else
  echo "ERROR: the gate lost its clause and a note after the section answered for it"
  exit 1
fi
