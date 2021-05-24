import requests
# r = requests.get('http://www.baidu.com')
# print(r.status_code) #状态
# #print(r.text[200:520]) #内容
# print(r.content)
# #r.encoding = 'utf8'
# r.encoding = r.apparent_encoding
# print(r.text)

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                         " Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000"}
# r = requests.get('https://book.douban.com/subject/1084336/comments/', headers=headers)
# print(r.text)

from bs4 import BeautifulSoup
import re
r = requests.get('https://book.douban.com/subject/1084336/comments/', headers=headers)
soup = BeautifulSoup(r.text, 'lxml')
# pattern = re.compile(r'user-stars')
# p = pattern.findall(soup.text)
# print(p)
