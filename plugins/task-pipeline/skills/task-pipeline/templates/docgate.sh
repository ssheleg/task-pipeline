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

set -u

FAIL=0
DOCS_DIR=${DOCS_DIR:-docs}
DEC_FILE=${DEC_FILE:-$DOCS_DIR/DECISIONS.md}
OQ_FILE=${OQ_FILE:-$DOCS_DIR/OPEN_QUESTIONS.md}
MAP_FILE=${MAP_FILE:-$DOCS_DIR/DOCMAP.md}
RETRO_GLOB=${RETRO_GLOB:-$DOCS_DIR/superpowers}

# ---------- ratchets: a floor may only fall. Raising one is a decision. ----------
PROP_FLOOR=${PROP_FLOOR:-0}        # allowed missing propagation citations
RESIDUE_FLOOR=${RESIDUE_FLOOR:-0}  # allowed unmarked citations of retired ids

TMP=$(mktemp -d 2>/dev/null || mktemp -d -t docgate)
trap 'rm -rf "$TMP"' EXIT

err()     { echo "ERR:     $*"; FAIL=1; }
ok()      { echo "ok:      $*"; }
skipmsg() { echo "skip:    $*"; }
dormant() { echo "dormant: $*"; }

# Strip fenced code blocks: sample content is not a claim about this repository.
# awk, because sed -i is not portable and this must run identically everywhere.
strip_fences() {
  awk '
    /^[ \t]*(```|~~~)/ { infence = !infence; print ""; next }
    { if (infence) print ""; else print }
  ' "$1"
}

# Every markdown file in scope, one per line.
find "$DOCS_DIR" -type f -name '*.md' 2>/dev/null | sort > "$TMP/files" || true
find . -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort >> "$TMP/files" || true
FILE_COUNT=$(wc -l < "$TMP/files" | tr -d ' ')

if [ "$FILE_COUNT" = "0" ]; then
  echo "FAIL: documentation gate — no markdown found under $DOCS_DIR"
  exit 1
fi

# Fence-stripped copies, addressed by a flattened path.
while IFS= read -r f; do
  [ -f "$f" ] || continue
  flat=$(echo "$f" | tr '/' '_')
  strip_fences "$f" > "$TMP/s_$flat"
done < "$TMP/files"

flat_of() { echo "$TMP/s_$(echo "$1" | tr '/' '_')"; }

# ---------- 1. relative links resolve ----------
_bad=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  dir=$(dirname "$f")
  # grep -o on the link target; keep the line number for the message.
  grep -n -o '](\([^) ]*\))' "$(flat_of "$f")" 2>/dev/null |
  sed 's/](\(.*\))/\1/' |
  while IFS=: read -r ln target; do
    case "$target" in
      http://*|https://*|mailto:*|'#'*|'') continue ;;
    esac
    base=${target%%#*}
    [ -n "$base" ] || continue
    if [ ! -e "$dir/$base" ]; then
      echo "$f:$ln: dangling link -> $target" >> "$TMP/badlinks"
    fi
  done
done < "$TMP/files"
if [ -s "$TMP/badlinks" ] 2>/dev/null; then
  _bad=$(wc -l < "$TMP/badlinks" | tr -d ' ')
  err "$_bad dangling relative link(s):"; sed 's/^/         /' "$TMP/badlinks"
else
  ok "relative links resolve ($FILE_COUNT files)"
fi

# ---------- 2. every id referenced is defined ----------
if [ ! -f "$DEC_FILE" ]; then
  dormant "id integrity — no $DEC_FILE yet"
  DECS=0; OQS=0
else
  # Read the FENCE-STRIPPED copy: a heading inside a ``` block is sample content,
  # not a definition. Reading the raw file here counts the format example as an
  # entry, and then "Next free ID" is wrong against a decision that never existed.
  grep -o '^### DEC-[0-9][0-9]*' "$(flat_of "$DEC_FILE")" | sed 's/^### //' | sort -u > "$TMP/dec_def"
  DECS=$(wc -l < "$TMP/dec_def" | tr -d ' ')
  : > "$TMP/oq_def"
  [ -f "$OQ_FILE" ] && grep -o '^| *OQ-[0-9][0-9]*' "$(flat_of "$OQ_FILE")" | sed 's/^| *//' | sort -u > "$TMP/oq_def"
  OQS=$(wc -l < "$TMP/oq_def" | tr -d ' ')
  cat "$TMP/dec_def" "$TMP/oq_def" | sort -u > "$TMP/defined"

  : > "$TMP/refs"
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    grep -v 'Next free ID' "$(flat_of "$f")" 2>/dev/null |
      grep -o '\(DEC\|OQ\)-[0-9][0-9]*' | sed "s|^|$f |" >> "$TMP/refs"
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

# ---------- 3. "Next free ID" == max defined + 1 ----------
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
  _claim=$(echo "$_claim" | sed 's/^0*//'); [ -n "$_claim" ] || _claim=0
  if [ ! -s "$_deffile" ]; then _max=0; else
    _max=$(sed "s/^$_prefix-//" "$_deffile" | sed 's/^0*//' | sort -n | tail -1)
    [ -n "${_max:-}" ] || _max=0
  fi
  _want=$((_max + 1))
  if [ "$((_claim))" -ne "$_want" ]; then
    err "$_file: 'Next free ID' claims $_prefix-$_claim, highest defined is $_max (expected $_want)"
  else
    ok "next free $_prefix id is correct ($_prefix-$_claim)"
  fi
}
check_next_free "$DEC_FILE" DEC "$TMP/dec_def"
check_next_free "$OQ_FILE"  OQ  "$TMP/oq_def"

# ---------- 4. a stated register size equals the computed one ----------
# Compute, never restate: a number written in prose is a number that goes stale.
if [ -f "$DEC_FILE" ] && grep -q 'Register size:' "$DEC_FILE" 2>/dev/null; then
  _stated=$(grep -o 'Register size:\** *\**[0-9][0-9]*' "$DEC_FILE" | head -1 | grep -o '[0-9][0-9]*')
  if [ "${_stated:-x}" != "$DECS" ]; then
    err "$DEC_FILE: states 'Register size: $_stated', computed $DECS"
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
if [ ! -f "$DEC_FILE" ]; then
  dormant "propagation — no $DEC_FILE yet"
  PROP_MISSING=0
else
  : > "$TMP/prop"
  _cur=""
  while IFS= read -r line; do
    case "$line" in
      '### DEC-'*) _cur=$(echo "$line" | grep -o 'DEC-[0-9][0-9]*') ;;
      *'Consequences / affects:'*)
        [ -n "$_cur" ] || continue
        echo "$line" | grep -o '`[^`]*`' | tr -d '`' | while IFS= read -r doc; do
          case "$doc" in *.md) ;; *) continue ;; esac
          [ -f "$doc" ] || { echo "$_cur $doc MISSINGFILE" >> "$TMP/prop"; continue; }
          if grep -q "$_cur" "$doc"; then :; else echo "$_cur $doc NOCITE" >> "$TMP/prop"; fi
        done ;;
    esac
  done < "$(flat_of "$DEC_FILE")"
  PROP_MISSING=0
  [ -f "$TMP/prop" ] && PROP_MISSING=$(wc -l < "$TMP/prop" | tr -d ' ')
  : > "$TMP/prop_new"
  if [ "$PROP_MISSING" -gt 0 ]; then
    while read -r id doc why; do
      _n=$(echo "$id" | sed 's/^DEC-//' | sed 's/^0*//'); [ -n "$_n" ] || _n=0
      [ "$_n" -ge "$PROP_FLOOR" ] && echo "$id -> $doc ($why)" >> "$TMP/prop_new"
    done < "$TMP/prop"
  fi
  if [ -s "$TMP/prop_new" ] 2>/dev/null; then
    err "decision(s) naming a document that does not cite them (floor DEC-$PROP_FLOOR):"
    sed 's/^/         /' "$TMP/prop_new"
  else
    ok "consequences propagate (backlog below the floor: $PROP_MISSING)"
  fi
