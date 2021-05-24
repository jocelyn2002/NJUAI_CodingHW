# 由于原始算法占用内存过大，在我的电脑上跑步起来，因此进行如下改进
from scipy.special import comb
from math import log

# STEP0 生成每一类关于每一个词的概率列表
news_dict = dict()
character_list = 'abcdefghijklmnopqrstuvwxyz'
find_name = {'World': 0, 'Sports': 1, 'Business': 2, 'Sci/Tech': 3}


#   生成每个词在每一类别（不同行）中单独出现概率
def generate_original(file_dir='train_texts.txt'):
    with open(file_dir, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line[:-1]
            words = line.split(' ')
            for word in words:
                j = 0
                # 处理成纯小写无标点
                word = word.lower()
                if len(word) > 1:
                    while word[0] not in character_list and len(word) > 1:
                        word = word[1:]
                    while word[-1] not in character_list and len(word) > 1:
                        word = word[:-1]
                for ke in word:
                    if ke not in character_list:
                        j = 1
                        break
                if word not in news_dict and j == 0:
                    news_dict[word] = [0, 0, 0, 0]
    with open('train_labels.txt', 'r') as f:
        label_list = f.readlines()
        for i in range(len(label_list)):
            label_list[i] = label_list[i][:-1]
    # 填充词表
    with open('train_texts.txt', 'r') as file:
        lines = file.readlines()
        for i in range(120000):
            print(i)
            # 处理成纯小写无标点
            line = lines[i][:-1]
            words = line.split(' ')
            for word in words:
                j = 0
                word = word.lower()
                if len(word) > 1:
                    while word[0] not in character_list and len(word) > 1:
                        word = word[1:]
                    while word[-1] not in character_list and len(word) > 1:
                        word = word[:-1]
                for ke in word:
                    if ke not in character_list:
                        j = 1
                        break
                if j == 0:
                    news_dict[word][find_name[label_list[i]]] += 1

    for i in range(4):
        sum = 0
        for j in news_dict:
            sum += news_dict[j][i]
        for j in news_dict:
            news_dict[j][i] /= sum

    return news_dict
#   组合数
def C(a,b):
    return comb(b,a)
#   判断所给出的一行是哪一类
def judge(line, data):
    line = line[:-1]
    words = line.split(' ')
    p = [0,0,0,0]
    word_dict = dict.fromkeys(data.keys(), 0)
    for word in words:
        # 处理成纯小写无标点
        word = word.lower()
        if len(word) > 1:
            while word[0] not in character_list and len(word) > 1:
                word = word[1:]
            while word[-1] not in character_list and len(word) > 1:
                word = word[:-1]
        if word in data:
            word_dict[word] += 1
    n_of_words = sum(word_dict.values())
    for word in data:
        for kind in range(4):
            p[kind] += log(C(word_dict[word], n_of_words)) + word_dict[word]*log(data[word][kind]+1e-6) + (n_of_words-word_dict[word])*log(1-data[word][kind]-1e-6)
    max = 0
    for kind in range(4):
        if p[kind]>p[max]:
            max = kind
    return max


if __name__ == '__main__':
    p_data = generate_original()
    j = []
    with open('test_texts.txt', 'r') as file:
        ff = 0
        for line in file.readlines():
            print(ff, end=' ')
            ff += 1
            j.append(judge(line, p_data))
            if ff==200:
                break
    with open('test_labels.txt', 'r') as file:
        label_list = file.readlines()
        for i0 in range(len(label_list)):
            label_list[i0] = find_name[label_list[i0][:-1]]

    label_list = label_list[:200]

    counter = 0
    for i in range(len(j)):
        if j[i] == label_list[i]:
            counter += 1
    print('accuracy:', counter/len(j))
