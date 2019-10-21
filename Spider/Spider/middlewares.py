# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import time
from .settings import IPPOOL
# from .utils.get_proxy import get_proxy


class  RandomProxy(object):
    def process_request(self,request,spider):
        proxy=random.choice(IPPOOL)
        print("当前使用的代理是："+proxy['ip'])
        if request.url.startswith("http://"):
            request.meta['proxy']="http://"+proxy['ip']+":"+proxy['port']
        elif request.url.startswith("https://"):
            request.meta['proxy'] = "https://" + proxy['ip'] + ":" + proxy['port']