import os

# file = open('dataset/all.txt','w',encoding='utf-8')
# for fname in os.listdir("dataset/pure/"):
#     file1 = open("dataset/pure/"+fname,'r',encoding='utf-8')
#     for line in file1:
#         file.write(line)
#     file1.close()
# for fname in os.listdir("dataset/testified/"):
#     file1 = open("dataset/testified/"+fname,'r',encoding='utf-8')
#     for line in file1:
#         file.write(line)
#     file1.close()
# file.close()

with open('dataset/old/untestified/big.txt','r',encoding='utf-8') as rfile:
    with open('dataset/newbig.txt','w',encoding='utf-8') as wfile:
        for line in rfile:
            line = line.split(" ")
            if len(line[0])==2:
                wfile.write(line[0]+" ")
