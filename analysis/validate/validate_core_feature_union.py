import ast
import os

import networkx as nx
from androguard.misc import AnalyzeAPK, AnalyzeDex, get_default_session

from analysis.module_decoupling.module_decoupling_for_apk import get_connected_components
from database.utils import feature_business_utils
from tools import tools
from tools.tools import write_excel_xlsx

dex_dir_path = r'D:\Android-exp\exp-example\haircomb\2024-01-11\shrink-dex-output'
android_apk_path = r"D:\Android-exp\exp-example\haircomb\apk\app-release-unsigned-shrink.apk"
class_names = []
candidate_class_list = []
candidate_method_list = []

d_list, apk_dx, modules = get_connected_components(android_apk_path)


def get_tpl_modules_in_apk():
    """
    获取模块解耦后的类名称的集合
    :return:
    """
    module_item_class_names = []
    for con_components in nx.connected_components(modules):
        cla_list = []
        for cla in con_components:
            cla = apk_dx.classes[cla]
            cla_list.append(cla.name)
        module_item_class_names.append(cla_list)
    return module_item_class_names


def compare_classes(dex_path):
    """
    每个DEX文件找到最佳的匹配类集合
    :param dex_path:
    :return:
    """
    for root, folders, files in os.walk(dex_path):
        for file in files:
            if not str(file).endswith(".dex"):  # 非dex结尾，跳过
                continue
            dex_file = os.path.join(root, file)
            dex_hash, d, t_dx = AnalyzeDex(dex_file)

            similarity_score = []
            for cd_cla_list in candidate_class_list:
                match_list = []
                for ca in d.get_classes():
                    ca = ca.name
                    if ca in cd_cla_list:
                        match_list.append(ca)
                match_sim = len(match_list) / len(d.get_classes())
                similarity_score.append(match_sim)
            print('{} --> {}'.format(file, max(similarity_score)))


def compare_methods(dex_path):
    """
    每个DEX文件找到最佳的匹配方法集合
    :param dex_path:
    :return:
    """
    for root, folders, files in os.walk(dex_path):
        for file in files:
            if not str(file).endswith(".dex"):  # 非dex结尾，跳过
                continue
            dex_file = os.path.join(root, file)
            dex_hash, d, t_dx = AnalyzeDex(dex_file)
            similarity_score = []
            for cd_method_list in candidate_method_list:
                match_list = []
                for me in d.get_methods():
                    me = me.full_name
                    if me in cd_method_list:
                        match_list.append(me)
                match_sim = len(match_list) / len(d.get_methods())
                similarity_score.append([len(match_list), len(d.get_methods()), match_sim])
            print('{} --> {}'.format(file, max(similarity_score, key=lambda x: x[2])))


def validate_method(dex_path):
    for con_components in nx.connected_components(modules):
        method_list = []
        for cla in con_components:
            cla = apk_dx.classes[cla]
            for method in cla.get_methods():
                method_list.append(method.full_name)
        candidate_method_list.append(method_list)
    compare_methods(dex_path)


def validate_class(dex_path):
    for con_components in nx.connected_components(modules):
        cla_list = []
        for cla in con_components:
            cla = apk_dx.classes[cla]
            cla_list.append(cla.name)
        candidate_class_list.append(cla_list)
    compare_classes(dex_path)


def validate_method_no_module_decoupling(apk_path, dex_path):
    apk_a, apk_d_list, apk_dxx = AnalyzeAPK(apk_path)
    methods = []
    for d in apk_d_list:
        for me in d.get_methods():
            methods.append(me.full_name)
    for root, folders, files in os.walk(dex_path):
        for file in files:
            if str(file).endswith(".dex"):
                dex_file = os.path.join(root, file)
                file = file.replace('@', ':')
                dex_hash, t_d, t_dx = AnalyzeDex(dex_file)
                match = set()
                for meth in t_d.get_methods():
                    if meth.full_name in methods:
                        match.add(meth.full_name)
                print('%-70s %-10s %s' % (file, len(t_d.get_methods()), len(match)))


