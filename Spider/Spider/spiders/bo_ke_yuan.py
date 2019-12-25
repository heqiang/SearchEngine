# -*- coding: utf-8 -*-
import scrapy
from ..items import BokeYuanItem
import  re
from ..utils.common import get_md5
from scrapy_redis.spiders import RedisCrawlSpider

class BoKeYuanSpider(scrapy.Spider):
    name = 'bo_ke_yuan'
    allowed_domains = ['cnblogs.com']
    # redis_key = "bo_ke_yuan.spider:start_urls"
    def start_requests(self):
        list = ['https://www.cnblogs.com/', 'https://www.cnblogs.com/pick/', 'https://www.cnblogs.com/candidate/']
        for url in list:
            yield scrapy.Request(url=url, callback=self.parse)
    #列表解析
    def parse(self, response):
        for url  in response.xpath('//div[@id="post_list"]/div'):
            url=url.xpath(".//a[@class='titlelnk']/@href").extract()[0]
            yield scrapy.Request(url=url,callback=self.detail_parse)
        next_page=response.xpath("//div[@class='pager']/a[contains(text(),'Next')]/@href").extract()
        if next_page:
            url='https://www.cnblogs.com'+next_page[0]
            page_num=re.findall('\d+', next_page[0])[0]
            print("当前正在爬取第{0}页".format(page_num))
            yield scrapy.Request(url,callback=self.parse)
    #详情解析
    def detail_parse(self,response):
        item = BokeYuanItem()
        for acticle in response.xpath('//div[@id="post_list"]/div'):
            item['title'] = acticle.xpath(".//a[@class='titlelnk']/text()").extract()[0]
            item['link_url'] = acticle.xpath(".//a[@class='titlelnk']/@href").extract()[0]
            content = acticle.xpath(".//p[@class='post_item_summary']/text()").extract()
            item['content'] = ",".join(content).strip()
            item['source'] = 'BoKeYuan'
            time = acticle.xpath(".//div[@class='post_item_foot']/text()").extract()
            item['time'] = time[1].replace('发布于', '').strip()
            # 评论数
            comment_num = acticle.xpath(".//span[@class='article_comment']/a/text()").extract()
            comment_num = re.findall("\d+", comment_num[0])
            item['comment_num'] = comment_num[0]
            # 阅读数
            read_num = acticle.xpath(".//span[@class='article_view']/a/text()").extract()
            read_num = re.findall("\d+", read_num[0])
            item['read_num'] = read_num[0]
            item['url_object_id'] = get_md5(item['link_url'])
            yield item