#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round-2 fairness probes: DS gets a bigger thinking budget on its two fails;
union gets one fresh attempt with a longer timeout on its two timeouts."""
import json, re, sys, time, urllib.request, urllib.error

sys.path.insert(0, ".")
import run_hard as rh


def call2(model, prompt, max_tokens, api, timeout):
    sess = "oa-hard2-%d" % int(time.time())
    url = rh.BASE + ("/messages" if api == "anthropic" else "/chat/completions")
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    if api == "anthropic":
        headers = {"x-api-key": rh.GO_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json",
                   "user-agent": "hermes-eval/1.0", "x-opencode-session": sess}
    else:
        headers = {"Authorization": "Bearer " + rh.GO_KEY, "content-type": "application/json",
                   "user-agent": "hermes-eval/1.0", "x-opencode-session": sess}
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST", headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return {"ok": False, "err": "HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:200]),
                "sec": round(time.time() - t0, 1)}
    except Exception as e:
        return {"ok": False, "err": str(e)[:200], "sec": round(time.time() - t0, 1)}
    sec = round(time.time() - t0, 1)
    if api == "anthropic":
        blocks = data.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
        return {"ok": True, "text": text, "sec": sec, "usage": data.get("usage"), "stop": data.get("stop_reason")}
    ch = (data.get("choices") or [{}])[0]
    return {"ok": True, "text": (ch.get("message") or {}).get("content") or "", "sec": sec,
            "usage": data.get("usage"), "stop": ch.get("finish_reason")}


T = {t["id"]: t for t in rh.TASKS}

PROBES = [
    ("ds_h3_64k",   "deepseek-v4.1-flash", "openai",    T["h3_coins"]["prompt"],  64000, 300, rh.truth_coins()),
    ("ds_h7_64k",   "deepseek-v4.1-flash", "openai",    T["h7_bigsum"]["prompt"], 64000, 300, rh.TRUTH_BIG),
    ("union_h3_re", "union-alpha",         "anthropic", T["h3_coins"]["prompt"],  24000, 240, rh.truth_coins()),
    ("union_h5_re", "union-alpha",         "anthropic", T["h5_listsum"]["prompt"], 12000, 240, rh.TRUTH_LS),
]

out = []
for name, model, api, prompt, mt, to, truth in PROBES:
    print("[%s] %s calling (max_tokens=%d, timeout=%ds) ..." % (time.strftime("%H:%M:%S"), name, mt, to), flush=True)
    r = call2(model, prompt, mt, api, to)
    if r.get("ok") and (r.get("text") or "").strip():
        nums = [int(x) for x in re.findall(r"\d+", r["text"])]
        ok = bool(nums) and nums[-1] == truth
        note = "last=%s truth=%s %s" % (nums[-1] if nums else None, truth, "PASS" if ok else "WRONG")
    else:
        ok = False
        note = r.get("err") or ("no output stop=%s" % r.get("stop"))
    res = {"probe": name, "ok": ok, "note": note, "sec": r.get("sec"), "usage": r.get("usage"),
           "stop": r.get("stop"), "text_head": (r.get("text") or "")[:120]}
    out.append(res)
    print("[%s] %s -> ok=%s sec=%s | %s" % (time.strftime("%H:%M:%S"), name, ok, r.get("sec"), note[:120]), flush=True)
    print("   usage:", json.dumps(r.get("usage"), ensure_ascii=False)[:220], "| head:", (r.get("text") or "")[:80].replace("\n", " "), flush=True)

json.dump(out, open("rerun2_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ALL PROBES DONE", flush=True)
