import librosa
import plotly.offline
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import time
import os
import sys
np.seterr(divide='ignore', invalid='ignore')

def form_music_datafram(direction, file_dir):
    # 创建datafram
    file = open(file_dir, 'a')
    t1 = time.time()
    x, sr = librosa.load(direction+'/'+os.listdir(direction)[0], sr=None)
    print('%.2f'%(time.time() - t1), end=' ')
    record = dict()
    for func in func_list:
        t0 = time.time()
        record.update(eval(func)(x, sr))
        print('%.2f'%(time.time() - t0), end=' ')
    print()
    data = pd.DataFrame(record, index=[0])
    data.to_csv(file, mode='a', index=False, line_terminator='\n')
    file.close()
    # 遍历音乐目录
    for i in os.listdir(direction)[1:]:
        file = open(file_dir, 'a')
        # 生成新记录
        music_dir = direction+'/'+i
        t1 = time.time()
        x, sr = librosa.load(music_dir, sr=None)
        print('%.2f'%(time.time()-t1), end=' ')
        record = dict()
        for func in func_list:
            t0 = time.time()
            record.update(eval(func)(x, sr))
            print('%.2f'%(time.time()-t0),end=' ')
        print()
        # 添加记录
        df2 = pd.DataFrame(record, index=[0])
        df2.to_csv(file, mode='a', index=False, header=False, line_terminator='\n')
        print('本曲用时：%.2f 曲名：%s' % ((time.time() - t1), i))
        print('总用时：%.2f' % (time.time() - t00))
        file.close()
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


func_list = ['mfcc', 'rolloff', 'zero_crossing', 'contrust',  'centroid', 'bandwidth', 'flatness',
              'stft',  'rms', 'poly','beat', 'cqt', 'cens', 'tempogram', 'tonnetz']
# 慢：, 'beat', 'cqt', 'cens', 'tempogram', 'tonnetz'
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


if __name__ == '__main__':
    t00 = time.time()
    folder_dir = r'G:\python\电音'
    file_dir = r'D:\OneDrive - smail.nju.edu.cn\desktop\music_classification\全分类表\电音.csv'
    form_music_datafram(folder_dir, file_dir)
    print('ok')
