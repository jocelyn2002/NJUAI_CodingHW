for i in range(1, 10):
    for j in range(0, 10):
        for k in range(0, 10):
            if i**3+j**3+k**3 == i*100+j*10+k:
                print(i*100+j*10+k)
