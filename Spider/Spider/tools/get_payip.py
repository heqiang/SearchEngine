import requests
import   json
import re
#api  json格式的ip获取


def get_pay_ip(url):
    res=requests.get(url)
