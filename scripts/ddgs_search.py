#!/usr/bin/env python3
"""
DDGS web search wrapper.
Run via terminal: python3 /d/Hermes/scripts/ddgs_search.py "your query" [max_results]
"""
import subprocess, sys, json

query = sys.argv[1] if len(sys.argv) > 1 else "test"
max_r = int(sys.argv[2]) if len(sys.argv) > 2 else 5

code = f'''
import os, sys
# Clean env to avoid Hermes venv contamination
for k in ['VIRTUAL_ENV', 'PYTHONPATH', 'PIP_REQUIRE_VIRTUALENV']:
    os.environ.pop(k, None)
sys.path = [p for p in sys.path if 'hermes-agent' not in p.lower()]

from ddgs import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text("{query}", max_results={max_r}))
    for r in results:
        print(f"TITLE: {{r.get('title','')}}")
        print(f"URL: {{r.get('href','')}}")
        print(f"BODY: {{r.get('body','')}}")
        print("---")
'''

result = subprocess.run(
    [sys.executable, '-c', code],
    capture_output=True, text=True, timeout=30
)

if result.returncode == 0:
    print(result.stdout)
else:
    print(f"ERROR (rc={result.returncode}):", result.stderr[:300], file=sys.stderr)
    sys.exit(1)