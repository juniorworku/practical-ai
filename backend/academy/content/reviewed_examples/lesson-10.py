def attempts(status,deadline=15):
    elapsed=count=0
    while status in {429,503} and count<3:
        cost=5+1
        if elapsed+cost>deadline: break
        elapsed+=cost;count+=1
    return count,elapsed
assert attempts(503)==(2,12)
assert attempts(401)==(0,0)
print('two transient attempts fit; authentication is not retried')

# Bounded exercise variation
assert attempts(503,5)==(0,0)
print("Exercise variation: PASS")
