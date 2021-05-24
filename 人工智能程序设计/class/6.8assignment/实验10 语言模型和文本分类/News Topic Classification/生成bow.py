import time
from math import log
from collections import Counter
news_dict = dict()
character_list = 'abcdefghijklmnopqrstuvwxyz'
find_name = {'World': 0, 'Sports': 1, 'Business': 2, 'Sci/Tech': 3}
with open('train_texts.txt', 'r') as file:
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
                news_dict[word] = 0
words_dict0 = news_dict.copy()
# 生成类名列表
with open('train_labels.txt', 'r') as f:
    label_list = f.readlines()
    for i in range(len(label_list)):
        label_list[i] = label_list[i][:-1]
# print(label_list)
for key in news_dict:
    news_dict[key] = [0 for i in range(len(label_list))]
news_dict['final+label'] = [find_name[i] for i in label_list]
# print(news_dict['final+label'])
print(news_dict['apple'])
# 填充词表
with open('train_texts.txt', 'r') as file:
    lines = file.readlines()
    for i in range(120000):   # i为行 词为列
        # print(i)
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
                news_dict[word][i] += 1
print('done part 1')
print(len(news_dict))
print(news_dict['apple'])

# # 这个函数速度极慢
# def P(d):
#     p = [0,0,0,0]
#     ff = 0
#     for word in d:
#         if ff % 100 == 0:
#             print(ff, p)
#         ff += 1
#         n_of_this_frequency = [0,0,0,0]
#         for index in range(120000):
#             if news_dict[word][index] == d[word]:
#                 n_of_this_frequency[news_dict['final+label'][index]] += 1
#         for i in range(4):
#             p[i] += n_of_this_frequency[i]
#     return p


# def get_frequency_dict(line):
#     line = line[:-1]
#     words = line.split(' ')
#     words_dict = words_dict0.copy()
#     for word in words:
#         word = word.lower()
#         if len(word) > 1:
#             while word[0] not in character_list and len(word) > 1:
#                 word = word[1:]
#             while word[-1] not in character_list and len(word) > 1:
#                 word = word[:-1]
#         if len(word) > 1:
#             words_dict[word] += 1
#     # for keys in words_dict:
#     #     if words_dict[keys]!=0:
#     #         print(words_dict[keys], end=' ')
#     return words_dict


# with open('test_texts.txt', 'r') as file:
#     predict_list = []
#     k = 0
#     for line in file.readlines():
#         print(k, end='  ')
#         t = time.time()
#         d = get_frequency_dict(line)
#         p_max = 0
#         p = P(d)
#         for i in range(4):
#             if p > p_max:
#                 p_max = p
#                 maxx = i
#         predict_list.append(maxx)
#         k += 1
#         print(time.time()-t)
#         break                           #####
# # print('done part 2')
# # time.sleep(10)
# # with open('test_labels.txt', 'r') as f:
# #     test_labels = f.readlines()
# #     for i in range(len(test_labels)):
# #         test_labels[i] = test_labels[i][:-1]
# # n = 0
# # for i in range(len(test_labels)):
# #     if test_labels[i] == predict_list[i]:
# #         n += 1
# # print('accuracy=', n/len(predict_list))
