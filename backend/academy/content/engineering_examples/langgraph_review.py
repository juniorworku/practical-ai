"""Optional installed-SDK comparison; in-memory checkpoints are not durable.
python langgraph_review.py after installing langgraph in the isolated env.
"""
from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt,Command
class State(TypedDict):
    draft:str
    approved:bool

def review(state:State):
    decision=interrupt({'draft':state['draft'],'question':'Approve this exact draft?'})
    return {'approved':decision is True}

builder=StateGraph(State);builder.add_node('review',review)
builder.add_edge(START,'review');builder.add_edge('review',END)
graph=builder.compile(checkpointer=InMemorySaver())
config={'configurable':{'thread_id':'synthetic-acme-thread-1'}}
first=graph.invoke({'draft':'Unopened within 14 days.','approved':False},config)
assert first.get('__interrupt__')
final=graph.invoke(Command(resume=True),config)
assert final['approved'] is True
print('SDK interrupt/resume passed; persistence and actor authorization must be added separately')
