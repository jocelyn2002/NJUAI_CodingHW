fl = 0
for i in range(100, 999):
    if i % 37 == 0:
        j = (i-(i//100)*100)*10 + i//100
        k = (j-(j//100)*100)*10 + j//100
        if j % 37 != 0 or k % 37 != 0:
            fl = 1
            break
if fl == 1:
    print("It's a false proposition.")
else:
    print("It's a true proposition.")
