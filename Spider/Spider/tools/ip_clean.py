import pymysql
from fake_useragent import UserAgent
import requests
import threading
# import ThreadClass


conn=pymysql.connect(
    host='localhost',
    user='root',
    password='1422127065',
    db='bishe',
    charset='utf8'
)

cursor=conn.cursor()

ua=UserAgent()


def delete(ip):
    print("-|开始删除无用ip:{0}".format(ip))
    delete_sql = 'delete  from proxy_ip where ip="{0}"'.format(ip)
    cursor.execute(delete_sql)
    conn.commit()
    return True

def jundge_ip(ip, port, category):
    print("开始判断ip:{}".format(ip))
    http_url = "https://www.baidu.com/"
    proxy_url = "{0}://{1}:{2}".format(category, ip, port)
    try:
        proxy_dict = {
            "http": proxy_url,
            "https": proxy_url
        }
        res = requests.get(http_url, proxies=proxy_dict, timeout=3)
    except Exception as e:
        delete(ip)
        return False
    else:
        code = res.status_code
        if code == 200:
            print("-|可用ip:{0}".format(ip))
            return True
        else:
            print("-|不可用ip:{0}".format(ip))
            delete(ip)
def clean_ip():
    get_all_ip="select ip,port,category from proxy_ip "
    result=cursor.execute(get_all_ip)
    for res in cursor.fetchall():
        ip = res[0]
        port = res[1]
        category = res[2]
        # return  ip,port,category
        jundge_ip(ip, port, category)

# threads=[]
# clean_ip_threading=threading.Thread(target=clean_ip)


if __name__ == '__main__':
    clean_ip()