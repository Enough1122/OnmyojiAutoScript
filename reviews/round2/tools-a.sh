#!/usr/bin/env bash
# reviewer-a helper for round2 OC batches (t1/t9). Absolute paths only.
REPO="anomalyco/opencode"
LOG="D:/Hermes/reviews/round2/r2-log-A.txt"
PROG="D:/Hermes/reviews/round2/progress-oc.txt"
RB="D:/Hermes/reviews/round2/rb"
TMPD="D:/Hermes/reviews/round2/tmp-a"
mkdir -p "$RB" "$TMPD"

logline() { printf '%s\n' "$1" >> "$LOG"; }

meta() {
  local N="$1" CAP="${2:-7000}"
  local row st cf t durl C R f bytes
  if ! row=$(gh api "repos/$REPO/pulls/$N" -q '[.state,.changed_files,.title,.diff_url]|@tsv' 2>&1); then
    echo "ERR|api|$row"; return 0
  fi
  IFS=$'\t' read -r st cf t durl <<<"$row" || true
  if [ -z "$st" ] || [ "$st" = "null" ]; then echo "ERR|api|$row"; return 0; fi
  if [ "$st" != "open" ]; then
    logline "$N skipped-closed"; echo "DISPO|$N|skipped-closed|title=$t"; sleep 3; return 0
  fi
  C=$(gh api "repos/$REPO/issues/$N/comments" -q 'length' 2>/dev/null || echo ERR)
  R=$(gh api "repos/$REPO/pulls/$N/reviews" -q 'length' 2>/dev/null || echo ERR)
  if [ "$C" = "ERR" ] || [ "$R" = "ERR" ]; then echo "ERR|len|$N"; return 0; fi
  if [ "$C" -gt 0 ] || [ "$R" -gt 0 ]; then
    logline "$N skipped-reviewed"; echo "DISPO|$N|skipped-reviewed|c=$C|r=$R|title=$t"; sleep 3; return 0
  fi
  f="$TMPD/diff-$N.diff"
  curl -sL "$durl" -o "$f" || { echo "ERR|curl|$N"; return 0; }
  bytes=$(wc -c < "$f")
  echo "DISPO|$N|review|title=$t"
  echo "STATS|$bytes|$cf"
  if [ "$bytes" -gt 200000 ] || [ "$cf" -gt 30 ]; then
    echo "TOOLARGE"; rm -f "$f"; return 0
  fi
  echo "DIFF|cap=$CAP"
  head -c "$CAP" "$f"
  local total=$(wc -c < "$f")
  if [ "$total" -gt "$CAP" ]; then echo ""; echo "TRUNCATED|shown=$CAP|total=$total|file=$f"; fi
}

post() { # post N bodyfile
  local N="$1" BF="$2"
  if gh pr comment "$N" --repo "$REPO" --body-file "$BF" >/dev/null 2>&1; then
    echo "$N" >> "$PROG"; logline "$N posted"; echo "POSTED|$N"; sleep 8
  else
    echo "RETRY_NEEDED|$N"
  fi
}

retry1() { # retry1 N bodyfile  -> sleep 60 then one attempt
  local N="$1" BF="$2"; sleep 60
  if gh pr comment "$N" --repo "$REPO" --body-file "$BF" >/dev/null 2>&1; then
    echo "$N" >> "$PROG"; logline "$N posted"; echo "POSTED|$N"; sleep 8
  else
    echo "STILL_FAILING|$N"
  fi
}

failfinal() { # failfinal N -> sleep 300 then mark failed-x
  local N="$1"; sleep 300; logline "$N failed-x"; echo "FAILED_X|$N"
}

case "$1" in
  meta) shift; meta "$@" ;;
  post) shift; post "$@" ;;
  retry1) shift; retry1 "$@" ;;
  failfinal) shift; failfinal "$@" ;;
  logline) shift; logline "$*" ;;
  *) echo "usage: tools-a.sh meta N [cap] | post N file | retry1 N file | failfinal N | logline text" ;;
esac
