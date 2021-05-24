for i in range(1, 21):
    for j in range(1, 34):
        for k in range(3, 301, 3):
            if (i+j+k == 100) & (5*i+3*j+k/3 == 100):
                print('rooster=%d,hen=%d,chick=%d'%(i, j, k))
