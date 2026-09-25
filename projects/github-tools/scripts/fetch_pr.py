# -*- coding: utf-8 -*-
"""fetch_pr.py <N> [dir] — dump PR liveness, comments, reviews, inline comments, diff."""
import json, os, sys, time
from urllib.request import Request, urlopen

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'

tok = [l.split('=', 1)[1].strip() for l in open(TOK_PATH, encoding='utf-8') if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json',
     'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'}


def g(url, retry=4, accept=None):
    hh = dict(H)
    if accept:
        hh['Accept'] = accept
    last = None
    for a in range(retry):
        try:
            return json.loads(urlopen(Request(url, headers=hh), timeout=45).read())
        except Exception as e:
            last = e
            if a == retry - 1:
                raise
            time.sleep(3 + a * 5)
    raise last


def raw(url, retry=4):
    last = None
    for a in range(retry):
        try:
            return urlopen(Request(url, headers=H), timeout=60).read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            if a == retry - 1:
                raise
            time.sleep(3 + a * 5)
    raise last


def main():
    n = int(sys.argv[1])
    outdir = sys.argv[2] if len(sys.argv) > 2 else None
    pr = g('%s/repos/%s/pulls/%d' % (BASE, REPO, n))
    print('=== PR %d ===' % n)
    print('title: %s' % pr.get('title'))
    print('state: %s draft=%s mergeable=%s mergeable_state=%s' % (
        pr.get('state'), pr.get('draft'), pr.get('mergeable'), pr.get('mergeable_state')))
    print('head: %s  base: %s' % (pr['head']['sha'], pr['base']['sha']))
    print('user: %s  commits=%s files=%s +%s -%s' % (
        pr['user']['login'], pr.get('commits'), pr.get('changed_files'),
        pr.get('additions'), pr.get('deletions')))
    print('created: %s updated: %s' % (pr.get('created_at'), pr.get('updated_at')))
    print('--- BODY ---')
    print((pr.get('body') or '').strip())
    print('--- FILES ---')
    files = g('%s/repos/%s/pulls/%d/files?per_page=100' % (BASE, REPO, n))
    for f in files:
        print('%s  +%s -%s  %s' % (f['filename'], f['additions'], f['deletions'], f['status']))

    print('--- ISSUE COMMENTS ---')
    for c in g('%s/repos/%s/issues/%d/comments?per_page=100' % (BASE, REPO, n)):
        print('### %s @ %s\n%s' % (c['user']['login'], c['created_at'], (c.get('body') or '').strip()))
        print('---')

    print('--- FORMAL REVIEWS ---')
    for r in g('%s/repos/%s/pulls/%d/reviews?per_page=100' % (BASE, REPO, n)):
        print('### %s [%s] @ %s\n%s' % (r['user']['login'], r.get('state'), r.get('submitted_at'), (r.get('body') or '').strip()))
        print('---')

    print('--- INLINE COMMENTS ---')
    for c in g('%s/repos/%s/pulls/%d/comments?per_page=100' % (BASE, REPO, n)):
        print('### %s @ %s  %s:%s (commit %s)\n%s' % (
            c['user']['login'], c['created_at'], c['path'], c.get('line') or c.get('original_line'),
            (c.get('commit_id') or '')[:8], (c.get('body') or '').strip()))
        print('---')

    if outdir:
        os.makedirs(outdir, exist_ok=True)
        d = raw('%s/repos/%s/pulls/%d' % (BASE, REPO, n), ) if False else None
        try:
            diff = urlopen(Request('%s/repos/%s/pulls/%d' % (BASE, REPO, n),
                                   headers=dict(H, Accept='application/vnd.github.v3.diff')), timeout=90).read().decode('utf-8', 'replace')
        except Exception as e:
            print('DIFF FETCH FAILED: %s' % e)
            diff = None
        if diff:
            p = os.path.join(outdir, '%d.diff' % n)
            open(p, 'w', encoding='utf-8').write(diff)
            print('diff saved: %s (%d chars)' % (p, len(diff)))


if __name__ == '__main__':
    main()
