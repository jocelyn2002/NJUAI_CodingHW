#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Author: Junchen
# @time: 7th, Jun, 2020

# cell 1
import pandas as pd
from tqdm import tqdm
import numpy as np

from sklearn.metrics import mean_squared_error,explained_variance_score
from sklearn.model_selection import KFold
import lightgbm as lgb

import warnings
warnings.filterwarnings('ignore')
import os
os.chdir('Q:/Course/Sophomore_2/Introduce to Machine Learning/ML_HW7') # 这里要自己修改一下，修改成存储 数据集的文件夹的 父目录

# baseline只用到gps定位数据，即train_gps_path
train_gps_path = './data/train0523.csv'
test_data_path = '../traindata/A_testData0531.csv'
order_data_path = '../traindata/loadingOrderEvent.csv'
port_data_path = '../traindata/port.csv'

NDATA = 5000
exl_char = ['>', '>>']
train_data = pd.read_csv(train_gps_path, nrows = NDATA, header=None)

train_data.to_csv('./fuckdata.csv', index = False, header = False)

fuck_data = pd.read_csv('./fuckdata.csv', header = None)
'''fuck_data.columns = ['loadingOrder','carrierName','timestamp','longitude',
                  'latitude','vesselMMSI','speed','direction','vesselNextport',
                  'vesselNextportETA','vesselStatus','vesselDatasource','TRANSPORT_TRACE']'''

fuck_data.to_csv('./fuckdata.csv', index = False)

def localchar(goalchar, info):
    for _ in range(len(info)):
        if(info[_] == goalchar):
            return _
    return -1

def normalize_port(batch_size, path):
    sum = 0
    for batch_data in pd.read_csv(path, chunksize = batch_size):
        #for sb in range(0,9):
            #print(batch_data.iloc[0, sb])

        '''batch_data.columns = ['loadingOrder','carrierName','timestamp','longitude',
                  'latitude','vesselMMSI','speed','direction','vesselNextport',
                  'vesselNextportETA','vesselStatus','vesselDatasource','TRANSPORT_TRACE']'''

        for _ in range(batch_size):
            for temp_char in exl_char:
                if temp_char in str(batch_data.iloc[_, 8]):
                    index = localchar(temp_char, batch_data.iloc[_, 8])
                    assert(index != -1)
                    batch_data.iloc[_, 8] = batch_data.iloc[_, 8][index + 1 :]

        batch_data.to_csv('Afternormalize2.csv', mode = 'a', index = False, header = None)
        sum += batch_size
        print("sum:", sum)

normalize_port(100, './fuckdata.csv')