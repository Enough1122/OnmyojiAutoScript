#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Head-to-head mini-eval v2 (resumable, parallel): union-alpha vs deepseek-v4.1-flash.
Usage: python -u run_cmp2.py --models union-alpha[,deepseek-v4.1-flash]
Skips tasks whose raw response file already exists (resume). Writes per-task result JSONs."""

import argparse, concurrent.futures, json, os, random, re, subprocess, sys, tempfile, time, urllib.request, urllib.error

TMP = os.environ.get("LOCALAPPDATA", r"C:\Users\admin\AppData\Local")
ENVF = os.path.join(TMP, "hermes", ".env")
OUT = r"D:/Hermes/tmp/oa_cmp"
os.makedirs(OUT, exist_ok=True)


def log(line, model):
    with open(os.path.join(OUT, "run_%s.log" % model.replace("/", "_")), "a", encoding="utf-8") as f:
        f.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), line))
        f.flush()


def read_key(name):
    with open(ENVF, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(name + " not found")


GO_KEY = read_key("OPENCODE_GO_API_KEY")
BASE = "https://opencode.ai/zen/go/v1"


def call(model, prompt, max_tokens, api, tag):
    sess = "oa-cmp-%d-%s" % (int(time.time()), tag)
    if api == "anthropic":
        url = BASE + "/messages"
        body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
        headers = {"x-api-key": GO_KEY, "anthropic-version": "2023-06-01",
                   "content-type": "application/json", "user-agent": "hermes-eval/1.0",
                   "x-opencode-session": sess}
    else:
        url = BASE + "/chat/completions"
        body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
        headers = {"Authorization": "Bearer " + GO_KEY, "content-type": "application/json",
                   "user-agent": "hermes-eval/1.0", "x-opencode-session": sess}
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST", headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "text": e.read().decode("utf-8", "replace")[:300],
                "sec": round(time.time() - t0, 1)}
    except Exception as e:
        return {"ok": False, "status": "EXC", "text": str(e)[:300], "sec": round(time.time() - t0, 1)}
    sec = round(time.time() - t0, 1)
    if api == "anthropic":
        blocks = data.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
        return {"ok": True, "text": text, "sec": sec, "usage": data.get("usage"),
                "stop": data.get("stop_reason"),
                "blocks": [b.get("type") for b in blocks if isinstance(b, dict)]}
    ch = (data.get("choices") or [{}])[0]
    return {"ok": True, "text": (ch.get("message") or {}).get("content") or "", "sec": sec,
            "usage": data.get("usage"), "stop": ch.get("finish_reason")}


def extract_code(text):
    blocks = re.findall(r"```(?:python)?[ \t]*\r?\n(.*?)```", text, re.S)
    return blocks[-1] if blocks else text


def run_cand(code, harness, tag):
    fd, path = tempfile.mkstemp(prefix="cand_%s_" % tag, suffix=".py", dir=OUT)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code + "\n\n" + harness)
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=25, cwd=OUT)
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT(possible infinite loop)"
    out = ((p.stdout or "").strip() + " || " + (p.stderr or "").strip())
    return ("ALL_PASS" in (p.stdout or "")), out[-260:]


H1 = r'''
import random
def brute(s, k):
    best = 0
    for i in range(len(s)):
        seen = set()
        for j in range(i, len(s)):
            seen.add(s[j])
            if len(seen) > k: break
            best = max(best, j - i + 1)
    return best
def run_tests(fn):
    for s, k, exp in [("eceba",2,3),("aa",1,2),("abc",0,0),("",2,0),("aabacbebebe",3,7)]:
        got = fn(s, k)
        assert got == exp, "case %r,%r -> %r != %r" % (s, k, got, exp)
    random.seed(7)
    for _ in range(300):
        n = random.randint(0, 60)
        s = "".join(random.choice("abcd") for _ in range(n))
        k = random.randint(0, 3)
        got, exp = fn(s, k), brute(s, k)
        assert got == exp, "random %r,%r -> %r != %r" % (s, k, got, exp)
    print("ALL_PASS")
run_tests(longest_k_distinct)
'''

H2 = r'''
import random
def run_tests(fn):
    assert fn([], 5) == -1, "empty"
    assert fn([1], 1) == 0, "single hit"
    assert fn([1], 0) == -1, "single miss"
    random.seed(11)
    for n in range(1, 40):
        arr = sorted(random.randint(-20, 20) for _ in range(n))
        for x in range(-25, 25):
            got = fn(list(arr), x)
            if x in arr:
                assert isinstance(got, int) and 0 <= got < len(arr) and arr[got] == x, "bad idx for %r in %r" % (x, arr)
            else:
                assert got == -1, "false hit %r in %r" % (x, arr)
    print("ALL_PASS")
run_tests(bsearch)
'''

T3_TRUTH = [x for x in range(1000, 10000)
            if x % 7 == 3 and x % 11 == 5 and sum(int(c) for c in str(x)) % 8 == 0]
T4_EXPECT = {"city": "福州", "cat": "雪碧", "verified": True, "items": [1, 2, 3]}

P1 = ("Write a Python function `longest_k_distinct(s: str, k: int) -> int` returning the length of "
      "the longest substring of `s` that contains at most `k` distinct characters. Requirements: O(n) time; "
      "must handle k=0 (return 0) and empty strings. Output ONLY the code inside a single ```python code "
      "block. No explanation.")
P2 = ("The Python function below has a bug: it can loop forever. Fix it so it always terminates and returns "
      "the index of `x` (any one occurrence is fine) or -1 when absent. Keep it a binary search (O(log n)). "
      "Output ONLY the fixed code inside a single ```python code block. No explanation.\n\n"
      "```python\n"
      "def bsearch(a, x):\n"
      "    lo, hi = 0, len(a)\n"
      "    while lo < hi:\n"
      "        mid = (lo + hi) // 2\n"
      "        if a[mid] == x:\n"
      "            return mid\n"
      "        elif a[mid] < x:\n"
      "            lo = mid\n"
      "        else:\n"
      "            hi = mid\n"
      "    return -1\n"
      "```")
P3 = ("求 1000 到 9999 之间所有满足下面条件的整数：除以 7 余 3、除以 11 余 5、且各位数字之和能被 8 整除。"
      "只输出这些数字，用英文逗号分隔，不要任何其他文字。")
P4 = ("只输出一个 JSON 对象，不要任何其他文字、不要 markdown 代码块。字段：city 为字符串\"福州\"；"
      "cat 为字符串\"雪碧\"；verified 为布尔值 true；items 为整数数组 [3,1,2] 升序排列后的结果。")
P5 = "蜘蛛有 8 条腿，甲虫有 6 条腿，两种虫一共 18 只、合计 118 条腿。问蜘蛛有几只？只输出一个数字。"


def ck_code(name):
    def _ck(r):
        if not r.get("ok") or not (r.get("text") or "").strip():
            return False, "no output (status=%s stop=%s)" % (r.get("status"), r.get("stop"))
        code = extract_code(r["text"])
        if ("def %s" % name) not in code:
            return False, "function %s not found in output" % name
        return run_cand(code, H1 if name == "longest_k_distinct" else H2, name)
    return _ck


def ck_t3(r):
    if not r.get("ok") or not (r.get("text") or "").strip():
        return False, "no output (status=%s stop=%s)" % (r.get("status"), r.get("stop"))
    nums = [int(x) for x in re.findall(r"\d+", r["text"])]
    got, truth = set(nums), set(T3_TRUTH)
    if got == truth:
        return True, "exact set match (%d numbers)" % len(truth)
    miss = sorted(truth - got)[:8]
    extra = sorted(got - truth)[:8]
    return False, "got %d, truth %d; missing %s; extra %s" % (len(got), len(truth), miss, extra)


def ck_t4(r):
    if not r.get("ok") or not (r.get("text") or "").strip():
        return False, "no output (status=%s stop=%s)" % (r.get("status"), r.get("stop"))
    t = r["text"].strip()
    try:
        d = json.loads(t)
    except Exception as e:
        return False, "not plain JSON: %s | head=%r" % (e, t[:90])
    return (d == T4_EXPECT), json.dumps(d, ensure_ascii=False)[:140]


def ck_t5(r):
    if not r.get("ok") or not (r.get("text") or "").strip():
        return False, "no output (status=%s stop=%s)" % (r.get("status"), r.get("stop"))
    nums = re.findall(r"\d+", r["text"])
    return (bool(nums) and int(nums[-1]) == 5), "answer tail=%r" % (r["text"][-60:])


TASKS = [
    {"id": "t1_code_sliding", "prompt": P1, "max_tokens": 3000, "check": ck_code("longest_k_distinct")},
    {"id": "t2_bugfix_bsearch", "prompt": P2, "max_tokens": 3000, "check": ck_code("bsearch")},
    {"id": "t3_crt_numbers", "prompt": P3, "max_tokens": 4000, "check": ck_t3},
    {"id": "t4_json_strict", "prompt": P4, "max_tokens": 2500, "check": ck_t4},
    {"id": "t5_word_problem", "prompt": P5, "max_tokens": 2500, "check": ck_t5},
]

API_OF = {"union-alpha": "anthropic", "deepseek-v4.1-flash": "openai"}


def run_task(m, t):
    tag = "%s__%s" % (m.replace("/", "_"), t["id"])
    rawpath = os.path.join(OUT, tag + ".txt")
    if os.path.exists(rawpath):
        try:
            r = json.load(open(rawpath, encoding="utf-8"))
            log("%s: reuse cached raw" % tag, m)
        except Exception:
            r = call(m, t["prompt"], t["max_tokens"], API_OF[m], t["id"])
    else:
        log("%s: calling (%s, max_tokens=%d)" % (tag, API_OF[m], t["max_tokens"]), m)
        r = call(m, t["prompt"], t["max_tokens"], API_OF[m], t["id"])
        with open(rawpath, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    try:
        ok, note = t["check"](r)
    except Exception as e:
        ok, note = False, "checker error: %s" % e
    res = {"model": m, "task": t["id"], "ok": ok, "note": note, "sec": r.get("sec"),
           "usage": r.get("usage"), "stop": r.get("stop"), "blocks": r.get("blocks"),
           "text_head": (r.get("text") or "")[:150].replace("\n", " ")}
    with open(os.path.join(OUT, "result_%s.json" % tag), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    log("%s: ok=%s sec=%s note=%s" % (tag, ok, r.get("sec"), note[:140]), m)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="union-alpha,deepseek-v4.1-flash")
    args = ap.parse_args()
    models = [x.strip() for x in args.models.split(",") if x.strip()]
    all_res = []
    for m in models:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            futs = [ex.submit(run_task, m, t) for t in TASKS]
            for fu in concurrent.futures.as_completed(futs):
                all_res.append(fu.result())
        summ = {"model": m, "passed": sum(1 for r in all_res if r["model"] == m and r["ok"]), "of": len(TASKS),
                "results": [r for r in all_res if r["model"] == m]}
        with open(os.path.join(OUT, "summary_%s.json" % m.replace("/", "_")), "w", encoding="utf-8") as f:
            json.dump(summ, f, ensure_ascii=False, indent=1)
        log("MODEL DONE %s: %d/%d" % (m, summ["passed"], summ["of"]), m)
        print("MODEL DONE %s: %d/%d" % (m, summ["passed"], summ["of"]), flush=True)
    print(json.dumps(all_res, ensure_ascii=False, indent=1), flush=True)


if __name__ == "__main__":
    main()
