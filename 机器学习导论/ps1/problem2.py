import pandas as pd
from matplotlib import pyplot as plt


def draw_pr(csv_data,output_name,label_name):
    csv_data.sort_values(by=output_name, ascending=False, inplace=True)
    output = csv_data[output_name].values
    label = csv_data[label_name].values
    x = list()
    y = list()
    for i in range(len(label)):
        tp=fp=fn=tn=0
        threshold = output[i]
        # 统计4个量
        for j in range(len(label)):
            if output[j]>=threshold:
                if label[j]==0:
                    fp+=1
                else:
                    tp+=1
            else:
                if label[j]==0:
                    tn+=1
                else:
                    fn+=1
        # 在图上建立一个点
        p=tp/(tp+fp)
        r=tp/(tp+fn)
        x.append(r)
        y.append(p)

    plt.plot(x,y)
    plt.show()
def draw_roc(csv_data,output_name,label_name):
    csv_data.sort_values(by=output_name, ascending=False, inplace=True)
    output = csv_data[output_name].values
    label = csv_data[label_name].values
    x = list()
    y = list()
    for i in range(len(label)):
        tp=fp=fn=tn=0
        threshold = output[i]
        # 统计4个量
        for j in range(len(label)):
            if output[j]>=threshold:
                if label[j]==0:
                    fp+=1
                else:
                    tp+=1
            else:
                if label[j]==0:
                    tn+=1
                else:
                    fn+=1
        # 在图上建立一个点
        tpr=tp/(tp+fn)
        fpr=fp/(tn+fp)
        
        x.append(fpr)
        y.append(tpr)

    plt.plot(x,y)
    plt.show()

    auc = 0;
    for i in range(len(x)-1):
        auc += 1/2 * (x[i+1]-x[i]) * (y[i]+y[i+1])
    return auc


csv_data = pd.read_csv("data.csv")
draw_pr(csv_data, "output", "label")
auc = draw_roc(csv_data, "output", "label")
print("AUC=",auc)