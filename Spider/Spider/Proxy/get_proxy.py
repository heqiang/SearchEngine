import requests
from lxml import etree



# proxy = {
#     'http': 'http://117.85.105.170:808',
#     'https': 'https://117.85.105.170:808'
# }
# '''head 信息'''
# head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
#              'Connection': 'keep-alive'}
# '''http://icanhazip.com会返回当前的IP地址'''
# res=requests.get("https://www.baidu.com",proxies=proxy,timeout=3)
# print(res.text)

# proxy = {
#     'http': 'http://117.85.105.170:808',
#     'https': 'https://117.85.105.170:808'
# }
# '''''head 信息'''
# head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
#              'Connection': 'keep-alive'}
# '''''http://icanhazip.com会返回当前的IP地址'''
# p = requests.get('http://icanhazip.com', headers=head, proxies=proxy)
# print(p.text)

def getproxy(url):
  res=requests.get(url,headers=head)
  html=etree.HTML(res.content)
  for  proxy  in  html.xpath("//table[@class='table table-bordered table-striped']/tbody/tr"):
        ip=proxy.xpath(".//td[@data-title='IP']/text()")[0]
        port=proxy.xpath(".//td[@data-title='PORT']/text()")[0]
        clean_proxy={
            "http":"http://{0}:{1}".format(ip,port),
            "https": "https://{0}:{1}".format(ip, port)
        }
        with open("proxy.txt","a") as  f:
            f.write(ip+port+"\n")
        try:
            res = requests.get("https://www.baidu.com", proxies={"http":"http://{0}:{1}".format(ip,port)}, timeout=3)
            if res.status_code==200:
                print(res.text)
                with open("proxy.txt","a") as f:
                    f.write(res.text)
            else:
                print("不可用")
        except Exception as e:
           print("不可用")
if __name__ == '__main__':
    for x in range(1,11):
        print("当前正在爬取第{}页".format(x))
        url='https://www.kuaidaili.com/free/inha/{0}/'.format(x)
        getproxy(url)
