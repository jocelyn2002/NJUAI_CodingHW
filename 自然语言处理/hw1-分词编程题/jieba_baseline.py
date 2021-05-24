import jieba
import numpy as np
import pandas as pd

r_file = open('dataset/test.txt','r', encoding='utf-8')
w_file = open('result/jieba_baseline.txt','w',encoding='utf-8')
for line in r_file.readlines():
    # 去除换行符
    line = line[:-1]
    
    seg_list = jieba.cut(line, cut_all=False)
    seg_list = ' '.join(seg_list)
    w_file.write(seg_list+'\n')

r_file.close()
w_file.close()