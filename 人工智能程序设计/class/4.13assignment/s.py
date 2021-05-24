                                                               #zhaoshu
# with open(r'D:\desktop\pi.txt') as file1:
#     p = file1.read()
#     if '1010' in p:
#         print('yeah!!!')
#     else:
#         print('no!!!')
                                                               #huiwenshu
# x = input()
# with open(r'D:\desktop\ssin.txt', 'w') as file2:
#     a = x+x[::-1]
#     file2.write(a)

                                                               # insert
# with open(r'D:\desktop\ssin.txt', 'r+') as file3:
#     p = file3.read()
#     file3.seek(0)
#     j = input()
#     file3.write(j+'\n')
#     file3.write(p)
                                                             # char
# with open(r'D:\desktop\ssin.txt', 'r+') as file4:
#     num_of_lines = len(file4.readlines())

# import os
# import shutil
# import time
# os.chdir(r'D:\desktop')
# for i in range(1, 1000):
#     if os.path.exists('aswekan'):
#         shutil.rmtree('aswekan')
#     else:
#         os.mkdir('aswekan')
#     time.sleep(0.01)

# import pandas as pd
# import os
# os.chdir(r'D:\desktop')
# data = pd.DataFrame({'name': ['a', 'b', 'c', 'd'], 'age': [1, 2, 3, 4]})
# data.to_excel('score.xlsx', sheet_name='score')

# import json
# import os
# import pandas as pd
# os.chdir(r'D:\desktop\ndb_total\ndb_total')
# with open('01001.json') as f:
#     data = json.load(f)
#     data = pd.DataFrame(data)
#     print(data)

# with open(r'D:\desktop\ssin.txt') as f:
#     lines = f.readlines()
#     for i in range(0, len(lines)):
#         lines[i] = lines[i][:-1]
#         lines[i] += '-'+lines[i][::-1]+'\n'
# with open(r'D:\desktop\ssin.txt', 'w') as f:
#     f.writelines(lines)

