dot_list = [',', '.', '!', '?']
long_list = []
lens = 0
x = input().split()
for i in x:
    while i[-1] in dot_list:
        i = i[:-1]
    if len(i) == lens and i not in long_list:
        long_list.append(i)
    elif len(i) > lens:
        lens = len(i)
        long_list = [i]
for j in long_list[:-1]:
    print(j, end=', ')
print(long_list[-1])
