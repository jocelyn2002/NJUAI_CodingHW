from os import name
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

shares = [55.22,56.34,55.52,55.53,56.94,58.88,58.18,57.09,58.38,58.54,57.72,58.02,57.81,58.71,60.84,61.08,61.74,62.16,60.80,60.87]

x = []
y = []
r = 5
for i in range(r,len(shares)):
    x.append(shares[i-r:i])
    y.append(shares[i])

model = LinearRegression()
model.fit(x,y)

print(model.coef_)
print(model.intercept_)
print(abs(model.predict(x)-y))

x_axis = np.arange(r,len(shares))
plt.figure()
plt.plot(x_axis,model.predict(x),label='y_pred')
plt.plot(x_axis,y,label='y_true')
plt.legend()
plt.show()
