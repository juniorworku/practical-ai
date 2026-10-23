import re

def retrieve(owner, query, documents, max_chars=80):
    terms = set(re.findall(r'\w+', query.lower()))
    ranked = []
    for row in documents:
        if row['owner'] != owner: continue
        overlap = len(terms & set(re.findall(r'\w+', row['text'].lower())))
        if overlap and len(row['text']) <= max_chars:
            ranked.append((overlap, row['id'], row))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in ranked[:2]]

rows = [{'id':'a1','owner':'a','text':'Refund window: 14 days.'},
        {'id':'b1','owner':'b','text':'Refund window: 365 days.'}]
assert [r['id'] for r in retrieve('a','refund window',rows)] == ['a1']
assert retrieve('a','salary',rows) == []
assert retrieve('a','refund',rows,max_chars=5) == []
print('Owner filtering precedes ranking; missing context abstains')