def validate_class_no_module_decoupling(apk_path, dex_path):
    cur_apk_a, cur_apk_d_list, cur_apk_dx = AnalyzeAPK(apk_path)
    classes = []
    for d in cur_apk_d_list:
        for cla in d.get_classes():
            classes.append(cla.name)
    for root, folders, files in os.walk(dex_path):
        for file in files:
            if str(file).endswith(".dex"):
                dex_file = os.path.join(root, file)
                file = file.replace('@', ':')
                dex_hash, d, t_dx = AnalyzeDex(dex_file)
                match = []
                methods = []
                for cla in d.get_classes():
                    if cla.name in classes:
                        match.append(cla.name)
                        for method in cla.get_methods():
                            methods.append(method.full_name)

                print(file, len(d.get_classes()), len(match), len(methods))


def validate_single_dex_no_module_decoupling(single_dex_path):
    classes = []
    for d in d_list:
        for cla in d.get_classes():
            classes.append(cla.name)
    dex_hash, dex_d, dex_dx = AnalyzeDex(single_dex_path)
    match = []
    for cla in dex_d.get_classes():
        if cla.name in classes:
            match.append(cla.name)
    return match


# 2023-05-17
def validate_apk_shrink_class(dex_path):
    """
    此方法用来验证apk在代码收缩模块解耦后比较dex中的class，对于dex中相同类名的类生成特征
    目的是验证类中方法数量的变化，由于收缩之后类中方法会被删除
    :param dex_path:
    :return:
    """
    module_item_class_names = get_tpl_modules_in_apk()

    for root, folders, files in os.walk(dex_path):
        for file in files:
            if not str(file).endswith(".dex"):  # 非dex结尾，跳过
                continue
            file_name = file[:-4].replace('@', ':')

            dex_file = os.path.join(root, file)
            dex_hash, dex_d, dex_dx = AnalyzeDex(dex_file)

            # apk模块解耦之后找到最佳匹配的模块，构建类名的集合
            match_result = []
            for cd_cla_list in module_item_class_names:
                match_list = []
                for ca in dex_d.get_classes():
                    ca_name = ca.name
                    if ca_name in cd_cla_list:
                        match_list.append(ca_name)
                match_result.append(match_list)
            best_match_result = max(match_result, key=len)

            # 每个dex在apk中找到最佳匹配的模块，构建类名的集合，给出apk和dex中分别对应的方法集合
            apk_method_names = []
            dex_method_names = []
            for cla_name in best_match_result:
                apk_class = apk_dx.classes[cla_name]
                for apk_method in apk_class.get_methods():
                    apk_method_names.append(apk_method.full_name)
                dex_class = dex_dx.classes[cla_name]
                for dex_method in dex_class.get_methods():
                    dex_method_names.append(dex_method.full_name)

            # real_apk_shrink_dex_class_names: apk代码收缩之后dex在其中比较到类集合，也就是APK代码收缩之后剩余的类
            real_apk_shrink_dex_class_names = validate_single_dex_no_module_decoupling(dex_file)

            # TPL名称
            # DEX中类数量 DEX中方法数量
            # 比较apk模块解耦产生的影响：DEX匹配shrink_APK类数量 DEX匹配md_shrink_APK类数量
            # 每个dex在apk中找到最佳匹配的模块，构建类名的集合，给出apk和dex中分别对应的方法集合
            print([file_name,
                   len(dex_d.get_classes()), len(dex_d.get_methods()),
                   len(real_apk_shrink_dex_class_names), len(best_match_result),
                   len(apk_method_names), len(dex_method_names)])


