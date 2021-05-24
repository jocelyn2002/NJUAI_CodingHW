x = input().split(',')
el = 0
for xi in x:
    num_list = list(str(i) for i in range(1, len(xi)+1))
    fl = 0
    for i in xi:
        if i in num_list:
            num_list.remove(i)
        else:
            fl = 1
            break
    if fl == 0:
        el = 1
        print(xi)
if el == 0:
    print('not found')
