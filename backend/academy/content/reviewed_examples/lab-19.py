ALLOWED={'search_policies'}
EXPECTED={'type':'object','required':['query'],'additionalProperties':False,
          'properties':{'query':{'type':'string','minLength':3,'maxLength':200}}}
CATALOG=[{'name':'search_policies','inputSchema':EXPECTED}]
POLICY={'id':'policy-1','text':'Refund window is 30 days','owner':'demo'}
def discover(catalog):
    accepted={}
    for tool in catalog:
        if tool.get('name') in ALLOWED and tool.get('inputSchema')==EXPECTED:
            accepted[tool['name']]=tool
    return accepted
def call(capabilities,name,arguments):
    if name not in ALLOWED or name not in capabilities: raise PermissionError('tool denied')
    if type(arguments) is not dict or set(arguments)!={'query'}: raise ValueError('arguments')
    query=arguments['query']
    if type(query) is not str or not 3<=len(query.strip())<=200: raise ValueError('query')
    return {'isError':False,'sources':[dict(POLICY)] if 'refund' in query.lower() else []}
known=discover(CATALOG)
assert set(known)=={'search_policies'}
assert call(known,'search_policies',{'query':'refund'})['sources'][0]['id']=='policy-1'
assert call(known,'search_policies',{'query':'warranty'})=={'isError':False,'sources':[]}
for name,args in [('delete',{'query':'refund'}),('search_policies',{'query':' '}),('search_policies',{'query':'refund','owner':'other'})]:
    try: call(known,name,args)
    except (ValueError,PermissionError): pass
    else: raise AssertionError('unsafe call executed')
assert discover([{'name':'search_policies','inputSchema':{'type':'string'}}])=={}
print('read-only discovery contract checked; calls validated; empty success distinguished')

# Bounded exercise variation
advertised=CATALOG+[{'name':'delete','inputSchema':EXPECTED}]
assert set(discover(advertised))=={'search_policies'}
try: call(discover(advertised),'delete',{'query':'refund'})
except PermissionError: pass
else: raise AssertionError('discovery granted write authority')
assert ALLOWED=={'search_policies'}
print("Exercise variation: PASS")
