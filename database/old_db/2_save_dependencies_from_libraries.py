import math
import logging
import threading
import time
import traceback
from tqdm import tqdm

import requests

from database.utils import database_utils_pool

log = logging.getLogger()


class GithubQ:
    def __init__(self):
        # self.HEADER = {
        #     "Authorization": "token  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"
        # }
        # self.BASE_Q_URL = "https://api.github.com/repos/{owner}/{repo}"
        # self.downloaded_count = 0
        self.total_count = 0

    def request(self, url, headers=None, timeout=60, retrytimes=3):
        # print("request json url:{}".format(url))
        i = 0
        while i < retrytimes:
            try:
                log.info("[request_ex] request json url {} start.".format(
                    url
                ))
                r = requests.get(url, headers=headers, timeout=timeout)
                log.info("[request_ex] request json url {}:{}".format(
                    r.status_code, url
                ))
                if 200 == r.status_code:
                    return r  # 正常时直接返回结果
                if 404 == r.status_code:
                    return None
            except Exception as e:
                traceback.print_exc()
                pass
                # log.error("{} exception!".format(url))
            i += 1
            log.error("{} err {}/{}, retry after 10s. ".format(url, str(i), str(retrytimes)));
            time.sleep(10)
        log.error("{} failed!".format(url))
        return None

    def process(self, data, url):
        res = self.request(url)
        if res is None:
            # print("request None")
            print("run 无结果")
            # libraries.io 没有返回结果
            business_utils.insert_in_no_requirement_file(data['f_id'], data['file_name'], data['version'])
            return None
        try:
            # print(f"{res.status_code} {url}")
            rjson = res.json()
            if rjson:
                if 'dependencies' in rjson and len(rjson['dependencies']) > 0:
                    fileid = data['f_id']
                    filename = data['file_name']
                    version = data['version']
                    # print("Insert dependencies")
                    # libraries.io 返回 dependencies 结果插入数据库
                    business_utils.insert_in_package_info_1(fileid, filename, version, rjson['dependencies'])
            return res
        except Exception as e:
            traceback.print_exc()
            log.error('{}: analyse error'.format(url))
            return None

    def run(self, i, para_list):
        self.total_count = len(para_list)
        try:
            with tqdm(total=self.total_count) as pbar:     # 进度条显示
                pbar.set_description(f"thread {i} processing ")
                for data, url in para_list:
                    pbar.update(1)
                    # self.downloaded_count += 1
                    # filename = data['file_name']
                    # version = data['version']
                    # print("\n----------------------")
                    # print(f"thread {i} Begin {self.downloaded_count}/{self.total_count} name={filename},ver={version}")
                    # if business_utils.is_exist_in_pakcage_info(filename, version):
                    # print("package_info 中已存在信息：包名：" + str(filename) + "版本：" + str(version))
                    # continue
                    res = self.process(data, url)
            log.info(f"thread {i} process done! ")
        except KeyboardInterrupt:
            pbar.close()
            raise
        pbar.close()


# 保存没有依赖的包名和版本
def insert_in_no_requirement_file(f_id, file_name, file_version):
    sql = "INSERT INTO no_requirement_file (file_name,file_version, f_id) VALUES ('%s','%s','%s')" % (
        file_name, file_version, f_id)
    database_utils_pool.insert(sql)


def insert_in_package_info_1(f_id, name, version, dependencies):
    for dependency in dependencies:
        dep_name = dependency['name']
        dep_version = dependency['requirements']

        sql4 = "INSERT INTO package_info (package_name,package_version,requirement,requirement_version," \
               "requirement_version_status,requirement_true_version,version_range, f_id) VALUES" \
               " ('%s','%s','%s','%s','%s','%s','%s','%s')" % (name, version, dep_name, dep_version, 0, 0, 0, f_id)
        try:
            database_utils_pool.insert(sql4)
            # print("package_info 插入成功！：包名：" + str(name) + "版本：" + str(version) + "依赖名：" + str(
            #     dep_name) + "依赖版本：" + str(dep_version))

        except Exception as e:
            print("sql4 dberror" + str(e))
            # directory_utils.move_file(projectDir, r'D:\ZhangTingwei\watchman-spider-file\sql4-error-file')
            pass
            # raise Exception


