import os

from androguard.misc import AnalyzeDex, AnalyzeAPK

from tools import tools

yes_cnt = 0
no_cnt = 0


def generate_feature_and_compare(apk_path, shrink_dex_path, android_dex_path):
    if not os.path.exists(shrink_dex_path):
        return
    global yes_cnt
    global no_cnt

    y_cnt = 0
    n_cnt = 0

    app, d_list, app_dx = AnalyzeAPK(apk_path)
    print(app.get_package())

    for root, folders, files in os.walk(android_dex_path):
        for file in files:
            if not str(file).endswith(".dex"):  # 非dex结尾，跳过
                continue
            file_name = file[:-4].replace('@', ':')

            dex_file = os.path.join(root, file)
            dex_hash, dex_d, dex_dx = AnalyzeDex(dex_file)

            # apk模块解耦之后找到最佳匹配的模块，构建类名的集合
            # match_result = []
            # for cd_cla_list in module_item_class_names:
            #     match_list = []
            #     for ca in dex_d.get_classes():
            #         ca_name = ca.name
            #         if ca_name in cd_cla_list:
            #             match_list.append(ca_name)
            #     match_result.append(match_list)
            # best_match_result = max(match_result, key=len)

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

            # 适用于核心特征并集时构建的dex
            # dex_core_method_union = get_core_method_in_curr_dex(file_name)

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


if __name__ == '__main__':

    path = r'F:\zc-data\RQ\RQ1\apks'
    # path = r'F:\zc-data\RQ\RQ1\small-scale'
    apk_folders = os.listdir(path)

    for apk_folder in apk_folders:
        apk_folder_path = os.path.join(path, apk_folder)
        folder_under_files = os.listdir(apk_folder_path)
        # print(folder_under_files)
        apk_path = ''
        for folder_under_file in folder_under_files:

            # todo: 验证未收缩代码开启改行代码即可
            # if not folder_under_file.endswith('-shrink.apk'):

            if folder_under_file.endswith('-shrink.apk'):
                apk_path = os.path.join(apk_folder_path, folder_under_file)
                break
        # shrink_dex_path = os.path.join(apk_folder_path, 'shrink-dex-output')
        # shrink_dex_path = os.path.join(apk_folder_path, 'apk-shrink-dex-output')
        shrink_dex_path = os.path.join(apk_folder_path, 'shrink-dex-output-final')
        android_dex_path = os.path.join(apk_folder_path, 'tpl')
        # android_dex_path = os.path.join(apk_folder_path, 'dex') # 暂时修改
        generate_feature_and_compare(apk_path, shrink_dex_path, android_dex_path)

    print('final result => y_cnt: {}  n_cnt: {}'.format(yes_cnt, no_cnt))
