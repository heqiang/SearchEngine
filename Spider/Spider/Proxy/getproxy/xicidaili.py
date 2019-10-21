import  requests
from  lxml import etree
from fake_useragent import UserAgent
ua=UserAgent()
import  json
# def kuaidaili(url):
#     header={
#         "User-Agent":ua.random,
#     }
#     res=requests.get(url,headers=header)
#     html=etree.HTML(res.content)
#     for proxy  in html.xpath("//table[@class='table table-bordered table-striped']/tbody/tr"):
#         ip=proxy.xpath('.//td[@data-title="IP"]/text()')
#
#         port=proxy.xpath('.//td[@data-title="PORT"]/text()')
#         proxy_baidu={
#             "http":"http://"+ip[0]+":"+port[0],
#             "https":"https://"+ip[0]+":"+port[0]
#         }
#         res=requests.get("https://www.baidu.com/",proxies=proxy_baidu,timeout=3)
#         if res.status_code==200:
#             print("可用")
#         else:
#             print("不可用")
# if __name__ == '__main__':
#     for x in range(3000):
#         url = 'https://www.kuaidaili.com/free/inha/{0}/'.format(x)
#         kuaidaili(url)
url='http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=0277c1b58f7f45e7bac8aab81727321a&count=10&expiryDate=0&format=1&newLine=2'
res=requests.get(url)
datas=json.loads(res.text)['msg']
for data in datas:
    print(data)
