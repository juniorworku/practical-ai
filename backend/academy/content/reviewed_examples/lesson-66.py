def diagnose(run):
    return {'unsupported_citation':'check selected source against observations','step_budget':'inspect repeated actions','abstained':'inspect retrieval coverage'}.get(run['status'],'inspect status')
run={'status':'unsupported_citation','trace':['search','finish']}
assert diagnose(run)=='check selected source against observations'
assert run['status']!='completed'
print('finish proposal is not success; unsupported citation directs source inspection')

# Bounded exercise variation
assert diagnose({'status':'step_budget'})=='inspect repeated actions'
print("Exercise variation: PASS")
