"""
给定依赖树文件
    - 预处理依赖树，转换成dependency_list (完成)
    - 下载前先判断 (完成)
        - 将当前依赖和查询到的依赖下载到public-library (完成)
        - 将下载的依赖（jar/aar）生成dex到public-dex (完成)
    - 生成规则前先判断 (已完成)
        - 根据依赖关系生成方法入口规则，写入文件 (已完成)
        - 根据规则配置文件生成shrink-dex (已完成)
        # todo (已完成，未测试)
        - 选取阈值，生成核心特征，存储数据库
"""
import logging
import os
import time
import warnings
import xml.etree.ElementTree as ET
import zipfile
from typing import List

import coloredlogs
import networkx as nx
import requests
from androguard.misc import get_default_session, AnalyzeDex

import generate_feature
import tools.tools
from database.utils.denpendency_business_utils import get_front_dependencies_from_mvn_by_gav, \
    get_front_dependencies_from_google_by_gav

public_library_path = r'D:\Android-exp\public-library'
public_dex_path = r'D:\Android-exp\public-dex'
base_rule_config_path = r'F:\zc-data\RQ\RQ2\small-scale\r8-config'

# 日志相关配置
TEST_FORMAT = '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s'
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt=TEST_FORMAT)

warnings.filterwarnings("ignore")


def read_dependency_file(dependency_file_path):
    dependencies_list = []
    with open(dependency_file_path, 'r') as f:
        content = f.readlines()
        for line in content:
            if line.strip() == '':
                continue
            tpl = line.split('@')[0]
            # ext = line.split('@')[1]
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


def query_current_dependency_from_mvn(gav: List[str]):
    mvn_dependency = get_front_dependencies_from_mvn_by_gav(gav[0], gav[1], gav[2])
    mvn_dependency_result = []
    for md in mvn_dependency:
        g = md['group_id']
        a = md['artifact_id']
        v = md['version']
        mvn_dependency_result.append([g, a, v])
    return mvn_dependency_result


def query_current_dependency_from_google_mvn(gav: List[str]):
    google_mvn_dependency = get_front_dependencies_from_google_by_gav(gav[0], gav[1], gav[2])
    google_mvn_dependency_result = []
    for gmd in google_mvn_dependency:
        g = gmd['group_id']
        a = gmd['artifact_id']
        v = gmd['version']
        google_mvn_dependency_result.append([g, a, v])
    return google_mvn_dependency_result


def download_dependency(gav: List[str]):
    downloaded_tpl = []
    # 当前tpl直接下载 ext可以删除
    download_tpl(gav, downloaded_tpl)
    # 处理依赖
    google_mvn_dependency_list = query_current_dependency_from_google_mvn(gav)
    mvn_dependency_list = query_current_dependency_from_mvn(gav)
    for google_mvn_dependency in google_mvn_dependency_list:
        download_tpl(google_mvn_dependency, downloaded_tpl)
    for mvn_dependency in mvn_dependency_list:
        download_tpl(mvn_dependency, downloaded_tpl)
    return downloaded_tpl


