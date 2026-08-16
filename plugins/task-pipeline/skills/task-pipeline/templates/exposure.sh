#!/usr/bin/env bash
# exposure.sh — how much unverified work has piled up in <project>, and what to look at.
#
# Seeded by task-pipeline (references/exposure.md). IT IS YOURS NOW.
#
# SCOPE: reads the verification ledger and the git tag list. It does NOT know whether a
#   confirmation was any good, whether a `pass` in the Auto column was watched failing,
#   or anything about code. Read this header before quoting a number from here.
#
# IT IS A MEASUREMENT, NOT A GATE, AND THAT IS LOAD-BEARING. It exits 0 whatever the
#   number is. A threshold here would be a target on `never`, and the ledger's own
#   doctrine says that column may never have one — the moment "unverified must be under
#   ten" exists, the cheapest way to satisfy it is to write a date nobody earned.
#   Exit 1 is reserved for "the ledger is here and I could not read it".
#
# NO PERCENTAGE, EVER. The request that produced this asked for "the probability of an
#   error". That is not computable from these inputs, and a number wearing a
#   measurement's clothes is the failure this whole pipeline exists to remove. What
#   prints is a vector with its components named, and a guard below refuses a `%`.
#
# PORTABLE to macOS bash 3.2: no grep -P, no readarray, no mapfile, no date -d.
#
# DORMANT, NOT SILENT: a project with no ledger yet prints why and exits 0. Dormant is
#   visible so it is not forgotten, and green so a freshly seeded project is not red.

set -u

DOCS_DIR=${DOCS_DIR:-docs}
# The artifact root is RESOLVED, not assumed — renamed `superpowers` → `evidence` on
# 2026-08-13, and every gate that hardcoded the old name went dormant in migrated
# projects, which reads exactly like having nothing to check.
if [ -z "${EVIDENCE_DIR:-}" ]; then
  if [ -d "$DOCS_DIR/evidence" ]; then EVIDENCE_DIR="$DOCS_DIR/evidence"
  elif [ -d "$DOCS_DIR/superpowers" ]; then EVIDENCE_DIR="$DOCS_DIR/superpowers"
  else EVIDENCE_DIR="$DOCS_DIR/evidence"
  fi
fi
LEDGER=${LEDGER:-$EVIDENCE_DIR/verification.md}
BOARD=${BOARD:-$EVIDENCE_DIR/backlog.md}
LIST_MAX=${LIST_MAX:-8}

if [ ! -f "$LEDGER" ]; then
  echo "dormant: exposure — no $LEDGER yet, so nothing has been shipped-and-unconfirmed"
  exit 0
fi

TMP=$(mktemp -d 2>/dev/null || mktemp -d -t exposure)
trap 'rm -rf "$TMP"' EXIT

# ---------- the ledger's rows ----------
# A row is a table line whose first cell is a REQ id. The header and the |---| separator
# are excluded by that shape rather than by counting lines, because a ledger grows
# sections and a line offset stops being true on the first one added.
awk -F'|' '
  NF >= 7 && $2 ~ /^[[:space:]]*[A-Za-z][A-Za-z0-9-]*-?[0-9]*[[:space:]]*$/ &&
  $2 !~ /^[[:space:]]*REQ[[:space:]]*$/ { print }
' "$LEDGER" > "$TMP/rows" 2>/dev/null

# `$(grep -c … || echo 0)` prints TWO zeroes when there are no matches: grep prints its
# 0 and exits 1, so the fallback runs too and the variable becomes "0\n0" — which then
# fails `[ "$ROWS" -eq 0 ]` with *integer expression expected* and takes the rest of the
# script with it. The fallback belongs OUTSIDE the substitution.
ROWS=$(grep -c '' "$TMP/rows" 2>/dev/null) || ROWS=0
if [ "$ROWS" -eq 0 ]; then
  echo "dormant: exposure — $LEDGER has no REQ rows yet"
  exit 0
fi

# Column order is the template's: REQ | What | Run | Shipped in | Auto | Human | Note.
# With awk -F'|' on a leading-pipe line those are $2..$8.

awk -F'|' '{ h=$7; gsub(/^[ \t]+|[ \t]+$/, "", h); if (h == "never") print }' \
  "$TMP/rows" > "$TMP/unverified"
UNVERIFIED=$(grep -c '' "$TMP/unverified" 2>/dev/null) || UNVERIFIED=0

# ---------- since: a date, or the literal `never checked` ----------
# ZERO WOULD BE A LIE IN THE DANGEROUS DIRECTION. "0 days" reads as *checked today*,
# which is the exact opposite of "nobody has ever looked", so the two cases print
# different words rather than different numbers.
awk -F'|' '{ h=$7; gsub(/^[ \t]+|[ \t]+$/, "", h);
             if (h ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/) print h }' \
  "$TMP/rows" | sort > "$TMP/dates"
NEWEST=$(tail -1 "$TMP/dates" 2>/dev/null)

