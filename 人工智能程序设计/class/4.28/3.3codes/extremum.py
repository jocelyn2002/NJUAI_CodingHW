# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 15:36:26 2019

@author: xiaoc
"""
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import minimize, basinhopping
def f(x):
      return x**2+1
      # return x**2+20*np.sin(x)+1
x = np.linspace(-10, 10, 1000)
x0 = 3
x_min = minimize(f, x0).x
# x_min = basinhopping(f, x0, stepsize = 3).x
plt.plot(x, f(x))
plt.scatter(x0, f(x0), marker='+')
plt.scatter(x_min, f(x_min), marker='D')
plt.show()


