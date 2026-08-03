#!/usr/bin/env bash
# check-docs.sh — the documentation gate for <project>.
#
# Seeded by task-pipeline (references/gates.md). IT IS YOURS NOW: extend it here,
# section by section. Each section is independent and removable.
#
# SCOPE: walks the markdown under docs/ (and this repository's own root .md files).
#   It does NOT check: prose meaning, whether a citation is the RIGHT one, code,
#   another repository's documents, or anything inside a fenced code block.
#   Read this header before quoting a green from here as evidence.
#
# EXIT CODE IS THE OUTPUT: non-zero on any failure. Nothing may run after the
#   VERDICT block at the bottom — a gate that appended a check after its verdict
#   printed FAIL and returned 0, and CI was green over it for an unknown period.
#
# PORTABLE to macOS bash 3.2: no grep -P, no sed -i, no readarray, no mapfile.
#
# PROGRESSIVE ARMING: a section whose input does not exist yet prints
#   "dormant: … — no <artefact> yet" and does NOT fail. Dormant is visible so it is
#   not forgotten, and green so a freshly seeded project does not start red.
#
# TWO REGISTER SHAPES, ONE CONTRACT: the project's decision home is either
#   docs/DECISIONS.md (ids DEC-####) or docs/adr/NNNN-slug.md (ids ADR-NNNN). Every
#   section below reads a NORMALISED INDEX built from whichever exists, so neither
#   shape is a second-class citizen. Having both is itself an error: one home per
#   project. Reading only one shape is how a fully populated ADR register sat behind
#   eight green "dormant" lines while a planted violation went uncaught.

set -u

FAIL=0
DOCS_DIR=${DOCS_DIR:-docs}
DEC_FILE=${DEC_FILE:-$DOCS_DIR/DECISIONS.md}
ADR_DIR=${ADR_DIR:-$DOCS_DIR/adr}
OQ_FILE=${OQ_FILE:-$DOCS_DIR/OPEN_QUESTIONS.md}
MAP_FILE=${MAP_FILE:-$DOCS_DIR/DOCMAP.md}
RETRO_GLOB=${RETRO_GLOB:-$DOCS_DIR/superpowers}

# ---------- ratchets: a floor may only fall. Raising one is a decision. ----------
# THE TWO FLOORS ARE DIFFERENT KINDS. Mixing them up is why this is spelled out.
#
# PROP_FLOOR is an ID THRESHOLD, not a count. An entry whose number is >= the floor
#   must have propagated; everything older is a counted backlog that may only shrink.
#   ADOPTING THIS GATE IN AN EXISTING REPOSITORY MEANS SETTING IT TO THE NEXT FREE
#   ID: from today the rule binds, and the history becomes one printed number instead
#   of a thousand failures nobody will fix. Lower it as tranches are cleared.
PROP_FLOOR=${PROP_FLOOR:-0}        # id threshold — entries >= this must propagate
#
# RESIDUE_FLOOR is a COUNT: how many unmarked citations of retired decisions are
#   tolerated. On adoption set it to what the repository measurably has today, then
#   only ever lower it.
RESIDUE_FLOOR=${RESIDUE_FLOOR:-0}  # count — tolerated unmarked citations, today's number

TMP=$(mktemp -d 2>/dev/null || mktemp -d -t docgate)
trap 'rm -rf "$TMP"' EXIT

err()     { echo "ERR:     $*"; FAIL=1; }
ok()      { echo "ok:      $*"; }
skipmsg() { echo "skip:    $*"; }
dormant() { echo "dormant: $*"; }

