# -*- coding: utf-8 -*-
"""post_review.py <number> — post one AI review for a PR.

Reads the review body from Temp/opencode/campaign/{n}.md, enforces the AI header,
dedupe-checks existing comments by Enough1122 (skip only if the exact authored body
is already present), POSTs to the issue comments endpoint, and reads the comment
back to require Enough1122 as author before printing POSTED.

Exit codes: 0 posted | 2 skipped-dup | 3 no md / bad header | 4 http error
"""
import json, sys, time, urllib.request
from urllib.request import Request, urlopen

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
MD_DIR = r'C:\Users\admin\AppData\Local\Temp\opencode\campaign'
REPO = 'NousResearch/hermes-agent'
HEADER = '> AI code review'
ME = 'Enough1122'

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + tok,
     'Content-Type': 'application/json'}


def g(url):
    return json.loads(urlopen(Request(url, headers=H), timeout=30).read())


def main():
    n = int(sys.argv[1])
    p = MD_DIR + '\\%d.md' % n
    try:
        body = open(p, encoding='utf-8').read().strip()
    except OSError:
        print('NO-MD %d' % n)
        sys.exit(3)
    if not body.startswith(HEADER):
        print('BAD-HEADER %d' % n)
        sys.exit(3)

    try:
        cs = g('https://api.github.com/repos/%s/issues/%d/comments?per_page=100' % (REPO, n))
    except Exception as e:
        print('HTTP-ERR %d %s' % (n, str(e)[:80]))
        sys.exit(4)
    mine = [c for c in cs if (c.get('user') or {}).get('login') == ME
            and HEADER in (c.get('body') or '')
            and (c.get('body') or '').strip() == body]
    if mine:
        print('SKIP-DUP %d (exact AI comment already present)' % n)
        sys.exit(2)

    data = json.dumps({'body': body}).encode()
    req = Request('https://api.github.com/repos/%s/issues/%d/comments' % (REPO, n), data=data, headers=H, method='POST')
    try:
        r = json.loads(urlopen(req, timeout=60).read())
    except Exception as e:
        print('HTTP-ERR %d %s' % (n, str(e)[:80]))
        sys.exit(4)
    comment_id = r.get('id')
    if not comment_id:
        print('HTTP-ERR %d POST response missing comment id' % n)
        sys.exit(4)
    try:
        receipt = g('https://api.github.com/repos/%s/issues/comments/%s' % (REPO, comment_id))
    except Exception as e:
        print('HTTP-ERR %d receipt read-back %s' % (n, str(e)[:80]))
        sys.exit(4)
    if (receipt.get('user') or {}).get('login') != ME:
        print('HTTP-ERR %d read-back author is not %s' % (n, ME))
        sys.exit(4)
    expected_url = 'https://github.com/%s/pull/%d#issuecomment-%s' % (REPO, n, comment_id)
    if r.get('html_url') != expected_url or receipt.get('html_url') != expected_url:
        print('HTTP-ERR %d read-back URL is not the canonical issuecomment URL' % n)
        sys.exit(4)
    if (receipt.get('body') or '').strip() != body:
        print('HTTP-ERR %d read-back body mismatch' % n)
        sys.exit(4)
    print('POSTED %d %s' % (n, r.get('html_url', '')))
    time.sleep(8)


if __name__ == '__main__':
    main()
