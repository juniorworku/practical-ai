def validate(config):
    if config.get('env')=='staging':
        if not config.get('database'): raise ValueError('database required')
        if config.get('debug') is not False: raise ValueError('debug must be disabled')
    return True
assert validate({'env':'staging','database':'synthetic','debug':False})
try: validate({'env':'staging','debug':False})
except ValueError as error: assert str(error)=='database required'
else: raise AssertionError('unsafe startup')
print('staging configuration validated without exposing values')

# Bounded exercise variation
try: validate({'env':'staging','database':'synthetic','debug':True})
except ValueError: pass
else: raise AssertionError('debug enabled')
print("Exercise variation: PASS")
