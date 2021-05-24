import time
jj = 7
t1 = time.time()
for i in range(0, jj):
    for j in range(0, jj):
        for k in range(0, jj):
            l=i**j**k
t2 = time.time()
delta_t = t2 - t1
print(delta_t)
