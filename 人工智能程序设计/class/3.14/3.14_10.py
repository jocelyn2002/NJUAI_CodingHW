list0 = [i for i in range(1, 101)]
x = int(input())
for i in list0:
    if i % x == 0:
        list0.remove(i)
list1 = [str(i) for i in list0]
for i in range(1,101):
    if str(i) in list1:
        if str(x) in list(str(i)):
            list1.remove(str(i))
list0 = [int(i) for i in list1]
k = 0
for i in list0:
    k += 1
    print(i, end='')
    if k % 10 == 0 and list0[-1] != i:
        print()
    elif list0[-1] != i:
        print(',', end='')
