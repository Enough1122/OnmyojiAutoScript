import urllib.request, json, time, os

env = open(r'C:\Users\admin\AppData\Local\hermes\.env', encoding='utf-8').read()
token = env.split('GITHUB_TOKEN=')[1].split()[0].strip()
camp = r'C:\Users\admin\AppData\Local\Temp\opencode\campaign'
prs = [104756,104758,104765,104766,104768,104772,104774,104775,104781,104783,104787,104797,104800,104805,104807,104808,104829,104830]

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def post(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Hermes-Agent', 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

results = {}
for n in prs:
    try:
        pr = get(f'https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}')
        ic = get(f'https://api.github.com/repos/NousResearch/hermes-agent/issues/{n}/comments')
        rv = get(f'https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/reviews')
        rc = get(f'https://api.github.com/repos/NousResearch/hermes-agent/pulls/{n}/comments')
        if not (pr.get('state') == 'open' and pr.get('draft') is False):
            results[n] = f"skipped (state={pr.get('state')} draft={pr.get('draft')})"
            print(n, results[n], flush=True)
            continue
        # Existing comments/reviews are comparison context, not a skip condition.
        # The caller must have completed semantic de-duplication before invoking this poster.
        body = open(os.path.join(camp, f'{n}.md'), encoding='utf-8').read()
        resp = post(f'https://api.github.com/repos/NousResearch/hermes-agent/issues/{n}/comments', {'body': body})
        results[n] = f"posted {resp.get('html_url')}"
        print(n, results[n], flush=True)
    except Exception as e:
        results[n] = f'ERROR {e}'
        print(n, results[n], flush=True)
    time.sleep(8)

with open(os.path.join(camp, '_result_e30_2.json'), 'w') as f:
    json.dump(results, f, indent=1)
print('DONE', flush=True)
