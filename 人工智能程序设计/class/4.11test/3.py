def R(a):
    i = 0
    flg = 0
    count = 1
    new_list = ''
    while i < len(a):
        if new_list:
            if new_list[-1] == a[i]:
                flg = 1
            else:
                new_list += str(count)
                flg = 0
                count = 1
        if flg == 1:
            count += 1
        else:
            new_list += a[i]
        i += 1
    new_list += str(count)
    return new_list


x = input()
print(R(x))
