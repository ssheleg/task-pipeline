#!/usr/bin/env bash
# TP-OUT-007's command check: `lessons.py query` over this fixture index must
# fire the webhook lesson (L-70cf4d4825df) on the task's nouns and leave the
# unrelated cache lesson (L-8487303c010c) out. The index is queried from a
# temporary copy, because the script takes a lock file beside the index and a
# check must not write into the tree it reads.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
scripts="${TASK_PIPELINE_SCRIPTS:-$here/../../../plugins/task-pipeline/skills/task-pipeline/scripts}"
if [ ! -f "$scripts/lessons.py" ]; then
  echo "expect-match: lessons.py not found under $scripts (set TASK_PIPELINE_SCRIPTS)" >&2
  exit 2
fi
tmp="$(mktemp -d)"
cp "$here/index.jsonl" "$tmp/index.jsonl"
out="$(python3 "$scripts/lessons.py" query webhook retry handler --index "$tmp/index.jsonl")"
rc=$?
rm -f "$tmp/index.jsonl" "$tmp/.lock"
rmdir "$tmp"
if [ "$rc" -ne 0 ]; then
  echo "expect-match: lessons.py query exited $rc" >&2
  exit 1
fi
case "$out" in
  *"[lesson L-8487303c010c]"*) echo "expect-match: the unrelated lesson fired" >&2; exit 1 ;;
esac
case "$out" in
  *"[lesson L-70cf4d4825df]"*) exit 0 ;;
  *) echo "expect-match: the webhook lesson did not fire: $out" >&2; exit 1 ;;
esac
