import os
import shutil

import tools.tools
from analysis.core_feature_analysis.android_r8_core_feature.core_feature_pipeline import generate_shrink_android_dex

public_library_path = r'E:\public-library'
public_dex_path = r'F:\public-dex'


def read_dependency_file(dep_file_path):
    dependencies_list = []
    with open(dep_file_path, 'r') as f:
        # 排除第一行非依赖项的影响
        f.readline()
        content = f.readlines()
        for line in content:
            if line.strip() == '':
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


def copy_shrink_dex_folders(dep_file_path, shrink_dex_path, shrunk_dex_folder_list):
    dependency_list = read_dependency_file(dep_file_path)
    for tpl_name in dependency_list:
        if tpl_name.replace(':', '@') in shrunk_dex_folder_list:
            print(tpl_name)
            for file_path in tools.tools.list_all_files(
                    os.path.join(r'F:\zc-data\RQ\RQ1\shrink-dex-output-final', tpl_name.replace(':', '@'))):
                target_output_path = os.path.join(shrink_dex_path, tpl_name.replace(':', '@'))
                if not os.path.exists(target_output_path):
                    os.makedirs(target_output_path)
                shutil.copy(file_path, target_output_path)


def copy_shrink_dex_folders_rq2(dep_file_path, shrink_dex_path, shrunk_dex_folder_list):
    dependency_list = read_dependency_file(dep_file_path)
    for tpl_name in dependency_list:
        # if tpl_name.replace(':', '@') in shrunk_dex_folder_list:
        gav = tpl_name.split(':')
        ga = gav[0] + '@' + gav[1] + '@'
        for sdf in shrunk_dex_folder_list:
            if ga in sdf:
                print(sdf)
                for file_path in tools.tools.list_all_files(
                        os.path.join(r'F:\zc-data\RQ\RQ2\shrink-dex-output', sdf)):
                    target_output_path = os.path.join(shrink_dex_path, sdf)
                    if not os.path.exists(target_output_path):
                        os.makedirs(target_output_path)
                    shutil.copy(file_path, target_output_path)


def copy_dex_files_rq2(dep_file_path, target_dex_output_path, no_shrink_dex_files):
    dependency_list = read_dependency_file(dep_file_path)
    for tpl_name in dependency_list:
        # if tpl_name.replace(':', '@') in shrunk_dex_folder_list:
        gav = tpl_name.split(':')
        ga = gav[0] + '@' + gav[1] + '@'
        for no_shrink_dex in no_shrink_dex_files:
            if ga in no_shrink_dex:
                print(no_shrink_dex)
                shutil.copy(os.path.join(public_dex_path, no_shrink_dex), target_dex_output_path)


def copy_r8_config_folders(dep_file_path, r8_config_path, r8_config_folder_list):
    dependency_list = read_dependency_file(dep_file_path)
    for tpl_name in dependency_list:
        if tpl_name.replace(':', '@') in r8_config_folder_list:
            print(tpl_name)
        if not os.path.exists(os.path.join(r'F:\zc-data\RQ\RQ1\r8-config', tpl_name.replace(':', '@'))):
            continue
        for file_path in tools.tools.list_all_files(
                os.path.join(r'F:\zc-data\RQ\RQ1\r8-config', tpl_name.replace(':', '@'))):
            target_output_path = os.path.join(r8_config_path, tpl_name.replace(':', '@'))
            if not os.path.exists(target_output_path):
                os.makedirs(target_output_path)
            shutil.copy(file_path, target_output_path)


def copy_dex_files(dep_file_path, target_dex_output_path, no_shrink_dex_files):
    dependency_list = read_dependency_file(dep_file_path)
    for tpl_name in dependency_list:
        if tpl_name.replace(':', '@') + '.dex' in no_shrink_dex_files:
            print(tpl_name)
            shutil.copy(os.path.join(public_dex_path, tpl_name.replace(':', '@') + '.dex'),
                        target_dex_output_path)


