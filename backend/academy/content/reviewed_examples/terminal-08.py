import hashlib,json
def digest(text): return hashlib.sha256(text.encode()).hexdigest()
source="print('14 days')"
note={'lesson':'terminal-08','artifact':'policy.py','revision':digest(source),'observed':'14 days','revisit':'what happens without evidence?'}
loaded=json.loads(json.dumps(note))
assert loaded['revision']==digest(source)
assert loaded['revision']!=digest("print('7 days')")
assert len(json.dumps(loaded))<1000
print('small session note preserved; changed source invalidates saved revision')

# Bounded exercise variation
loaded['next']='rerun supported and missing-evidence cases';assert len(json.dumps(loaded))<1000
print("Exercise variation: PASS")
