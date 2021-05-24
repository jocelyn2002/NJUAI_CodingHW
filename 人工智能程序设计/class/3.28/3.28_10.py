import math
x = input().split()
y = input().split()
min_len = math.fabs(float(x[0])-float(y[0]))
for i in x:
    for j in y:
        k = math.fabs(float(i)-float(j))
        if k < min_len:
            min_len = k
print(int(min_len))
