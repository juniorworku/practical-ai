import re
def terms(text): return set(re.findall(r'[a-z0-9]+',text.lower()))
def search(query,docs):
    ranked=[(len(terms(query)&terms(d['text'])),d['id']) for d in docs]
    return [id for score,id in sorted(ranked,key=lambda x:(-x[0],x[1])) if score>0]
docs=[{'id':'b','text':'delivery window'},{'id':'a','text':'refund window'}]
assert search('REFUND',docs)==['a']
assert search('warranty',docs)==[]
print('normalized lexical match; zero-score rows excluded')

# Bounded exercise variation
assert search('window',docs)==['a','b']
print("Exercise variation: PASS")
