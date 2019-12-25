# -*- coding: utf-8 -*-
import scrapy
from ..items import Aliyun_tec
from ..utils.common import get_md5
from scrapy_redis.spiders import RedisCrawlSpider

class AnswerSpider(scrapy.Spider):
    name = 'answer'
    allowed_domains = ['aliyun.com']
    start_urls = ['https://yq.aliyun.com/zt/articles-554317?spm=a2c4e.11155472.0.0.45a94cff54IU3g']
    # redis_key = "aliyun.spider:start_urls"
    def parse(self, response):
        for  x in  response.xpath("//section[@class='yq-new-list yq-n-l-blog']/div/a/@href").extract():
            url='https://yq.aliyun.com/'+x
            yield scrapy.Request(url,callback=self.detail)
        next_page=response.xpath("//div[@class='y-page-list']/a[last()]/@href").extract()
        if  next_page:
                url='https://yq.aliyun.com'+next_page[0]
                yield  scrapy.Request(url,callback=self.parse)
    def detail(self,response):
        item=Aliyun_tec()
        item['title']="".join(response.xpath("//h2[@class='blog-title']/text()").extract()).strip()
        item['tags'] = ",".join(response.xpath("//ul[@class='tag-group']/li/a/span/text()").extract())
        item['time'] = response.xpath("//span[@class='b-time icon-shijian1']/text()").extract()[0]
        item['content'] = "".join(response.xpath("//div[@class='content-detail unsafe markdown-body']/p/text()").extract())
        item['link_url'] = response.url
        item['url_object_id'] = get_md5(response.url)
        item['source'] = '阿里云网络技术论坛 '
        yield item