def validate_apk_shrink_method(dex_path):
    """
    对于给定shrink_apk,分析其中TPL方法集合的存在情况
    :param dex_path:
    :return:
    """
    module_item_class_names = get_tpl_modules_in_apk()

    for root, folders, files in os.walk(dex_path):
        for file in files:
            if not str(file).endswith(".dex"):  # 非dex结尾，跳过
                continue
            file_name = file[:-4].replace('@', ':')

            dex_file = os.path.join(root, file)
            dex_hash, dex_d, dex_dx = AnalyzeDex(dex_file)

            # apk模块解耦之后找到最佳匹配的模块，构建类名的集合
            match_result = []
            for cd_cla_list in module_item_class_names:
                match_list = []
                for ca in dex_d.get_classes():
                    ca_name = ca.name
                    if ca_name in cd_cla_list:
                        match_list.append(ca_name)
                match_result.append(match_list)
            best_match_result = max(match_result, key=len)

            # 根据最佳匹配的类名的集合，构建APK方法名的集合
            apk_method_names = []
            for cla_name in best_match_result:
                apk_class = apk_dx.classes[cla_name]
                for apk_method in apk_class.get_methods():
                    if apk_method.is_external():
                        continue
                    apk_method_names.append(apk_method.full_name)

            # 根据APK方法名的集合，构建dex方法名的集合(存在略有不同的情况)
            dex_method_names = []
            for dex_class in dex_dx.get_classes():
                for dex_method in dex_class.get_methods():
                    if dex_method.is_external():
                        continue
                    if dex_method.full_name in apk_method_names:
                        dex_method_names.append(dex_method.full_name)

            # 根据APK方法名的集合,分析哪些方法不在dex中 => R8关于lambda生成得到方法 and others
            # dex_all_method_names = []
            # for dex_method in dex_dx.get_methods():
            #     if dex_method.is_external():
            #         continue
            #     dex_all_method_names.append(dex_method.full_name)
            # for apk_method_full_name in apk_method_names:
            #     if apk_method_full_name not in dex_all_method_names:
            #         print(apk_method_full_name)

            # res = set(apk_method_names) - set(dex_methods_names)  # R8关于lambda生成得到方法

            # TPL文件名称
            # SHRINK_APK最佳匹配方法集合（代码收缩之后APK中某个TPL剩余方法集合）
            # SHRINK_APK最佳匹配方法集合对应ANDROID_DEX中方法的集合
            # ANDROID_DEX中原本方法集合
            print(
                '%-80s %-10s %10s %s' % (
                    file_name, len(apk_method_names), len(dex_method_names), len(dex_d.get_methods())))

            # 清空session，减少内存占用
            session = get_default_session()
            session.reset()


def generate_feature_and_compare(dex_path):
    # tpl_db_data = format_features_from_db()

    module_item_class_names = get_tpl_modules_in_apk()

    for root, folders, files in os.walk(dex_path):
        for file in files:
            if not str(file).endswith(".dex"):  # 非dex结尾，跳过
                continue
            file_name = file[:-4].replace('@', ':')

            dex_file = os.path.join(root, file)
            dex_hash, dex_d, dex_dx = AnalyzeDex(dex_file)

            # apk模块解耦之后找到最佳匹配的模块，构建类名的集合
            match_result = []
            for cd_cla_list in module_item_class_names:
                match_list = []
                for ca in dex_d.get_classes():
                    ca_name = ca.name
                    if ca_name in cd_cla_list:
                        match_list.append(ca_name)
                match_result.append(match_list)
            best_match_result = max(match_result, key=len)
            # print(file_name, len(best_match_result), len(dex_d.get_classes()))

            # core_cla_count, core_fined_feature = generate_feature.generate_fined_feature_cfg(apk_dx, best_match_result)
            #
            # for tpl_info in tpl_db_data:
            #     db_tpl_name = tpl_info['tpl_name']
            #     # db_tpl_core_class_count = tpl_info['core_cla_count']
            #     # db_tpl_core_method_count = tpl_info['core_method_count']
            #     db_tpl_core_fine_grained_feature = tpl_info['core_fined_feature']
            #     if db_tpl_name == file_name and db_tpl_core_fine_grained_feature:
            #         result = set(core_fined_feature).intersection(set(db_tpl_core_fine_grained_feature))
            #         print('%-80s %-10s %-10s %-10s %s' % (file_name, len(core_fined_feature), len(db_tpl_core_fine_grained_feature), len(result),
            #                                               len(result) / len(db_tpl_core_fine_grained_feature)))

            # 根据最佳匹配的类名的集合，构建APK方法名的集合
            apk_method_names = []
            for cla_name in best_match_result:
                apk_class = apk_dx.classes[cla_name]
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
            dex_core_method_union = get_current_dex_core_method_union(file_name)

            # 适用于核心特征并集时构建的dex
            # dex_core_method_union = get_core_method_in_curr_dex(file_name)

            result = []
            for dex_method_full_name in dex_method_names:
                if dex_method_full_name in dex_core_method_union:
                    result.append(dex_method_full_name)
            if dex_core_method_union:
                print(
                    '%-80s %-10s %-10s %-10s %-10s %s' % (
                        file_name, len(dex_d.get_methods()), len(dex_method_names), len(dex_core_method_union),
                        len(result),
                        len(result) / len(dex_core_method_union)))


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


