#!/bin/bash
# t16-step1.sh N -- state/dedup/diff fetch for PR N. Prints compact report + diff.
set -u
N="$1"
BASE="D:/Hermes/reviews/round2"
REPO="NousResearch/hermes-agent"
LOG="$BASE/t16-disposition.log"
TMP="$BASE/tmp-t8"
mkdir -p "$TMP" "$BASE/rb"

state="$(gh api "repos/$REPO/pulls/$N" -q .state 2>"$TMP/t16-err-$N.txt")"
rc=$?
if [ $rc -ne 0 ] || [ "$state" != "open" ]; then
  echo "$N skipped-closed" >> "$LOG"
  echo "== $N skipped-closed (state='$state' err=$(head -c 120 "$TMP/t16-err-$N.txt" | tr '\n' ' '))"
  sleep 3
  exit 0
fi

meta="$(gh api "repos/$REPO/pulls/$N" -q '"\(.title)\t\(.changed_files)\t\(.additions)\t\(.deletions)\t\(.diff_url)"')"
IFS=$'\t' read -r TITLE NF NA ND DIFFURL <<<"$meta"

cmtn="$(gh api "repos/$REPO/issues/$N/comments" -q 'length' 2>/dev/null)"
revn="$(gh api "repos/$REPO/pulls/$N/reviews" -q 'length' 2>/dev/null)"
if [ "${cmtn:-0}" -gt 0 ] || [ "${revn:-0}" -gt 0 ]; then
  echo "$N skipped-reviewed" >> "$LOG"
  echo "== $N skipped-reviewed (comments=${cmtn:-ERR} reviews=${revn:-ERR}) title=$TITLE"
  sleep 3
  exit 0
fi

curl -sL "$DIFFURL" -o "$TMP/t16-diff-$N.diff"
size=$(wc -c < "$TMP/t16-diff-$N.diff")
nf=$(grep -c '^diff --git' "$TMP/t16-diff-$N.diff")

if [ "$size" -gt 200000 ] || [ "$nf" -gt 30 ]; then
  printf '> AI code review -- automated review for reference; please use your judgment.\n\nDiff too large for automated review -- recommend human review.\n' > "$BASE/rb/rb-$N.md"
  echo "== $N LARGE size=$size files=$nf title=$TITLE (rb written; run post step)"
  exit 0
fi

echo "== $N REVIEW size=$size files=$nf +$NA -$ND title=$TITLE"
echo "--- FILELIST ---"
grep '^diff --git' "$TMP/t16-diff-$N.diff" | sed 's/^diff --git a\///; s/ b\/.*$//' | head -40
echo "--- DIFF ---"
if [ "$size" -le 40000 ]; then
  cat "$TMP/t16-diff-$N.diff"
else
  head -c 25000 "$TMP/t16-diff-$N.diff"
  echo ""
  echo "[...snip middle; full copy at $TMP/t16-diff-$N.diff ...]"
  tail -c 10000 "$TMP/t16-diff-$N.diff"
fi