if [ -z "$NEWEST" ]; then
  SINCE="never checked"
else
  # Portable day arithmetic: BSD date and GNU date disagree on every flag that matters,
  # so ask python, which both platforms have and which will not silently return today.
  DAYS=$(python3 - "$NEWEST" <<'PY' 2>/dev/null
import datetime, sys
try:
    d = datetime.date.fromisoformat(sys.argv[1])
except ValueError:
    sys.exit(1)
print((datetime.date.today() - d).days)
PY
)
  if [ -z "${DAYS:-}" ]; then
    echo "FAIL: exposure — $LEDGER has a Human date this script cannot parse: $NEWEST"
    exit 1
  fi
  SINCE="$DAYS days since the last human confirmation"
fi

# ---------- releases: what has gone out on top of it ----------
# Tags, not commits: a release is what an operator feels. Counted since the newest
# confirmation date where there is one, and over the whole tag list where there is not —
# because "no release has ever followed a confirmation" and "no confirmation exists" are
# the same fact from two directions.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ -z "$NEWEST" ]; then
    RELEASES=$(git tag --list 'v*' 2>/dev/null | grep -c '') || RELEASES=0
  else
    RELEASES=$(git log --tags --simplify-by-decoration --since="$NEWEST" \
                 --pretty='%d' 2>/dev/null | grep -o 'tag: v[0-9][^,)]*' | sort -u | grep -c '') || RELEASES=0
  fi
else
  RELEASES="?"
fi

LINE="exposure: $UNVERIFIED unverified · $SINCE · $RELEASES releases carry one"

# ---------- the guard the doctrine names ----------
# Not decoration: a later hand adding "(N%)" here is exactly how the estimate-wearing-a-
# measurement's-clothes returns, and it would return looking helpful.
case "$LINE" in
  *%*) echo "FAIL: exposure — the line contains a percentage: $LINE"
       echo "      references/exposure.md: no percentage, ever. A single score invites a"
       echo "      threshold, and a threshold here is a target on \`never\`."
       exit 1 ;;
esac

echo "$LINE"

# ---------- the check-list: a number without it says there is a problem, not where ----------
if [ "$UNVERIFIED" -eq 0 ]; then
  echo "         every shipped row carries a human confirmation"
  exit 0
fi

# Oldest first by `Shipped in`, which is the only ordering this repository can defend.
# Version sort, so v1.9.0 precedes v1.10.0 — a lexical sort puts the newer one first and
# hands the operator the wrong end of the list.
awk -F'|' '{ req=$2; ship=$5; what=$3;
             gsub(/^[ \t]+|[ \t]+$/, "", req);
             gsub(/^[ \t]+|[ \t]+$/, "", ship);
             gsub(/^[ \t]+|[ \t]+$/, "", what);
             # Truncated on a WORD boundary, never mid-character: awk counts bytes
             # here, so `substr(what, 1, 56)` cut a Cyrillic letter in half and printed
             # a replacement glyph. Appending whole words cannot land inside one.
             short = ""; n = split(what, w, " ");
             for (i = 1; i <= n; i++) {
               if (length(short) + length(w[i]) + 1 > 56) break;
               short = (short == "" ? w[i] : short " " w[i]);
             }
             if (short == "") short = substr(what, 1, 20);
             printf "%s\t%s\t%s\n", ship, req, short }' \
  "$TMP/unverified" | LC_ALL=C sort -t"$(printf '\t')" -k1,1V > "$TMP/sorted"
# LC_ALL=C, and not for speed: the `What` column carries em-dashes and Cyrillic, and BSD
# sort exits with `Illegal byte sequence` on them under a UTF-8 locale — printing the
# error to stderr, producing an EMPTY list, and leaving the exposure line above it
# looking perfectly fine. A check-list that silently becomes empty is worse than no
# check-list, because the number above it still says there is work.
# The delimiter is a literal tab: the first draft said `-t.` and version-sorted on
# nothing.

echo "         oldest first, by the release that shipped it:"
head -"$LIST_MAX" "$TMP/sorted" | while IFS="$(printf '\t')" read -r ship req what; do
  # Blast radius from the board where it carries a row, reusing its stated input rather
  # than inventing a weight here. Absent is printed as absent, never as a default.
  blast=""
  if [ -f "$BOARD" ]; then
    blast=$(grep -m1 "| $req |" "$BOARD" 2>/dev/null | awk -F'|' '{ b=$5; gsub(/^[ \t]+|[ \t]+$/, "", b); print b }')
  fi
  if [ -n "$blast" ]; then
    printf '           %-10s %-12s %s  [blast %s]\n' "$ship" "$req" "$what" "$blast"
  else
    printf '           %-10s %-12s %s\n' "$ship" "$req" "$what"
  fi
done

REST=$((UNVERIFIED - LIST_MAX))
if [ "$REST" -gt 0 ]; then
  echo "           … and $REST more — the full list is \`/task-pipeline checkup\`"
fi
exit 0
