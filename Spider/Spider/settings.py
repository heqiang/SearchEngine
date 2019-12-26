# -*- coding: utf-8 -*-

# Scrapy settings for Spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Spider'

SPIDER_MODULES = ['Spider.spiders']
NEWSPIDER_MODULE = 'Spider.spiders'


ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1  #设置时间间隔为1s，防止被禁
DOWNLOAD_TIMEOUT = 5 #设置超时时间
RETRY_ENABLED = True #设置开启重试
RETRY_TIMES = 3 #设置重试次数

DOWNLOADER_MIDDLEWARES = {
   'Spider.middlewares.SpiderDownloaderMiddleware': None,
    'Spider.middlewares.Uamid': 300,
    # 'Spider.middlewares.RandomProxy':10

}


ITEM_PIPELINES = {
       'scrapy_redis.pipelines.RedisPipeline': 2,
        'Spider.pipelines.ElasticsearchPipeline': 4
    }
#
#布隆过滤
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
REDIS_URL = 'redis://localhost:6379/1'
BLOOMFILTER_HASH_NUMBER = 6
BLOOMFILTER_BIT = 30
SCHEDULER_PERSIST = True



#scrapy-redis


# REDIS_HOST = "localhost"
# # # 指定数据库的端口号
# REDIS_PORT = 6379
#
# #使用scrapy-redis的去重组件，不使用scrapy默认的去重
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# #使用scrapy-redis的调度组件，不使用scrapy的默认调度器
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# #使用队列形式
# SCHEDULER_QUEUE_CLASS="scrapy_redis.queue.SpiderQueue"
# #允许暂停，redis请求记录不丢失
# SCHEDULER_PERSIST = True

