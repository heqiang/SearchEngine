import pymysql
from fake_useragent import UserAgent
import requests
from lxml import etree

conn=pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    db='database',
    charset='utf8'
)
cursor=conn.cursor()
ua=UserAgent()
class GetIp(object):
    # 无效ip删除
    def delete(self, ip):
        delete_sql = 'delete  from proxy_ip where ip="{0}"'.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    # ip判断
    def jundge_ip(self, ip, port, category):
        http_url = "https://www.baidu.com/"
        proxy_url = "{0}://{1}:{2}".format(category, ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
                "https":proxy_url
            }
            res = requests.get(http_url, proxies=proxy_dict,timeout=3)
        except Exception as e:
            self.delete(ip)
            return False
        else:
            code = res.status_code
            if code==200:
                print("可用ip:{0}://{1}:{2}".format(category, ip, port))
                return True
            else:
                print("不可用ip")
                self.delete(ip)

    def get_random_ip(self):
        # 随机获取一个ip
        ranodm_sql = 'select ip,port,category FROM  proxy_ip ORDER BY RAND() LIMIT 1'
        result = cursor.execute(ranodm_sql)
        for res in cursor.fetchall():

            ip = res[0]
            port = res[1]
            category = res[2]
            #代理判断是否有效
            jundge = self.jundge_ip(ip, port, category)
            if jundge:
                proxy="{0}://{1}:{2}".format(category, ip, port)
                return  proxy
            else:
                return self.get_random_ip()
if __name__ == '__main__':
    GetIp().get_random_ip()
