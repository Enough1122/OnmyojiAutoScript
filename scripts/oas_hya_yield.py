"""Aggregate Hyakkiyakou yield per ticket from the OAS log, without screenshots.

The task itself logs no reward data (the only OCR asset is O_BEAN_NUMBER, which
reads the bean counter). What it *does* log is every shikigami the agent locked
onto, as `Focus changed, now: <name>`. Those names come from the same oashya label
table that grades rarity, so rarity distribution per ticket can be reconstructed
from the log alone.

A ticket boundary is `Hyakkiyakou End` (or the `count: N/M` line that follows).
"""
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, r'D:/Hermes/repos/OAS')
from oashya.labels import CLASSINDEX as CI  # noqa: E402

FOCUS_RE = re.compile(r'^\S+ \S+ \|\s+agent\.py:\d+ \|\s+INFO \| Focus changed, now: (.+?)\s*$')
COUNT_RE = re.compile(r'^\S+ \S+ \|\s+script_task\.py:\d+ \|\s+INFO \| count: (\d+)/(\d+)\s*$')
BUFF_RE = re.compile(r'^\S+ \S+ \|\s+agent\.py:\d+ \|\s+INFO \| Focus changed, now: (.+?)\s*$')
BUFF_NAMES = {'好友UP', '概率UP', '式神减速', '砸豆加速', '冰冻'}

NAME_TO_RARITY = {}
for _i in range(0, 300):
    try:
        from oashya.labels import id2name
        _n = id2name(_i)
    except Exception:
        continue
    if not _n or _n == '?':
        continue
    if CI.MIN_SP <= _i <= CI.MAX_SP:
        NAME_TO_RARITY[_n] = 'SP'
    elif CI.MIN_SSR <= _i <= CI.MAX_SSR:
        NAME_TO_RARITY[_n] = 'SSR'
    elif CI.MIN_SR <= _i <= CI.MAX_SR:
        NAME_TO_RARITY[_n] = 'SR'
    elif CI.MIN_R <= _i <= CI.MAX_R:
        NAME_TO_RARITY[_n] = 'R'
    elif CI.MIN_N <= _i <= CI.MAX_N:
        NAME_TO_RARITY[_n] = 'N'
    elif CI.MIN_G <= _i <= CI.MAX_G:
        NAME_TO_RARITY[_n] = 'G'


def parse(path, since_line=0):
    tickets = []
    cur = None
    with open(path, encoding='utf-8', errors='replace') as fh:
        for idx, line in enumerate(fh, 1):
            if idx <= since_line:
                continue
            m = BUFF_RE.match(line)
            if m:
                name = m.group(1)
                if cur is None:
                    cur = {'line': idx, 'targets': Counter(), 'buffs': Counter()}
                if name in BUFF_NAMES:
                    cur['buffs'][name] += 1
                else:
                    cur['targets'][name] += 1
                continue
            m = COUNT_RE.match(line)
            if m and cur is not None:
                cur['n'] = int(m.group(1))
                cur['of'] = int(m.group(2))
                tickets.append(cur)
                cur = None
    return tickets


def main():
    log = Path(sys.argv[1] if len(sys.argv) > 1 else r'D:/Hermes/repos/OAS/log/2026-09-26_oas.txt')
    since = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    tickets = parse(log, since)
    if not tickets:
        print('no completed tickets found')
        return

    print(f'log={log.name}  since_line={since}  tickets={len(tickets)}')
    print()
    hdr = f'{"#":>3} {"rare seen (unique)":<46} {"N":>3} {"R":>3} {"SR":>3} {"SSR":>3} {"SP":>3} {"buffs":<12}'
    print(hdr)
    print('-' * len(hdr))
    tot = Counter()
    for t in tickets:
        c = Counter()
        unknown = []
        for name, n in t['targets'].items():
            r = NAME_TO_RARITY.get(name)
            if r is None:
                unknown.append(name)
            else:
                c[r] += n
        tot.update(c)
        rare = ', '.join(f'{r}{c[r]}' for r in ('SSR', 'SP') if c[r])
        if unknown:
            rare += ('  ?' + ','.join(unknown[:3])) if rare else '?' + ','.join(unknown[:3])
        buffs = ','.join(f'{b}x{k}' for b, k in t['buffs'].items()) or '-'
        print(f'{t.get("n", "?"):>3} {rare[:46]:<46} {c["N"]:>3} {c["R"]:>3} {c["SR"]:>3} {c["SSR"]:>3} {c["SP"]:>3} {buffs:<12}')
    print('-' * len(hdr))
    print(f'{"TOT":>3} {"":<46} {tot["N"]:>3} {tot["R"]:>3} {tot["SR"]:>3} {tot["SSR"]:>3} {tot["SP"]:>3}')
    rare_tickets = sum(1 for t in tickets
                       if any(NAME_TO_RARITY.get(n) in ('SSR', 'SP') for n in t['targets']))
    print()
    print(f'tickets with any SSR/SP target locked: {rare_tickets}/{len(tickets)}')


if __name__ == '__main__':
    main()
