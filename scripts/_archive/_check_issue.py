#!/usr/bin/env python3
import json, urllib.request, sys, os

url = "https://api.github.com/repos/NousResearch/hermes-agent/issues/53016"
req = urllib.request.Request(url)
token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if token:
    req.add_header("Authorization", f"Bearer {token}")
req.add_header("Accept", "application/vnd.github+json")

try:
    resp = urllib.request.urlopen(req, timeout=15)
    d = json.loads(resp.read().decode())
    print(f"#{d['number']}: {d['title']}")
    print(f"State: {d['state']}")
    print(f"Created: {d['created_at']}")
    print(f"Updated: {d['updated_at']}")
    print(f"Comments: {d['comments']}")
    labels = [l['name'] for l in d['labels']]
    print(f"Labels: {labels if labels else '(none)'}")
    print(f"URL: {d['html_url']}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
