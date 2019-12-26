# -*- coding: utf-8 -*-
import scrapy
from ..items import iteye
from ..utils.common import get_md5
import re
from datetime import datetime

class IteyeSpider(scrapy.Spider):
    name = 'iteye'
    allowed_domains = ['iteye.com']
    start_urls = ['https://www.iteye.com/ask?page=42']

    def parse(self, response):
        page=re.findall("\d+", response.url)
        if  page:
            print("正在爬取第{0}页".format(page[0]))
        for x  in response.xpath("//div[@id='ask_list']/div/div[@class='summary']/h3/a/@href").extract():
             url="https://www.iteye.com"+x
             yield scrapy.Request(url,callback=self.detail,dont_filter=True)
        next_page=response.xpath("//a[@class='next_page']/@href").extract()
        if next_page:
            url = "https://www.iteye.com" + next_page[0]
            yield scrapy.Request(url,callback=self.parse,dont_filter=True)

    def detail(self,response):
        item=iteye()
        item['title'] = ",".join(response.xpath("//h3/a/text()").extract())
        item['tags'] = ",".join(response.xpath("//div[@class='tags']/a/text()").extract())
        time_= response.xpath("//div[@class='ask_label']/span/text()").extract()
        new_time=time_[0].replace(r'年', '-').replace(r'月', '-').replace(r'日', '')
        item['time']=datetime.strptime(new_time, '%Y-%m-%d %H:%M')
        item['content'] = ".".join(response.xpath("//div[@class='new_content']//text()").extract()).strip()
        item['link_url'] = response.url
        item['url_object_id'] = get_md5(response.url)
        item['source'] = 'iteye'
        yield item