def download_tpl(gav: List[str], downloaded_tpl: List[str]):
    group_id = gav[0]
    artifact_id = gav[1]
    version = gav[2]

    # 跳过所有不符合版本规则的version
    if '-' in version or '+' in version or '[' in version:
        return

    # todo: 数据库规范化之后可以跳过
    if '$' in group_id or '$' in artifact_id or '$' in version:
        return

    # print(groupId, artifactId, version)
    tpl_name = group_id + '@' + artifact_id + '@' + version

    DOT_AAR = '.aar'
    DOT_JAR = '.jar'

    tpl_file_path1 = os.path.join(public_library_path, tpl_name + DOT_AAR)
    tpl_file_path2 = os.path.join(public_library_path, tpl_name + DOT_JAR)

    # print(tpl_file_path1, tpl_file_path2)

    # 已经下载好，直接添加
    if os.path.exists(tpl_file_path1):
        downloaded_tpl.append(tpl_file_path1)
        # log
        logger.debug("已下载 " + tpl_file_path1)
    elif os.path.exists(tpl_file_path2):
        downloaded_tpl.append(tpl_file_path2)
        # log
        logger.debug("已下载 " + tpl_file_path2)
    else:
        # headers
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Connection': 'close'
        }

        base_url1 = 'https://maven.google.com'
        url1 = "{}/{}/{}/{}/{}-{}".format(base_url1, group_id.replace('.', '/'), artifact_id, version, artifact_id,
                                          version)

        base_url2 = 'https://repo1.maven.org/maven2'
        url2 = "{}/{}/{}/{}/{}-{}".format(base_url2, group_id.replace('.', '/'), artifact_id, version, artifact_id,
                                          version)
        urls = [url1 + DOT_AAR, url2 + DOT_JAR, url2 + DOT_AAR, url1 + DOT_JAR]
        for u in urls:
            try:
                # 网络请求
                requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                res = s.get(u, headers=headers)
                time.sleep(0.3)
                if 200 == res.status_code:
                    # if not os.path.exists(public_library_path):
                    #     os.makedirs(public_library_path)
                    ext_name = u.split('/')[-1].split('.')[-1]
                    file_name = tpl_name + '.' + ext_name

                    file_path = os.path.join(public_library_path, file_name)
                    with open(file_path, 'wb') as f:
                        f.write(res.content)

                    # 添加已经下载的tpl
                    downloaded_tpl.append(file_path)
                    # log
                    logger.info("下载完成 " + file_path)
                    break  # 正确url之后应该退出循环
            except Exception:
                print('异常', u)
                time.sleep(5)


def format_tpl_name(tpl_name):
    if ':' in tpl_name:
        return tpl_name.split(':')
    elif '@' in tpl_name:
        return tpl_name.split('@')
    return None


def convert_tpl_to_android_dex(downloaded_tpl):
    """
    转换tpl到android dex，并存储dex到public-dex
    :return:
    """
    converted_android_dex = []

    # 转换dex
    for tpl_file_path in downloaded_tpl:
        # 判断dex是否已经存在
        tpl_file_name = tpl_file_path.split('\\')[-1][:-4]
        android_dex_path = os.path.join(public_dex_path, tpl_file_name + '.dex')
        # 已经生成过dex，跳过即可
        if os.path.exists(android_dex_path):
            converted_android_dex.append(android_dex_path)
            continue

        # dex文件不存在
        parent_dir = os.path.dirname(tpl_file_path)

        # aar处理，先提取jar文件，然后重命名处理
        if tpl_file_path.endswith('.aar'):
            # 解压 提取classes.jar 文件
            arr_file = tpl_file_path.split("\\")[-1]
            aar_name = os.path.splitext(arr_file)[0]  # 分离文件名 和 后缀名

            # 解压文件夹更新
            if not zipfile.is_zipfile(tpl_file_path):
                pass
            else:
                try:
                    with zipfile.ZipFile(tpl_file_path, 'r') as zip_file:
                        for name in zip_file.namelist():
                            if name == "classes.jar":
                                zip_file.extract(name, parent_dir)
                                old_path = os.path.join(parent_dir, name)
                                jar_path = os.path.join(parent_dir, aar_name) + '.jar'
                                try:
                                    os.rename(old_path, jar_path)
                                except Exception:
                                    os.remove(jar_path)
                                    os.rename(old_path, jar_path)
                                jar_to_dex(jar_path, converted_android_dex, True)
                except zipfile.BadZipfile:
                    print('{}无法打开受损的zipfile'.format(tpl_file_path))
                except Exception:
                    print('{}解压文件发生错误'.format(tpl_file_path))

        # jar处理
        if tpl_file_path.endswith('.jar'):
            jar_to_dex(tpl_file_path, converted_android_dex, False)

    return converted_android_dex


