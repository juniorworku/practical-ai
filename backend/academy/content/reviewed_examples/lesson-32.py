def windows(text,size=4,overlap=1):
    if size<=0 or not 0<=overlap<size: raise ValueError('invalid window')
    return [text[i:i+size] for i in range(0,len(text),size-overlap)]
assert windows('abcdefgh')==['abcd','defg','gh']
try: windows('abc',4,4)
except ValueError: pass
else: raise AssertionError('zero stride accepted')
print('stride=3; final short window retained; zero stride rejected')

# Bounded exercise variation
assert windows('abcdefgh',4,0)==['abcd','efgh']
print("Exercise variation: PASS")