def process(i, urls):
    # log.info(f"Thread {i} Begin process {len(urls)} urls...")
    gq = GithubQ()
    gq.run(i, urls)


def split_list(list, n):
    step_count = math.ceil(len(list) / n)  # 向上取整
    for i in range(0, len(list), step_count):
        end = i + step_count
        if end > len(list):
            end = len(list)
        # print(f"yield: {i}:{end}")
        yield list[i:end]  # 返回某个值之后，继续执行直到程序结束


def query_tpl_data():
    sql = "select groupId, artifactId, version from maven_pkg_info"
    """
    从数据库中取出全部TPL信息，将 groupId 和 artifactId 拼接在一起
    :return: set
    """
    pass


if __name__ == '__main__':
    key_list = ["1a705ade5a15dca63defb51170f64a58",  # xmq
                "10e2ea78cd92ee26ec9105730879c393",  # hhy github
                "ed4c58592e1e41183ff2444de08154b0",  # huk521 github
                "4182b1a70e1fb0f6e58f00b7fc0d36b9",  # hu420 github
                "facdcee355da70a1bb759188f8fe852b",  # wwtecdev github
                "a54c237182ea1921fca69b8b288f89f5",  # SIA-hhy
                "b589c52affd3a56da5838cae319aba5f",  # 1024085213@qq.com
                "4be087ca0f8e3ded136d428c43434f52",  # xumeiqiu2019@stumail.neu.edu.cn
                "a3a89224a3bf2f85d3a35e26e0d6c621",  # 1910472@stu.neu.edu.cn
                "5621e1932583e6f468f62cc8f20f91a2",  # xumeiqiu2017@qq.com
                "1844eae9c1c7cbf03fa3e1c159f28947",
                "c8b3e5d2209a89d0ad380817648f5d15",
                "916d108dc30aac79a26ea9a2cdc4c67e",
                "687cb16aa6dd544f0fb5084b1081e1d5",
                "bb3b8290dff2d4855d3277ab0400bdcc",
                "434c23888e65270bc3d0178b90528b27",
                "e9785152f3bd02e9e7ea079932665e62",
                "ee825767f0925788b984168383a81447",
                "097f8c4a6f3c2f3cd2f64812847bd09b",
                "2413ecc2a9fc8c201eb834d45b1e6adf",
                "423953110adc3679bb2837c6294c1c94",  # huk522@163.com
                "c370b16b51fd61c085ebc23bfa7e1af9",  # huk523@163.com
                "38e916ce78481b055078abc21e97245a",  # huk524@163.com
                "ad153d280e9d359567ed53604967db74",  # huk525@163.com
                "6495dc43d11eb5684158c3652d367b7f",  # huk527
                "a38d68eaa5b92aa47cebeaff2bbe2e77",  # huk528
                "35d001efcc6674bf0837aaf28c338874",  # huk529
                "fa3f891184654cfcf6e92167f37d87ba",  # huk530
                ]

    base_url = "https://libraries.io/api/maven/{query}/dependencies?api_key={key}"

    todo_data = []  # 从数据库中取

    _idx = 0

    for list_arr in split_list(todo_data, len(key_list)):
        urls = []
        for data in list_arr:
            fileid = data['f_id']
            filename = data['file_name']
            version = data['version']
            key = key_list[_idx]
            temp_url = base_url.format(query=filename + "/" + version, key=key)
            urls.append((data, temp_url))
        threading.Thread(target=process, args=(_idx + 1, urls)).start()
        _idx += 1
