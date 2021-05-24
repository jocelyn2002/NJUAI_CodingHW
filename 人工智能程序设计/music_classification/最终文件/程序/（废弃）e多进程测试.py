from multiprocessing import Process, Pipe
import joblib
from 录音 import *
from a音乐特征提取 import *
import pandas as pd
import time
import warnings
def child(second, i, d):
    name = str(i) + '.wave'
    warnings.filterwarnings("ignore")
    logi = joblib.load('逻辑斯蒂回归模型.m')
    print('ok')
    while True:
        t1 = time.time()
        x, sr = record_music(second, name)
        record = dict()
        for func in func_list:
            record.update(eval(func)(x, sr))
        data = pd.DataFrame(record, index=[0])
        d.send(logi.predict(data))
        try:
            time.sleep(7.5-(time.time()-t1))
        except ValueError:
            pass
def child2(p0,p1,p2,p3,p4):
    pip = [p0, p1, p2, p3, p4]
    v = [0, 0, 0, 0, 0]
    r = 0
    while True:
        t0 = time.time()
        v[r] = pip[r].recv()
        for r1 in range(r, 0, -1):
            if v[r1] in v[:r1]:
                print(v[r1])
                break
            else:
                print(v[r])
        if r < 4:
            r += 1
        else:
            r -= 4
        try:
            time.sleep(1.5-(time.time()-t0))
        except ValueError:
            pass


if __name__ == '__main__':
    pipe = []
    for i in range(5):
        pipe.append(Pipe())
        p = Process(target=child, args=(5, i, pipe[i][0]))
        time.sleep(1.5)
        p.start()
    print('to show')
    p2 = Process(target=child2, args=(pipe[0][1], pipe[1][1], pipe[2][1], pipe[3][1], pipe[4][1]))
    p2.start()
    p2.join()
