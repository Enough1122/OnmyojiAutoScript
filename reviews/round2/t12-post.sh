#!/bin/bash
REPO=$1; N=$2; BF=$3
LOG=/d/Hermes/reviews/round2/r2-log-D.txt
PROG=/d/Hermes/reviews/round2/progress-hm.txt
OUT=$(gh pr comment $N --repo $REPO --body-file "$BF" 2>&1); RC=$?
if [ $RC -ne 0 ]; then
  echo "attempt1 rc=$RC: $(echo "$OUT" | head -c 300)"
  case "$OUT" in
    *403*|*429*|*"rate limit"*|*"Rate limit"*|*abuse*|*secondary*)
      sleep 60
      OUT=$(gh pr comment $N --repo $REPO --body-file "$BF" 2>&1); RC=$? ;;
  esac
fi
if [ $RC -eq 0 ]; then
  echo "posted-url: $OUT"
  echo $N >> "$PROG"
  echo "$N posted" >> "$LOG"; echo "$N posted"
  sleep 8; exit 0
fi
echo "final-fail: $(echo "$OUT" | head -c 300)"
echo "$N failed-x" >> "$LOG"; echo "$N failed-x"
sleep 300
exit 1