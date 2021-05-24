import regex
import re
import os
import time


# 规则
patterns = [
    ["[0-9]+(\.[0-9]+)?%?",None],                      # 纯数字、百分数情况
    ["[0-9][:∶][0-9]",None],                           # 比分
    ["[a-zA-Z0-9@_\.]+\.com(\.cn)?",None],             # 网址
    ["[a-zA-Z&]+",None],                               # 英文单词
    ["[0-9]+(\.[0-9]+)?余万",None],                     # 金额
    ["[0-9]+(\.[0-9]+)?万亿",None],                     # 另一种金额
    ["[0-9]+(\.[0-9]+)?[万亿余]",None],                 # 还有一种金额
    ["[0-9一二三四五六七八九十百两]+年[前后间内]",[-2,-1]], # 年的一些搭配
    ["20[0-9]{2}-20[0-9]{2}年",None],                   # 年的另一种情况
    ["20[0-9]{2}-20[0-9]{2}年度",[-2]],                 # 年度区间
    ["20[0-9]{2}年度",[-2]],                            # 年度
    ["[(20)(19)][0-9]{2}年底",None],                 # 年底
    ["[0-9]{1,2}：[0-9]{2}-[0-9]{1,2}：[0-9]{2}",None], # 中文时间区间    
    ["[0-9]{1,2}：[0-9]{1,2}",None],                    # 中文时间
]


# 初始化测试文件与生成文件
def init_files():
    test_file = open('dataset/test.txt','r', encoding='utf-8')
    result_file = open('result/181220010.txt','w',encoding='utf-8')

    return test_file,result_file

# 用分词文本更新词频字典
def update_dict(file_name):
    origin_size = len(dic.keys())
    file = open(file_name,'r',encoding='utf-8')
    for line in file:
        words = line[:-1].split(" ")
        for word in words:
            # 过滤空值和单字
            if len(word)<=0: # or match_rule(word)
                continue
            if dic.get(word,0)!=0:
                dic[word] += 1
            else:
                dic[word] = 1
    file.close()

    print("Done:       %s  %d words"%(file_name,len(dic.keys())-origin_size))

# 使用训练文件生成词频字典
def generate_dict():
    # 原始数据
    # for fname in os.listdir("dataset/pure/"):
    #     update_dict("dataset/pure/"+fname)
    # # 经过验证的优质数据
    # for fname in os.listdir("dataset/testified/"):
    #     update_dict("dataset/testified/"+fname)
    # 未经验证的数据
    # for fname in os.listdir("dataset/untestified/"):
    #     update_dict("dataset/untestified/"+fname)
    
    # 经过整合的完整数据
    update_dict("dataset/all.txt")
    update_dict("dataset/newbig.txt")

    print("All Done:   %d words total"%len(dic.keys()))

# 使用原始训练集生成切分词字典
def generate_pure_seg():
    pure_dic = dict()
    dir_path = "dataset/old/pure/"
    # 原始数据
    for fname in os.listdir(dir_path):
        file = open(dir_path+fname,'r',encoding='utf-8')
        for line in file:
            line = line[:-1]
            segs = regex.findall(" . . ",line,overlapped=True)
            for seg in segs:
                if pure_dic.get(seg,0)==0:
                    pure_dic[seg] = 1
                else:
                    pure_dic[seg] += 1
            # break
        file.close()
    
    print("Pure length: ",len(pure_dic.keys()))
    return pure_dic

# 使用原始训练集生成完整词字典
def generate_pure_con():
    pure_dic = dict()
    dir_path = "dataset/old/pure/"
    for fname in os.listdir(dir_path):
        file = open(dir_path+fname,'r',encoding='utf-8')
        for line in file:
            words = line[:-1].split(" ")
            for word in words:
                # 过滤空值
                if len(word)==0: # or match_rule(word)
                    continue
                if pure_dic.get(word,0)!=0:
                    pure_dic[word] += 1
                else:
                    pure_dic[word] = 1
        file.close()
    return pure_dic

# 基于规则匹配
def match_rule(string):
    for pattern in patterns:
        if re.search('^'+pattern[0]+'$',string)!=None:
            return pattern[1]
    return 0

