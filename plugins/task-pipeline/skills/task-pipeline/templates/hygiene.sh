#!/usr/bin/env bash
# hygiene.sh — the artifact hygiene gate for <project>.
#
# Seeded by task-pipeline (references/gates.md). IT IS YOURS NOW: extend it here,
# section by section. Each section is independent and removable.
#
# WHAT IT IS FOR: the defect class an AGENT produces and no other check looks for —
#   a half-resolved merge, a stub that outlived its task, a generation cut off in the
#   middle, a file "shortened" while being rewritten, a batch of edits where one
#   applied twice, a section opened and abandoned.
#
# SCOPE: walks tracked files. In diff mode it walks only what this run changed; in
#   tree mode it walks everything, behind per-check floors.
#   It does NOT check: prose meaning, code correctness, style, formatting, spelling,
#   another repository, or generated output. It is not a linter — your language has
#   one, and this is not it.
#   KNOWN FALSE-POSITIVE SURFACES, one per check, because a gate that hides them
#   gets disabled the first time it is wrong:
#     1 conflict markers   — a document explaining merge conflicts
#     2 placeholders       — only a LINE-LEADING marker counts. The word TODO in the
#                            middle of a sentence is prose, not a stub. This
#                            distinction is the whole check: measured on the project
#                            that ships it, 28 of 33 hits were ordinary English.
#     3 unterminated fence — a fence deliberately shown unclosed as an example
#     4 truncation stubs   — a document quoting one as an example of what not to do
#     5 duplicated block   — a legitimately repeated stanza 3+ lines long
#     6 empty section      — a heading used as a one-line record. If you have those,
#                            they want to be list items: a heading promises a section.
#   Read this header before quoting a green from here as evidence.
#
# IT NEVER EDITS. It reports file:line and exits non-zero. None of the six is safely
#   machine-fixable: deleting a "duplicated block" sometimes deletes a legitimate
#   repetition, and deleting a TODO erases a reminder instead of discharging it.
#   Fixing is the agent's job, and task-pipeline's references/build.md makes it one.
#
# EXIT CODE IS THE OUTPUT: non-zero on any failure. Nothing may run after the
#   VERDICT block at the bottom — a gate that appended a check after its verdict
#   printed FAIL and returned 0, and CI was green over it for an unknown period.
#
# PORTABLE to macOS bash 3.2: no grep -P, no sed -i, no readarray, no mapfile.
#
# PROGRESSIVE ARMING: a check whose input does not exist prints
#   "dormant: … — no <input>" and does NOT fail. Dormant is visible so it is not
#   forgotten, and green so a freshly seeded project does not start red.
#
# TWO MODES, AND THE DIFFERENCE IS THE POINT:
#   diff mode (HYGIENE_BASE set) — ZERO tolerance. This run wrote it, this run fixes
#     it. There is no floor, because a floor for work you just did is a licence.
#   tree mode (default)          — per-check RATCHET FLOORS. A count at or below its
#     floor passes; above it fails. A floor may only fall. This is what lets an
#     existing repository adopt the gate without starting red, while forgiving
#     nothing new.

set -u

FAIL=0
HYGIENE_BASE=${HYGIENE_BASE:-}
HYGIENE_EXCLUDE=${HYGIENE_EXCLUDE:-graphify-out/}
HYGIENE_FLOOR_1=${HYGIENE_FLOOR_1:-0}
HYGIENE_FLOOR_2=${HYGIENE_FLOOR_2:-0}
HYGIENE_FLOOR_3=${HYGIENE_FLOOR_3:-0}
HYGIENE_FLOOR_4=${HYGIENE_FLOOR_4:-0}
HYGIENE_FLOOR_5=${HYGIENE_FLOOR_5:-0}
HYGIENE_FLOOR_6=${HYGIENE_FLOOR_6:-0}

TMP=${TMPDIR:-/tmp}/hygiene.$$
mkdir -p "$TMP" || exit 2
trap 'rm -rf "$TMP"' EXIT

err() { echo "  FAIL: $*"; FAIL=1; }
ok() { echo "  ok:   $*"; }
dormant() { echo "  dormant: $*"; }

# ---------- the file list ----------
# git is the source of truth for "authored": generated and ignored files are not
# this gate's business, and scanning them is how a gate becomes noise.
if git rev-parse --git-dir >/dev/null 2>&1; then
  if [ -n "$HYGIENE_BASE" ]; then
    MODE=diff
    { git diff --name-only "$HYGIENE_BASE" 2>/dev/null
      git diff --name-only 2>/dev/null
      git diff --name-only --cached 2>/dev/null
    } | sort -u > "$TMP/all"
  else
    MODE=tree
    git ls-files > "$TMP/all"
  fi
else
  MODE=tree
  find . -type f -not -path './.git/*' | sed 's|^\./||' > "$TMP/all"
fi

: > "$TMP/files"
while read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || continue
  case "$f" in
    $HYGIENE_EXCLUDE*) continue ;;
  esac
  echo "$f" >> "$TMP/files"
done < "$TMP/all"

NFILES=$(wc -l < "$TMP/files" | tr -d ' ')
: > "$TMP/md"
while read -r f; do
  case "$f" in *.md) echo "$f" >> "$TMP/md" ;; esac
done < "$TMP/files"
NMD=$(wc -l < "$TMP/md" | tr -d ' ')

echo "hygiene gate — mode $MODE · $NFILES file(s), $NMD markdown"

# The floor a check is judged against. Diff mode has none: zero tolerance.
floor_for() {
  if [ "$MODE" = diff ]; then echo 0; return; fi
  eval "echo \${HYGIENE_FLOOR_$1}"
}

