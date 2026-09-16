# -*- coding: utf-8 -*-
"""post_followup.py <number> — post a SECOND (follow-up) AI comment on a PR.

Unlike post_review.py (which enforces one-AI-review-per-PR), this posts the
body from Temp/opencode/campaign/{n}.md as an additional comment on the issue
thread. Dedupe is content-level: if the most recent comment by Enough1122 has
the exact same body, it is skipped.

Exit codes: 0 posted | 2 skipped-dup | 3 no md | 4 http error
"""
import json, sys, time, urllib.request
from urllib.request import Request, urlopen

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
MD_DIR = r'C:\Users\admin\AppData\Local\Temp\opencode\campaign'
REPO = 'NousResearch/hermes-agent'
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
    try:
        cs = g('https://api.github.com/repos/%s/issues/%d/comments?per_page=100' % (REPO, n))
    except Exception as e:
        print('HTTP-ERR %d %s' % (n, str(e)[:80]))
        sys.exit(4)
    mine = [c for c in cs if (c.get('user') or {}).get('login') == ME]
    if mine and (mine[-1].get('body') or '').strip() == body:
        print('SKIP-DUP %d (identical follow-up already posted)' % n)
        sys.exit(2)
    data = json.dumps({'body': body}).encode()
    req = Request('https://api.github.com/repos/%s/issues/%d/comments' % (REPO, n), data=data, headers=H, method='POST')
    try:
        r = json.loads(urlopen(req, timeout=60).read())
    except Exception as e:
        print('HTTP-ERR %d %s' % (n, str(e)[:80]))
        sys.exit(4)
    print('POSTED %d %s' % (n, r.get('html_url', '')))
    time.sleep(8)


if __name__ == '__main__':
    main()
