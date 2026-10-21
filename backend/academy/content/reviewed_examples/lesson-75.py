def sequential(work,overhead): return sum(work)+overhead
def parallel(work,overhead): return max(work,default=0)+overhead
assert sequential([20,30],5)==55
assert parallel([20,30],5)==35
assert parallel([20,30],15)==45
print('fixture paths: sequential=55, parallel=35, extra hierarchy=45')

# Bounded exercise variation
assert parallel([20,30,50],5)==55
print("Exercise variation: PASS")
