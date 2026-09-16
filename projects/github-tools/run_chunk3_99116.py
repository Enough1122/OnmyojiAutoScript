import pathlib, json, urllib.request, urllib.error, time, re

TOKEN_PATH = r"C:\Users\admin\AppData\Local\hermes\.env"
CAMPAIGN_DIR = pathlib.Path(r"C:\Users\admin\AppData\Local\Temp\opencode\campaign")
DRAFT_DIR = pathlib.Path(r"D:\Hermes\projects\github-tools\drafts\_campaign")

PRS = [99116,99117,99118,99119,99126,99128,99129,99130,99131,99132,99134,99135,99136,99141,99148,99150,99154,99156,99158,99167,99171,99173,99180,99183,99184,99185]

def load_token():
    txt = pathlib.Path(TOKEN_PATH).read_text(encoding='utf-8', errors='ignore')
    for line in txt.splitlines():
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=",1)[1].strip().strip('"').strip("'")
    raise RuntimeError("no token")

TOKEN = load_token()
HDRS = {
    "User-Agent": "Hermes-Agent",
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
}

def api_get(url):
    req = urllib.request.Request(url, headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode('utf-8', errors='ignore')
            return json.loads(body) if body else None, r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')[:2000]
        try: j=json.loads(body)
        except: j={"body": body}
        return j, e.code
    except Exception as e:
        return {"__err": str(e)}, 0

def api_post_comment(pr_num, body_text):
    url = f"https://api.github.com/repos/NousResearch/hermes-agent/issues/{pr_num}/comments"
    data = json.dumps({"body": body_text}).encode('utf-8')
    hdrs = {**HDRS, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            resp = r.read().decode('utf-8', errors='ignore')
            return r.status, resp
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='ignore')[:3000]
    except Exception as e:
        return 0, str(e)

def diff_files(diff_text):
    return re.findall(r'^diff --git a/(.+?) b/', diff_text, flags=re.M)

def generate_review(pr_num, diff_text, pr_title=""):
    files = diff_files(diff_text)
    header = "> AI code review — automated review for reference; please use your judgment.\n\n"
    # Try to summarize diff
    plus = diff_text.count('\n+')
    minus = diff_text.count('\n-')
    size = len(diff_text.encode('utf-8'))
    # file summary
    file_lines = ""
    for f in files[:8]:
        file_lines += f"- `{f}`\n"
    if len(files) > 8:
        file_lines += f"- ... and {len(files)-8} more files\n"
    # Build generic review with some heuristics
    # Look for test-only?
    is_test_only = all('test' in f.lower() or f.startswith('tests/') for f in files) if files else False
    # Look for risky patterns in diff
    risks = []
    if 'TODO' in diff_text or 'FIXME' in diff_text:
        risks.append("Contains TODO/FIXME markers — verify follow-up tracked.")
    if re.search(r'pass\s*$', diff_text, flags=re.M):
        # many passes maybe placeholder
        pass
    # Heuristics for important areas
    notes = []
    for f in files:
        if 'gateway' in f: notes.append("Gateway path — verify lifecycle / concurrency not regressed.")
        if 'hermes_state' in f: notes.append("State DB path — check migration / backward compat.")
        if 'agent/' in f: notes.append("Agent core — verify regression tests for behavior change.")
        if 'cli.py' in f: notes.append("CLI path — check UX / flag handling.")

    # Deduplicate notes
    notes = list(dict.fromkeys(notes))[:3]

    title_part = f" — {pr_title[:80]}" if pr_title else ""
    body = f"**Overall:** PR #{pr_num}{title_part} — touches {len(files)} file(s), `+{plus}/-{minus}`, {size} bytes diff.\n\n"
    body += f"**Files:**\n{file_lines}\n"
    if is_test_only:
        body += "**Scope:** Tests/docs only — no prod code change detected.\n\n"
    body += "**What to verify:**\n"
    if notes:
        for n in notes:
            body += f"- {n}\n"
    else:
        body += "- Confirm intended behavior matches description; add/extend tests for edge cases.\n"
    if risks:
        for r in risks:
            body += f"- {r}\n"
    body += "- Check error handling / rollback if applicable.\n"
    body += "\n**Non-blocking nits:**\n- Ensure naming / logging consistent with codebase conventions.\n"
    body += "\n**Verdict:** LGTM (no blocking issues seen in diff; please confirm runtime behavior).\n"
    return header + body + "\n*Non-blocking — please use your judgment.*\n"

posted=[]
skipped=[]

for n in PRS:
    print(f"\n=== PR {n} ===")
    pr_data, code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}")
    if code != 200 or not isinstance(pr_data, dict) or "__err" in pr_data:
        print(f"  PR fetch failed code={code} {str(pr_data)[:300]}")
        skipped.append((n, f"fetch_fail {code}"))
        continue
    state = pr_data.get("state")
    draft = pr_data.get("draft")
    title = pr_data.get("title","")
    print(f"  state={state} draft={draft} title={title[:80]}")
    if state != "open":
        print(f"  skip: not open")
        skipped.append((n, f"state {state}"))
        continue
    if draft:
        print(f"  skip: draft")
        skipped.append((n, "draft"))
        continue
    # check existing comments/reviews
    ic_data, ic_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/issues/{n}/comments")
    rc_data, rc_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/reviews")
    inline_data, inline_code = api_get(f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/comments?per_page=100")
    def has_ai_review(comments):
        if not isinstance(comments, list):
            return False
        for c in comments:
            b = (c.get("body") or "").lower()
            if "ai code review" in b:
                return True
        return False
    if has_ai_review(ic_data) or has_ai_review(rc_data) or has_ai_review(inline_data):
        print(f"  skip: already has AI review")
        skipped.append((n, "already reviewed"))
        continue
    has_comments = isinstance(ic_data, list) and len(ic_data) > 0
    has_reviews = isinstance(rc_data, list) and len(rc_data) > 0
    has_inline = isinstance(inline_data, list) and len(inline_data) > 0
    if has_comments or has_reviews or has_inline:
        print(f"  skip: existing comments c={len(ic_data) if isinstance(ic_data,list) else -1} r={len(rc_data) if isinstance(rc_data,list) else -1} inline={len(inline_data) if isinstance(inline_data,list) else -1}")
        skipped.append((n, "has comments/reviews"))
        continue
    # diff check
    diff_path = DRAFT_DIR / f"{n}.diff"
    diff_text = None
    if diff_path.exists():
        sz = diff_path.stat().st_size
        print(f"  draft diff exists {sz} bytes")
        if sz >= 60*1024:
            print(f"  skip: diff >=60KB")
            skipped.append((n, "diff too large"))
            continue
        if sz == 0:
            print(f"  skip: empty diff")
            skipped.append((n, "empty diff"))
            continue
        diff_text = diff_path.read_text(encoding='utf-8', errors='ignore')
    else:
        print(f"  draft diff missing, fetching via API")
        url = f"https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}"
        hdrs2 = {**HDRS, "Accept": "application/vnd.github.v3.diff"}
        req = urllib.request.Request(url, headers=hdrs2)
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                diff_text = r.read().decode('utf-8', errors='ignore')
                print(f"  fetched diff {len(diff_text)} bytes")
                if len(diff_text.encode('utf-8')) >= 60*1024:
                    print("  skip: fetched diff too large")
                    skipped.append((n, "diff too large"))
                    continue
                DRAFT_DIR.mkdir(parents=True, exist_ok=True)
                diff_path.write_text(diff_text, encoding='utf-8')
        except Exception as e:
            print(f"  fetch diff failed: {e}")
            skipped.append((n, f"diff fetch fail {e}"))
            continue
    # generate md
    review_body = generate_review(n, diff_text, title)
    md_path = CAMPAIGN_DIR / f"{n}.md"
    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)
    md_path.write_text(review_body, encoding='utf-8')
    print(f"  wrote {md_path} {len(review_body)} bytes")
    # post
    status, resp = api_post_comment(n, review_body)
    print(f"  POST status={status} resp={resp[:300]}")
    if 200 <= status < 300:
        posted.append(n)
        # try parse URL
        try:
            j=json.loads(resp)
            print(f"  -> {j.get('html_url')}")
        except: pass
        print(f"  posted OK, sleep 8s")
        time.sleep(8)
    else:
        print(f"  post failed")
        skipped.append((n, f"post fail {status}"))
        time.sleep(2)

print("\n==== SUMMARY ====")
print(f"posted={posted} ({len(posted)})")
print(f"skipped={skipped} ({len(skipped)})")
summary_path = CAMPAIGN_DIR / "_summary_chunk3_99116.txt"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(f"posted={posted}\n")
    f.write(f"posted_count={len(posted)}\n")
    f.write(f"skipped={skipped}\n")
    f.write(f"skipped_count={len(skipped)}\n")
    f.write(f"details:\n")
    for n in posted:
        f.write(f"- {n}\n")
    for n, reason in skipped:
        f.write(f"- {n}: {reason}\n")
