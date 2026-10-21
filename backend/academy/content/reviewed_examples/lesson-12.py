def validate(body):
    if not isinstance(body,dict) or set(body)!={'question'}: raise ValueError('fields')
    if type(body['question']) is not str or not 3<=len(body['question'].strip())<=2000: raise ValueError('question')
    return body
assert validate({'question':'Refund?'})['question']=='Refund?'
try: validate({'question':'Refund?','debug':True})
except ValueError as error: assert str(error)=='fields'
else: raise AssertionError('extra field accepted')
print('valid question accepted; extra fields rejected')

# Bounded exercise variation
for value in ['   ',123]:
    try: validate({'question':value})
    except ValueError: pass
    else: raise AssertionError('invalid question accepted')
print("Exercise variation: PASS")
