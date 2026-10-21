def cost(inputs,outputs,input_rate,output_rate):
    if min(inputs,outputs,input_rate,output_rate)<0: raise ValueError('negative usage or rate')
    return (inputs*input_rate+outputs*output_rate)/1_000_000
assert sum([300,5000,200])==5500
assert cost(1000,500,1,2)==0.002
print('sequential budget=5500 ms; fixture cost=0.002')

# Bounded exercise variation
assert cost(1000,1000,1,2)==0.003
print("Exercise variation: PASS")
