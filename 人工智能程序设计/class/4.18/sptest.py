import requests
import re
from bs4 import BeautifulSoup
import time
import os
location = 'https://movie.douban.com/subject/1652592/comments?start=220&amp;limit=20&amp;sort=new_score&amp;status=P&amp;percent_type='
r = requests.get(location)
patterns = re.compile('<a href="(.*)" data-page="" class="next">后页 >')
p = re.findall(patterns, r.text)
print(r.text)
print(p)