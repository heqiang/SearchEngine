# -*- coding: utf-8 -*-
import scrapy
from   ..items import oschina
import datetime
import re
from ..utils.common import get_md5
from scrapy_redis.spiders import RedisCrawlSpider
z=datetime.datetime.now().strftime('%Y-%m-%d').split('-')
class OschinaSpider(scrapy.Spider):
    name = 'oschina'
    allowed_domains = ['oschina.net']
    # start_urls = ['http://oschina.net/']

    def start_requests(self):
        for x in  range(500,503):
            url='https://www.oschina.net/blog/widgets/_blog_index_recommend_list?classification=0&p={0}&type=ajax'.format(x)
            print("正在爬取第{0}页".format(str(x)))
            yield scrapy.Request(url=url,callback=self.parse)
    def parse(self, response):
        link_urls=response.xpath("//div[@class='item blog-item']/div[@class='content']/a/@href").extract()
        for link_url  in link_urls:
            yield scrapy.Request(link_url,callback=self.detail_parse,meta={"link_url":link_url})

    def detail_parse(self,response):
         item=oschina()
         title=response.xpath('//h2[@class="header"]/text()').extract()
         item['title']=title[0].strip()
         with open("oschina.txt",'a') as f:
             f.write(item['title']+"\n")
         time= response.xpath("//div[@class='extra ui horizontal list meta-wrap']/div[1]/text()").extract()
         time=time[1].strip().replace("发布于","")
         if len(time)<17:
                 time=re.findall("\d+",time)
                 item['time']="{0}-{1}-{2}".format(z[0],time[0],time[1])
         else:
             item['time']=time
         item['content'] = ','.join(response.xpath('//div[@id="articleContent"]//text()').extract()).strip()
         # =content.replace("\n","").split()
         item['link_url'] = response.meta['link_url']
         item['url_object_id'] =get_md5(item['link_url'])
         item['source'] = "OSCHINA"
         item['comment_num'] = response.xpath("//div[@class='extra ui horizontal list meta-wrap']/div[6]/a/span/text()").extract()[0]
         item['Collection_num'] = response.xpath("//div[@class='extra ui horizontal list meta-wrap']/div[4]/span/text()").extract()[0]  # 收藏数
         read_num = response.xpath("//div[@class='extra ui horizontal list meta-wrap']/div[3]/text()").extract()
         item['read_num']=re.findall("\d+",read_num[0])[0]
         item['praise_num'] = response.xpath("//div[@class='extra ui horizontal list meta-wrap']/div[5]/a/span/text()").extract()[0]
         tag= response.xpath("//div[@class='tags']//a/text()").extract()
         item['tag']=','.join(tag)
         yield item