def get_core_method_in_curr_dex(curr_dex):
    files = tools.list_all_files(dex_dir_path)
    curr_dex_name = curr_dex.split("\\")[-1]
    method_set = set()
    for dex_file in files:
        # 只需找符合条件的dex
        dex_file_name = dex_file.split("\\")[-1][:-4].replace("@", ":")
        if dex_file_name != curr_dex_name:
            continue
        if dex_file.endswith(".dex"):
            _, target_dvm, target_dx = AnalyzeDex(dex_file)
            for method in target_dvm.get_methods():
                method_set.add(method.full_name)
    return method_set


def format_features_from_db():
    data = feature_business_utils.get_all_tpl_feature()
    for tpl_info in data:
        tpl_info['course_feature'] = ast.literal_eval(tpl_info['course_feature'])
        tpl_info['fined_feature'] = ast.literal_eval(tpl_info['fined_feature'])
        if tpl_info['core_fined_feature']:
            tpl_info['core_fined_feature'] = ast.literal_eval(tpl_info['core_fined_feature'])
        else:
            tpl_info['core_fined_feature'] = []
    return data


def get_tpl_base_info(dex_path):
    """
    :param dex_path:
    :return:
    """
    excel_data = []
    # 遍历获取所有dex文件中class和method信息
    for root, folders, files in os.walk(dex_path):
        for file_name in files:
            if str(file_name).endswith(".dex"):
                dex_file = os.path.join(root, file_name)
                file_name = file_name.replace('@', ':')
                dex_hash, dex_dvm, dex_dx = AnalyzeDex(dex_file)
                excel_data.append([file_name, len(dex_dvm.get_classes()), len(dex_dvm.get_methods())])
    # android dex 基本信息写入EXCEL
    write_excel_xlsx(r'C:\Users\DELL\Desktop\new.xlsx', '20230511-apk-base-info', excel_data)


if __name__ == '__main__':
    android_dex_path = r'D:\Android-exp\exp-example\haircomb\libraries\dex'

    # 给定dex在解耦的模块中找到最佳的匹配类集合和方法集合（给出比例）
    # validate_class(dex_path)
    # validate_method(dex_path)

    # 给定dex在未解耦的模块中找到最佳的匹配类集合和方法集合
    # validate_class_no_module_decoupling(apk_path, dex_path)
    # validate_method_no_module_decoupling(apk_path, dex_path)

    # 输出dex的名称 类数量 方法数量
    # get_tpl_base_info(dex_path)

    # apk代码收缩后 模块解耦中 最佳匹配类集合 & 最佳匹配方法集合
    # validate_apk_shrink_class(dex_path)
    # validate_apk_shrink_method(android_dex_path)

    generate_feature_and_compare(android_dex_path)
