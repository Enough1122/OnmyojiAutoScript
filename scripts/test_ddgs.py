import subprocess, sys, os

code = '''
import os, sys
# Clean environment
for k in ['VIRTUAL_ENV', 'PYTHONPATH', 'PIP_REQUIRE_VIRTUALENV']:
    os.environ.pop(k, None)
# Remove hermes-agent paths from sys.path
sys.path = [p for p in sys.path if 'hermes-agent' not in p.lower()]

from ddgs import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text("DeepSeek API 峰谷定价", max_results=5))
    print(f"Got {len(results)} results")
    for r in results:
        print(f"TITLE: {r.get('title','')[:60]}")
        print(f"URL: {r.get('href','')}")
        print(f"BODY: {r.get('body','')[:150]}")
        print()
'''

result = subprocess.run(
    [sys.executable, '-c', code],
    capture_output=True, text=True, timeout=30
)
print('STDOUT:', result.stdout[:1000])
print('STDERR:', result.stderr[:500])
print('RC:', result.returncode)
