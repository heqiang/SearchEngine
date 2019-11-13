import time
import re
import datetime
import pymysql
import jieba
import jieba.analyse
from elasticsearch import Elasticsearch
from collections import Counter
import pandas as pd
# firsttime=time.strftime("%Y-%m-%d", time.localtime())
# lasttime=time.strftime("%H:%M:%S", time.localtime())
# new_firsttime=firsttime.split("-")
# new_lasttime=lasttime.split(":")
# print(firsttime)
# print(new_lasttime)
#
# list= ['\napple',
#              '\n'
#              '時代革命, 光復香港, 跟暴亂暴動扯在一起, 那些以時代革命光復香港為其政治宣言的人, 不可以參選, 因為他們傾向犯法, '
#              '擾亂香港公共秩序\n']
# # print(list[1])
# PublishTime='2019-07-1' #26分鐘前  1天前
# if "小時" in PublishTime:
#     hour=re.match('\d+',PublishTime).group()
#     new_time=datetime.datetime.now()+datetime.timedelta(hours=-int(hour))
#     print(new_time.strftime("%Y-%m-%d %H:%M:%S"))
# elif "分鐘"in PublishTime :
#     minu = re.match('\d+', PublishTime).group()
#     new_time=datetime.datetime.now()+datetime.timedelta(minutes=-int(minu))
#     print(new_time.strftime("%Y-%m-%d %H:%M:%S"))
# elif "天" in PublishTime:
#     day=re.match("\d+",PublishTime).group()
#     new_time=datetime.datetime.now()+datetime.timedelta(days=-int(day))
#     print(new_time.strftime("%Y-%m-%d %H:%M:%S"))
# else:
#     PublishTime=PublishTime+" "+"{0}:{1}:{2}".format(00,00,00)
#     new_time=datetime.datetime.strptime(PublishTime,"%Y-%m-%d %H:%M:%S")
#     print(new_time)
# #
client=Elasticsearch(hosts=["127.0.0.1"])
conn=pymysql.connect(
    host='localhost',
    user='root',
    password='1422127065',
    db='bishe',
    charset="utf8"
)
cur=conn.cursor()
list_words=[]
def get_keywords():
    select_sql="select searchtitle from  user_search where user_id=11"
    cur.execute(select_sql)
    for x in cur.fetchall():
        seg_list=jieba.analyse.extract_tags(x[0],topK=20)
        if len(seg_list)>1:
            for x  in seg_list:
                list_words.append(x.lower())

    conn.close()
if __name__ == '__main__':
    get_keywords()
    res=Counter(list_words)

    for x in res.most_common(10):
        print(x[0])
        print(x[1])
