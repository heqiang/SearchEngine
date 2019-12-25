# -*- coding: utf-8 -*-
import scrapy
from ..items import csdnitem
import  datetime
import time
import json
import re
from ..utils.common import get_md5
from fake_useragent import UserAgent


list=['java','python','sql','android','javascript','web','arch','db','game','mobile','ops','sec','cloud','fund']
ua=UserAgent()

current_time=z=datetime.datetime.now().strftime('%Y-%m-%d')
z=datetime.datetime.now().strftime('%Y-%m-%d').split('-')
header={
    'User-Agent':ua.random,
}
class CsdnSpider(scrapy.Spider):
    name = 'csdn'
    allowed_domains = ['csdn.net']
    def start_requests(self):
        for  x in range(500):
            for name in list:
                url_time=int(time.time()*1000000)
                url='https://www.csdn.net/api/articles?type=more&category={0}&shown_offset={1}'.format(name,str(url_time))
                yield scrapy.Request(url=url,callback=self.parse,headers=header)
    def parse(self, response):
        item = csdnitem()
        if response.text:
            datas=json.loads(response.text)['articles']
            for data in datas:
                item["link_url"] = data['url']
                item['title'] =data['title']
                item['content'] =data['desc']
                item['source'] = "CSDN"
                item['tag']=data['tag']
                time =data['created_at']
                if  "小时"  in time:
                    item['time'] = current_time
                elif  "天" in time:
                    day=re.match("\d+",time).group()
                    new_day=int(z[2])-int(day)
                    item['time']=z[0]+"-"+z[1]+"-"+str(new_day)

                else:
                    time = z[0] + "年" + time
                    item['time'] = time.replace("年", '-').replace("月", '-').replace("日", '')
                item['url_object_id'] = get_md5(item['link_url'])
                item['read_num'] =data['views']
                item['comment_num'] =data['comments']
                yield item



