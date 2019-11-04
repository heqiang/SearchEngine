from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from  fake_useragent import UserAgent


class Uamid(UserAgentMiddleware):
     #初始化 必须加User_agent
     def __init__(self,user_agent=""):
         self.user_agent=user_agent
     #请求处理
     def process_request(self, request, spider):
         #随机选择代理
         ua=UserAgent(verify_ssl=False)
         print("当前User_Agent是："+ua.random)
         request.headers.setdefault('User-Agent',ua.random)#请求的request带上ua
         # request.proxy
