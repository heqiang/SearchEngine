# -*- coding: utf-8 -*-
import scrapy
from  fake_useragent  import UserAgent
from ..items import WannnegSqlItem
ua=UserAgent()


class Top250Spider(scrapy.Spider):
    name = 'top250'
    allowed_domains = ['douban.com']

    def __init__(self):
        self.header={
            "User-Agent":ua.random
        }
    def start_requests(self):
        url='https://movie.douban.com/top250'
        yield scrapy.Request(url=url,callback=self.parse,headers=self.header)
    def parse(self, response):
        item=WannnegSqlItem()
        for  x in response.xpath("//ol[@class='grid_view']/li"):
            item['title']=x.xpath(".//div[@class='hd']/a/span[1]/text()").extract()[0]
            item['comment'] = x.xpath(".//div[@class='star']/span[last()]/text()").extract()[0]
            item['link'] = x.xpath(".//div[@class='hd']/a/@href").extract()[0]
            item['quote'] = x.xpath(".//p[@class='quote']/span/text()").extract()[0]
            item['rank'] = x.xpath(".//span[@class='rating_num']/text()").extract()[0]
            yield item
        next_page=response.xpath("//link[@rel='next']/@href").extract()
        if next_page:
            next_page_url='https://movie.douban.com/top250'+next_page[0]
            yield scrapy.Request(next_page_url,callback=self.parse,headers=self.header)


