x = input()
x = list(x)
sum0 = 0
i = 0
while i < len(x):
    if x[i] == 'A':
        sum1 = 1
        sum0 += sum1
        for k in range(1, len(x)-i):
            if x[i+k] != 'A':
                break
            else:
                sum1 += 1
                sum0 += sum1
        i += k
    i += 1
print(sum0)







