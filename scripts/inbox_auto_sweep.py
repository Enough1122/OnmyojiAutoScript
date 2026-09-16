# -*- coding: utf-8 -*-
"""GitHub 收件箱自动清理(cron 任务,由 Hermes 调度器按 cron 表达式拉起)

分类规则(经 2026-08-23 全量人工校准):
  KEEP  - 自己的 PR 上有动态 / 最新评论 @Enough1122 / 直接向我们提问 / 内容实质但无法确定意图
  DELETE- 致谢与修复告知、disposition 收条、CI 状态播报、已合并/关闭摘要、
          自己评论的回声、无正文的推送事件等纯告知类

同一线程只提醒一次(state 文件记录已提醒的 thread id;有新活动会再次提醒)。

用法:
  python inbox_auto_sweep.py            # 正常清理
  python inbox_auto_sweep.py --dry-run  # 只分类不删除

传输层说明(2026-08-23):全部走 gh CLI(`gh api`)。.env 的 GITHUB_TOKEN 对通知
只有读权限,线程级 PUT/PATCH/DELETE 一律 404;gh CLI(classic token,notifications
scope)下 DELETE 与集合级 PUT 实测可用(线程级 PUT 仍为 GitHub 侧 404 怪癖,本脚本未用)。
"""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

ME = 'Enough1122'
BASE = 'https://api.github.com'
STATE_PATH = r'D:\Hermes\projects\github-tools\drafts\_inbox_sweep_state.json'
LOG_PATH = r'D:\Hermes\projects\github-tools\drafts\_inbox_sweep_log.jsonl'
OWN_PRS_ALERT_ALWAYS = {66926, 75476, 70725, 81108, 81174, 81231, 80785, 81530, 91984, 82211}

_consec_rl = 0

def _api(url, method='GET', paginate=False):
    """单次 gh api 调用。返回 (ok, json_or_errmsg)。空响应体 -> {}。"""
    endpoint = url.split('api.github.com', 1)[-1]
    cmd = ['gh', 'api']
    if method != 'GET':
        cmd += ['-X', method]
    cmd.append(endpoint)
    if paginate:
        cmd.append('--paginate')
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=120)
    if p.returncode != 0:
        return False, (p.stderr or '').strip()
    raw = p.stdout.strip()
    if not raw:
        return True, {}
    try:
        return True, json.loads(raw)
    except ValueError:
        # --paginate 多页输出是逐页拼接的 JSON 数组文本,手动合并
        decoder = json.JSONDecoder()
        items, pos = [], 0
        while pos < len(raw):
            obj, end = decoder.raw_decode(raw, pos)
            items.extend(obj if isinstance(obj, list) else [obj])
            nxt = raw.find('\n', end)
            if nxt == -1:
                break
            pos = nxt
        return True, items

def g(url, method='GET'):
    """带退避的 API 调用:403/429 等 60s 重试,连续 3 次失败放弃本轮(不动收件箱)。"""
    global _consec_rl
    for attempt in range(3):
        ok, data = _api(url, method)
        if ok:
            _consec_rl = 0
            return data
        msg = str(data)
        if ('403' in msg or '429' in msg) and attempt < 2:
            time.sleep(60 * (attempt + 1))
            continue
        _consec_rl += 1
        if _consec_rl >= 3:
            print(f'SILENT (api 连续失败,{msg[:80]})')
            sys.exit(0)
        return {'__error__': msg[:150]}
    return {'__error__': 'unreachable'}

def g_all(url):
    ok, data = _api(url, paginate=True)
    if not ok:
        print(f'SILENT (fetch failed: {str(data)[:80]})')
        sys.exit(0)
    return data if isinstance(data, list) else [data]

ASK_RE = re.compile(r'@Enough1122|could you|can you|please take a look|any update|thoughts\?|\?\s*$', re.I)
ACK_RE = re.compile(
    r'thanks (for|—|--) the review|addressed|resolved all|fixed in|pushed|disposition|'
    r'no change required|no changes needed|informational only|final disposition|'
    r'follow-up (pushed|commit)|rebased and updated|acted on point', re.I)

def load_state():
    try:
        return json.load(open(STATE_PATH, encoding='utf-8'))
    except Exception:
        return {}

