# -*- coding: utf-8 -*-
"""post_batch.py <n1> <n2> ... [--workers=K] — post many AI review comments concurrently.

Same per-PR guarantees as post_one.py (SOP header, liveness re-check, Enough1122 dedupe),
but runs the whole batch through a thread pool with **no inter-post sleeps**
(2026-09-21 user ruling: 先别考虑限流,触发了再说 — deal with 403/429 if it actually fires).

Prints one line per PR (ascending), then a summary line.
Exit codes: 0 = at least one POSTED/SKIP | 3 = every PR errored | 2 = bad usage.
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import post_one  # noqa: E402


def _one(n):
    try:
        return n, post_one.post(n, 0.0)
    except Exception as e:  # noqa: BLE001
        return n, 'ERR %d %s' % (n, str(e)[:140])


def main():
    nums = []
    workers = int(os.environ.get('POST_WORKERS', '4'))
    for a in sys.argv[1:]:
        if a.startswith('--workers='):
            workers = int(a.split('=', 1)[1])
        elif a.startswith('--'):
            continue
        else:
            nums.append(int(a))
    if not nums:
        print('usage: post_batch.py <n1> <n2> ... [--workers=K]')
        return 2

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        out = list(ex.map(_one, nums))

    posted = skip = err = 0
    for n, st in sorted(out):
        print(st, flush=True)
        if st.startswith('POSTED'):
            posted += 1
        elif st.startswith('SKIP'):
            skip += 1
        else:
            err += 1
    print('summary: posted=%d skip=%d err=%d (workers=%d)' % (posted, skip, err, workers))
    if posted == 0 and skip == 0:
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