# Strip what a reader never sees: fenced code blocks AND html comments. Sample
# content is not a claim about this repository. The comment half is not fussiness —
# a status line carrying `<!-- or: Superseded by ADR-0012 -->` made an entry read as
# retired and invented an undefined id, from one aside nobody renders.
# awk, because sed -i is not portable and this must run identically everywhere.
strip_asides() {
  awk '
    /^[ \t]*(```|~~~)/ { infence = !infence; print ""; next }
    infence { print ""; next }
    {
      line = $0
      # A comment carried over from an earlier line.
      if (incomment) {
        if (match(line, /-->/)) { line = substr(line, RSTART + RLENGTH); incomment = 0 }
        else { print ""; next }
      }
      # Comments that open and close on this line.
      while (match(line, /<!--.*-->/)) sub(/<!--.*-->/, "", line)
      # An opener with no closer: KEEP THE PREFIX. Dropping the whole line threw
      # away the "- **Status:** Accepted" that preceded the comment, and the entry
      # then had no status at all — the id vanished from the index and every
      # document citing it was reported as citing something undefined.
      if (match(line, /<!--/)) { line = substr(line, 1, RSTART - 1); incomment = 1 }
      print line
    }
  ' "$1"
}

# Every markdown file in scope, one per line.
find "$DOCS_DIR" -type f -name '*.md' 2>/dev/null | sort > "$TMP/files" || true
find . -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort >> "$TMP/files" || true
FILE_COUNT=$(wc -l < "$TMP/files" | tr -d ' ')

if [ "$FILE_COUNT" = "0" ]; then
  echo "FAIL: documentation gate — no markdown found in $DOCS_DIR/ or the repository root."
  echo "      Seed the doc map and the registers first (task-pipeline stage 0, phase 1b),"
  echo "      or point DOCS_DIR at wherever this project keeps its documentation."
  exit 1
fi

# Fence-stripped copies, addressed by a flattened path.
while IFS= read -r f; do
  [ -f "$f" ] || continue
  flat=$(echo "$f" | tr '/' '_')
  strip_asides "$f" > "$TMP/s_$flat"
done < "$TMP/files"

flat_of() { echo "$TMP/s_$(echo "$1" | tr '/' '_')"; }

# ---------- 0. the decision home — exactly one, and which shape ----------
# entries: ID <TAB> FILE <TAB> STATUS-LINE      edges: SRC <TAB> MARKER <TAB> TARGET
# conseq:  ID <TAB> DOC
: > "$TMP/entries"; : > "$TMP/edges"; : > "$TMP/conseq"
SHAPE="none"; ID_PREFIX=""

have_reg=0; [ -f "$DEC_FILE" ] && have_reg=1
have_adr=0
if [ -d "$ADR_DIR" ]; then
  find "$ADR_DIR" -type f -name '[0-9][0-9][0-9][0-9]-*.md' 2>/dev/null | sort > "$TMP/adrfiles"
  [ -s "$TMP/adrfiles" ] && have_adr=1
fi

if [ "$have_reg" = "1" ] && [ "$have_adr" = "1" ]; then
  err "two decision homes: $DEC_FILE and $ADR_DIR both hold entries — one project, one register (references/documentation.md)"
fi

# Pull the six owed fields out of one entry body on stdin, for id $1 in file $2.
harvest_entry() {  # id file  (body on stdin)
  _id=$1; _file=$2
  while IFS= read -r line; do
    case "$line" in
      *'Status:'*)
        grep -q "^$_id	" "$TMP/entries" 2>/dev/null || \
          printf '%s\t%s\t%s\n' "$_id" "$_file" "$line" >> "$TMP/entries" ;;
      *'Consequences / affects:'*)
        echo "$line" | grep -o '`[^`]*`' | tr -d '`' | while IFS= read -r doc; do
          case "$doc" in *.md) printf '%s\t%s\n' "$_id" "$doc" >> "$TMP/conseq" ;; esac
        done ;;
      *'Supersedes:'*|*'Contradicts:'*|*'Refines:'*)
        _mk=$(echo "$line" | grep -o 'Supersedes\|Contradicts\|Refines' | head -1)
        echo "$line" | grep -o '\(DEC\|ADR\)-[0-9][0-9]*' | while IFS= read -r tgt; do
          [ "$tgt" = "$_id" ] || printf '%s\t%s\t%s\n' "$_id" "$_mk" "$tgt" >> "$TMP/edges"
        done ;;
    esac
  done
}

if [ "$have_reg" = "1" ]; then
  SHAPE="register"; ID_PREFIX="DEC"
  # Split the fence-stripped register into one body per "### DEC-####" heading.
  awk -v out="$TMP" '
    /^### DEC-[0-9]+/ { id=$2; sub(/[^A-Za-z0-9-].*/,"",id); n++; f=out "/e_" n; ids[n]=id }
    n { print > f }
    END { for (i=1;i<=n;i++) print ids[i] > (out "/e_ids") }
  ' "$(flat_of "$DEC_FILE")"
  if [ -f "$TMP/e_ids" ]; then
    _n=0
    while IFS= read -r _id; do
      _n=$((_n + 1))
      harvest_entry "$_id" "$DEC_FILE" < "$TMP/e_$_n"
    done < "$TMP/e_ids"
  fi
elif [ "$have_adr" = "1" ]; then
  SHAPE="adr"; ID_PREFIX="ADR"
  while IFS= read -r af; do
    _num=$(basename "$af" | sed 's/^\([0-9][0-9]*\)-.*/\1/')
    harvest_entry "ADR-$_num" "$af" < "$(flat_of "$af")"
  done < "$TMP/adrfiles"
fi

DECS=$(wc -l < "$TMP/entries" | tr -d ' ')
case "$SHAPE" in
  none) dormant "decision home — neither $DEC_FILE nor $ADR_DIR/NNNN-*.md yet" ;;
  *)    ok "decision home: $SHAPE ($DECS entr$([ "$DECS" = "1" ] && echo y || echo ies), ids $ID_PREFIX-####)" ;;
esac

# ---------- 1. relative links resolve ----------
while IFS= read -r f; do
  [ -f "$f" ] || continue
  dir=$(dirname "$f")
  grep -n -o '](\([^) ]*\))' "$(flat_of "$f")" 2>/dev/null |
  sed 's/](\(.*\))/\1/' |
  while IFS=: read -r ln target; do
    case "$target" in
      http://*|https://*|mailto:*|'#'*|'') continue ;;
    esac
    base=${target%%#*}
    [ -n "$base" ] || continue
    [ -e "$dir/$base" ] || echo "$f:$ln: dangling link -> $target" >> "$TMP/badlinks"
  done
done < "$TMP/files"
if [ -s "$TMP/badlinks" ] 2>/dev/null; then
  err "$(wc -l < "$TMP/badlinks" | tr -d ' ') dangling relative link(s):"
  sed 's/^/         /' "$TMP/badlinks"
else
  ok "relative links resolve ($FILE_COUNT files)"
fi

# ---------- 2. every id referenced is defined ----------
if [ "$SHAPE" = "none" ]; then
  dormant "id integrity — no decision home yet"
  OQS=0
else
  cut -f1 "$TMP/entries" | sort -u > "$TMP/dec_def"
  : > "$TMP/oq_def"
  [ -f "$OQ_FILE" ] && grep -o '^| *OQ-[0-9][0-9]*' "$(flat_of "$OQ_FILE")" | sed 's/^| *//' | sort -u > "$TMP/oq_def"
  OQS=$(wc -l < "$TMP/oq_def" | tr -d ' ')
  cat "$TMP/dec_def" "$TMP/oq_def" | sort -u > "$TMP/defined"

  : > "$TMP/refs"
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    grep -v 'Next free ID' "$(flat_of "$f")" 2>/dev/null |
      grep -o "\($ID_PREFIX\|OQ\)-[0-9][0-9]*" | sed "s|^|$f |" >> "$TMP/refs"
  done < "$TMP/files"

  : > "$TMP/undef"
  sort -u "$TMP/refs" | while read -r f id; do
    grep -qx "$id" "$TMP/defined" || echo "$f: $id referenced, never defined" >> "$TMP/undef"
  done
  if [ -s "$TMP/undef" ] 2>/dev/null; then
    err "undefined id(s):"; sed 's/^/         /' "$TMP/undef"
  else
    ok "every referenced id is defined ($DECS decisions, $OQS open questions)"
  fi
fi

# ---------- 3. the id allocator is sound ----------
# Register shape: a stated "Next free ID" must equal max defined + 1.
# ADR shape: there is no such line — the filename IS the allocator, so the sound
# check is that no two files claim one number.
check_next_free() {
  _file=$1; _prefix=$2; _deffile=$3
  [ -f "$_file" ] || { dormant "next-free-$_prefix — no $_file yet"; return; }
  _claim=$(grep -o "Next free ID:\** *\`\?$_prefix-[0-9][0-9]*" "$_file" | head -1 |
           grep -o '[0-9][0-9]*$')
  if [ -z "${_claim:-}" ]; then
    err "$_file: no parsable 'Next free ID: \`$_prefix-NNNN\`' line"
    return
  fi
  # Strip leading zeros BEFORE any arithmetic: bash reads 0009 as octal, 9 is not
  # an octal digit, the expansion errors, the `if` takes its else branch and the
  # check prints ok. It passed for every id ending 0-7 and was silent for 8 and 9.
  # Found by the probe; the check was wrong, not the probe.
  _claim_raw=$_claim
  _claim=$(echo "$_claim" | sed 's/^0*//'); [ -n "$_claim" ] || _claim=0
  if [ ! -s "$_deffile" ]; then _max=0; else
    _max=$(sed "s/^$_prefix-//" "$_deffile" | sed 's/^0*//' | sort -n | tail -1)
    [ -n "${_max:-}" ] || _max=0
  fi
  _want=$((_max + 1))
  if [ "$_claim" -ne "$_want" ]; then
    err "$_file: 'Next free ID' claims $_prefix-$_claim, highest defined is $_max (expected $_want)"
  else
    ok "next free $_prefix id is correct ($_prefix-$_claim_raw)"
  fi
}
case "$SHAPE" in
  register) check_next_free "$DEC_FILE" DEC "$TMP/dec_def" ;;
  adr)
    # Count from the FILENAMES, not from the entry index. The index keeps one row
    # per id on purpose (an entry has one status line), and that dedupe silently
    # swallowed the very thing this check looks for: a second file claiming a
    # number already taken. The filename is the allocator, so the filename is what
    # gets counted. The check was wrong, not the probe.
    _dupes=$(sed 's|.*/||; s|^\([0-9][0-9]*\)-.*|\1|' "$TMP/adrfiles" | sort | uniq -d | tr '\n' ' ')
    _adr_n=$(wc -l < "$TMP/adrfiles" | tr -d ' ')
    if [ -n "$(echo "$_dupes" | tr -d ' ')" ]; then
      err "duplicate ADR number(s) — two files claim one id: $_dupes"
    else
      ok "ADR numbers are unique ($_adr_n files)"
    fi ;;
  *) dormant "id allocator — no decision home yet" ;;
esac
check_next_free "$OQ_FILE" OQ "$TMP/oq_def"

# ---------- 4. a stated register size equals the computed one ----------
# Compute, never restate: a number written in prose is a number that goes stale.
_size_src=""
[ "$SHAPE" = "register" ] && _size_src=$DEC_FILE
if [ -n "$_size_src" ] && grep -q 'Register size:' "$_size_src" 2>/dev/null; then
  _stated=$(grep -o 'Register size:\** *\**[0-9][0-9]*' "$_size_src" | head -1 | grep -o '[0-9][0-9]*')
  if [ "${_stated:-x}" != "$DECS" ]; then
    err "$_size_src: states 'Register size: $_stated', computed $DECS"
  else
    ok "stated register size matches the computed one ($DECS)"
  fi
else
  dormant "register-size cross-check — no 'Register size:' line stated"
fi

# ---------- 5. consequences propagation (RATCHETED) ----------
# A document named in an entry's "Consequences / affects:" line must cite that
# entry. Writing down where a decision must propagate and then not propagating is
# the exact failure the loop exists to prevent.
PROP_MISSING=0
if [ "$SHAPE" = "none" ]; then
  dormant "propagation — no decision home yet"
else
  : > "$TMP/prop"
  while IFS="$(printf '\t')" read -r id doc; do
    [ -n "${doc:-}" ] || continue
    if [ ! -f "$doc" ]; then echo "$id -> $doc (MISSINGFILE)" >> "$TMP/prop"
    elif grep -q "$id" "$doc"; then :
    else echo "$id -> $doc (NOCITE)" >> "$TMP/prop"; fi
  done < "$TMP/conseq"
  [ -f "$TMP/prop" ] && PROP_MISSING=$(wc -l < "$TMP/prop" | tr -d ' ')
  : > "$TMP/prop_new"
  if [ "$PROP_MISSING" -gt 0 ]; then
    while IFS= read -r row; do
      _n=$(echo "$row" | grep -o '[0-9][0-9]*' | head -1 | sed 's/^0*//'); [ -n "$_n" ] || _n=0
      [ "$_n" -ge "$PROP_FLOOR" ] && echo "$row" >> "$TMP/prop_new"
    done < "$TMP/prop"
  fi
  if [ -s "$TMP/prop_new" ] 2>/dev/null; then
    err "entr(y|ies) naming a document that does not cite them (floor $ID_PREFIX-$PROP_FLOOR):"
    sed 's/^/         /' "$TMP/prop_new"
  else
    ok "consequences propagate (backlog below the floor: $PROP_MISSING)"
  fi
fi

# ---------- 6. supersede / contradict annotates the target ----------
# One word for "adds to" and "replaces a clause of" is unenforceable, so the
# markers are distinct and only two of them oblige the target to say so.
if [ "$SHAPE" = "none" ]; then
  dormant "supersede annotations — no decision home yet"
else
  : > "$TMP/ann"
  while IFS="$(printf '\t')" read -r src marker target; do
    [ -n "${target:-}" ] || continue
    [ "$marker" = "Refines" ] && continue          # additive: no annotation owed
    _status=$(grep "^$target	" "$TMP/entries" | head -1 | cut -f3)
    if [ -z "$_status" ]; then
      echo "$src $marker $target: target is not a defined entry" >> "$TMP/ann"
    else
      case "$_status" in
        *"$src"*) ;;
        *) echo "$target: status line does not record that $src ${marker}s it" >> "$TMP/ann" ;;
      esac
    fi
  done < "$TMP/edges"
  if [ -s "$TMP/ann" ] 2>/dev/null; then
    err "unannotated supersede/contradict target(s):"; sed 's/^/         /' "$TMP/ann"
  else
    ok "supersede and contradict targets are annotated"
  fi
fi

# ---------- 7. retired-decision residue (RATCHETED) ----------
# A document citing a WHOLLY RETIRED id must say so in the same breath. The unit
# is a line: one marker on it exempts every id on it. That is a real blind spot,
# measured and accepted — a tighter window produced mostly noise, and a gate that
# is mostly noise is a gate people switch off.
RESIDUE=0
if [ "$SHAPE" = "none" ]; then
  dormant "retired residue — no decision home yet"
else
  : > "$TMP/retired"
  while IFS="$(printf '\t')" read -r id file status; do
    case "$status" in
      *Superseded\ by*|*Reversed*) echo "$id" >> "$TMP/retired" ;;
    esac
  done < "$TMP/entries"
  if [ -s "$TMP/retired" ] 2>/dev/null; then
    : > "$TMP/res"
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      [ "$f" = "$DEC_FILE" ] && continue
      case "$f" in "$ADR_DIR"/*) continue ;; esac
      while IFS= read -r rid; do
        grep -n "$rid" "$(flat_of "$f")" 2>/dev/null | while IFS=: read -r ln text; do
          case "$text" in
            *supersed*|*Supersed*|*retired*|*Retired*|*reversed*|*Reversed*) ;;
            *) echo "$f:$ln cites $rid (retired) without saying so" >> "$TMP/res" ;;
          esac
        done
      done < "$TMP/retired"
    done < "$TMP/files"
    [ -f "$TMP/res" ] && RESIDUE=$(wc -l < "$TMP/res" | tr -d ' ')
    if [ "$RESIDUE" -gt "$RESIDUE_FLOOR" ]; then
      err "$RESIDUE unmarked citation(s) of retired decisions (floor $RESIDUE_FLOOR):"
      sed 's/^/         /' "$TMP/res"
    else
      ok "no unmarked citation of a retired decision (residue $RESIDUE, floor $RESIDUE_FLOOR)"
    fi
  else
    ok "no retired decisions yet"
  fi
fi

# ---------- 8. status vocabularies are closed ----------
# An unrecognised status is worse than a missing one: it looks answered, and every
# check on that row skips in silence.
if [ "$SHAPE" = "none" ]; then
  dormant "decision status vocabulary — no decision home yet"
else
  : > "$TMP/vocab"
  while IFS="$(printf '\t')" read -r id file status; do
    case "$status" in
      *Accepted*|*Superseded\ by*|*Reversed*) ;;
      *) echo "$file: $id has an unknown status ->${status#*Status:}" >> "$TMP/vocab" ;;
    esac
  done < "$TMP/entries"
  if [ -s "$TMP/vocab" ] 2>/dev/null; then
    err "decision status vocabulary:"; sed 's/^/         /' "$TMP/vocab"
  else
    ok "decision statuses are inside the closed vocabulary"
  fi
fi

if [ -f "$OQ_FILE" ]; then
  : > "$TMP/oqvocab"
  grep -n '^| *OQ-[0-9]' "$(flat_of "$OQ_FILE")" 2>/dev/null | while IFS= read -r row; do
    case "$row" in
      *'| Open '*|*'| Open|'*|*Open\ \|*|*Resolved→*|*Dropped*) ;;
      *) echo "$OQ_FILE:${row%%:*}: unknown question status" >> "$TMP/oqvocab" ;;
    esac
  done
  if [ -s "$TMP/oqvocab" ] 2>/dev/null; then
    err "open-question status vocabulary:"; sed 's/^/         /' "$TMP/oqvocab"
  else
    ok "open-question statuses are inside the closed vocabulary"
  fi
else
  dormant "open-question status vocabulary — no $OQ_FILE yet"
fi

# ---------- 9. every commit SHA named in the retro resolves ----------
# A file:line rots at the next edit; a SHA carries the diff, the message and the
# parent forever. A document may not send a reader to something absent.
if [ ! -d .git ]; then
  skipmsg "commit-SHA resolution — not a git working tree"
elif [ ! -d "$RETRO_GLOB" ]; then
  dormant "commit-SHA resolution — no $RETRO_GLOB yet"
else
  : > "$TMP/sha"
  find "$RETRO_GLOB" -type f -name '*.md' 2>/dev/null | sort | while IFS= read -r f; do
    grep -n -o '`[0-9a-f][0-9a-f]*`' "$(flat_of "$f")" 2>/dev/null |
    while IFS=: read -r ln tok; do
      s=$(echo "$tok" | tr -d '`')
      case ${#s} in 7|8|9|10|11|12|40) ;; *) continue ;; esac
      git rev-parse --verify --quiet "$s^{commit}" >/dev/null 2>&1 ||
        echo "$f:$ln: commit \`$s\` does not resolve" >> "$TMP/sha"
    done
  done
  if [ -s "$TMP/sha" ] 2>/dev/null; then
    err "unresolvable commit reference(s):"; sed 's/^/         /' "$TMP/sha"
  else
    ok "every commit reference in $RETRO_GLOB resolves"
  fi
fi

# ---------- 10. the doc map and the registers agree, BOTH directions ----------
# The direction that feels redundant is the one that finds things: a register the
# map never names is a register nobody is told about.
if [ ! -f "$MAP_FILE" ]; then
  dormant "doc-map coverage — no $MAP_FILE yet"
else
  # Forward direction is scoped to the "## Registers" table: that table is a CLAIM
  # about what exists. The SSOT table below it legitimately names documents a young
  # project has not written yet, and failing on those would make the gate seed red.
  # TABLE ROWS ONLY. Reading every backtick in the section swept up the prose note
  # under the table ("an existing docs/adr/ IS the register") and reported it as a
  # missing file — a claim the note never made. A row is a claim; a sentence is not.
  : > "$TMP/map"
  awk '/^## Registers/ { on = 1; next } on && /^## / { exit } on && /^\|/ { print }' \
    "$(flat_of "$MAP_FILE")" | grep -o '`[^`]*`' | tr -d '`' | sort -u > "$TMP/map"
  : > "$TMP/mapmiss"
  while IFS= read -r doc; do
    case "$doc" in *'<'*|*'>'*) continue ;; esac
    case "$doc" in *.md|*/) ;; *) continue ;; esac
    [ -e "$doc" ] || [ -e "${doc%/}" ] ||
      echo "$MAP_FILE names $doc, which does not exist" >> "$TMP/mapmiss"
  done < "$TMP/map"
  for reg in "$DEC_FILE" "$OQ_FILE"; do
    [ -f "$reg" ] || continue
    grep -q "$(basename "$reg")" "$TMP/map" ||
      echo "$reg exists but $MAP_FILE never names it" >> "$TMP/mapmiss"
  done
  if [ "$SHAPE" = "adr" ]; then
    grep -q "adr" "$TMP/map" ||
      echo "$ADR_DIR is this project's decision home but $MAP_FILE never names it" >> "$TMP/mapmiss"
  fi
  if [ -s "$TMP/mapmiss" ] 2>/dev/null; then
    err "doc map / register disagreement:"; sed 's/^/         /' "$TMP/mapmiss"
  else
    ok "doc map and registers agree in both directions"
  fi
fi

# ---------- VERDICT — nothing may run after this block ----------
if [ "$FAIL" -ne 0 ]; then
  echo "FAIL: documentation gate"
  exit 1
fi
echo "OK: documentation gate — shape $SHAPE · ${DECS:-0} decisions · ${OQS:-0} open questions · propagation backlog ${PROP_MISSING:-0} (floor $PROP_FLOOR) · retired residue ${RESIDUE:-0} (floor $RESIDUE_FLOOR)"
exit 0
