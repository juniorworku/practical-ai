TOOLS={'search_policies':lambda query:['p1'] if query=='refund' else []}
def call(name,arguments):
    if name not in TOOLS: raise ValueError('unknown tool')
    if set(arguments)!={'query'} or type(arguments['query']) is not str: raise ValueError('arguments')
    return TOOLS[name](arguments['query'])
assert call('search_policies',{'query':'refund'})==['p1']
try: call('delete_documents',{'query':'all'})
except ValueError: pass
else: raise AssertionError('undiscovered tool invoked')
print('application dispatch allowlist enforced; protocol not simulated as verified')

# Bounded exercise variation
try: call('search_policies',{'query':'refund','scope':'other'})
except ValueError: pass
else: raise AssertionError('untrusted scope accepted')
print("Exercise variation: PASS")
