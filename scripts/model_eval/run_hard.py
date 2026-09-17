#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hard-mode mini-eval v3: union-alpha vs deepseek-v4.1-flash.
7 tasks, all mechanically checkable. Usage: python -u run_hard.py --models union-alpha[,...]
"""
import argparse, concurrent.futures, json, os, random, re, subprocess, sys, tempfile, time, urllib.request, urllib.error

TMP = os.environ.get("LOCALAPPDATA", r"C:\Users\admin\AppData\Local")
ENVF = os.path.join(TMP, "hermes", ".env")
OUT = r"D:/Hermes/tmp/oa_hard"
os.makedirs(OUT, exist_ok=True)

REF_BF_SRC = r'''
def _ref_bf(code, inp):
    cells = [0] * 30000
    ptr = 0
    out = []
    inp = list(inp)
    bmap = {}
    stack = []
    for i, c in enumerate(code):
        if c == '[':
            stack.append(i)
        elif c == ']':
            j = stack.pop()
            bmap[i] = j
            bmap[j] = i
    ip = 0
    steps = 0
    while ip < len(code):
        steps += 1
        if steps > 5000000:
            raise RuntimeError("reference step limit exceeded")
        c = code[ip]
        if c == '>':
            ptr = (ptr + 1) % 30000
        elif c == '<':
            ptr = (ptr - 1) % 30000
        elif c == '+':
            cells[ptr] = (cells[ptr] + 1) % 256
        elif c == '-':
            cells[ptr] = (cells[ptr] - 1) % 256
        elif c == '.':
            out.append(chr(cells[ptr]))
        elif c == ',':
            cells[ptr] = ord(inp.pop(0)) if inp else 0
        elif c == '[':
            if cells[ptr] == 0:
                ip = bmap[ip]
        elif c == ']':
            if cells[ptr] != 0:
                ip = bmap[ip]
        ip += 1
    return "".join(out)
'''

HELLO = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."

H_BF = REF_BF_SRC + r'''
def run_tests(fn):
    hello = __HELLO__
    assert _ref_bf(hello, "") == "Hello World!\n", "REF HELLO BROKEN: %r" % _ref_bf(hello, "")
    cases = [
        (hello, ""),
        (",[.,]", "abc"),
        (",[.,]", ""),
        ("++[>+++<-]>.", ""),
        ("+[+].", ""),
        ("++++[>++++[>++++<-]<-]>>.", ""),
    ]
    for prog, inp in cases:
        exp = _ref_bf(prog, inp)
        got = fn(prog, inp)
        assert got == exp, "BF case failed: prog=%r... inp=%r got=%r exp=%r" % (prog[:30], inp, got[:60], exp[:60])
    print("ALL_PASS")
run_tests(bf)
'''.replace("__HELLO__", repr(HELLO))

REF_RE_SRC = r'''
def _ref_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(2, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '*':
                dp[i][j] = dp[i][j - 2] or (dp[i - 1][j] and (p[j - 2] == s[i - 1] or p[j - 2] == '.'))
            else:
                dp[i][j] = dp[i - 1][j - 1] and (p[j - 1] == s[i - 1] or p[j - 1] == '.')
    return dp[m][n]
'''

FIXED_RE = [
    ("aa", "a", False), ("aa", "a*", True), ("ab", ".*", True), ("aab", "c*a*b", True),
    ("mississippi", "mis*is*p*.", False), ("ab", ".*c", False), ("aa", "a*a", True),
    ("", ".*", True), ("", "a*", True), ("a", "", False), ("aaa", "a*a*a*", True),
    ("a", "a*b*", True), ("abc", "a.c", True), ("aaa", "aaaa", False), ("abcd", "d*", False),
    ("", "", True), ("a", ".*..a*", False),
]

H_RE = REF_RE_SRC + r'''
import random
FIXED = __FIXED__

def run_tests(fn):
    for s, p, exp in FIXED:
        got = fn(s, p)
        assert got == exp, "regex fixed failed: %r %r got %r exp %r" % (s, p, got, exp)
    random.seed(13)
    atoms = ["a", "b", "."]
    for _ in range(300):
        s = "".join(random.choice("ab") for _ in range(random.randint(0, 14)))
        toks = []
        for _ in range(random.randint(0, 6)):
            toks.append(random.choice(atoms))
            if random.random() < 0.5:
                toks.append("*")
        p = "".join(toks)
        exp = _ref_match(s, p)
        got = fn(s, p)
        assert got == exp, "regex random failed: %r %r got %r exp %r" % (s, p, got, exp)
    s = "a" * 20
    p = "a*a*a*a*a*a*a*a*a*a*a*b"
    exp = _ref_match(s, p)
    got = fn(s, p)
    assert got == exp, "regex stress failed: got %r exp %r" % (got, exp)
    print("ALL_PASS")
run_tests(is_match)
'''.replace("__FIXED__", repr(FIXED_RE))


def log(line, model):
    with open(os.path.join(OUT, "run3_%s.log" % model.replace("/", "_")), "a", encoding="utf-8") as f:
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
    sess = "oa-hard-%d-%s" % (int(time.time()), tag)
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
        with urllib.request.urlopen(req, timeout=180) as r:
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


def extract_code(text, fname):
    blocks = re.findall(r"```(?:python)?[ \t]*\r?\n(.*?)```", text or "", re.S)
    for b in reversed(blocks):
        if "def %s" % fname in b:
            return b
    return text or ""


def run_cand(code, harness, tag):
    fd, path = tempfile.mkstemp(prefix="cand_%s_" % tag, suffix=".py", dir=OUT)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code + "\n\n" + harness)
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=40, cwd=OUT)
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT(possible infinite loop / too slow)"
    out = ((p.stdout or "").strip() + " || " + (p.stderr or "").strip())
    return ("ALL_PASS" in (p.stdout or "")), out[-260:]


def ck_code(fname, harness):
    def _ck(r):
        if not r.get("ok") or not (r.get("text") or "").strip():
            return False, "no output (status=%s stop=%s)" % (r.get("status"), r.get("stop"))
        code = extract_code(r["text"], fname)
        if ("def %s" % fname) not in code:
            return False, "function %s not found in output" % fname
        return run_cand(code, harness, fname)
    return _ck


def ck_number(truth):
    def _ck(r):
        if not r.get("ok") or not (r.get("text") or "").strip():
            return False, "no output (status=%s stop=%s)" % (r.get("status"), r.get("stop"))
        nums = [int(x) for x in re.findall(r"\d+", r["text"])]
        if not nums:
            return False, "no number in output: %r" % r["text"][:80]
        ok = nums[-1] == truth
        note = "last=%d truth=%d" % (nums[-1], truth)
        if len(nums) > 1:
            note += " (extra numbers in text: %d)" % len(nums)
        return ok, note
    return _ck


# ---- ground truths ----
def truth_coins(target=400, coins=(1, 3, 4, 7, 13, 29, 71, 127)):
    dp = [0] * (target + 1)
    dp[0] = 1
    for c in coins:
        for v in range(c, target + 1):
            dp[v] += dp[v - c]
    return dp[target]


def truth_kaprekar():
    cnt = 0
    for n in range(1000, 10000):
        if len(set(str(n))) < 2:
            continue
        x, steps = n, 0
        while x != 6174 and steps < 20:
            d = "".join(sorted(str(x).zfill(4)))
            x = int(d[::-1]) - int(d)
            steps += 1
        if steps == 7:
            cnt += 1
    return cnt


def build_listsum(n=300):
    vals = [(i, (i * 137 + (i * i) % 97) % 1000) for i in range(1, n + 1)]
    truth = sum(v for k, (i, v) in enumerate(vals) if k > 0 and v > vals[k - 1][1])
    lines = "\n".join("%d,%d" % t for t in vals)
    return lines, truth


LINES, TRUTH_LS = build_listsum()
TRUTH_D17 = "142857"[(10000 - 1) % 6]
TRUTH_BIG = sum(int(c) for c in str(3 ** 1000))

TASKS = [
    {"id": "h1_bf_interp", "max_tokens": 6000, "check": ck_code("bf", H_BF), "prompt": (
        "Write a Python function `bf(code: str, inp: str = '') -> str` that executes a Brainfuck program and "
        "returns its output. Spec: 30000 cells initialised to 0, pointer starts at cell 0, cells are unsigned "
        "8-bit and WRAP (255+1 -> 0, 0-1 -> 255), tape pointer position is NOT clamped (wraps around), ',' reads "
        "the next byte of `inp` or 0 at EOF, '.' appends chr(cell) to output, '[', ']' are loops, any other "
        "character is ignored. Must handle nested loops. Output ONLY the code inside a single ```python code "
        "block. No explanation, no test code.")},
    {"id": "h2_regex", "max_tokens": 6000, "check": ck_code("is_match", H_RE), "prompt": (
        "Write a Python function `is_match(s: str, p: str) -> bool` implementing regex matching with support "
        "for '.' (matches any single character) and '*' (matches zero or more of the PRECEDING element). The "
        "match must cover the ENTIRE string. Output ONLY the code inside a single ```python code block. No "
        "explanation, no test code.")},
    {"id": "h3_coins", "max_tokens": 24000, "check": ck_number(truth_coins()), "prompt": (
        "有面值 1, 3, 4, 7, 13, 29, 71, 127 的硬币，每种面值数量不限。要凑出恰好 400，不考虑顺序，"
        "共有多少种不同的凑法？只输出一个数字，不要任何其他文字。")},
    {"id": "h4_kaprekar", "max_tokens": 24000, "check": ck_number(truth_kaprekar()), "prompt": (
        "卡普雷卡(Kaprekar)操作：把一个四位数（不足四位时前面补 0）的各位数字按降序排列和升序排列各组成一个数，"
        "用大数减小数得到新数；重复此操作直到得到 6174。问：在 1000 到 9999 之间所有「至少有两个不同数字」的"
        "整数中，恰好需要 7 次操作才到达 6174 的数字有多少个？只输出一个数字，不要任何其他文字。")},
    {"id": "h5_listsum", "max_tokens": 10000, "check": ck_number(TRUTH_LS), "prompt": (
        "以下是 300 行数据，每行格式为 id,value。请找出所有满足「该行 value 严格大于上一行 value」的行"
        "（从第 2 行开始比较起），把这些行的 value 全部相加，输出总和。只输出一个数字，不要任何其他文字。\n\n"
        + LINES)},
    {"id": "h6_digit7", "max_tokens": 10000, "check": ck_number(int(TRUTH_D17)), "prompt": (
        "1/7 化成小数是 0.142857142857...（循环）。小数点后第 10000 位是哪个数字？只输出一个数字，"
        "不要任何其他文字。")},
    {"id": "h7_bigsum", "max_tokens": 24000, "check": ck_number(TRUTH_BIG), "prompt": (
        "3 的 1000 次方（3^1000）的十进制表示中，所有数字之和是多少？只输出一个数字，不要任何其他文字。")},
]

API_OF = {"union-alpha": "anthropic", "deepseek-v4.1-flash": "openai"}


def selftest():
    ns = {}
    exec(REF_BF_SRC, ns)
    exec(REF_RE_SRC, ns)
    ref_bf, ref_match = ns["_ref_bf"], ns["_ref_match"]
    hello = ref_bf(HELLO, "")
    print("ref bf hello ->", repr(hello))
    assert hello == "Hello World!\n", "hello program wrong"
    assert ref_bf(",[.,]", "abc") == "abc"
    assert ref_bf(",[.,]", "") == ""
    assert ref_bf("++[>+++<-]>.", "") == "\x06"
    assert ref_bf("+[+].", "") == "\x00"
    bad = [c for c in FIXED_RE if ref_match(c[0], c[1]) != c[2]]
    print("ref regex mismatches:", bad)
    assert not bad, "reference regex disagrees with fixed expectations"
    print("truth h3 coins       =", truth_coins())
    print("truth h4 kaprekar-7  =", truth_kaprekar())
    print("truth h5 listsum     =", TRUTH_LS)
    print("truth h6 digit#10000 =", TRUTH_D17)
    print("truth h7 digitsum3^1000 =", TRUTH_BIG)
    print("SELFTEST OK")


def run_task(m, t, attempts_meta):
    tag = "%s__%s" % (m.replace("/", "_"), t["id"])
    rawpath = os.path.join(OUT, tag + ".txt")
    r = None
    if os.path.exists(rawpath):
        try:
            r = json.load(open(rawpath, encoding="utf-8"))
            log("%s: reuse cached raw" % tag, m)
        except Exception:
            r = None
    if r is None:
        tried = 0
        for mt in (t["max_tokens"], min(t["max_tokens"] * 2, 32000)):
            tried += 1
            log("%s: calling %s (max_tokens=%d, attempt %d)" % (tag, API_OF[m], mt, tried), m)
            r = call(m, t["prompt"], mt, API_OF[m], "%s-%d" % (t["id"], tried))
            r["_attempt"] = tried
            r["_max_tokens_used"] = mt
            if r.get("ok") and (r.get("text") or "").strip():
                break
            time.sleep(3)
        with open(rawpath, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    try:
        ok, note = t["check"](r)
    except Exception as e:
        ok, note = False, "checker error: %s" % e
    res = {"model": m, "task": t["id"], "ok": ok, "note": note, "sec": r.get("sec"),
           "attempts": r.get("_attempt"), "usage": r.get("usage"), "stop": r.get("stop"),
           "blocks": r.get("blocks"), "text_head": (r.get("text") or "")[:150].replace("\n", " ")}
    with open(os.path.join(OUT, "result_%s.json" % tag), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    log("%s: ok=%s sec=%s note=%s" % (tag, ok, r.get("sec"), note[:150]), m)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="union-alpha,deepseek-v4.1-flash")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    models = [x.strip() for x in args.models.split(",") if x.strip()]
    all_res = []
    for m in models:
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
            futs = [ex.submit(run_task, m, t, None) for t in TASKS]
            for fu in concurrent.futures.as_completed(futs):
                all_res.append(fu.result())
        summ = {"model": m, "passed": sum(1 for r in all_res if r["model"] == m and r["ok"]), "of": len(TASKS),
                "results": [r for r in all_res if r["model"] == m]}
        with open(os.path.join(OUT, "summary3_%s.json" % m.replace("/", "_")), "w", encoding="utf-8") as f:
            json.dump(summ, f, ensure_ascii=False, indent=1)
        log("MODEL DONE %s: %d/%d" % (m, summ["passed"], summ["of"]), m)
        print("MODEL DONE %s: %d/%d" % (m, summ["passed"], summ["of"]), flush=True)
    print(json.dumps(all_res, ensure_ascii=False, indent=1), flush=True)


if __name__ == "__main__":
    main()
