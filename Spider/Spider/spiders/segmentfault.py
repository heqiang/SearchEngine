# -*- coding: utf-8 -*-
import scrapy
from ..items import Segmentfault
from ..utils.common import get_md5
import re
import datetime
from fake_useragent import UserAgent
import time
import logging
from scrapy_redis.spiders import RedisCrawlSpider
ua=UserAgent()

header={
    'User-Agent':ua.random
}
z=datetime.datetime.now().strftime('%Y-%m-%d')
new_z=z.split('-')
class SegmentfaultSpider(scrapy.Spider):
    name = 'segmentfault'
    allowed_domains = ['segmentfault.com']
    start_urls = ['https://segmentfault.com/blogs/newest?page=3200']
    # redis_key = "segmentfault.spider:start_urls"
    def parse(self, response):
         link_urls=response.xpath("//h2[@class='title blog-type-common blog-type-1']/a/@href").extract()
         for link_url in link_urls:
                 link_url="https://segmentfault.com"+link_url
                 yield scrapy.Request(url=link_url,callback=self.detail_parse,meta={"link_url":link_url},headers=header)
         next_page=response.xpath("//a[@rel='next']/@href").extract()
         next_page_num=re.search("\d+", next_page[0]).group()
         if next_page:
             print("正在爬取第{0}页".format(next_page_num))
             url="https://segmentfault.com"+next_page[0]
             time.sleep(3)
             logging.info("正在爬取第{0}页".format(next_page_num))
             yield scrapy.Request(url=url,callback=self.parse)
    def detail_parse(self,response):
         item=Segmentfault()
         item["title"] = response.xpath("//h1[@id='articleTitle']/a/text()").extract()[0]
         time= response.xpath("//div[@class='article__authorright']/span/text()").extract()
         new_time=time[0].strip()
         if "分钟" or "小时" in new_time:
                item["time"]=z
         elif "天" in new_time:
             new_t=re.search("\d+", new_time).group()
             #获取发布时间的天数
             new_day=int(new_z[2])-int(new_t)
             item["time"]="{0}-{1}-{2}".format(new_z[0],new_z[1],new_day)
         else:
             item["time"]=new_time
         content= response.xpath("//div[@class='article fmt article__content']//text()").extract()
         item["content"]=",".join(content).strip()
         item["link_url"] = response.meta['link_url']
         item["url_object_id"] =get_md5(item["link_url"])
         item["source"] = "segmentfault"
         tag = response.xpath("//li[@class='tagPopup mb5']/a/text()").extract()
         item["tag"]=",".join(tag).replace("\n","").replace(" ","").strip(",")
         read_num= response.xpath("//div[@class='content__tech hidden-xs']/span/text()").extract()
         item["read_num"]=re.search("\d+",",".join(read_num[0])).group()
         yield item