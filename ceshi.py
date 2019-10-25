# import time
# import re
# import datetime
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
