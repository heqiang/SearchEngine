# -*- coding: utf-8 -*-
import scrapy
from ..items import five_one_ctoItem
import re
import datetime
from ..utils.common import get_md5
from scrapy_redis.spiders import RedisCrawlSpider
z=datetime.datetime.now().strftime('%Y-%m-%d').split('-')

class A51ctoSpider(scrapy.Spider):
    name = '51cto'
    allowed_domains = ['51cto.com']
    header={
        'Host': ' blog.51cto.com',
        'Connection': ' keep-alive',
        'Upgrade-Insecure-Requests': ' 1',
        'User-Agent': ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Sec-Fetch-Mode': ' navigate',
        'Accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Sec-Fetch-Site': ' none',
        'Accept-Language': ' zh-CN,zh;q=0.9,en;q=0.8,zh-HK;q=0.7',
        'Cookie': ' yd_cookie=cc00a574-7e31-405c6f77888e1c69acfd52252b2ef7d0ae81; acw_tc=b65cfd2615711895300841778e764498f4f942fc1f095d94a2db0aa79bd1ed; PHPSESSID=2dsdrp4q313256vm10fciisfev; showMsgOver=1; blog_activity_blog95=1; gr_user_id=c156ef30-27d9-4181-a209-20f6ee751594; gr_session_id_8c51975c40edfb67=ac6ea49f-d60b-4ac9-818f-9a3d09804692; Hm_lvt_2283d46608159c3b39fc9f1178809c21=1571189532; Hm_lpvt_2283d46608159c3b39fc9f1178809c21=1571189532; gr_session_id_8c51975c40edfb67_ac6ea49f-d60b-4ac9-818f-9a3d09804692=true; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1',
    }
    # redis_key = "51cto.spider:start_urls"
    def start_requests(self):#url='https://blog.51cto.com/original'
        url='https://blog.51cto.com/artcommend/p300'
        yield scrapy.Request(url=url,callback=self.url_parse,headers=self.header)
    #列表url解析 传递了标题url  收藏数 阅读数 评论数
    def  url_parse(self,response):
        for article in response.xpath('//ul[@class="artical-list"]/li'):
            url=article.xpath(".//a[@class='tit']/@href").extract()[0]
            Collection_num = article.xpath('.//div[@class="bot"]/span[3]/text()').extract()
            Collection_num= re.findall("\d+", Collection_num[0])[0]
            read_num = article.xpath('.//div[@class="bot"]/span[1]/text()').extract()
            read_num = re.findall("\d+", read_num[0])[0]
            comment_num = article.xpath('.//div[@class="bot"]/span[2]/text()').extract()
            comment_num = re.findall("\d+", comment_num[0])[0]
            yield scrapy.Request(url=url,callback=self.parse,meta={"link_url":url,
                                                                   "Collection_num":Collection_num,
                                                                   "read_num":read_num,
                                                                   "comment_num":comment_num
                                                                   },headers=self.header)
        #列表翻页
        next_page = response.xpath("//li[@class='next']/a/@href").extract()
        if next_page:
            url = next_page[0]
            page_num = re.findall('p\d+', url)[0].replace('p', '')
            print("正在爬取" + page_num + "页")
            yield scrapy.Request(url=url, callback=self.url_parse,headers=self.header)
    #详情解析
    def parse(self, response):
       item=five_one_ctoItem()
       item['title'] = response.xpath("//h1[@class='artical-title']/text()").extract()[0]
       item['link_url'] = response.meta['link_url']
       content = response.xpath("//div[@class='con artical-content editor-preview-side']//text()").extract()
       item['content'] =','.join(content).strip()
       item['time'] = response.xpath("//a[@class='time fr']/text()").extract()[0]
       item['Collection_num'] = response.meta['Collection_num']
       item['read_num'] = response.meta['read_num']
       item['comment_num'] = response.meta['comment_num']
       item['source'] = "51cto"
       item['url_object_id'] = get_md5(item['link_url'])
       item['tag']= ",".join(response.xpath("//div[@class='for-tag mt26']/a/text()").extract())
       yield item
