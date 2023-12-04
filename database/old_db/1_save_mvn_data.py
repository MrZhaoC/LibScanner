import json
import threading
import time

import pymysql

db = pymysql.connect(host='localhost',
                     user='root',
                     password='zcroot',
                     database='maven_repo',
                     charset='utf8',
                     autocommit=True)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()


def insert_tpl_data(data):
    # 判断插入数据是否存在数据库
    query_data = query_tpl_data()

    time_s = time.perf_counter()
    # 求两个集合的差
    insert_data = data.difference(query_data)
    time_e = time.perf_counter()
    print("排除已经存在数据库中的数据，用时(s)==>", time_e - time_s)
    # 排序
    t = sorted(insert_data, key=lambda x: (x[0], x[1], x[2]), reverse=False)

    # 批量插入数据
    sql = "insert into maven_pkg_info(groupId, artifactId, version, pom_url) values(%s, %s, %s, %s)"
    try:
        time_start = time.perf_counter()
        # 执行sql语句
        cursor.executemany(sql, t)
        # 提交到数据库执行
        db.commit()
        time_end = time.perf_counter()
        print("插入数据", len(insert_data), "条，用时(s)==>", time_end - time_start)
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        print(e)
        print("数据插入失败")


def query_tpl_data():
    sql = 'select groupId, artifactId, version, pom_url from maven_pkg_info'
    tpls = []
    try:
        time_start = time.perf_counter()
        cursor.execute(sql)
        db.commit()
        result = cursor.fetchall()
        time_end = time.perf_counter()
        print("查询数据", len(result), "条，用时(s)==>", time_end - time_start)
        tpls = set(result)
    except Exception as e:
        db.rollback()
        print(e)
    return tpls


def read_pkg_info():
    insert_data = set()
    with open(r'H:\maven-data\gav.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.startswith("{\"groupId\""):
                jo = json.loads(line)
                ones = list()
                ones.append(jo['groupId'])
                ones.append(jo['artifactId'])
                ones.append(jo['version'])
                ones.append(jo['url'])
                insert_data.add(tuple(ones))
            else:
                print(line)
    insert_tpl_data(insert_data)


if __name__ == '__main__':
    read_pkg_info()