def jar_to_dex(jar_file_path, converted_android_dex, aar_flag):
    # 转换jar to dex
    jar_full_name = jar_file_path.split("\\")[-1]
    jar_name = os.path.splitext(jar_full_name)[0]
    dex_file_name = jar_name + '.dex'

    try:
        # cmd = r"d8 {0} --release  --intermediate --output {1}".format(
        #     jar_file, output_path)

        cmd = r"d8 {0} " \
              r"--release  " \
              r"--intermediate " \
              r"--output {1} " \
              r"--lib E:\android\sdk\platforms\android-33\android.jar".format(jar_file_path, public_dex_path)
        os.system(cmd)

        # 打印日志
        logger.debug(jar_file_path)

        # aar生成的jar使用完删除
        if aar_flag:
            try:
                os.remove(jar_file_path)
            except Exception:
                print("{} 文件删除失败".format(jar_file_path))

        try:
            android_dex_path = os.path.join(public_dex_path, dex_file_name)
            os.rename(os.path.join(public_dex_path, 'classes.dex'), android_dex_path)
            # 转换成功的dex加入列表
            converted_android_dex.append(android_dex_path)
        except Exception as e:
            os.remove(os.path.join(public_dex_path, dex_file_name))
            os.rename(os.path.join(public_dex_path, 'classes.dex'), os.path.join(public_dex_path, dex_file_name))
    except Exception as e:
        print(e)


def analysis_method_entry_from_dependency(format_dex_name, target_dex_path, converted_android_dex, default_config):
    """
    根据依赖关系生成方法入口规则，并写入配置文件
    :return:
    """
    _, target_dvm, target_dx = AnalyzeDex(target_dex_path)

    target_method_full_name_list = []

    # 得到目标dex的所有方法名(全限定类名+方法信息)集合
    for method in target_dvm.get_methods():
        target_method_full_name_list.append(method.full_name)

    # config_output_path = 配置文件输出路径 + 每个dex的名称
    config_output_path = os.path.join(base_rule_config_path, format_dex_name)
    # todo 提前判断
    if not os.path.exists(config_output_path):
        os.makedirs(config_output_path)
    # else:

    # 2024-01-02修改
    for i, file in enumerate(converted_android_dex):
        if i == 0:
            continue
        # 获取文件名和后缀
        file_name = file.split('\\')[-1]
        file_ext = os.path.splitext(file)[-1]

        # 2023-12-04 修改
        final_format_keep_rule_path = r'%s\%s-keep-rule.cfg' % (config_output_path, file_name[:-4])
        # 已经生成过keep-rule-cfg，跳过即可
        if os.path.exists(final_format_keep_rule_path):
            logger.debug('已经生成过config,无需再次config {}'.format(final_format_keep_rule_path))
            continue

        # analysis method entry
        if file_ext == '.dex':
            method_entry_list = []
            _, fd_dvm, fd_dx = AnalyzeDex(file)
            for class_x in fd_dx.get_classes():
                for method_x in class_x.get_methods():
                    if method_x.full_name in target_method_full_name_list:
                        method_entry_list.append(method_x)
            if method_entry_list:
                format_method_keep_rules = tools.tools.format_method_keep_rule(method_entry_list)
                # 写入文件
                with open(final_format_keep_rule_path, 'w', encoding='utf-8') as f:
                    for kr in format_method_keep_rules:
                        f.write(kr + '\n')
                    # 追加默认配置
                    f.writelines(default_config)
            else:
                print('方法入口集合为空', file)

            # 清空session，减少内存占用
            session = get_default_session()
            session.reset()

    return config_output_path


