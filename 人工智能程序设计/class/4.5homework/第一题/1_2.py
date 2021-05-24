import numpy as np


def pearson(a, b):
    average_a = np.mean(a)
    average_b = np.mean(b)
    fenzi = sum((a-average_a)*(b-average_b))
    fenmu = (sum((a-average_a)**2)**0.5)*(sum((b-average_b)**2)**0.5)
    return fenzi/fenmu


milk_kg = np.array([(1, 3, 4, 7), (50, 65, 60, 63)])
print(pearson(milk_kg[0], milk_kg[1]))
