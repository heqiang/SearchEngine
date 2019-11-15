import requests
import json
import time
url='http://lab.crossincode.com/proxy/get/?num=10&head=https'

def get_proxy():
    time.sleep(3)
    proxy_text=requests.get(url)
    get_proxy=json.loads(proxy_text.text)['proxies']
    proxy_list=[]
    for  proxy in get_proxy:
         proxy=proxy['https']
         proxy_list.append(proxy)
    return proxy_list