fi

# ---------- 6. supersede / contradict annotates the target ----------
# One word for "adds to" and "replaces a clause of" is unenforceable, so the
# markers are distinct and only two of them oblige the target to say so.
if [ ! -f "$DEC_FILE" ]; then
  dormant "supersede annotations — no $DEC_FILE yet"
else
  : > "$TMP/ann"
  _cur=""
  while IFS= read -r line; do
    case "$line" in
      '### DEC-'*) _cur=$(echo "$line" | grep -o 'DEC-[0-9][0-9]*') ;;
      *'Supersedes:'*|*'Contradicts:'*)
        [ -n "$_cur" ] || continue
        echo "$line" | grep -o 'DEC-[0-9][0-9]*' | while IFS= read -r target; do
          [ "$target" = "$_cur" ] && continue
          _status=$(awk -v t="### $target " '
            index($0, t) == 1 { found = 1; next }
            found && /^### DEC-/ { exit }
            found && /Status:/ { print; exit }
          ' "$(flat_of "$DEC_FILE")")
          case "$_status" in
            *"$_cur"*) ;;
            *) echo "$target: status line does not record that $_cur retires or contradicts it" >> "$TMP/ann" ;;
          esac
        done ;;
    esac
  done < "$(flat_of "$DEC_FILE")"
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
if [ ! -f "$DEC_FILE" ]; then
  dormant "retired residue — no $DEC_FILE yet"
  RESIDUE=0
