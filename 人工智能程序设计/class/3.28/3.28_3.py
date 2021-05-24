def cleanr_list(a):
    b = []
    for i in a:
        while (ord(i[0]) not in range(ord('a'), ord('z')+1)) and (ord(i[0]) not in range(ord('A'), ord('Z')+1)):
            i = i[1:]
        while (ord(i[-1]) not in range(ord('a'), ord('z') + 1)) and (ord(i[-1]) not in range(ord('A'), ord('Z') + 1)):
            i = i[:-1]
        b.append(i)
    return b


x = list(input().split(','))
n = int(input())
print(cleanr_list(x)[n-1])

