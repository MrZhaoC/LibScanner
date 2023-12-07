import os
import time

import requests

from database.utils.feature_business_utils import get_feature_info_by_tpl_name
from generate_feature import process_dex_files
from tools.tpl_to_dex import preprocessing

mvn_base_link = r'https://repo1.maven.org/maven2/'
mvn_file_path = r"D:\Android-exp\gav_index_popular.txt"

# public_library_path = r'D:\Android-exp\public-library'

queue = []


def get_popular_mvn_data(output_path):
    # files = tools.tools.list_all_files(public_library_path)
    result = []
    with open(mvn_file_path, 'r', encoding='utf-8') as f:
        items = f.readlines()
    for item in items:
        gav = item.split(";")[0]
        popular = int(item.split(";")[1])
        if popular < 1000:
            continue
        # 查询数据库，判断当前tpl是否已经完成特征的构建存储
        # if check_db(item.split(";")[0]):
        #     print('feature database已经存在 %s' % item.split(";")[0])
        #     continue

        # todo：判断当前tpl是否已经下载过
        # public_tpl_path = check_public_library(item.split(";")[0], files)
        # if public_tpl_path:
        #     shutil.copy(public_tpl_path, output_path)
        #     tpl_file_name = public_tpl_path.split('\\')[-1]
        #     print('public library已经存在 %s' % tpl_file_name)
        #     queue.append(os.path.join(output_path, tpl_file_name))
        #     continue

        jar_file_path = os.path.join(output_path, gav.replace(':', '@') + '.jar')
        aar_file_path = os.path.join(output_path, gav.replace(':', '@') + '.aar')
        if os.path.exists(jar_file_path):
            print('已经下载 {}'.format(jar_file_path))
            continue
        elif os.path.exists(aar_file_path):
            print('已经下载 {}'.format(aar_file_path))
            continue
        else:
            result.append(item.split(";")[0])
    return result


def check_db(gav):
    item = get_feature_info_by_tpl_name(gav)
    return item


def check_public_library(gav, files):
    public_lib_tpl_path = None
    for file in files:
        format_file_name = file.split('\\')[-1][:-4]
        if gav == format_file_name:
            public_lib_tpl_path = file
            break
    return public_lib_tpl_path


def construct_complete_link_download(output_path):
    result = get_popular_mvn_data(output_path)
    mvn_links = []
    tpl_detail_link = mvn_base_link + '{}/{}/{}/{}-{}'
    for item in result:
        gav = item.split(':')
        group_id = gav[0]
        artifact_id = gav[1]
        version_num = gav[2]
        detail_link = tpl_detail_link.format(group_id.replace('.', '/'), artifact_id, version_num, artifact_id,
                                             version_num)
        mvn_links.append([item, detail_link])
    return mvn_links


def download_jar_aar(output_path):
    mvn_links = construct_complete_link_download(output_path)
    for gav, link in mvn_links:
        jar_file_link = link + ".jar"
        aar_file_link = link + ".aar"

        # todo: 实际使用时需要修改
        # if len(queue) > 10:
        #     convert_mvn_tpl_2_dex(output_path)

        try:
            jar_file = requests.get(jar_file_link)
            if 200 == jar_file.status_code:
                print(jar_file_link)
                jar_file_name = gav.replace(':', '@') + '.jar'
                # jar_size = int(jar_file.headers['Content-Length'])  # kb to byte
                with open(os.path.join(output_path, jar_file_name), 'wb') as f:
                    # for tq in tqdm(range(jar_size), desc='%s 下载中' % jar_file_name):
                    f.write(jar_file.content)

                # queue.append(os.path.join(output_path, jar_file_name))
        except Exception:
            print('异常', aar_file_link)
            time.sleep(3)
        try:
            aar_file = requests.get(aar_file_link)
            if 200 == aar_file.status_code:
                print(aar_file_link)
                aar_file_name = gav.replace(':', '@') + '.aar'
                # aar_size = int(aar_file.headers['Content-Length'])
                with open(os.path.join(output_path, aar_file_name), 'wb') as f:
                    # for tq in tqdm(range(aar_size), desc='%s 下载中' % aar_file_name):
                    f.write(aar_file.content)

                # queue.append(os.path.join(output_path, aar_file_name))
        except Exception:
            print('异常', aar_file_link)
            time.sleep(3)


def convert_mvn_tpl_2_dex(output_path):
    dex_path = os.path.join(output_path, 'dex')
    preprocessing(output_path, dex_path)
    # 清空队列
    for tpl_file_path in queue:
        try:
            os.remove(tpl_file_path)
        except Exception:
            print("{}文件删除失败".format(tpl_file_path))
    # 特征存储数据库
    # dex_2_feature_db(dex_path)


def dex_2_feature_db(dex_path):
    process_dex_files(dex_path)


if __name__ == '__main__':
    download_jar_aar(r'D:\mvn-library')
