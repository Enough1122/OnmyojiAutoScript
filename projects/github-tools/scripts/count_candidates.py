# -*- coding: utf-8 -*-
"""count_candidates.py — 统计战役待审候选（对 GitHub 只读，不发帖）。

以本地 drafts/_campaign_state.json 的 frontier 为断点（见 PROMPT-inbox-pr.md §2.1），
列出编号 > frontier 的全部 open PR，并按战役口径逐条活检：
    非 draft + 零 issue 评论 + 零 inline 评论 + 零 review + <=15 文件 + diff(+) <100KB
超限（>15 文件或 >=100KB）但零关注的 PR 记入 deferred，并滚动覆盖
_campaign_state.json 的 deferred 列表（backlog 留底，断点不遗忘，见 §2.1）。
输出合格数、排除原因分布与逐条明细（JSON 快照）。

用法:
    python count_candidates.py            # 读 _campaign_state.json 的 frontier
    python count_candidates.py 112810     # 显式指定 frontier

写入 drafts/_candidates_snapshot.json；deferred 同步进 _campaign_state.json。
注意：size 用 additions+deletions 近似，真正 <100KB 判定在拉 diff 时复核。
"""
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen

TOK = [l.split('=', 1)[1].strip()
       for l in open(r'C:\Users\admin\AppData\Local\hermes\.env', encoding='utf-8')
       if l.startswith('GITHUB_TOKEN=')][0]
H = {'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json',
     'Authorization': 'Bearer ' + TOK}
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'
STATE = r'D:\Hermes\projects\github-tools\drafts\_campaign_state.json'
OUT = r'D:\Hermes\projects\github-tools\drafts\_candidates_snapshot.json'
FILES_MAX = 15
SIZE_MAX = 100000


def get(url, retries=3):
    """GET with backoff; 返回 (json, next_link_or_None)。"""
    for a in range(retries):
        try:
            with urlopen(Request(url, headers=H), timeout=30) as r:
                link = r.headers.get('Link', '')
                return json.loads(r.read()), link
        except Exception as e:
            if '403' in str(e) or '429' in str(e):
                time.sleep(60 * (a + 1))
                continue
            if a == retries - 1:
                raise
            time.sleep(2 * (a + 1))


def next_link(link):
    for part in link.split(','):
        if 'rel="next"' in part:
            return part[part.index('<') + 1:part.index('>')]
    return None


def main():
    if len(sys.argv) > 1:
        frontier = int(sys.argv[1])
    else:
        frontier = json.load(open(STATE, encoding='utf-8')).get('frontier', 0)
    print('frontier = %d' % frontier)

    # 1) 收集 open 且编号 > frontier 的 PR（新→旧，Link 头精确翻页）
    cands = []
    url = BASE + f'/repos/{REPO}/pulls?state=open&sort=created&direction=desc&per_page=100'
    while url:
        page, link = get(url)
        stop = False
        for pr in page:
            if pr['number'] <= frontier:
                stop = True
                break
            cands.append(pr)
        if stop:
            break
        url = next_link(link)
        time.sleep(0.2)
    print('open PRs > %d: %d' % (frontier, len(cands)))

    # 2) 并发活检（并发 6，防 secondary 限流）
    def biopsy(pr):
        n = pr['number']
        d, _ = get(BASE + f'/repos/{REPO}/pulls/{n}')
        rv, _ = get(BASE + f'/repos/{REPO}/pulls/{n}/reviews')
        n_reviews = len(rv) if isinstance(rv, list) else 0
        size = (d.get('additions') or 0) + (d.get('deletions') or 0)
        zero_attention = (d.get('comments', 0) == 0 and d.get('review_comments', 0) == 0
                          and n_reviews == 0)
        files = d.get('changed_files') or 0
        over_limit = files > FILES_MAX or size >= SIZE_MAX
        return {'n': n, 'draft': bool(d.get('draft')),
                'comments': d.get('comments', 0),
                'review_comments': d.get('review_comments', 0),
                'reviews': n_reviews, 'files': files,
                'size': size, 'created': (d.get('created_at') or '')[:10],
                'title': (d.get('title') or '')[:70],
                'eligible': (not d.get('draft') and zero_attention
                             and files <= FILES_MAX and size < SIZE_MAX),
                'deferred': (not d.get('draft') and zero_attention and over_limit)}

    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(biopsy, cands):
            results.append(r)
            time.sleep(0.05)

    elig = [r for r in results if r['eligible']]
    deferred = [{'n': r['n'], 'files': r['files'], 'size': r['size'],
                 'created': r['created'], 'title': r['title']}
                for r in results if r['deferred']]
    json.dump({'frontier': frontier, 'open_above': len(cands),
               'eligible': len(elig), 'deferred': deferred, 'rows': results},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # deferred 滚动覆盖进 campaign state（backlog 留底）
    try:
        st = json.load(open(STATE, encoding='utf-8'))
        st['deferred'] = deferred
        json.dump(st, open(STATE, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    except FileNotFoundError:
        print('NOTE: campaign state 不存在，deferred 仅写入快照')

    n_draft = sum(1 for r in results if r['draft'])
    n_att = sum(1 for r in results if not r['draft']
                and (r['comments'] or r['review_comments'] or r['reviews']))
    n_def = len(deferred)
    print('eligible: %d' % len(elig))
    print('excluded: draft=%d, has-attention=%d, deferred(over-limit)=%d'
          % (n_draft, n_att, n_def))
    if elig:
        print('eligible range: #%d .. #%d  created %s .. %s'
              % (min(r['n'] for r in elig), max(r['n'] for r in elig),
                 min(r['created'] for r in elig), max(r['created'] for r in elig)))
    if deferred:
        top = sorted(deferred, key=lambda r: -r['size'])[:5]
        print('deferred top-5 by size: '
              + ', '.join('#%d(%dKB,%df)' % (r['n'], r['size'] // 1024, r['files']) for r in top))
    print('snapshot: ' + OUT)


if __name__ == '__main__':
    main()
