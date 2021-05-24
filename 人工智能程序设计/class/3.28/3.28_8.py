x = input().split()
for i in range(0, len(x)):
    while x[i] and x[i][-1] in ',.\"?!':
        x[i] = x[i][:-1]
    while x[i] and x[i][0] in ',.\"?!':
        x[i] = x[i][1:]
fl = 0
for i in x:
    try:
        print(float(i))
    except:
        pass
    else:
        fl = 1
if fl == 0:
    print('Not Found!')



