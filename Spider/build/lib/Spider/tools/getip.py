import pymysql
from fake_useragent import UserAgent
import requests
from lxml import etree


conn=pymysql.connect(
    host='localhost',
    user='root',
    password='1422127065',
    db='bishe',
    charset='utf8'
)

cursor=conn.cursor()

ua=UserAgent()



class GetIp(object):
    # 无效ip删除
    def delete(self, ip):
        delete_sql = 'delete  from proxy_ip where ip={0}'.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    # ip判断
    def jundge_ip(self, ip, port, category):
        http_url = "https://www.baidu.com/"
        proxy_url = "{0}://{1}:{2}".format(category, ip, port)
        try:
            proxy_dict = {
                "http": proxy_url
            }
            res = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            self.delete_ip(ip)
            return False
        else:
            code = res.status_code
            if code >= 200 and code < 300:
                print("可用ip")
                return True
            else:
                print("不可用ip")
                self.delete_ip(ip)

    def get_random_ip(self):
        # 随机获取一个ip
        ranodm_sql = 'select ip,port,category FROM  proxy_ip ORDER BY RAND() LIMIT 1'
        result = cursor.execute(ranodm_sql)
        for res in cursor.fetchall():
            print(res)
            ip = res[0]
            port = res[1]
            category = res[2]
            jundge = self.jundge_ip(ip, port, category)
            if jundge:
                return "{0}://{1}:{2}".format(category, ip, port)
            else:
                return self.get_random_ip()
if __name__ == '__main__':
    res=GetIp().get_random_ip()
    print(res)