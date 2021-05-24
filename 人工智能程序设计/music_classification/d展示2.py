import joblib
import librosa
from 播放 import *
from a音乐特征提取 import *
import pandas as pd
import time
import warnings
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    logi = joblib.load('逻辑斯蒂回归模型.m')
    while True:
        t0 = time.time()
        x, sr = record_music(10)
        t1 = time.time()
        print(t1-t0, end='  ')
        record = dict()
        for func in func_list:
            record.update(eval(func)(x, sr))
        data = pd.DataFrame(record, index=[0])
        pre = logi.predict(data)
        print(time.time()-t1, end='')
        print(pre)
