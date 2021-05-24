import joblib
import wave
import pyaudio
from a音乐特征提取 import *
import pandas as pd
import time
from multiprocessing import Process, Pipe
import warnings
warnings.filterwarnings("ignore")


def play_music(f, second):
    p = pyaudio.PyAudio()
    rate = f.getframerate()
    chunk = rate * second
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(), rate=rate, output=True)
    data = f.readframes(chunk)
    while data:
        stream.write(data)
        data = f.readframes(chunk)
    # RATE / CHUNK * RECORD_SECONDS
    stream.stop_stream()
    stream.close()
    p.terminate()
def analyse_music(f, second):
    logi = joblib.load('逻辑斯蒂回归模型.m')
    record = dict()
    for func in func_list:
        record.update(eval(func)(x, 44100))
    data = pd.DataFrame(record, index=[0])
    d.send(logi.predict(data))
if __name__ == '__main__':
    file_name = 0
    file = wave.open(file_name, "rb")
    p1 = Process(target=play_music, args=(file, 1))
    p2 = Process(target=analyse_music, args=(file, 1))
