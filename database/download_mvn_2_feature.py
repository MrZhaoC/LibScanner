import os
import time

import requests

from tools.tpl_to_dex import preprocessing
from generate_feature import process_dex_files

mvn_base_link = r'https://repo1.maven.org/maven2/'
mvn_file_path = r"D:\Android-exp\gav_index_popular.txt"

queue = []


def get_popular_mvn_data():
    result = []
    with open(mvn_file_path, 'r', encoding='utf-8') as f:
        items = f.readlines()
    for item in items:
        if int(item.split(";")[1]) < 5:
            continue
        # append gav
        result.append(item.split(";")[0])
    return result


def construct_complete_link_download():
    result = get_popular_mvn_data()
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
    mvn_links = construct_complete_link_download()
    for gav, link in mvn_links:
        jar_file_link = link + ".jar"
        aar_file_link = link + ".aar"

        # 有可能都找不到
        jar_file = requests.get(jar_file_link)
        aar_file = requests.get(aar_file_link)

        # todo: 注意爬取的速度
        time.sleep(5)

        # todo: 实际使用时需要修改
        # if len(queue) > 3:
        #     convert_mvn_tpl_2_dex(output_path)

        if 200 == jar_file.status_code:
            print(jar_file_link)
            jar_file_name = gav.replace(':', '@') + '.jar'
            jar_size = int(jar_file.headers['Content-Length'])  # kb to byte
            with open(os.path.join(output_path, jar_file_name), 'wb') as f:
                # for tq in tqdm(range(jar_size), desc='%s 下载中' % jar_file_name):
                f.write(jar_file.content)

            queue.append(os.path.join(output_path, jar_file_name))
        # if 404 == jar_file.status_code:
        #     print('error url %s' % jar_url)

        if 200 == aar_file.status_code:
            print(aar_file_link)
            aar_file_name = gav.replace(':', '@') + '.aar'
            aar_size = int(aar_file.headers['Content-Length'])
            with open(os.path.join(output_path, aar_file_name), 'wb') as f:
                # for tq in tqdm(range(aar_size), desc='%s 下载中' % aar_file_name):
                f.write(aar_file.content)

            queue.append(os.path.join(output_path, aar_file_name))
        # if 404 == aar_file.status_code:
        #     print('error url %s' % aar_url)


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
    dex_2_feature_db(dex_path)


def dex_2_feature_db(dex_path):
    process_dex_files(dex_path)


if __name__ == '__main__':
    download_jar_aar(r'D:\mvn-library')
