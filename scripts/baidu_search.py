#!/usr/bin/env python3
"""
Baidu AI Search wrapper for Hermes.
Usage: python3 /d/Hermes/scripts/baidu_search.py <query> [count] [freshness]

Uses BAIDU_API_KEY from .env file or environment variable.
Free tier: 50 queries/day
"""
import subprocess, sys, os, re, json

query = sys.argv[1] if len(sys.argv) > 1 else "test"
count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
freshness = sys.argv[3] if len(sys.argv) > 3 else ""

# Read API key from .env
env_path = "C:\\Users\\admin\\AppData\\Local\\hermes\\.env"
api_key = os.environ.get("BAIDU_API_KEY", "")
if not api_key:
    try:
        with open(env_path) as f:
            for line in f:
                m = re.match(r'BAIDU_API_KEY="(.+?)"', line)
                if m:
                    api_key = m.group(1)
                    break
    except:
        pass

if not api_key:
    print("ERROR: BAIDU_API_KEY not found. Set it in .env or environment.")
    sys.exit(1)

# Build JSON payload
payload = {"query": query, "count": count}
if freshness:
    payload["freshness"] = freshness

# Run the skill script
script_path = "D:\\Hermes\\skills\\baidu-search\\scripts\\search.py"
env = os.environ.copy()
env["BAIDU_API_KEY"] = api_key

result = subprocess.run(
    [sys.executable, script_path, json.dumps(payload, ensure_ascii=False)],
    capture_output=True, text=True, timeout=30, env=env
)

# Parse and format output
if result.returncode == 0:
    try:
        data = json.loads(result.stdout.split("success")[-1].strip())
        print(f"共 {len(data)} 条结果\n")
        for i, r in enumerate(data, 1):
            print(f"{i}. [{r.get('website','?')}] {r.get('title','')}")
            print(f"   {r.get('url','')}")
            print(f"   {r.get('date','')}")
            content = r.get('content','')[:200]
            print(f"   {content}")
            print()
    except json.JSONDecodeError:
        print(result.stdout)
else:
    print(f"ERROR (rc={result.returncode}):", result.stderr[:300])
    sys.exit(1)