def save_state(st):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    json.dump(st, open(STATE_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def main():
    dry = '--dry-run' in sys.argv
    notifs = g_all(BASE + '/notifications?per_page=100')
    if not isinstance(notifs, list):
        print('SILENT (notifications fetch failed)')
        return

    urls = sorted({n['subject'].get('url') for n in notifs if n['subject'].get('url')})
    lcus = sorted({n['subject'].get('latest_comment_url') for n in notifs
                   if n['subject'].get('latest_comment_url')})
    with ThreadPoolExecutor(max_workers=12) as ex:
        subj = dict(zip(urls, ex.map(g, urls)))
    with ThreadPoolExecutor(max_workers=12) as ex:
        lcs = dict(zip(lcus, ex.map(g, lcus)))

    state = load_state()
    keep, deleted = [], []

    for n in notifs:
        s = n['subject']
        tid = n['id']
        si = subj.get(s.get('url')) or {}
        num = si.get('number')
        pr_author = (si.get('user') or {}).get('login') if s['type'] == 'PullRequest' else None
        ld = lcs.get(s.get('latest_comment_url')) or {}
        lc_user = (ld.get('user') or {}).get('login') if isinstance(ld, dict) else None
        body = (ld.get('body') or '')[:1000] if isinstance(ld, dict) else ''
        row = {'repo': n['repository']['full_name'], 'num': num,
               'title': (s['title'] or '')[:70], 'pr_author': pr_author,
               'state': si.get('state'), 'last_by': lc_user, 'updated': n['updated_at'][:16],
               'url': (ld.get('html_url') if isinstance(ld, dict) else '') or ''}

        if pr_author == ME:
            row['why'] = 'own-pr' + ('(top10)' if num in OWN_PRS_ALERT_ALWAYS else '')
            keep.append(row)
        elif lc_user == ME:
            row['why'] = 'self-echo'
            deleted.append(row)
        elif body and ASK_RE.search(body):
            row['why'] = 'asked-directly'
            keep.append(row)
        elif body and ACK_RE.search(body):
            row['why'] = 'ack-note'
            deleted.append(row)
        elif not body.strip():
            row['why'] = 'event-no-body'
            deleted.append(row)
        else:
            row['why'] = 'unclassified-keep'
            keep.append(row)

    # 只对"新活动或未提醒过"的 keep 项提醒
    fresh_keep = [r for r in keep
                  if state.get(str(r['num']) + r['title'][:20]) != r['updated']]

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    if not fresh_keep:
        print(f'SILENT ({len(notifs)} unread, all informational)'
              + ('' if not notifs else f'; swept {len(deleted)}'))
    else:
        print(f'[inbox] {len(notifs)} 未读,需关注 {len(fresh_keep)} 条:')
        for r in fresh_keep:
            print(f"  - [{r['why']}] {r['repo']} #{r['num']} ({r['pr_author']}) {r['title']}")
            if r.get('url'):
                print(f'    {r["url"]}')
        if deleted:
            print(f'(另自动清理纯告知类 {len(deleted)} 条)')

    # 实际执行删除(需要 thread id,重新匹配)
    del_map = {}
    for n in notifs:
        s = n['subject']
        si = subj.get(s.get('url')) or {}
        key = (si.get('number'), (s.get('title') or '')[:70])
        del_map[key] = n['id']

    if not dry:
        ok = fail = 0
        for r in deleted:
            tid = del_map.get((r['num'], r['title']))
            if not tid:
                continue
            try:
                g(BASE + f'/notifications/threads/{tid}', 'DELETE')
                ok += 1
            except Exception:
                fail += 1
            time.sleep(0.2)
        for r in keep:
            state[str(r['num']) + r['title'][:20]] = r['updated']
        keys_alive = {str(r['num']) + r['title'][:20] for r in keep}
        for k in list(state):
            if k not in keys_alive and len(state) > 200:
                del state[k]
        save_state(state)
        log_rec = {'ts': now, 'unread': len(notifs), 'kept': len(keep),
                   'fresh_kept': len(fresh_keep), 'deleted': len(deleted),
                   'del_ok': ok, 'del_fail': fail, 'dry': False}
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_rec, ensure_ascii=False) + '\n')
        if deleted:
            print(f'[sweep] 已清理 {ok} 条(fail {fail}),日志 -> {os.path.basename(LOG_PATH)}')
    else:
        print(f'[dry-run] 将保留 {len(keep)} 条 / 清理 {len(deleted)} 条')

if __name__ == '__main__':
    main()
