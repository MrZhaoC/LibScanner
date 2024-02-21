import pymysql
from dbutils.pooled_db import PooledDB

pool = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=None,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
    maxcached=None,  # 链接池中最多闲置的链接，0和None不限制
    maxshared=3,
    # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    ping=0,
    # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
    host='localhost',
    port=3306,
    user="root",
    # password="op90OP()",
    password="zcroot",
    database="new_maven",
    # host='219.216.64.21',
    # port=3306,
    # user="root",
    # password="12345678",
    # database="java",
    charset='latin1'
)


def create_conn_cursor():
    try:
        conn = pool.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        return conn, cursor
    except Exception as e:
        print("create_cnn_cursor 错误信息：" + str(e))


def fetchall(sql):
    conn, cursor = create_conn_cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def fetchone(sql):
    try:
        conn, cursor = create_conn_cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print("fetchone 错误信息：" + str(e))


def insert(sql):
    try:
        conn, cursor = create_conn_cursor()
        res = cursor.execute(sql)
        conn.commit()
        conn.close()
    except Exception as e:
        print("insert 错误信息：" + str(e))


def insert_one(sql, val):
    try:
        conn, cursor = create_conn_cursor()
        res = cursor.execute(sql, val)
        conn.commit()
        conn.close()
    except Exception as e:
        print("insert 错误信息：" + str(e))


def insert_batch(sql, values):
    try:
        conn, cursor = create_conn_cursor()
        res = cursor.executemany(sql, values)
        conn.commit()
        conn.close()
    except Exception as e:
        print("insert 错误信息：" + str(e))


def update(sql):
    try:
        conn, cursor = create_conn_cursor()
        res = cursor.execute(sql)
        conn.commit()
        conn.close()
    except Exception as e:
        print("update 错误信息：" + str(e))


if __name__ == '__main__':
    sql = 'select group_id, artifact_id, version from google_maven_infos'
    result = fetchall(sql)
    for item in result:
        print(item)