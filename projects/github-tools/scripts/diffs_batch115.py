# -*- coding: utf-8 -*-
"""Fetch PR diffs for a durable-pool campaign list.

Input : drafts/_batch115_list.json (flat list of PR numbers, ascending)
Output: drafts/_campaign/{N}.diff + drafts/_batch115_final.json (all fetched PRs)
Policy: every successfully fetched diff is saved and returned, regardless of size.
        Large diffs are counted for reporting and routed to the durable deep lane.
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen

TOK_PATH = r'C:\Users\admin\AppData\Local\hermes\.env'
BASE = 'https://api.github.com'
REPO = 'NousResearch/hermes-agent'
OUT = r'D:\Hermes\projects\github-tools\drafts\_campaign'
LARGE = 100000  # reporting threshold only; never an exclusion gate

tok = [line.split('=', 1)[1].strip() for line in open(TOK_PATH, encoding='utf-8')
       if line.startswith('GITHUB_TOKEN=')][0]
H = {
    'User-Agent': 'Hermes-Agent',
    'Accept': 'application/vnd.github.v3.diff',
    'Authorization': 'Bearer ' + tok,
}

LIST = sys.argv[1] if len(sys.argv) > 1 else r'D:\Hermes\projects\github-tools\drafts\_batch115_list.json'
FINAL = sys.argv[2] if len(sys.argv) > 2 else r'D:\Hermes\projects\github-tools\drafts\_batch115_final.json'
nums = json.load(open(LIST, encoding='utf-8'))
os.makedirs(OUT, exist_ok=True)
print('batch:', len(nums), nums[0], '..', nums[-1], flush=True)


def fetch(n):
    path = os.path.join(OUT, '%d.diff' % n)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return n, os.path.getsize(path), 'cached'
    for attempt in range(3):
        try:
            diff = urlopen(
                Request('%s/repos/%s/pulls/%d' % (BASE, REPO, n), headers=H),
                timeout=60,
            ).read()
            open(path, 'wb').write(diff)
            return n, len(diff), 'ok'
        except Exception as exc:
            if attempt == 2:
                return n, -1, 'ERR ' + str(exc)[:60]
            time.sleep(2 + attempt * 2)


started = time.time()
results = []
with ThreadPoolExecutor(max_workers=10) as executor:
    for index, result in enumerate(executor.map(fetch, nums), 1):
        results.append(result)
        if index % 25 == 0:
            print('  ...%d/%d %.0fs' % (index, len(nums), time.time() - started), flush=True)

ready = [result for result in results if result[2] in ('ok', 'cached')]
large = [result for result in ready if result[1] >= LARGE]
errors = [result for result in results if result[2].startswith('ERR')]
print('OK: %d | large>=100KB: %d | ERR: %d | %.0fs' % (
    len(ready), len(large), len(errors), time.time() - started))
print('large:', sorted(result[0] for result in large))
print('err:', sorted((result[0], result[2]) for result in errors))

final = sorted(result[0] for result in ready)
json.dump(final, open(FINAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('FINAL ready:', len(final))