def generate_shrink_android_dex(input_library_path, config_output_path, shrink_item_path):
    # todo: 提起判断，已经完成shrink的直接返回
    if not os.path.exists(shrink_item_path):
        os.makedirs(shrink_item_path)
    # else:

    # 2024-01-02 修改
    for config_file in tools.tools.list_all_files(config_output_path):
        config_file_name = config_file.split('\\')[-1][:-4]

        old_path = os.path.join(shrink_item_path, 'classes.dex')
        new_path = os.path.join(shrink_item_path, config_file_name[:-10] + '.dex')
        # 当前dex已经shrink，跳过即可
        if os.path.exists(new_path):
            logger.debug('已经完成过shrink,无需再次shrink {}'.format(new_path))
            continue
        try:
            cmd = 'java -jar  %s ' \
                  '--release ' \
                  '--no-minification ' \
                  '--output %s ' \
                  '--pg-conf %s ' \
                  '--lib E:\\android\\sdk\\platforms\\android-33\\android.jar ' \
                  '--lib E:\\JDK8 %s' \
                  % ('../../../libs/r8-3.2.74.jar', shrink_item_path, config_file, input_library_path)
            os.system(cmd)
        except Exception:
            print("Android R8 Error")
            # 发生异常 跳过
            continue
        # 重命名
        try:
            # 2023-09-20 修改
            os.rename(old_path, new_path)
            # shutil.(old_path, new_path)
        except FileNotFoundError:
            print(f"File '{old_path}' not found.")
        except PermissionError:
            print(f"You don't have permission to rename the file.")
        except Exception as e:
            print(f"An error occurred: {e}")


def process_core_feature_set(shrink_dex_path):
    dex_folder_path = os.listdir(shrink_dex_path)

    for dex_folder in dex_folder_path:
        dex_folder_name = format_tpl_name(dex_folder)
        files = tools.list_all_files(os.path.join(shrink_dex_path, dex_folder))

        multi_dex_core_feature_set = []

        for file in files:
            if file.endswith('.dex'):
                # filename = tools.get_filename_from_path(file).replace('@', ':')
                _, target_dvm, target_dx = AnalyzeDex(file)

                class_name_set = set()  # 收集每个dex中所有的class file name
                for class_name in target_dvm.get_classes():
                    class_name_set.add(class_name.name)

                _, core_fined_feature = generate_feature.generate_fined_feature_cfg(target_dx,
                                                                                    class_name_set)
                multi_dex_core_feature_set.append(set(core_fined_feature))

        cluster_num, cluster_result = core_feature_cluster(multi_dex_core_feature_set)
        save_core_feature_to_db(dex_folder_name, cluster_num, cluster_result)


def core_feature_cluster(multi_dex_core_feature_set):
    threshold = 0.9
    cfcs = get_core_feature_result_by_graph(multi_dex_core_feature_set, threshold)

    result = []

    for component in cfcs:
        cluster_item = set()
        for index in component:
            for feature in multi_dex_core_feature_set[index]:
                cluster_item.add(feature)
        result.append(cluster_item)
    # 返回核心特征划分个数 和 划分好的特征集合
    return len(cfcs), result


def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


def get_core_feature_result_by_graph(multi_dex_core_feature_set, threshold):
    G = nx.Graph()
    for i, set1 in enumerate(multi_dex_core_feature_set):
        G.add_node(i)
        for j, set2 in enumerate(multi_dex_core_feature_set):
            if j <= i:  # Avoid duplicate computation
                continue
            similarity = jaccard_similarity(set1, set2)
            if similarity > threshold:
                G.add_edge(i, j, weight=similarity)
    core_feature_cluster_result = list(nx.connected_components(G))
    return core_feature_cluster_result


def save_core_feature_to_db(dex_folder_name, cluster_num, cluster_result):
    # todo: save之前先判断库中是否存在
    pass