# 进行重切分检查，并根据前向、后向进行相应列表操作
def pure_append(string,seg,forward):
    # 只考虑两字词情况，当训练集中分开的比合起来的多，则把他们分开
    if len(string)==2 and pure_seg.get(' '+string[0]+' '+string[1]+' ',0)>pure_con.get(string,0):
        if forward==True:        
            seg.append(string[0])
            seg.append(string[1])
        else:
            seg.insert(0,string[1])
            seg.insert(0,string[0])
    else:
        if forward==True:
            seg.append(string)
        else:
            seg.insert(0,string)

# 最大前向匹配
def max_forward(string,w_seg=None):
    # 方便初次调用，不必写个None
    if w_seg==None:
        w_seg = list()
    # 无词可分，直接返回
    if len(string)==0:
        return w_seg
    
    str1 = string[0]
    str2 = string[1:]
    # 从最长位置开始匹配，逐渐变短
    for i in range(len(string),0,-1):
        j = match_rule(string[:i])
        # 规则匹配成功，按照规则，直接添加
        if  j!=0:
            str1 = string[:i]
            str2 = string[i:]
            if j==None:
                # pure_append(str1,w_seg,True)
                w_seg.append(str1)
            else:
                old = 0
                for point in j:
                    str11 = str1[old:point]
                    # pure_append(str11,w_seg,True)
                    w_seg.append(str11)
                    old = point
                str12 = str1[old:]
                # pure_append(str12,w_seg,True)
                w_seg.append(str12)
            return max_forward(str2,w_seg)
        
        # 词库匹配成功
        if string[:i] in dic.keys():
            str1 = string[:i]
            str2 = string[i:]
            break

    # 如果都没有成功，则此时str1为蛋子，对后续进行递归操作
    pure_append(str1,w_seg,True)
    return max_forward(str2,w_seg)

# 最大后向匹配
def max_backward(string,w_seg=None):
    if w_seg == None:
        w_seg = list()
    
    if len(string)==0:
        return w_seg

    str1 = string[-1]
    str2 = string[:-1]
    for i in range(len(string),1,-1):
        j = match_rule(string[-i:])
        if j!=0:
            str1 = string[-i:]
            str2 = string[:-i]
            if j==None:
                # pure_append(str1,w_seg,False)
                w_seg.insert(0,str1)
            else:
                old = len(str1)
                for point in range(len(j)):
                    str11 = str1[j[-point-1]:old]
                    # pure_append(str11,w_seg,False)
                    w_seg.insert(0,str11)
                    old = j[-point-1]
                str12 = str1[:old]
                # pure_append(str12,w_seg,False)
                w_seg.insert(0,str12)
            return max_backward(str2,w_seg)
        
        if string[-i:] in dic.keys():
            str1 = string[-i:]
            str2 = string[:-i]
            break

    pure_append(str1,w_seg,False)
    # w_seg.insert(0,str1)
    return max_backward(str2,w_seg)

# 评价分割好坏，评价指标是平均词频（未出现的词词频为0）
def evaluate(segs):
    v = 0.0
    for word in segs:
        v += dic.get(word,0)
    return v / len(segs)

# 分词函数，双向匹配
def cut(r_file,w_file):
    i = 0
    for line in r_file:
        if i%100==0:
            print(i)
        i+=1

        # 去掉\n
        line = line[:-1] 
        # 寻找最优分割序列
        segs = list()
        max_value = 0

        # 反向匹配
        new_segs = max_backward(line)
        new_value = evaluate(new_segs)
        if (new_value > max_value):
            segs = new_segs
            max_value = new_value
        
        # 正向匹配
        new_segs = max_forward(line)
        new_value = evaluate(new_segs)
        if (new_value > max_value):
            segs = new_segs
            max_value = new_value
        
        w_file.write(" ".join(segs) + '\n')

    r_file.close()
    w_file.close()




# 程序开始
begin = time.time()
dic = dict() # 全局词库
pure_seg = generate_pure_seg()
pure_con = generate_pure_con()


# 构建词频字典
generate_dict()
# print(dic.keys())
gt = time.time()

# 分词
test_file, result_file = init_files()
cut(test_file,result_file)
ct = time.time()

print("Train time:",gt-begin)
print("Test  time:",ct-gt)
