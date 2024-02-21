import os

from androguard.misc import AnalyzeDex, AnalyzeAPK

from tools import tools

yes_cnt = 0
no_cnt = 0


def generate_feature_and_compare(apk_path, shrink_dex_path, android_dex_path):
    global yes_cnt
    global no_cnt

    y_cnt = 0
    n_cnt = 0

    app, d_list, app_dx = AnalyzeAPK(apk_path)
    print(app.get_package())

    for dex_file in tools.list_all_files(android_dex_path):
        if not dex_file.endswith(".dex"):  # 非dex结尾，跳过
            continue
        file_name = dex_file.split('\\')[-1][:-4].replace('@', ':')

        dex_hash, dex_d, dex_dx = AnalyzeDex(dex_file)

        # todo: 主要逻辑，排除APK直接调用的影响
        FILTER = False
        for dex_class_name in dex_d.get_classes():
            if dex_class_name.name in filter_class_names:
                FILTER = True
                break
        if FILTER:
            continue

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
        # 适用于多个dex情况，核心特征划分时构建的dex
        dex_core_method_union = get_current_dex_core_method_union(file_name, shrink_dex_path)

        result = []
        for dex_method_full_name in dex_method_names:
            if dex_method_full_name in dex_core_method_union:
                result.append(dex_method_full_name)
        if dex_core_method_union:
            if len(dex_core_method_union) >= len(dex_method_names):
                yes_cnt += 1
                y_cnt += 1
            else:
                no_cnt += 1
                n_cnt += 1
            print(
                '%-80s %-10s %-10s %-10s %-10s %s' % (
                    file_name, len(dex_d.get_methods()), len(dex_method_names), len(dex_core_method_union),
                    len(result),
                    len(result) / len(dex_core_method_union)))

    print('y_cnt: {}  n_cnt: {}'.format(y_cnt, n_cnt))


def get_current_dex_core_method_union(dex_name, shrink_dex_path):
    """
    根据给定dex，返回当前dex核心方法并集
    :param dex_name:
    :return:
    """
    dex_dirs = os.listdir(shrink_dex_path)

    method_set = set()
    for dex_folder in dex_dirs:
        dex_folder_name = dex_folder.replace('@', ':')
        # 只寻找符合条件的dex
        if dex_folder_name != dex_name:
            continue
        files = tools.list_all_files(os.path.join(shrink_dex_path, dex_folder))
        for file in files:
            if file.endswith('.dex'):
                _, target_dvm, target_dx = AnalyzeDex(file)
                for method in target_dvm.get_methods():
                    method_set.add(method.full_name)
    return method_set


filter_class_names = []

if __name__ == '__main__':

    with open(r'D:\project\pycharm\ATVHunter\apk\filter-dependency.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            filter_class_names.append(line.strip())

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
        generate_feature_and_compare(apk_path, shrink_dex_path, android_dex_path)

    print('final result => y_cnt: {}  n_cnt: {}'.format(yes_cnt, no_cnt))
