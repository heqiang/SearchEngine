# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import time
from .utils.get_proxy import get_proxy
from .tools.getip import GetIp
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from  fake_useragent import UserAgent


#s随机代理
class  RandomProxy(object):
    def process_request(self,request,spider):
       get_ip=GetIp()
       request.meta['proxy']=get_ip.get_random_ip()


#随机请求头
class Uamid(UserAgentMiddleware):
    # 初始化 必须加User_agent
    def __init__(self, user_agent=""):
        self.user_agent = user_agent

    # 请求处理
    def process_request(self, request, spider):
        # 随机选择代理
        ua = UserAgent(verify_ssl=False)
        print("当前User_Agent是：" + ua.random)
        request.headers.setdefault('User-Agent', ua.random)  # 请求的request带上ua

