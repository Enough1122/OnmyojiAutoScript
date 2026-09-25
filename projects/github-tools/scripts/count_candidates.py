# -*- coding: utf-8 -*-
"""count_candidates.py — 统计战役待审候选（对 GitHub 只读，不发帖）。

以本地 drafts/_campaign_state.json 的 frontier 为断点，列出编号 > frontier 的
全部 open PR。基本候选条件只有 open、非 draft；已有评论/review 只作语义对照，
大 diff 进入 deep lane，不能被筛掉或自动 deferred。

输出合格数、lane 分布、排除原因与逐条明细（JSON 快照），并保留 state 中已有的
deferred 历史；本脚本不再把大任务写成新的 deferred。
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
LINES_MAX = 250


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
        files = d.get('changed_files') or 0
        lane = 'fast' if files <= FILES_MAX and size <= LINES_MAX else 'deep'
        return {'n': n, 'draft': bool(d.get('draft')),
                'comments': d.get('comments', 0),
                'review_comments': d.get('review_comments', 0),
                'reviews': n_reviews, 'files': files,
                'size': size, 'lane': lane, 'created': (d.get('created_at') or '')[:10],
                'title': (d.get('title') or '')[:70],
                'eligible': not d.get('draft'),
                'deferred': False}

    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(biopsy, cands):
            results.append(r)
            time.sleep(0.05)

    elig = [r for r in results if r['eligible']]
    fast = [r for r in elig if r['lane'] == 'fast']
    deep = [r for r in elig if r['lane'] == 'deep']
    deferred = []
    json.dump({'frontier': frontier, 'open_above': len(cands),
               'eligible': len(elig), 'fast': len(fast), 'deep': len(deep),
               'deferred': deferred, 'rows': results},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # 保留历史 deferred；大任务现在进入 deep lane，不再覆盖或追加到 deferred。
    try:
        st = json.load(open(STATE, encoding='utf-8'))
        st.setdefault('deferred', [])
        json.dump(st, open(STATE, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    except FileNotFoundError:
        print('NOTE: campaign state 不存在，快照仍已写入')

    n_draft = sum(1 for r in results if r['draft'])
    n_att = sum(1 for r in results if not r['draft']
                and (r['comments'] or r['review_comments'] or r['reviews']))
    print('eligible: %d (fast=%d, deep=%d)' % (len(elig), len(fast), len(deep)))
    print('excluded: draft=%d; existing-attention kept for semantic dedupe=%d'
          % (n_draft, n_att))
    if elig:
        print('eligible range: #%d .. #%d  created %s .. %s'
              % (min(r['n'] for r in elig), max(r['n'] for r in elig),
                 min(r['created'] for r in elig), max(r['created'] for r in elig)))
    print('snapshot: ' + OUT)


if __name__ == '__main__':
    main()
