import sys
import joblib
import librosa
import plotly.offline
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import time
import os
import sys
logi = joblib.load('逻辑斯蒂回归模型.m')
func_list = ['mfcc', 'rolloff', 'zero_crossing', 'contrust',  'centroid', 'bandwidth', 'flatness',
              'stft',  'rms', 'poly','beat', 'cqt', 'cens', 'tempogram', 'tonnetz']
# 慢：, 'beat', 'cqt', 'cens', 'tempogram', 'tonnetz'
def chief(name, a):
    dict1 = dict()
    if len(a.shape) > 1:
        for i in range(0, a.shape[0]):
            dict1.update({name+str(i)+'_mean': a[i, :].mean()})
            dict1.update({name+str(i)+'_std': a[i, :].std()})
    else:
        dict1.update({name + '_mean': a.mean()})
        dict1.update({name + '_std': a.std()})
    return dict1

def mfcc(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.mfcc(x, sr)
    return chief(myname, a)
def zero_crossing(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.zero_crossing_rate(x)
    return chief(myname, a)
def beat(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.beat.tempo(y=x, sr=sr)
    return chief(myname, a)
def tempogram(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.tempogram(y=x, sr=sr)
    return chief(myname, a)
def rolloff(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.spectral_rolloff(y=x, sr=sr)
    dict1 = dict()
    dict1.update({myname: a.mean()})
    return dict1
def contrust(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.spectral_contrast(y=x, sr=sr)
    return chief(myname, a)
def centroid(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.spectral_centroid(y=x, sr=sr)
    return chief(myname, a)
def bandwidth(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.spectral_bandwidth(y=x, sr=sr)
    return chief(myname, a)
def flatness(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.spectral_flatness(y=x)
    return chief(myname, a)
def cqt(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.chroma_cqt(y=x, sr=sr)
    return chief(myname, a)
def stft(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.chroma_stft(y=x, sr=sr)
    return chief(myname, a)
def cens(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.chroma_cens(y=x, sr=sr)
    return chief(myname, a)
def rms(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.rms(y=x)
    return chief(myname, a)
def poly(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.poly_features(y=x, sr=sr)
    return chief(myname, a)
def tonnetz(x, sr):
    myname = str(sys._getframe().f_code.co_name)
    a = librosa.feature.tonnetz(y=x, sr=sr)
    return chief(myname, a)


# 传入切好片的x 和音乐本身的sr, 输出分类名称
def judge(x, sr):
    record = dict()
    for func in func_list:
        record.update(eval(func)(x, sr))
    data = pd.DataFrame(record, index=[0])
    return logi.predict(data)