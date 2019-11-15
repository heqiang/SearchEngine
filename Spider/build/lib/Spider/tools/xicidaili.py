import  requests
from scrapy.selector import Selector
from fake_useragent import UserAgent
from lxml import etree
from Spider.Spider.tools.conn_datebase import ConnDatabase
from Spider.Spider.tools.getip import GetIp


ua=UserAgent()

def get_ip():
    for x in range(1,3580):
        res=GetIp().get_random_ip()
        url='https://www.xicidaili.com/nn/{0}'.format(x)
        header={
            "User-Agent":ua.random
        }
        proxy_dict = {
            "HTTP": res,
            "HTTP": res
        }
        res = requests.get(url, headers=header, proxies=proxy_dict)

        if res.status_code==200:
            html=etree.HTML(res.text)
            all_ip=html.xpath("//table[@id='ip_list']/tr")
            for x  in all_ip[1:]:
                ip=x.xpath(".//td[2]/text()")[0]
                port=x.xpath(".//td[3]/text()")[0]
                category=x.xpath(".//td[6]/text()")[0]
                ConnDatabase(ip,port,category)
