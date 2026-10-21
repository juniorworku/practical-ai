models={'single':{'quality':.95,'cost':1,'latency':100},'team':{'quality':.8,'cost':3,'latency':200}}
def eligible(row): return row['quality']>=.9 and row['latency']<=150
assert eligible(models['single']) and not eligible(models['team'])
assert models['team']['cost']==3*models['single']['cost']
print('synthetic team fails quality and latency gates despite more workers')

# Bounded exercise variation
revised={**models['team'],'quality':.96,'latency':140};assert eligible(revised) and revised['cost']==3
print("Exercise variation: PASS")
