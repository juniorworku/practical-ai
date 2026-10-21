def validate(answer,allowed):
    if set(answer)!={'text','citations'} or type(answer['text']) is not str: raise ValueError('shape')
    if type(answer['citations']) is not list or any(type(x) is not str for x in answer['citations']): raise ValueError('citations type')
    if not set(answer['citations'])<=set(allowed): raise ValueError('unknown citation')
    return answer
assert validate({'text':'14 days','citations':['p1']},['p1'])['text']=='14 days'
try: validate({'text':'14 days','citations':['invented']},['p1'])
except ValueError: pass
else: raise AssertionError('invented citation accepted')
print('shape and citation membership checked; factual support unjudged')

# Bounded exercise variation
try: validate({'text':'14 days','citations':'p1'},['p1'])
except ValueError as error: assert str(error)=='citations type'
else: raise AssertionError('string accepted')
print("Exercise variation: PASS")
