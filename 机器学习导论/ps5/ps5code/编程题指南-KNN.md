## 编程题指南——KNN

### 主要内容

实现基本的KNN算法，并在指定的数据集上进行测试。

### 数据指定

训练数据/train数据集: train_data.csv, train_labels.csv。分别代表训练样本的特征和标记。

测试数据/test数据集: test_data.csv,代表测试样本的特征。

### 相关说明

你需要在main.py中的各个函数的编写，函数接口已经写好并做好注释。

 def distance(self, one_sample, X_train) #输入为一个样本和训练样本，输出为该样本与训练集中所有样本的距离；建议欧氏距离
 def get_k_neighbor_labels(self, distances, y_train, k) #输入为某一样本与训练集中的样本的距离，以及训练集的标签及k的大小，本题为5；输出为k个近邻的类别标签
 def vote(self, one_sample, X_train, y_train, k) #标签统计，票数最多的标签即该测试样本的预测标签
 def predict(self, X_test, X_train, y_train) #对测试集进行预测

### 评分标准
(5/20)完成get_k_neighbor_labels函数编写
(10/20)完成vote函数编写
(15/20)完成predict函数编写
(20/20)对训练样本的预测结果比较好
！！！当然，以上分数是在代码是手动独立完成，且能顺利运行的基础上

   

### 注意事项

- 请勿使用库文件，保证代码是手动实现的。
- 提交文件包括：1.学号.py；2.学号_ypred.csv
将以上文件一同放在作业pdf同一个文件夹下。