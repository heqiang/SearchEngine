import  pymysql
import requests


# conn = pymysql.connect(
#     host="localhost",
#     user="root",
#     passwd="1422127065",
#     database="search_engine"
# )

# def  get_ip():

    # cur=conn.cursor()
    # sql="SELECT id,ip,port from xi_ci_ip"
    # cur.execute(sql)
    # data=cur.fetchall()
    # for  x in data:
    #     id=x[0]
    #     #     ip=x[1]
    #     #     port=x[2]
proxy = {
     'http':'http://122.242.131.41:9000',
     'https':'https://171.35.161.106:9999'
}
try:
    res = requests.get('https://www.baidu.com/', porxies=proxy, timeout=3)
    print('能使用')
except Exception as e:
    print("不能使用")
    #         sql="DELETE  from  xi_ci_ip  WHERE  id="+str(id)
    #         cur.execute(sql)
    #         conn.commit()
    #         print(ip+"-已删除")
    # conn.close()
if __name__ == '__main__':
    # get_ip()
    pass
