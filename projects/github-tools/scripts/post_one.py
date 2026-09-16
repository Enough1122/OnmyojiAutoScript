# -*- coding: utf-8 -*-
"""post_one.py <PR_NUMBER> — post a single AI review comment with SOP guarantees.

Reads the review body from C:\\Users\\admin\\AppData\\Local\\Temp\\opencode\\campaign\\<N>.md
Guarantees:
  - SOP header present (prefixes it if the draft omitted it)
  - pre-post dedupe: skip if Enough1122 already left an 'AI code review' comment
  - POST as issue comment, then sleep 8
Prints one of: POSTED <url> | SKIP_DUPE | SKIP_STALE | ERR <msg>
"""
import json, os, sys, time, urllib.request
from urllib.request import Request, urlopen

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'
MD_DIR = r'C:\Users\admin\AppData\Local\Temp\opencode\campaign'
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


def main():
    n = int(sys.argv[1])
    path = os.path.join(MD_DIR, '%d.md' % n)
    if not os.path.exists(path):
        print('ERR %d no draft file' % n)
        return 2
    body = open(path, encoding='utf-8').read().strip()
    if not body:
        print('ERR %d empty draft' % n)
        return 2
    if not body.startswith('> AI code review'):
        body = HEADER + '\n\n' + body
        open(path, 'w', encoding='utf-8').write(body)

    # liveness re-check: PR must still be open, non-draft, and still unreviewed
    pr = g('%s/repos/%s/pulls/%d' % (BASE, REPO, n))
    if pr.get('state') != 'open' or pr.get('draft'):
        print('SKIP_STALE %d state=%s draft=%s' % (n, pr.get('state'), pr.get('draft')))
        return 0

    cs = g('%s/repos/%s/issues/%d/comments?per_page=100' % (BASE, REPO, n))
    if any(c['user']['login'] == 'Enough1122' and 'AI code review' in (c.get('body') or '') for c in cs):
        print('SKIP_DUPE %d (my AI review already present)' % n)
        return 0
    if len(cs):
        print('SKIP_STALE %d (someone commented: %d)' % (n, len(cs)))
        return 0

    rvs = g('%s/repos/%s/pulls/%d/reviews?per_page=100' % (BASE, REPO, n))
    if len(rvs):
        print('SKIP_STALE %d (someone reviewed: %d)' % (n, len(rvs)))
        return 0
    rc = g('%s/repos/%s/pulls/%d/comments?per_page=100' % (BASE, REPO, n))
    if len(rc):
        print('SKIP_STALE %d (inline review comments: %d)' % (n, len(rc)))
        return 0

    data = json.dumps({'body': body}).encode('utf-8')
    req = Request('%s/repos/%s/issues/%d/comments' % (BASE, REPO, n), data=data, headers=H, method='POST')
    r = json.loads(urlopen(req, timeout=60).read())
    print('POSTED %d %s' % (n, r['html_url']))
    time.sleep(8)
    return 0


if __name__ == '__main__':
    sys.exit(main())
