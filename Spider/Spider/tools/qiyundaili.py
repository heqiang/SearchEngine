import  requests
from lxml import etree
from Spider.Spider.tools.conn_datebase import ConnDatabase
from Spider.Spider.tools.getip import GetIp
from fake_useragent import  UserAgent
import  re
ua=UserAgent()

def get_ip(url):
        page=re.findall("\d+",url)
        print("正在抓取第{0}页".format(page[0]))
        # header = {
        #         #     "User-Agent": ua.random
        #         # }    , headers=header
        res = requests.get(url)
        if res.status_code == 200:
            html = etree.HTML(res.text)
            all_ip = html.xpath("//table[@class='table table-bordered table-striped']/tbody/tr")
            for x in all_ip:
                if '高匿' in x.xpath(".//td[3]/text()"):
                    try:
                        ip = x.xpath(".//td[1]/text()")
                        if  ip:
                            ip=ip[0]
                            port = x.xpath(".//td[2]/text()")[0]
                            category = x.xpath(".//td[4]/text()")[0]
                            print("{0}://{1}:{2}".format(category,ip,port))
                            ConnDatabase(ip, port, category)
                    except Exception as e:
                         print("error_url:"+url)
                         continue
if __name__ == '__main__':
    # for x in range(23, 1300):
        url='https://www.qydaili.com/free/?action=china&page=95'
        # url = 'http://www.qydaili.com/free/?action=china&page={0}'.format(x)
        get_ip(url)
