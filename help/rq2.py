import ast
import os

from androguard.misc import AnalyzeAPK, AnalyzeDex

from database.utils.feature_business_utils import get_tpl_features
from tools import tools
from tools.tools import read_dependency_file


def format_features_from_db(db_table_name):
    dependency_names = []
    data = get_tpl_features(db_table_name)
    for tpl_info in data:
        if tpl_info['core_fined_feature']:
            dependency_names.append(tpl_info['tpl_name'])
    return dependency_names


def generate_feature_and_compare(apk_path, shrink_dex_path, android_dex_path):
    remove_in_apk = []
    app, d_list, app_dx = AnalyzeAPK(apk_path)
    print(app.get_package())

    for dex_file in tools.list_all_files(android_dex_path):
        if not dex_file.endswith(".dex"):  # 非dex结尾，跳过
            continue
        file_name = dex_file.split('\\')[-1][:-4].replace('@', ':')

        dex_hash, dex_d, dex_dx = AnalyzeDex(dex_file)

        # apk未模块解耦找到最佳匹配集合
        match_list = []
        app_classes = []
        for app_class in app_dx.get_classes():
            if app_class.is_external():
                continue
            app_classes.append(app_class.name)
        for dex_clazz in dex_d.get_classes():
            if dex_clazz.name in app_classes:
                match_list.append(dex_clazz.name)
        best_match_result = match_list

        # 根据最佳匹配的类名的集合，构建APK方法名的集合
        apk_method_names = []
        for cla_name in best_match_result:
            apk_class = app_dx.classes[cla_name]  # todo: 后面要修改 app_dx -> apk_dx
            for apk_method in apk_class.get_methods():
                if apk_method.is_external():
                    continue
                # 新添加空方法跳过
                # if apk_method.get_length() == 0:
                #     continue
                apk_method_names.append(apk_method.full_name)

        # 根据APK方法名的集合，构建dex方法名的集合(存在略有不同的情况)
        dex_method_names = []
        for dex_class in dex_dx.get_classes():
            for dex_method in dex_class.get_methods():
                if dex_method.is_external():
                    continue
                # 新添加空方法跳过
                # if dex_method.get_length() == 0:
                #     continue
                if dex_method.full_name in apk_method_names:
                    dex_method_names.append(dex_method.full_name)
        if len(dex_method_names) == 0:
            remove_in_apk.append(file_name)
        # print('%-80s %-10s %s' % (file_name, len(dex_d.get_methods()), len(dex_method_names)))
    return remove_in_apk


if __name__ == '__main__':

    path = r'F:\zc-data\RQ\RQ1\apks'

    apk_folders = os.listdir(path)

    for apk_folder in apk_folders:
        apk_folder_path = os.path.join(path, apk_folder)
        folder_under_files = os.listdir(apk_folder_path)
        print(folder_under_files)
        apk_path = ''
        for folder_under_file in folder_under_files:
            if folder_under_file.endswith('-shrink.apk'):
                apk_path = os.path.join(apk_folder_path, folder_under_file)
                break
        shrink_dex_path = os.path.join(apk_folder_path, 'shrink-dex-output-final')
        android_dex_path = os.path.join(apk_folder_path, 'tpl')
        remove_in_apk = generate_feature_and_compare(apk_path, shrink_dex_path, android_dex_path)

        dep_names = format_features_from_db(apk_folder.replace('.', '_'))

        apk_dependency_tree_file_path = os.path.join(apk_folder_path, 'dependency.txt')
        dependency_list = read_dependency_file(apk_dependency_tree_file_path)

        filter_dependency_data = []
        for dep_name in dep_names:
            # if dep_name in dependency_list:
            if dep_name in dependency_list and dep_name not in remove_in_apk:
                filter_dependency_data.append(dep_name)
        print(len(dependency_list), len(filter_dependency_data))

        new_dependency_file_path = os.path.join(os.path.join(r'F:\zc-data\RQ\RQ2\apks', apk_folder), 'dependency1.txt')
        with open(new_dependency_file_path, 'w') as f:
            f.write('\n')
            for fdd in filter_dependency_data:
                f.write(fdd + '\n')




