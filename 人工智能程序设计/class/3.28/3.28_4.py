def twonums_sum(m, lst):
    for i in range(0, len(lst)):
        for j in range(0, len(lst)):
            if lst[i] + lst[j] == int(m):
                return i, j
    else:
        return -1


list1 = [1,4,5,6,7,8,9,10,11,12,13,15,18,19,20,21,29,34,54,65]
n = input()
if twonums_sum(n, list1) == -1:
    print('not found')
else:
    print(twonums_sum(n, list1))

