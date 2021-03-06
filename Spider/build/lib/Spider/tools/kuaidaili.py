import  requests
from scrapy.selector import Selector
from fake_useragent import UserAgent
from lxml import etree
from Spider.Spider.tools.conn_datebase import ConnDatabase
from Spider.Spider.tools.getip import GetIp
from fake_useragent import  UserAgent

ua=UserAgent()
def get_ip():
    for x in range(30, 1300):
        res = GetIp().get_random_ip()
        url = 'https://www.kuaidaili.com/free/inha/{0}/'.format(x)
        header = {
            "User-Agent": ua.random
        }
        proxy_dict={
            "HTTP":res,
            "HTTP":res
        }
        res = requests.get(url, headers=header,proxies=proxy_dict)
        if res.status_code == 200:
            html = etree.HTML(res.text)
            all_ip = html.xpath("//table[@class='table table-bordered table-striped']/tbody/tr")
            for x in all_ip:
                ip = x.xpath(".//td[1]/text()")[0]
                port = x.xpath(".//td[2]/text()")[0]
                category = x.xpath(".//td[4]/text()")[0]
                print("{0}://{1}:{2}".format(category,ip,port))
                ConnDatabase(ip, port, category)
if __name__ == '__main__':
    get_ip()