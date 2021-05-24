x = input().split()
sums = 0
for i in range(1, int(x[1])+1):
    s1 = int(x[0]*i)
    sums += s1
print(sums)
