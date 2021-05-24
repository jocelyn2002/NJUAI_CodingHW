import os
if not os.path.exists("data"):
    if not os.path.exists('baseline'):
        os.chdir('Q:/Course/Sophomore_2/Introduce to Machine Learning/ML_HW7')
    else:
        os.chdir('baseline')
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error,explained_variance_score
from sklearn.model_selection import KFold
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')
from math import sqrt,pi
from dask.distributed import Client
import dask.dataframe as dd
import time
from geopy.distance import geodesic


# 均方误差
def mse_score_eval(preds, valid):
    labels = valid.get_label()
    scores = mean_squared_error(y_true=labels, y_pred=preds)
    return 'mse_score', scores, True
# 通过经纬度差值计算km/h
def cor2speed(lat,lon,lat_diff,lon_diff,sec_diff):
    # print(lat,lon,lat_diff,lon_diff)
    lat = float(lat)
    lon = float(lon)
    lat_0 = lat-lat_diff
    lon_0 = lon-lon_diff
    length = geodesic((lat_0,lon_0), (lat,lon)).km
    # print(length,sec_diff/3600)
    return length/(sec_diff/3600.0)
# 按照官网上对运单GPS数据的说明，重命名训练数据的列名
def set_data_columns(data):
    data.columns = ['loadingOrder','carrierName','timestamp','longitude',
                  'latitude','vesselMMSI','speed','direction','vesselNextport',
                  'vesselNextportETA','vesselStatus','vesselDatasource','TRANSPORT_TRACE']
    return data
# 这是一个数据预处理函数
def get_data(data, mode='train'): # 针对训练数据 和 测试数据 分别将部分关于时间的列转换为 datetime 时间格式
    
    assert mode=='train' or mode=='test' or 'valid'
    
    if mode=='train' or mode=='valid':
        data['vesselNextportETA'] = pd.to_datetime(data['vesselNextportETA'], infer_datetime_format=True) # 使用自动识别推理出的时间格式，把这'vesselNextportETA'转化为时间格式
    elif mode=='test':
        data['temp_timestamp'] = data['timestamp'] # 拷贝'timestamp'列
        data['onboardDate'] = pd.to_datetime(data['onboardDate'], infer_datetime_format=True)
    data['timestamp'] = pd.to_datetime(data['timestamp'], infer_datetime_format=True)
    data['longitude'] = data['longitude'].astype(float)
    data['loadingOrder'] = data['loadingOrder'].astype(str)
    data['latitude'] = data['latitude'].astype(float)
    data['speed'] = data['speed'].astype(float)
    data['direction'] = data['direction'].astype(float) # 把特征都变成浮点数类型

    return data


# 做特征工程的函数
def get_feature(df, mode='train'):
    
    assert mode=='train' or mode=='test' or 'valid'
    
    df.sort_values(['loadingOrder', 'timestamp'], inplace=True) # 将数据按 订单号 和 时间戳 两列进行 升序排列，排列结果替换元数据
    # 特征只选择经纬度、速度\方向
    df['lat_diff'] = df.groupby('loadingOrder')['latitude'].diff(1) # 返回按 订单号 分类以后 维度的差分(变化)
    df['lon_diff'] = df.groupby('loadingOrder')['longitude'].diff(1) # 返回按 订单号 分类以后 经度的差分(变化)
    df['diff_seconds'] = df.groupby('loadingOrder')['timestamp'].diff(1).dt.total_seconds() # 返回按 订单号 分类以后 时间的差分，差分化成秒，除以60转化为时间

    # df['speed'] = df.apply(lambda x: cor2speed(x['latitude'],x['longitude'],x['lat_diff'],x['lon_diff'],x['diff_seconds']) if not pd.isna(x['lon_diff']) and x['diff_seconds']>0 else x['speed'], axis=1)
    df['speed_diff'] = df.groupby('loadingOrder')['speed'].diff(1) # 返回按 订单号 分类以后 速度的差分(变化)
    
    df['anchor'] = df.apply(lambda x: 1 if x['lat_diff'] <= 0.03 and x['lon_diff'] <= 0.03
                            and x['speed_diff'] <= 0.3 and x['diff_minutes'] <= 600 else 0, axis=1) # 对每一列应用函数，判断船是否抛锚停下。
    
    if mode=='train' or mode=='valid':
        group_df = df.groupby('loadingOrder')['timestamp'].agg(mmax='max', count='count', mmin='min').reset_index()

        # vesselNextportETA = df.groupby('loadingOrder')['vesselNextportETA'].last()
        # vesselNextportETA.columns = ['loadingOrder', 'vesselNextportETA']
        # group_df = group_df.merge(vesselNextportETA,on='loadingOrder', how='left')
        
        group_df['label'] = (group_df['mmax']-group_df['mmin']).dt.total_seconds()

        # 使用已有ETA代替手动计算的ETA(效果不好，放弃)
        # group_df['label'] = group_df.apply(lambda x: (x['vesselNextportETA']-x['mmin']) if x['vesselNextportETA'] is not np.nan else group_df['label'], axis=1)
    elif mode=='test':
        group_df = df.groupby('loadingOrder')['timestamp'].agg(count='count').reset_index()
        
    anchor_df = df.groupby('loadingOrder')['anchor'].agg('sum').reset_index()
    anchor_df.columns = ['loadingOrder', 'anchor_cnt']
    group_df = group_df.merge(anchor_df, on='loadingOrder', how='left')
    group_df['anchor_ratio'] = group_df['anchor_cnt'] / group_df['count']

    agg_function = ['min', 'max', 'mean', 'median']
    agg_col = ['latitude', 'longitude', 'speed', 'direction']

    group = df.groupby('loadingOrder')[agg_col].agg(agg_function).reset_index()
    group.columns = ['loadingOrder'] + ['{}_{}'.format(i, j) for i in agg_col for j in agg_function]
    group_df = group_df.merge(group, on='loadingOrder', how='left')
    
    return group_df

