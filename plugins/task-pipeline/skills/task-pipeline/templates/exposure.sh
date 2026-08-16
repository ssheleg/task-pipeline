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

# ---------- the ledger's rows, resolved BY HEADER ----------
# The first draft keyed on position — `NF >= 7`, status in field 7 — and on a ledger with
# four columns it did not report a shape mismatch. It found FOUR rows out of 298, because
# those four happened to contain a `|` inside inline code and so crossed the field count by
# accident, then printed **"0 unverified · every shipped row carries a human confirmation"**.
# The most reassuring sentence available, derived from punctuation. In a tool whose whole
# purpose is to stop silent greens.
#
# So the status column is found by NAME, per section, and a ledger with no such column is
# DORMANT rather than clean. Three shapes exist in this family already — `Human`, `Status`,
# `Watched` — and a fourth will arrive without asking.
awk -F'|' '
  function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
  function lower(s) { return tolower(s) }
  # A header is a row whose first cell names the id column. Everything after it, until the
  # next header, is read with THAT header shape.
  {
    if (NF < 3) next
    c1 = lower(trim($2))
    if (c1 == "req" || c1 == "id" || c1 == "#") {
      nf = NF; scol = 0; sname = ""
      for (i = 2; i < NF; i++) {
        n = lower(trim($i))
        # `human` is the specific one and wins outright; the others are accepted so a
        # differently-shaped ledger is read rather than declared unreadable.
        # ORDER MATTERS, and getting it wrong reads the gate instead of the person.
        # `sheleg-design`'"'"'s ledger carries BOTH `Last verified` (a date and what was
        # watched) and `Status` (which holds `**green**`); preferring `status` reported
        # 174 confirmed rows from the column that says the suite passed.
        if (n == "human") { scol = i; sname = n; break }
        if (n == "last verified" && sname != "human") { scol = i; sname = n }
        if (scol == 0 && (n == "status" || n == "state")) { scol = i; sname = n }
        # `Verified by`, `Confirmed` and `How it is checked` name the EVIDENCE, not the
        # state — five members hold shell commands there. A column of commands read as a
        # column of statuses is how `python3 test/validate.py` became an unreadable status.
      }
      next
    }
    if (nf == 0) next                      # rows before any header
    if (trim($2) ~ /^[-: ]+$/) next        # the |---| separator
    if (NF != nf) next                     # a row of another shape
    if (scol == 0) { headerless++; next }  # counted, so the caller can say so
    print trim($2) "\t" trim($(scol)) "\t" trim($3) "\t" (nf > 5 ? trim($5) : "")
  }
  END { print "##HEADERLESS " headerless+0 > "/dev/stderr"
        print "##COLUMN " (sname == "" ? "-" : sname) > "/dev/stderr" }
' "$LEDGER" > "$TMP/rows" 2>"$TMP/meta"

ROWS=$(grep -c '' "$TMP/rows" 2>/dev/null) || ROWS=0
HEADERLESS=$(sed -n 's/^##HEADERLESS //p' "$TMP/meta" 2>/dev/null)
HEADERLESS=${HEADERLESS:-0}
SCOL=$(sed -n 's/^##COLUMN //p' "$TMP/meta" 2>/dev/null)
SCOL=${SCOL:--}

if [ "$ROWS" -eq 0 ]; then
  if [ "$HEADERLESS" -gt 0 ]; then
    # THE CASE THAT WAS SILENTLY GREEN. Rows exist and none can be read, which is the one
    # answer that must never be spelled "0 unverified".
      echo "dormant: exposure — $LEDGER has $HEADERLESS row(s) but no column named Human,"
    echo "         Last verified, Status or State. Columns like Verified by or How it is"
    echo "         checked name the EVIDENCE, not the state, and are deliberately not read."
    echo "         Nothing here can say whether anybody looked, so this reports no number."
    exit 0
  fi
  echo "dormant: exposure — $LEDGER has no REQ rows yet"
  exit 0
fi
if [ "$HEADERLESS" -gt 0 ]; then
  echo "note:    $HEADERLESS row(s) sit under a header with no status column and are not counted"
fi

# Unconfirmed is a small closed vocabulary, and the empty cell is in it: a blank status is
# the commonest way a row means "nobody has said", and reading it as confirmed inverts the
# file's purpose.
# NORMALISED first: these ledgers write `**never**`, not `never`. Bold hid three real
# unverified rows in one member and seven in another, and both reported zero.
awk -F'\t' '{ s=tolower($2); gsub(/[*`]/, "", s); gsub(/^[ \t]+|[ \t]+$/, "", s);
              if (s=="never" || s=="" || s=="-" || s=="no" || s=="unverified" ||
                  s=="pending" || s=="none") print }' \
  "$TMP/rows" > "$TMP/unverified"
