import json, collections

path = r'D:\Hermes\gh_notifications.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

# gh api --paginate --slurp returns [page1, page2, ...]; each page is a list
pages = data if isinstance(data, list) else [data]
items = []
for page in pages:
    if isinstance(page, list):
        items.extend(page)
    else:
        items.append(page)

unread = [n for n in items if n.get('unread')]

print('total_fetched =', len(items))
print('unread_total  =', len(unread))
print('--- reason breakdown (unread) ---')
reasons = collections.Counter(n.get('reason') for n in unread)
for r, c in reasons.most_common():
    print(f'{r}: {c}')
print('--- top3 repos (unread) ---')
repos = collections.Counter(n.get('repository', {}).get('full_name') for n in unread)
for name, c in repos.most_common(3):
    print(f'{name}: {c}')
