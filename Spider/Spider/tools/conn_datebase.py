import  pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='1422127065',
    db='bishe',
    charset='utf8'
)
cursor = conn.cursor()


def ConnDatabase(ip,port,category):
    insert_sql = 'insert into proxy_ip(ip,port,category) values("{0}","{1}","{2}")'.format(ip, port, category)
    cursor.execute(insert_sql)
    res=cursor.rowcount()
    print(res)
    conn.commit()