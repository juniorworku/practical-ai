"""Deterministic teaching references. No production AI, authorization, or external effects."""
import re
from decimal import Decimal, InvalidOperation

def retrieve(query, passages, k=3):
    if isinstance(k, bool) or not isinstance(k, int) or k<1: raise ValueError('k must be a positive integer')
    terms=set(re.findall(r'\w+',query.lower()))
    scored=[]
    for passage in passages:
        score=len(terms & set(re.findall(r'\w+',passage['text'].lower())))
        if score: scored.append((score,passage['id'],dict(passage)))
    return [p for _,_,p in sorted(scored,key=lambda x:(-x[0],x[1]))[:k]]

def validate_record(record):
    errors=[]
    values={}
    for key in ['quantity','unit_price','total']:
        raw=record.get(key)
        if raw is None or isinstance(raw,bool):
            errors.append(key+':invalid');continue
        try:
            value=Decimal(str(raw))
            if not value.is_finite() or value<0 or (key=='quantity' and (value==0 or value!=value.to_integral_value())):
                raise ValueError
            values[key]=value
        except (InvalidOperation,ValueError):errors.append(key+':invalid')
    if not record.get('currency'):errors.append('currency:missing')
    if len(values)==3 and values['quantity']*values['unit_price']!=values['total']:
        errors.append('total:mismatch')
    return errors

def validate_citations(answer,citations,available):
    if not isinstance(answer,str) or not answer.strip() or not isinstance(citations,list) or not citations:return False
    if not all(isinstance(x,str) for x in citations):return False
    return len(set(citations))==len(citations) and set(citations)<=set(available)

def run_agent(decide,max_steps=3):
    if isinstance(max_steps,bool) or not isinstance(max_steps,int) or max_steps<1:raise ValueError('positive step limit required')
    trace=[]
    for _ in range(max_steps):
        try: action=decide(tuple(trace))
        except Exception:return {'status':'failed','trace':trace}
        if action not in ('retrieve','answer','abstain'):return {'status':'failed','trace':trace}
        trace.append(action)
        if action in ('answer','abstain'):return {'status':action,'trace':trace}
    return {'status':'step_limit','trace':trace}

def routing_metrics(expected,predicted):
    if len(expected)!=len(predicted):raise ValueError('one prediction per case required')
    matrix={}
    for actual,guess in zip(expected,predicted):
        row=matrix.setdefault(actual,{})
        row[guess]=row.get(guess,0)+1
    return {'count':len(expected),'correct':sum(a==b for a,b in zip(expected,predicted)),'confusion':matrix}

def net_minutes(volume,manual,assisted,review,exceptions,exception_minutes):
    numbers=[volume,manual,assisted,review,exceptions,exception_minutes]
    if any(isinstance(n,bool) or not isinstance(n,(int,float)) or not __import__('math').isfinite(n) or n<0 for n in numbers) or exceptions>1:
        raise ValueError('nonnegative finite values and an exception proportion are required')
    return volume*(manual-assisted-review-exceptions*exception_minutes)
