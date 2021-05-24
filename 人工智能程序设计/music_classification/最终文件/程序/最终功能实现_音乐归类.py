import librosa
import numpy as np
import pandas as pd
import sys
import audiosegment
import pyaudio
import wave
import os
import joblib
import warnings

warnings.filterwarnings('ignore')
#播放音频的函数

def music_show(music_name):
  
    chunk = 1024 
    f = wave.open(music_name,"rb")
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                    channels = f.getnchannels(), rate = f.getframerate(),
                    output = True)
    
    data = f.readframes(chunk)
    
    while data != '':
        stream.write(data)
        data = f.readframes(chunk)

    stream.stop_stream()
    stream.close()

    p.terminate()
    
    

#生成单个音频文件数据函数部分

np.seterr(divide='ignore', invalid='ignore')

def form_music_datafram(filename):
    # 创建dataframe

    x, sr = librosa.load(filename)

    record = dict()
    for func in func_list:
        record.update(eval(func)(x, sr))

    data = pd.DataFrame(record, index=[0])
    return data
    

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


#切割音频的函数
#输入一个音频文件的地址
#保存这个音频中时长为一分二十秒左右的内容
def audio_cut(filename, savename):
    file = audiosegment.from_file(filename)
    file = file[20000:25500]
    file.export(savename, format = 'wav')
    
    
def generate_single_data(filename):
    #先将原音频进行切割
    temp_savename = 'tempo'
    audio_cut(filename, temp_savename)
    
    #生成数据
    data = form_music_datafram(temp_savename)
    
    return data



'''
#knn部分


#返回字典中最大值的键
def largest_key(dic):

    for key, item in dic.items():
        if item == max(list(dic.values())):
            return key


#距离
def distance(datas1, datas2):
    sume = 0
    for i in datas1.index:
        sume += (datas1[i] - datas2[i]) ** 2
    return (sume ** 0.5).values[0]


#knn
    
def knn(data, data_X, data_Y):
    #求距离
    res = []
    for i in range(len(data_X)):
        temp = {'result': data_Y.iloc[i], 'distance': distance(data, data_X.iloc[i])}
        res.append(temp)
        
    
    #升序排列
    res = sorted(res, key = lambda item: item['distance'])
    
    #取前k个数据
    res = res[0:k]
    
    #加权平均
    result = {}
    values = list(set(data_Y.values))
    for column in values:
        result[column] = 0
        #求总距离
    distance_sum = 0
    for item in res:
        distance_sum += item['distance']
        #加权
    for item in res:
        result[item['result']] += 1 - item['distance'] / distance_sum
        
    out = largest_key(result)
    return out
'''

'''

#读取数据集函数部分

#读取时将数据集降维的函数
def data_pca(k, data):
    data1 = np.matrix(data.iloc[:,0:-1]) #此文件中降维对象的最后一列是字符串，作出了修改
    C = ((data1.T).dot(data1)) / len(data1)
    a, eigenvectors = np.linalg.eig(C)
    C = data1.dot(eigenvectors[0:19].T)
    data1 = np.column_stack(((np.matrix(data.iloc[:,0]).reshape(len(data),1)), C))
    data = pd.DataFrame(data1)
    return data


#读取并处理、降维
def load_dataset(filename):
    
    k = 20

    #读取文件
    f = open(filename)
    data = pd.read_csv(f)

    #先将最后一列保存
    Y = data.iloc[:, -1]
    #数据集在存储时貌似有问题，出现了NaN，这里将其去除
    data.dropna(inplace = True)

    #降维
    data = data_pca(k, data)
    data['style'] = Y
    #至此，降维后的数据集已经在data中
    
    return data
'''

#创建文件夹函数
def mkdir(path):
    os.makedirs(path)

#分类函数
def judge(filename):
    logi = joblib.load('逻辑斯蒂回归模型.m')
    data = generate_single_data(filename)
    return logi.predict(data)

#音频文件移动函数
def cut_dirs(data_path, new_path, name):
    """
    :param path：指定的文件夹路径
    :param new_path：要将该文件夹剪切到的路径
    """
    cur_path = os.path.join(data_path, name);
    new_file_path = os.path.join(new_path, name);
    os.rename(cur_path,new_file_path);
    print('ok')

#分类函数
def music_tag(res_path, data_path):
        #step 1:创建八个文件夹
        type_list = ['钢琴', '小提琴', '吉他', '长笛', '电音', 'rap',
                     '萨克斯', 'vocal']
        for i in type_list:
           try:
               mkdir(res_path + '/' + i )
           except:
               pass
  
        #step 2:遍历所有的音频
        for i in os.listdir(data_path):
            # 一个音频的地址为music_dir
            
            music_dir = data_path + '\\' + i
            
        #step 3:对音频分类
            variety = judge(music_dir)[0]
            
        #step 4:根据分类结果移动文件
            path = res_path + '\\' + variety
            name = i
            cut_dirs(data_path, path, name)
            
            
res_path = r'list'
data_path = r'test'
music_tag(res_path, data_path)


data_filename = r'D:\study\大一下学期\programming\huangshujian\final_design\Instruments_wav\Vilolin_wav\Arthur Grumiaux - Schwanengesang, D.957：Ständchen.wav'
dataset_filename = r'D:\study\大一下学期\programming\huangshujian\final_design\全分类表\all_data.3.csv'

'''
#播放音频
music_show(data_filename)
'''


