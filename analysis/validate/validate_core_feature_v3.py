import os

from androguard.misc import AnalyzeAPK, AnalyzeDex

from tools import tools

dex_dir_path = r'F:\zc-data\RQ\RQ1\small-scale-by-ga\shrink-dex-output'
android_apk_path = r"F:\zc-data\RQ\RQ1\small-scale-by-ga\com.appmindlab.nano_1315_src\app-release-unsigned-shrink.apk"

"""
直接通过APK方法进行验证，没有考虑所有类的情况，该文件考虑删除
"""


def generate_feature_and_compare(apk_path, dex_path):
    app, d_list, app_dx = AnalyzeAPK(apk_path)
    print(app.get_package())

    y_cnt = 0
    n_cnt = 0

    for root, folders, files in os.walk(dex_path):
        for file in files:
            if not str(file).endswith(".dex"):  # 非dex结尾，跳过
                continue
            file_name = file[:-4].replace('@', ':')

            dex_file = os.path.join(root, file)
            dex_hash, dex_d, dex_dx = AnalyzeDex(dex_file)

            app_method_full_names = []
            for app_d in d_list:
                for app_method in app_d.get_methods():
                    app_method_full_names.append(app_method.full_name)
            best_match_method_list = []
            for dex_method in dex_d.get_methods():
                if dex_method.full_name in app_method_full_names:
                    best_match_method_list.append(dex_method.full_name)

            # 适用于多个dex情况，核心特征划分时构建的dex
            dex_core_method_union = get_current_dex_core_method_union(file_name)

            result = []
            if dex_core_method_union:
                for dex_method_full_name in best_match_method_list:
                    if dex_method_full_name in dex_core_method_union:
                        result.append(dex_method_full_name)
                if len(dex_core_method_union) >= len(best_match_method_list):
                    y_cnt += 1
                else:
                    n_cnt += 1
                print(
                    '%-80s %-10s %-10s %-10s %-10s %s' % (
                        file_name, len(dex_d.get_methods()), len(best_match_method_list), len(dex_core_method_union),
                        len(result),
                        len(result) / len(dex_core_method_union)))

        print('y_cnt: {}  n_cnt: {}'.format(y_cnt, n_cnt))


def get_current_dex_core_method_union(dex_name):
    """
    根据给定dex，返回当前dex核心方法并集
    :param dex_name:
    :return:
    """
    dex_dirs = os.listdir(dex_dir_path)

    method_set = set()
    for dex_folder in dex_dirs:
        dex_folder_name = dex_folder.replace('@', ':')
        # 只寻找符合条件的dex
        if dex_folder_name != dex_name:
            continue
        files = tools.list_all_files(os.path.join(dex_dir_path, dex_folder))
        for file in files:
            if file.endswith('.dex'):
                _, target_dvm, target_dx = AnalyzeDex(file)
                for method in target_dvm.get_methods():
                    method_set.add(method.full_name)
    return method_set


if __name__ == '__main__':
    android_dex_path = r'F:\zc-data\RQ\RQ1\small-scale-by-ga\dex'
    generate_feature_and_compare(android_apk_path, android_dex_path)
