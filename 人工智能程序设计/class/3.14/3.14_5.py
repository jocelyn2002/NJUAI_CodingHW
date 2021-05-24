x = float(input())
jie = 1
sums = 0
for i in range(1, 1000):
    plus = x**(2*i-1) / jie * (-1)**(i+1)
    sums += plus
    jie *= (2*i+1)*2*i
    if abs(plus) < 1e-8:
        break
print('%.1f' % sums)
