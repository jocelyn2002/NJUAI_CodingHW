# -*- coding: utf-8 -*-
"""
Basic idea of the program:
     1. Grab a few webpages from sina and extract the roll news subjects
     2. Segment words using Python the package jieba
         2.1 Filter out the stop words
         2.2 Only keep nouns
     3. Load all the words(with some appearing multiple times) into the package wordcloud
     4. That's it!

@author: Dazhuang
"""

import jieba.posseg as pseg
import matplotlib.pyplot as plt
from os import path
import re
import requests
from scipy.misc import imread
from wordcloud import WordCloud

def fetch_sina_news():
    PATTERN = re.compile('________________')
    BASE_URL = '_________________________'
    with open('subjects.txt', 'w', encoding='utf-8') as f:
        r = requests.get(BASE_URL)
        data = r.text.encode('utf-8').decode('unicode-escape')
        p = re.findall(PATTERN, data)
        for s in p:
            f.write(s)
    
def extract_words():
    with open('subjects.txt', 'r', encoding='utf-8') as f:
        news_subjects = f.readlines()
    
    stop_words = set(line.strip() for line in open('stopwords.txt', encoding='utf-8'))
    
    newslist = []
    for subject in news_subjects:
        if subject.isspace():
            continue
        # segment words line by line
        p = re.compile("n[a-z0-9]{0,2}")    # n, nr, ns, ... are the flags of nouns
        word_list = pseg.___________(subject)     
        for word, flag in word_list:
            if _______________ and _________________ != None:
                newslist.append(word)
    
    content = {}
    for item in newslist:
        content[item] = content.__________(item, 0) + 1
    
    d = path.dirname(__file__)
    mask_image = imread(path.___________(d, "mickey.png"))
    wordcloud = WordCloud(font_path='simhei.ttf', background_color="grey", mask=mask_image, max_words=10).generate_from_frequencies(______________)
    # Display the generated image:
    plt.imshow(wordcloud)
    plt.axis("off")
    wordcloud.to_file('wordcloud.jpg')
    plt.show()
    
if __name__ == "__main__":
    fetch_sina_news()
    extract_words()