else
  : > "$TMP/retired"
  _cur=""
  while IFS= read -r line; do
    case "$line" in
      '### DEC-'*) _cur=$(echo "$line" | grep -o 'DEC-[0-9][0-9]*') ;;
      *'Status:'*)
        [ -n "$_cur" ] || continue
        case "$line" in
          *Superseded\ by*|*Reversed*) echo "$_cur" >> "$TMP/retired" ;;
        esac
        _cur="" ;;
    esac
  done < "$(flat_of "$DEC_FILE")"
  RESIDUE=0
  if [ -s "$TMP/retired" ] 2>/dev/null; then
    : > "$TMP/res"
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      [ "$f" = "$DEC_FILE" ] && continue
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
if [ -f "$DEC_FILE" ]; then
  : > "$TMP/vocab"
  grep -n 'Status:' "$(flat_of "$DEC_FILE")" 2>/dev/null | while IFS= read -r hit; do
    case "$hit" in
      *Accepted*|*Superseded\ by*|*Reversed*|*'`Status`'*) ;;
      *) echo "$DEC_FILE:${hit%%:*}: unknown decision status -> ${hit#*Status:}" >> "$TMP/vocab" ;;
    esac
  done
  if [ -s "$TMP/vocab" ] 2>/dev/null; then
    err "decision status vocabulary:"; sed 's/^/         /' "$TMP/vocab"
  else
    ok "decision statuses are inside the closed vocabulary"
  fi
else
  dormant "decision status vocabulary — no $DEC_FILE yet"
fi

if [ -f "$OQ_FILE" ]; then
  : > "$TMP/oqvocab"
  grep -n '^| *OQ-[0-9]' "$(flat_of "$OQ_FILE")" 2>/dev/null | while IFS= read -r row; do
    case "$row" in
      *'| Open '*|*'| Open|'*|*Open\ \|*|*Resolved→DEC-*|*Dropped*) ;;
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
  : > "$TMP/map"
  awk '/^## Registers/ { on = 1; next } on && /^## / { exit } on { print }' \
    "$(flat_of "$MAP_FILE")" | grep -o '`[^`]*\.md`' | tr -d '`' | sort -u > "$TMP/map"
  : > "$TMP/mapmiss"
  while IFS= read -r doc; do
    case "$doc" in *'<'*|*'>'*) continue ;; esac
    [ -e "$doc" ] || echo "$MAP_FILE names $doc, which does not exist" >> "$TMP/mapmiss"
  done < "$TMP/map"
  for reg in "$DEC_FILE" "$OQ_FILE"; do
    [ -f "$reg" ] || continue
    grep -q "$(basename "$reg")" "$TMP/map" ||
      echo "$reg exists but $MAP_FILE never names it" >> "$TMP/mapmiss"
  done
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
echo "OK: documentation gate — ${DECS:-0} decisions · ${OQS:-0} open questions · propagation backlog ${PROP_MISSING:-0} (floor $PROP_FLOOR) · retired residue ${RESIDUE:-0} (floor $RESIDUE_FLOOR)"
exit 0
