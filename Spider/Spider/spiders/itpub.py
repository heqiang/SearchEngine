# -*- coding: utf-8 -*-
import scrapy
from ..items import itpubItem
import json
from scrapy.http import FormRequest
from ..utils.common import get_md5
from fake_useragent import UserAgent
import time

ua=UserAgent()
class ItpubSpider(scrapy.Spider):
    name = 'itpub'
    allowed_domains = ['itpub.net']
    def start_requests(self):
        for  x  in  range(200,500):
            random_time = int(time.time() * 1000000)
            data={
                'categoryid': '0',
                'subcategoryid': '0',
                'type': '0',
                'lasttime': '1565660229',
                'page': str(x),
                '_t': str(random_time)
            }
            url="https://z.itpub.net/api/v1/topicinfo/list"
            yield FormRequest(url,formdata=data,callback=self.detail_parse)
            print("正在发起第{0}次请求".format(str(x-2)))


    def detail_parse(self, response):
       if response.text:
            datas=json.loads(response.text)['data']['items']#十条数据
            if datas:
                for  data  in datas:
                  link_url='https://z.itpub.net/topic/'+str(data['id'])
                  tag= data['subcategoryname']
                  comment_num = data['comments']
                  yield scrapy.Request(url=link_url,callback=self.parse,meta={'link_url':link_url,
                                                                                     'comment_num':comment_num,
                                                                                     'tag':tag
                                                                                     })
    def parse(self,response):
        item = itpubItem()
        item["title"] =response.xpath("//div[@class='wenzhang_box']/h1/text()").extract()[0]
        item['link_url']=response.meta['link_url']
        content=response.xpath("//div[@class='main']/p/text()").extract()
        item["content"]=','.join(content)
        item["time"] = response.xpath("//div[@class='time3']/i/text()").extract()[0]
        item['source'] = 'itpub技术栈'
        item['url_object_id']=get_md5(item['link_url'])
        item['comment_num'] = response.meta['comment_num']  # 评论数
        item['tag']=response.meta['tag']
        yield item
