import os
import time
import xml.etree.ElementTree as ET

import requests

mvn_base_link = r'https://repo1.maven.org/maven2/'
google_mvn_link = r'https://maven.google.com/'

apk_dependency_set_path = r'F:\zc-data\RQ\RQ2\small-scale'


def read_dependency_file(read_result):
    dependencies_list = []
    for line in read_result:
        if line.strip() == '':
            continue
        if 'project :' in line:
            continue

        tpl = line.split('@')[0]
        tpl = tpl.replace('|', '').replace('+', '').replace('---', '').replace('\\', '').lstrip()
        if '>' in tpl:
            tpl = tpl.split('->')
            gav = tpl[0].split(':')
            final_gav = gav[0] + ':' + gav[1] + ':' + tpl[1].strip().replace('(*)', '').replace('(c)', '').strip()
            dependencies_list.append(final_gav)
        else:
            _gav = tpl.replace('(*)', '').replace('(c)', '').strip()
            dependencies_list.append(_gav)

    print('原依赖树依赖项个数：', len(dependencies_list))
    print('去重之后依赖项个数：', len(set(dependencies_list)))
    return set(dependencies_list)


def construct_complete_link_download():
    read_tpl_result = read_multi_dependency_file()
    mvn_gav_list = []
    google_mvn_gav_list = []

    # todo: like：https://repo1.maven.org/maven2/bd/com/ipay/sdk/sdk-android/maven-metadata.xml
    tpl_detail_link = mvn_base_link + '{}/{}/maven-metadata.xml'
    artifactId_version_url = google_mvn_link + '{}/group-index.xml?hl=zh-cn'

    for item in read_tpl_result:
        gav = item.split(':')
        group_id = gav[0]
        artifact_id = gav[1]

        # google-mvn
        # aid_version_url = artifactId_version_url.format(group_id.replace('.', '/'))
        # try:
        #     group_index_xml_response = requests.get(aid_version_url)
        #     time.sleep(0.5)
        #     if group_index_xml_response.status_code == 200:
        #         root = ET.fromstring(group_index_xml_response.content)
        #         for child in root:
        #             if artifact_id == child.tag:
        #                 versions = child.attrib['versions']
        #                 all_version = versions.split(',')
        #                 for v in all_version:
        #                     gav = '{}:{}:{}'.format(group_id, child.tag, v)
        #                     print('google-mvn--', gav)
        #                     google_mvn_gav_list.append(gav)
        # except:
        #     time.sleep(3)

        # mvn
        detail_link = tpl_detail_link.format(group_id.replace('.', '/'), artifact_id)
        try:
            metadata_xml_response = requests.get(detail_link)
            time.sleep(0.5)
            if metadata_xml_response.status_code == 200:
                root = ET.fromstring(metadata_xml_response.content)
                for child in root.iter('version'):
                    gav = '{}:{}:{}'.format(group_id, artifact_id, child.text)
                    print('mvn--', gav)
                    mvn_gav_list.append(gav)
        except:
            time.sleep(3)

    return mvn_gav_list, google_mvn_gav_list


def read_multi_dependency_file():
    apk_dependency_folders = os.listdir(apk_dependency_set_path)

    read_result = []
    for apk_dependency_folder in apk_dependency_folders:

        if os.path.isfile(os.path.join(apk_dependency_set_path, apk_dependency_folder)):
            continue

        apk_dependency_file_path = os.path.join(os.path.join(apk_dependency_set_path, apk_dependency_folder),
                                                'dependency.txt')
        # print(apk_dependency_file_path)
        with open(apk_dependency_file_path, 'r') as f:
            f.readline()
            read_result.extend(f.readlines())
    return read_dependency_file(read_result)


if __name__ == '__main__':
    # result = read_multi_dependency_file()
    # all_dependency_path = r'F:\zc-data\RQ\RQ1\all-dependency.txt'
    # with open(all_dependency_path, 'w') as f:
    #     for item in result:
    #         f.write(item + '\n')

    mvn_result, google_mvn_result = construct_complete_link_download()
    with open(r"F:\zc-data\RQ\RQ2\small-scale\all-dependency.txt", 'w') as f:
        for item in mvn_result:
            f.write(item + '\n')
        for item in google_mvn_result:
            f.write(item + '\n')
