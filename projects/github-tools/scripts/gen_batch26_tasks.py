# -*- coding: utf-8 -*-
"""一次性:生成 batch26 剩余 19 条 PR 的子代理 prompt 文件 _batch26_tasks19.json"""
import json

BRIEF = r'D:\Hermes\projects\github-tools\AGENT-BRIEF-batch26.md'
TODO = r'D:\Hermes\projects\github-tools\drafts\_batch26_todo19.json'
OUT = r'D:\Hermes\projects\github-tools\drafts\_batch26_tasks19.json'

brief = open(BRIEF, encoding='utf-8').read()
todo = json.load(open(TODO, encoding='utf-8'))
tasks = []
for n_str, info in todo.items():
    n = int(n_str)
    pre = 'apply_ok=%s mergeable_state=%s files=%d' % (info['apply_ok'], info['mergeable'], info['files'])
    if not info['apply_ok']:
        pre += ' → 补丁基于旧版 main,按"机械 rebase"快审(看改动意图与明显冲突即可,不必深读语义),note 注明基于旧 main'
    if info['pairs']:
        pre += '; 配对预警:与 %s 共享文件、只能落一个,结论必须写明' % info['pairs']
    if n in (117749, 117765):
        pre += ';另:配对对象 #117777 已因已有他人 review 被 SKIP,本条独立审'
    tasks.append(brief + (
        '\n\n## 本任务(PR %d)\n'
        '- diff: D:\\Hermes\\projects\\github-tools\\drafts\\_campaign\\%d.diff(先核对文件头确为 PR %d 的改动)\n'
        '- verdict 写入: D:\\Hermes\\projects\\github-tools\\drafts\\_verdict_batch26_%d.json\n'
        '- 草稿(仅 v=DRAFT 时): C:\\Users\\admin\\AppData\\Local\\Temp\\opencode\\campaign\\%d.md\n'
        '- 预检(已跑,勿重跑): %s\n'
        '- 活检:先 gh api repos/NousResearch/hermes-agent/pulls/%d 确认仍 open 且非 draft;'
        '已关/已有他人 review 或 issue 评论 → SKIP_STALE(note 写原因)\n'
        % (n, n, n, n, n, pre, n)))
json.dump(tasks, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('tasks:', len(tasks), 'total chars:', sum(len(t) for t in tasks))