UNVERIFIED=$(grep -c '' "$TMP/unverified" 2>/dev/null) || UNVERIFIED=0

# A THIRD BUCKET, because two are not enough. A status that is neither a known
# unconfirmed word nor a date is UNREADABLE — `last tuesday`, `soon`, `ask Ben`. Counting
# it as confirmed is how a shrug becomes a clean bill, which the fixture for this line
# caught the moment it was written.
awk -F'\t' '{ s=tolower($2); gsub(/[*`]/, "", s); gsub(/^[ \t]+|[ \t]+$/, "", s);
               if (s=="never" || s=="" || s=="-" || s=="no" || s=="unverified" ||
                   s=="pending" || s=="none") next;
               if ($2 ~ /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/) next;
               if (s=="pass" || s=="yes" || s=="verified" || s=="ok" || s=="observed" ||
                   s=="confirmed" || s=="green") next;
               print }' "$TMP/rows" > "$TMP/unreadable"
UNREADABLE=$(grep -c '' "$TMP/unreadable" 2>/dev/null) || UNREADABLE=0

# ---------- since: a date, or the literal `never checked` ----------
# ZERO WOULD BE A LIE IN THE DANGEROUS DIRECTION. "0 days" reads as *checked today*,
# which is the exact opposite of "nobody has ever looked", so the two cases print
# different words rather than different numbers.
awk -F'\t' '{ if ($2 ~ /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/) {
                   match($2, /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/);
                   print substr($2, RSTART, RLENGTH) } }' \
  "$TMP/rows" | sort > "$TMP/dates"
NEWEST=$(tail -1 "$TMP/dates" 2>/dev/null)

if [ -z "$NEWEST" ]; then
  # THREE FACTS, NOT TWO. "nobody has ever looked", "this shape records no dates" and
  # "somebody wrote something nobody can read" are different, and the first draft printed
  # the middle one for the last — a clean bill two lines under a shrug.
  if [ "$UNREADABLE" -gt 0 ]; then
    SINCE="never checked ($UNREADABLE status(es) this script cannot read)"
  elif [ "$UNVERIFIED" -eq 0 ]; then
    SINCE="no confirmation dates recorded"
  else
    SINCE="never checked"
  fi
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
    echo "FAIL: exposure — $LEDGER has a confirmation date this script cannot parse: $NEWEST"
    exit 1
  fi
  # The same discipline as the clean bill below: only a `Human` column licenses the word
  # "human". Any other column records that something looked, not that somebody did.
  if [ "$SCOL" = "human" ]; then
    SINCE="$DAYS days since the last human confirmation"
  else
    SINCE="$DAYS days since the last \`$SCOL\` entry"
  fi
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
# A SHRUG IS NOT A CLEAN BILL. A status that is neither a date nor a known word means
# somebody wrote something and nobody can act on it; printing "every shipped row is
# confirmed" over that is the failure this whole file exists to prevent.
if [ "$UNREADABLE" -gt 0 ]; then
  echo "         $UNREADABLE row(s) carry a status that is neither a date nor a known word,"
  echo "         so no clean bill is printed over them:"
  cut -f1,2 "$TMP/unreadable" | head -"$LIST_MAX" | sed 's/^/           /'
  if [ "$UNVERIFIED" -eq 0 ]; then exit 0; fi
fi

if [ "$UNVERIFIED" -eq 0 ]; then
  # NAME THE COLUMN. `Human` means a person; `Status`, `State` and `Watched` do not
  # distinguish a person from a command — the umbrella's own ledger says `verified` means
  # "a person **or a command** looked", so claiming a human confirmation from that column
  # is a stronger sentence than the data supports.
  if [ "$SCOL" = "human" ]; then
    echo "         every shipped row carries a human confirmation"
  else
    echo "         every shipped row is confirmed in its \`$SCOL\` column — which does not"
    echo "         separate a person from a command; only a \`Human\` column does that"
  fi
  exit 0
fi

# Oldest first by `Shipped in`, which is the only ordering this repository can defend.
# Version sort, so v1.9.0 precedes v1.10.0 — a lexical sort puts the newer one first and
# hands the operator the wrong end of the list.
awk -F'\t' '{ req=$1; what=$3; ship=$4;
             if (ship == "") ship = "—";
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
    blast=$(awk -F'|' -v req="$req" '
      function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
      # BY HEADER, not by index — the same lesson as the status column, and it was left
      # two lines away for a whole release. `$5` is `Blast` in an eight-column board and
      # `Size` in the ten-column one this repository SEEDS, so a host project`s check-list
      # printed `[blast L]`: the size of the work, labelled as who it hurts.
      tolower(trim($2)) == "id" { for (i = 2; i < NF; i++) if (tolower(trim($i)) == "blast") bcol = i; next }
      bcol && trim($2) == req { print trim($(bcol)); exit }
    ' "$BOARD" 2>/dev/null)
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