def pre_main(dependency_file_path, shrink_dex_path):
    dependency_list = read_dependency_file(dependency_file_path)

    for tpl_name in dependency_list:
        gav = format_tpl_name(tpl_name)

        # downloaded_tpl[0] 为 target_tpl
        # 得到所有 已经下载过的 和 当前下载完成的 gav_file路径集合
        downloaded_tpl = download_dependency(gav)

        if len(downloaded_tpl) == 0:
            continue

        # todo:
        logger.debug(tpl_name.replace(':', '@') + '<--->' + downloaded_tpl[0].split('\\')[-1][:-4])

        # 判断当前目标tpl是否在已经下载的目录中
        if tpl_name.replace(':', '@') != downloaded_tpl[0].split('\\')[-1][:-4]:
            continue

        # 得到所有 已经转换过的dex 和 当前转换完成的dex 文件路径集合
        converted_android_dex = convert_tpl_to_android_dex(downloaded_tpl)

        if len(converted_android_dex) == 0:
            continue

        # todo: step 1: 构建r8配置文件和shrink dex
        target_dex_name = converted_android_dex[0].split('\\')[-1][:-4]
        format_dex_name = tpl_name.replace(':', '@')
        if format_dex_name == target_dex_name:
            input_library_path = downloaded_tpl[0]
            # todo:
            default_config = []
            try:
                with zipfile.ZipFile(input_library_path, 'r') as zip_ref:
                    for zip_file_name in zip_ref.namelist():
                        # todo: 解析proguard.txt文件内容生成规则
                        if zip_file_name == 'proguard.txt':
                            with zip_ref.open(zip_file_name) as f:
                                for line in f.readlines():
                                    default_config.append(str(line, encoding='utf-8'))
                        # todo: 解析AndroidManifest.xml文件内容生成规则
                        if zip_file_name == 'AndroidManifest.xml':
                            with zip_ref.open(zip_file_name) as f:
                                content = f.read().decode('utf-8')
                                root = ET.fromstring(content)
                                # 暂时没有用到，配合 .开头类使用
                                package_name = root.attrib['package']
                                class_name_rules = set()
                                for child in root.iter('provider'):
                                    class_name_rules.add('-keep class ' + child.attrib[
                                        '{http://schemas.android.com/apk/res/android}name'] + ' { <init>(); }')
                                for child in root.iter('service'):
                                    class_name_rules.add('-keep class ' + child.attrib[
                                        '{http://schemas.android.com/apk/res/android}name'] + ' { <init>(); }')
                                for child in root.iter('receiver'):
                                    class_name_rules.add('-keep class ' + child.attrib[
                                        '{http://schemas.android.com/apk/res/android}name'] + ' { <init>(); }')
                                for child in root.iter('activity'):
                                    class_name_rules.add('-keep class ' + child.attrib[
                                        '{http://schemas.android.com/apk/res/android}name'] + ' { <init>(); }')
                                default_config.extend(list(class_name_rules))
            except:
                pass
            # todo: 添加默认的配置文件内容，默认配置文件的位置后续可能需要修改
            base_rule_path = r"D:\Android-exp\exp-example\base.cfg"
            with open(base_rule_path, 'r', encoding='utf-8') as f:
                default_config.extend(f.readlines())

            # 生成r8配置文件
            config_output_path = analysis_method_entry_from_dependency(format_dex_name, converted_android_dex[0],
                                                                       converted_android_dex, default_config)

            shrink_item_path = os.path.join(shrink_dex_path, format_dex_name)

            generate_shrink_android_dex(input_library_path, config_output_path, shrink_item_path)

            logger.critical('tpl:{} dex:{} config:{} shrink:{}'.format(len(downloaded_tpl), len(converted_android_dex),
                                                                       len(os.listdir(config_output_path)),
                                                                       len(os.listdir(shrink_item_path)))) \
    # todo 2: 收缩的dex选择阈值划分存储特征数据库
    # 到此处，经过shrink的dex已经全部完成，准备构建核心特征
    # 此函数包含 核心特征划分 和 存取数据库
    # process_core_feature_set(shrink_dex_path)


if __name__ == '__main__':
    if not os.path.exists(public_library_path):
        os.makedirs(public_library_path)
    if not os.path.exists(public_dex_path):
        os.makedirs(public_dex_path)
    if not os.path.exists(base_rule_config_path):
        os.makedirs(base_rule_config_path)

    # todo:项目依赖文件
    dep_file_path = r"F:\zc-data\RQ\RQ2\small-scale\all-dependency.txt"
    # todo: shrink-dex输出文件夹
    shrink_dex_output_path = r'F:\zc-data\RQ\RQ2\small-scale\shrink-dex-output'

    pre_main(dep_file_path, shrink_dex_output_path)