def r8_config_add_apk_rules(apk_folders_path, apk_folder_list):
    for apk_folder_item in apk_folder_list:
        apk_folder_item_path = os.path.join(apk_folders_path, apk_folder_item)
        apk_config_path = os.path.join(apk_folder_item_path, 'configuration.txt')
        if not os.path.exists(apk_config_path):
            print(apk_config_path)
            continue
        with open(apk_config_path, 'r') as acp:
            apk_r8_config_content = acp.readlines()
        apk_r8_config_item_path = os.path.join(apk_folder_item_path, 'r8-config')
        for config_file in tools.tools.list_all_files(apk_r8_config_item_path):
            with open(config_file, 'a') as cf:
                cf.writelines(apk_r8_config_content)


if __name__ == '__main__':

    path = r'F:\zc-data\RQ\RQ2\apks'

    """
    turn参数说明:
        0 : 根据APK依赖关系复制符合条件的shrink-dex-folder到APK文件夹下
        1 : 根据APK依赖关系复制符合条件的未被代码收缩的dex到APK文件夹下
        2 : 根据APK依赖关系复制符合条件的r8-config-folder到APK文件夹下
        3 : 根据APK文件夹下r8-config生成对应的shrink-dex存储到指定文件夹
    """

    turn = 1

    apk_folders = os.listdir(path)
    if turn == 0:
        shrunk_dex_folders = os.listdir(r'F:\zc-data\RQ\RQ2\shrink-dex-output')
        for apk_folder in apk_folders:
            apk_folder_path = os.path.join(path, apk_folder)
            dependency_file_path = os.path.join(apk_folder_path, 'dependency.txt')
            # if os.path.exists(os.path.join(apk_folder_path, 'shrink-dex-output')):
            #     shutil.rmtree(os.path.join(apk_folder_path, 'shrink-dex-output'))
            copy_shrink_dex_folders_rq2(dependency_file_path, os.path.join(apk_folder_path, 'shrink-dex-output'),
                                    shrunk_dex_folders)
    if turn == 1:
        complete_dex_files = os.listdir(public_dex_path)
        for apk_folder in apk_folders:
            apk_folder_path = os.path.join(path, apk_folder)
            dependency_file_path = os.path.join(apk_folder_path, 'dependency.txt')
            if not os.path.exists(os.path.join(apk_folder_path, 'tpl')):
                os.makedirs(os.path.join(apk_folder_path, 'tpl'))
            # copy_dex_files(dependency_file_path, os.path.join(apk_folder_path, 'tpl'), complete_dex_files)
            copy_dex_files_rq2(dependency_file_path, os.path.join(apk_folder_path, 'tpl'), complete_dex_files)
    if turn == 2:
        r8_config_folders = os.listdir(r'F:\zc-data\RQ\RQ1\r8-config')
        for apk_folder in apk_folders:
            apk_folder_path = os.path.join(path, apk_folder)
            dependency_file_path = os.path.join(apk_folder_path, 'dependency.txt')
            copy_r8_config_folders(dependency_file_path, os.path.join(apk_folder_path, 'r8-config'), r8_config_folders)
    if turn == 3:
        # 根据每个apk文件夹r8-config生成对应的shrink-dex-folder
        for apk_folder in apk_folders:
            apk_folder_path = os.path.join(path, apk_folder)
            for shrink_dex_folder in os.listdir(os.path.join(apk_folder_path, 'r8-config')):
                print(shrink_dex_folder)

                shrink_item_path = os.path.join(os.path.join(apk_folder_path, 'apk-shrink-dex-output'),
                                                shrink_dex_folder)
                r8_config_input_folder = os.path.join(os.path.join(apk_folder_path, 'r8-config'), shrink_dex_folder)
                input_library_path = os.path.join(public_library_path, shrink_dex_folder)
                aar_file = input_library_path + '.aar'
                jar_file = input_library_path + '.jar'
                if os.path.exists(aar_file):
                    print(aar_file)
                    generate_shrink_android_dex(aar_file, r8_config_input_folder, shrink_item_path)
                elif os.path.exists(jar_file):
                    print(jar_file)
                    generate_shrink_android_dex(jar_file, r8_config_input_folder, shrink_item_path)
                else:
                    print(aar_file, jar_file + '都不存在')
