# -*- coding: utf-8 -*-
"""post_one.py <PR_NUMBER> — post a single AI review comment with SOP guarantees.

Reads the review body from C:\\Users\\admin\\AppData\\Local\\Temp\\opencode\\campaign\\<N>.md
Guarantees:
  - SOP header present (prefixes it if the draft omitted it)
  - pre-post dedupe: skip only if Enough1122 already posted the exact same review body
  - POST as issue comment
  - read the created comment back and require Enough1122 as author
  - require the canonical current-PR issuecomment URL and identical body
Prints one of: POSTED <url> | SKIP_DUPE | SKIP_STALE | ERR <msg>

Sleep between posts is OFF by default (2026-09-21: 用户定"先别考虑限流,触发了再说").
Set POST_SLEEP=<seconds> to reintroduce a pause; post_batch.py posts concurrently.
"""
import json, os, sys, time, urllib.request
from urllib.request import Request, urlopen

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'
MD_DIR = r'C:\Users\admin\AppData\Local\Temp\opencode\campaign'
# 2026-09-21: 子代理现在把草稿写在项目里的 drafts/_pending/（SOP §2.3），老位置保留兼容
MD_DIRS = [r'D:\Hermes\projects\github-tools\drafts\_pending', MD_DIR]
HEADER = '> AI code review — automated review for reference; please use your judgment.'

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json',
     'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'}


def g(url, retry=3):
    for a in range(retry):
        try:
            return json.loads(urlopen(Request(url, headers=H), timeout=30).read())
        except Exception as e:
            if a == retry - 1:
                raise
            time.sleep(2 + a * 2)


def post(n, sleep_secs=0.0):
    """Post the draft for PR `n`. Returns a status string (never raises on HTTP error paths)."""
    n = int(n)
    path = next((os.path.join(d, '%d.md' % n) for d in MD_DIRS
                 if os.path.exists(os.path.join(d, '%d.md' % n))), None)
    if not path:
        return 'ERR %d no draft file' % n
    body = open(path, encoding='utf-8').read().strip()
    if not body:
        return 'ERR %d empty draft' % n
    if not body.startswith('> AI code review'):
        body = HEADER + '\n\n' + body
        open(path, 'w', encoding='utf-8').write(body)

    # Liveness re-check: PR must still be open and non-draft. Other reviewers' comments
    # are context for semantic de-duplication, not a skip condition (2026-09-25 policy).
    pr = g('%s/repos/%s/pulls/%d' % (BASE, REPO, n))
    if pr.get('state') != 'open' or pr.get('draft'):
        return 'SKIP_STALE %d state=%s draft=%s' % (n, pr.get('state'), pr.get('draft'))

    cs = g('%s/repos/%s/issues/%d/comments?per_page=100' % (BASE, REPO, n))
    if any(
        c['user']['login'] == 'Enough1122'
        and 'AI code review' in (c.get('body') or '')
        and (c.get('body') or '').strip() == body
        for c in cs
    ):
        return 'SKIP_DUPE %d (exact AI review already present)' % n

    data = json.dumps({'body': body}).encode('utf-8')
    req = Request('%s/repos/%s/issues/%d/comments' % (BASE, REPO, n), data=data, headers=H, method='POST')
    r = json.loads(urlopen(req, timeout=60).read())
    comment_id = r.get('id')
    if not comment_id:
        return 'ERR %d post response missing comment id' % n
    receipt = g('%s/repos/%s/issues/comments/%s' % (BASE, REPO, comment_id))
    if (receipt.get('user') or {}).get('login') != 'Enough1122':
        return 'ERR %d read-back author is not Enough1122' % n
    expected_url = ('https://github.com/%s/pull/%d#issuecomment-%s'
                    % (REPO, n, comment_id))
    if r.get('html_url') != expected_url or receipt.get('html_url') != expected_url:
        return 'ERR %d read-back URL is not the canonical issuecomment URL' % n
    if (receipt.get('body') or '').strip() != body:
        return 'ERR %d read-back body mismatch' % n
    if sleep_secs:
        time.sleep(sleep_secs)
    return 'POSTED %d %s' % (n, r['html_url'])


def main():
    if len(sys.argv) < 2:
        print('usage: post_one.py <PR_NUMBER>')
        return 2
    sleep_secs = float(os.environ.get('POST_SLEEP', '0'))
    st = post(int(sys.argv[1]), sleep_secs)
    print(st)
    return 2 if st.startswith('ERR') else 0


if __name__ == '__main__':
    sys.exit(main())
