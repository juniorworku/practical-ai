POLICIES={'p1':'refund 14 days','p2':'support weekdays'}
def search(query):
    if type(query) is not str or not 3<=len(query)<=200: raise ValueError('query length')
    words=set(query.lower().split())
    return [{'id':id,'text':text} for id,text in POLICIES.items() if words&set(text.split())]
assert search('refund')==[{'id':'p1','text':'refund 14 days'}]
try: search('')
except ValueError: pass
else: raise AssertionError('blank search accepted')
print('read-only evidence returned; blank query rejected')

# Bounded exercise variation
assert search('warranty')==[]
print("Exercise variation: PASS")
