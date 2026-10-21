def release(candidate,previous,probes,compatible=True):
    if not compatible: return {'selected':previous,'status':'manual_review'}
    return {'selected':candidate if all(probes.values()) else previous,'status':'local_staging_only'}
assert release('v2','v1',{'db':False,'queue':True})['selected']=='v1'
assert release('v2','v1',{'db':True,'queue':True})['selected']=='v2'
print('dependency readiness gates promotion; scope remains local staging')

# Bounded exercise variation
assert release('v2','v1',{'db':True},False)=={'selected':'v1','status':'manual_review'}
print("Exercise variation: PASS")
