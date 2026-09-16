#!/usr/bin/env python3
import json, urllib.request, os

# Source the token from .env
token_file = "/c/Users/admin/AppData/Local/hermes/.env"
with open(token_file) as f:
    for line in f:
        if line.startswith("GITHUB_TOKEN="):
            token = line.split("=", 1)[1].strip()
            os.environ["GITHUB_TOKEN"] = token
            break

token = os.environ.get("GITHUB_TOKEN", "").strip()
if not token:
    print("No token found")
    exit(1)

data = json.dumps({"body": "Correction: OS is Windows 11, not Windows 10 as stated in the original report. Issue confirmed on Windows 11."}).encode()

req = urllib.request.Request(
    "https://api.github.com/repos/NousResearch/hermes-agent/issues/53016/comments",
    data=data,
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"
    }
)
resp = urllib.request.urlopen(req, timeout=15)
d = json.loads(resp.read().decode())
print(f"Comment posted: {d.get('id')}")
