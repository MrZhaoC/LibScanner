"""
给定依赖树文件
    - 预处理依赖树，转换成dependency_list (完成)
    - 下载前先判断 (完成)
        - 将当前依赖和查询到的依赖下载到public-library (完成)
        - 将下载的依赖（jar/aar）生成dex到public-dex (完成)
    - 生成规则前先判断 (进行中)
        - 根据依赖关系生成方法入口规则，写入文件
        - 根据规则配置文件生成shrink-dex
        # todo
        - 选取阈值，生成核心特征，存储数据库
"""
from typing import List

from database.utils.denpendency_business_utils import get_front_dependencies_from_mvn_by_gav, \
    get_front_dependencies_from_google_by_gav
from tools.android_gradle_dependency_graph import get_curr_parents
from tools.tools import write_excel_xlsx


def read_dependency_file(dependency_file_path):
    dependencies_list = []
    with open(dependency_file_path, 'r') as f:
        content = f.readlines()
        for line in content:
            tpl = line.split('@')[0]
            ext = line.split('@')[1]
            tpl = tpl.replace('|', '').replace('+', '').replace('---', '').replace('\\', '').lstrip()
            if '>' in tpl:
                tpl = tpl.split('->')
                gav = tpl[0].split(':')
                final_gav = gav[0] + ':' + gav[1] + ':' + tpl[1].strip().replace('(*)', '').replace('(c)', '').strip()
                dependencies_list.append((final_gav, ext))
            else:
                _gav = tpl.replace('(*)', '').replace('(c)', '').strip()
                dependencies_list.append((_gav, ext))
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


def format_tpl_name(tpl_name):
    if ':' in tpl_name:
        return tpl_name.split(':')
    elif '@' in tpl_name:
        return tpl_name.split('@')
    return None


def pre_main(dependency_file_path):
    dependency_list = read_dependency_file(dependency_file_path)

    result = []

    for tpl_name, ext in dependency_list:
        gav = format_tpl_name(tpl_name)  # 视情况看是否需要修改
        mvn_dependency = query_current_dependency_from_mvn(gav)
        google_maven_dependency = query_current_dependency_from_google_mvn(gav)
        apk_dependency = get_curr_parents(tpl_name)
        result.append([tpl_name, len(mvn_dependency), len(google_maven_dependency), len(apk_dependency)])
        print('%s mvn:%-10s google_mvn:%-10s apk:%-10s' % (
            tpl_name, len(mvn_dependency), len(google_maven_dependency), len(
                apk_dependency)))
    return result


if __name__ == '__main__':
    dep_file_path = r'D:\Desktop\haircomb_dependencies.txt'

    output_result = pre_main(dep_file_path)

    write_excel_xlsx(r'D:\Desktop\2023-11-13.xlsx', 'kind_dependency_count', output_result)
