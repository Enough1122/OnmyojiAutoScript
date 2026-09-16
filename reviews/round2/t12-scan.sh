#!/bin/bash
REPO=$1; shift
LOG=/d/Hermes/reviews/round2/r2-log-D.txt
touch "$LOG"
for N in "$@"; do
  grep -q "^$N " "$LOG" && { echo "$N already-done"; continue; }
  S=$(gh api repos/$REPO/pulls/$N -q .state 2>&1)
  if [ "$S" != "open" ]; then
    case "$S" in *404*) echo "note: $N HTTP404 treated closed" ;; esac
    echo "$N skipped-closed" >> "$LOG"; echo "$N skipped-closed"; sleep 3; continue
  fi
  C=$(gh api repos/$REPO/issues/$N/comments -q 'length' 2>/dev/null)
  R=$(gh api repos/$REPO/pulls/$N/reviews -q 'length' 2>/dev/null)
  case "$C" in "") C=0;; esac
  case "$R" in "") R=0;; esac
  if [ "$C" -gt 0 ] || [ "$R" -gt 0 ]; then
    echo "$N skipped-reviewed" >> "$LOG"; echo "$N skipped-reviewed"; sleep 3; continue
  fi
  URL=$(gh api repos/$REPO/pulls/$N -q .diff_url)
  curl -sL "$URL" -o /tmp/t12-$N.patch
  B=$(wc -c < /tmp/t12-$N.patch); F=$(grep -c '^diff --git' /tmp/t12-$N.patch)
  T=$(gh api repos/$REPO/pulls/$N -q .title 2>&1)
  echo "@@REVIEW $N|$B|$F|$T"
  break
done
echo SCAN-DONE