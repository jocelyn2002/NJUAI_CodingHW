x = int(input())
a = []
for i in range(2, 101):
    for j in range(2, 101):
        d = i**j
        if d <= x:
            a.append(d)
        else:
            break
a.sort()
a = list(set(a))
a.sort()
print(a)
