def structural(answer,ids):
    return type(answer.get('text')) is str and type(answer.get('citations')) is list and set(answer['citations'])<=set(ids)
answer={'text':'90 days','citations':['p1']}
evidence={'p1':'14 days'}
assert structural(answer,evidence)
human={'supported':False,'reason':'90 contradicts 14'}
assert not human['supported']
assert not structural({'text':14,'citations':['p1']},evidence)
print('wrong fact passes structure; separate semantic review rejects it')

# Bounded exercise variation
answer['text']='14 days';assert structural(answer,evidence)
human={'supported':True,'reason':'matches exact fixture period'};assert human['supported']
print("Exercise variation: PASS")