judge() { # judge <n> <count> <label>
  _f=$(floor_for "$1")
  if [ "$2" -gt "$_f" ]; then
    err "check $1 — $3: $2 finding(s), floor $_f"
    sed 's/^/         /' "$TMP/hits$1"
  else
    ok "check $1 — $3: $2 (floor $_f)"
  fi
}

if [ "$NFILES" -eq 0 ]; then
  dormant "every check — no files in scope"
  C1=0; C2=0; C3=0; C4=0; C5=0; C6=0
else

# ---------- 1. conflict markers ----------
: > "$TMP/hits1"
while read -r f; do
  grep -n -E '^(<<<<<<< |=======$|>>>>>>> )' "$f" 2>/dev/null |
    sed "s|^|$f:|" >> "$TMP/hits1"
done < "$TMP/files"
C1=$(wc -l < "$TMP/hits1" | tr -d ' ')
judge 1 "$C1" "conflict markers"

# ---------- 2. surviving placeholders ----------
# A LINE-LEADING marker, optionally behind a comment introducer. Not the word.
: > "$TMP/hits2"
while read -r f; do
  grep -n -E '^[[:space:]]*([#/*<!-]+[[:space:]]*)*(TODO|TBD|FIXME|XXX)\b' "$f" 2>/dev/null |
    sed "s|^|$f:|" >> "$TMP/hits2"
done < "$TMP/files"
C2=$(wc -l < "$TMP/hits2" | tr -d ' ')
judge 2 "$C2" "surviving placeholders"

# ---------- 3. unterminated code fence ----------
: > "$TMP/hits3"
if [ "$NMD" -eq 0 ]; then
  dormant "check 3 — unterminated fence: no markdown in scope"
  C3=0
else
  while read -r f; do
    # grep -c exits 1 on zero matches, so a `|| echo 0` would append a SECOND zero
    # and make the test below see "0\n0". Swallow the status instead.
    n=$(grep -c '^[[:space:]]*```' "$f" 2>/dev/null) || n=0
    [ -z "$n" ] && n=0
    if [ "$n" -gt 0 ] && [ "$(expr "$n" % 2)" -ne 0 ]; then
      echo "$f:1: odd fence count ($n) — a code block is not closed" >> "$TMP/hits3"
    fi
  done < "$TMP/md"
  C3=$(wc -l < "$TMP/hits3" | tr -d ' ')
  judge 3 "$C3" "unterminated fence"
fi

# ---------- 4. truncation stubs ----------
# LINE-LEADING, exactly like check 2, and for exactly the same reason: the first
# version matched the phrase anywhere and fired three times on the very documents
# that DEFINE these patterns. A stub is a line standing in for content; a phrase in
# the middle of a sentence is prose about stubs.
: > "$TMP/hits4"
while read -r f; do
  grep -n -E '^[[:space:]]*([#/*<!-]+[[:space:]]*)*(\.\.\. existing code|\[TRUNC|rest of (the )?file unchanged|unchanged\.\.\.)' "$f" 2>/dev/null |
    sed "s|^|$f:|" >> "$TMP/hits4"
done < "$TMP/files"
C4=$(wc -l < "$TMP/hits4" | tr -d ' ')
judge 4 "$C4" "truncation stubs"

# ---------- 5. duplicated adjacent block ----------
# The mechanical form of "re-verify every edit in a batch": a retry that duplicated
# instead of replacing leaves two identical blocks back to back. Three lines is the
# floor because two-line repeats occur legitimately (table rows, list pairs).
: > "$TMP/hits5"
while read -r f; do
  awk -v F="$f" '
    NF { blk = blk "\n" $0; n++; next }
    {
      if (n >= 3) { if (blk == prev) print F ":" NR ": duplicated " n "-line block"; prev = blk }
      else prev = ""
      blk = ""; n = 0
    }
    END { if (n >= 3 && blk == prev) print F ":" NR ": duplicated " n "-line block at end of file" }
  ' "$f" >> "$TMP/hits5" 2>/dev/null
done < "$TMP/files"
C5=$(wc -l < "$TMP/hits5" | tr -d ' ')
judge 5 "$C5" "duplicated adjacent block"

# ---------- 6. empty section ----------
# A heading of level N followed by a heading of level <= N with no body between.
# FENCED CONTENT COUNTS AS BODY — the first version of this check skipped fenced
# lines entirely and so reported every section whose body is one code block.
: > "$TMP/hits6"
if [ "$NMD" -eq 0 ]; then
  dormant "check 6 — empty section: no markdown in scope"
  C6=0
else
  while read -r f; do
    awk -v F="$f" '
      /^[[:space:]]*(```|~~~)/ { fence = !fence; prev = 0; next }
      fence { prev = 0; next }
      /^#{1,6} / {
        match($0, /^#+/); lvl = RLENGTH
        if (prev && lvl <= prev) print F ":" NR ": empty section — h" prev " then h" lvl " with no body"
        prev = lvl; next
      }
      NF { prev = 0 }
    ' "$f" >> "$TMP/hits6" 2>/dev/null
  done < "$TMP/md"
  C6=$(wc -l < "$TMP/hits6" | tr -d ' ')
  judge 6 "$C6" "empty section"
fi

fi

# ---------- VERDICT — nothing may run after this block ----------
if [ "$FAIL" -ne 0 ]; then
  echo "FAIL: hygiene gate — mode $MODE · conflict ${C1} · placeholder ${C2} · fence ${C3} · truncation ${C4} · duplicate ${C5} · empty-section ${C6}"
  exit 1
fi
echo "OK: hygiene gate — mode $MODE · $NFILES file(s) · conflict ${C1} · placeholder ${C2} · fence ${C3} · truncation ${C4} · duplicate ${C5} · empty-section ${C6}"
exit 0
