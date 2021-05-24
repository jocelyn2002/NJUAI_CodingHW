# -*- coding: utf-8 -*-
"""
Basic idea of the program:
     1. search bilibili for your keywords
     2. save each bullet and their frequency
     3. Load all the words(with some appearing multiple times) into the package wordcloud
     4. That's it!

@author: 上学威龙
"""
import jieba.posseg as pseg
import jieba
import matplotlib.pyplot as plt
from os import path
import re
import requests
from scipy.misc import imread
from wordcloud import WordCloud

Maxthon = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                         " Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000"}

def bilibili_fetch_bullets(keyword, mode='default'):
    # 获取关键词对应的所有av号
    n = 1
    av_id_list = []
    while True:
        base_url = 'https://search.bilibili.com/all?keyword='+keyword+'&from_source=banner_search&page='+str(n)
        base_page = requests.get(base_url)
        print(base_page, n)
        base_page.encoding = base_page.apparent_encoding
        av_ids = re.findall('<a href="//www.bilibili.com/video/av(.*?)\?', base_page.text)
        if av_ids:
            n += 1
            av_id_list += av_ids
        else:
            break;
        if mode=='default':
            break

    # print(av_id_list)
   #创建字典，统计不同弹幕数量
    pattern_cid = re.compile('''\[{"cid":(.*?),"page":1''')
    pattern_danmu = re.compile('">(.*?)<\/d>')
    danmu_dict = {}
    for av in av_id_list:
        url = 'https://www.bilibili.com/video/av'+av
        page = requests.get(url, headers=Maxthon)
        #print(page.text)
        page.encoding = page.apparent_encoding
        cids = re.findall(pattern_cid, page.text)
        danmu_url = 'http://comment.bilibili.com/'+cids[0]+'.xml'
        print(danmu_url)
        danmu_page = requests.get(danmu_url, headers=Maxthon)
        danmu_page.encoding = danmu_page.apparent_encoding
        danmus = re.findall(pattern_danmu, danmu_page.text)
        print(len(danmus))
        for danmu in danmus:
            if danmu in danmu_dict.keys():
                danmu_dict[danmu] += 1
            else:
                danmu_dict[danmu] = 1
    #写入文件
    danmu_list2 = sorted(danmu_dict.items(), key=lambda x:x[1], reverse=True)
    with open(keyword+'_b站全弹幕.txt', 'w', encoding='utf-8') as f:
        for danmu in danmu_list2:
            f.write(str(danmu[1])+' '*(12-2*len(str(danmu[1])))+danmu[0])
            f.write('\n')

def extract_words(keyword):
    with open(keyword+'_b站全弹幕.txt', 'r', encoding='utf-8') as f:
        danmus = f.readlines()

    # stop_words = set(line.strip() for line in open('stopwords.txt', encoding='utf-8'))
    worddict = {}
    for i in range(0,500):
        danmu = danmus[i]
        # print(danmu)
        i1 = 0
        i2 = 0
        for i in range(1,20):
            if danmu[i] == ' ':
                i1 = i
                break
        for i in range(i1,20):
            if danmu[i] != ' ':
                i2 = i
                break
        worddict[danmu[i2:-1]]=int(danmu[:i1])
    # d = path.dirname(__file__)
    mask_image = imread("cxkball.jpg")
    wordcloud = WordCloud(
        # width=32,
        # height=18,
        font_path='simhei.ttf',
        background_color="white",
        mask=mask_image,
        max_words=500,
        prefer_horizontal=2
    ).generate_from_frequencies(worddict)
    # Display the generated image:
    plt.imshow(wordcloud)
    plt.axis("off")
    wordcloud.to_file('wordcloud.jpg')
    plt.show()


if __name__ == "__main__":
    # keywords = input().split()
    # keyword = '%20'.join(keywords)
    #bilibili_fetch_bullets(keyword, mode='all')
    extract_words('蔡徐坤')
