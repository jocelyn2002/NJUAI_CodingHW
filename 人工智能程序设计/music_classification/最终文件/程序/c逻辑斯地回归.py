import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import sklearn.preprocessing
import joblib

music_list = ['钢琴', '吉他', '小提琴', '电音', '萨克斯', 'vocal', 'rap', '长笛']
p = list()
for i in range(0, len(music_list)):
    p.append(pd.read_csv(r'D:\OneDrive - smail.nju.edu.cn\desktop\music_classification\全分类表\\'
                         + music_list[i] + '.csv'))
    p[i]['曲风'] = music_list[i]
data = p[0]
for i in range(1, 8):
    data = data.append(p[i], ignore_index=True)
x = data.iloc[:, :-1]
y = data.iloc[:, -1]
luoji = LogisticRegression(solver='newton-cg', multi_class='auto', class_weight='balanced')
luoji.fit(x, y)
joblib.dump(luoji, '逻辑斯蒂回归模型.m')

# shibie = [0,0,0,0,0,0,0,0]
# zongshu = [0,0,0,0,0,0,0,0]
# list0 = ['钢琴', '吉他', '小提琴', '电音', '萨克斯', 'vocal', 'rap', '长笛']
# for time in range(0, 10):
#     print(time)
#     x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=None)
#     # x_train_std = sklearn.preprocessing.scale(x_train)
#     # x_test_std = sklearn.preprocessing.scale(x_test)
#     x_train_std = x_train
#     x_test_std = x_test
#     logi1 = LogisticRegression(solver='newton-cg', multi_class='auto', class_weight='balanced')
#     logi1.fit(x_train_std, y_train)
#     y_predict = logi1.predict(x_test_std)
#     for name in range(0, len(list0)):
#         for i in range(0, len(y_predict)):
#             if y_test.values[i] == list0[name]:
#                 zongshu[name] += 1
#                 if y_test.values[i] == y_predict[i]:
#                     shibie[name] += 1
# for name in range(0, len(list0)):
#     print(list0[name], '识别率:', shibie[name]/zongshu[name])



