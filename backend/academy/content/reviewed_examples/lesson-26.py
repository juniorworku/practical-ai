from queue import Queue
store={'a':{'state':'accepted','text':'refund 14 days','chunks':[]}}
def work(document_id):
    doc=store[document_id]
    if doc['state']=='ready': return
    doc['state']='indexing'
    doc['chunks']=[doc['text']]
    doc['state']='ready'
queue=Queue();queue.put('a');queue.put('a')
while not queue.empty():
    work(queue.get());queue.task_done()
assert store['a']['state']=='ready' and store['a']['chunks']==['refund 14 days']
print('worker performed ingestion; duplicate delivery did not duplicate chunks')

# Bounded exercise variation
work('a');assert len(store['a']['chunks'])==1
print("Exercise variation: PASS")
