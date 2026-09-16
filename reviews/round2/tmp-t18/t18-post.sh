#!/bin/bash
# t18-post.sh N -- post review comment for PR N, record progress/disposition.
set -u
N="$1"
BASE="D:/Hermes/reviews/round2"
REPO="NousResearch/hermes-agent"
LOG="$BASE/r2-log-H.txt"
RB="$BASE/rb/rb-$N.md"
TMP="$BASE/tmp-t8"

ok=0
for attempt in 1 2 3; do
  if gh pr comment "$N" --repo "$REPO" --body-file "$RB" >/dev/null 2>"$TMP/t18-posterr-$N.txt"; then
    ok=1; break
  fi
  err=$(tr '\n' ' ' < "$TMP/t18-posterr-$N.txt" | head -c 200)
  echo "   attempt $attempt failed: $err"
  if [ $attempt -eq 1 ]; then sleep 60; elif [ $attempt -eq 2 ]; then sleep 300; fi
done

if [ $ok -eq 1 ]; then
  echo "$N" >> "$BASE/progress-hm.txt"
  echo "$N posted" >> "$LOG"
  echo "== $N posted"
  sleep 8
else
  echo "$N failed-x" >> "$LOG"
  echo "== $N failed-x"
fi
