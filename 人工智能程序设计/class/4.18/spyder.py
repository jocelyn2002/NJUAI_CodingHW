import requests
import re
from bs4 import BeautifulSoup
import time
import os
Maxthon = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                         " Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000"
           
           }
location = 'https://movie.douban.com/subject/1652592/comments?start=0&limit=20&sort=new_score&status=P'
# 'https://movie.douban.com/subject/20645098/'
i = 1
os.chdir(r'D:\desktop\pyproject1\dh\class\4.18\alita_comments')
while i > 0:
    r = requests.get(location, headers=Maxthon)
    soup = BeautifulSoup(r.text, 'lxml')
    comment_0 = soup.find_all('span', {'class': 'short'})
    file_name = str(i)+'.txt'
    file = open(file_name, 'w', encoding='utf-8')
    for item in comment_0:
        file.write(item.string)
        file.write('\n\n')
    patterns = re.compile('<a href="(.*)" data-page="" class="next">后页 >')
    p = re.findall(patterns, r.text)
    file.close()
    if p:
        location = 'https://movie.douban.com/subject/1652592/comments' + p[0]
        print(location)
        i = i+1
        time.sleep(1)
    else:
        break
print('finished')
