import os

from androguard.misc import AnalyzeDex

from tools import tools

DOT_DEX = '.dex'


def generate_method_keep_rule(front_dependency_dex_dir_path, t_dvm, target_dex_file, base_kr_path):
    """
    所有下游依赖构建的keep_rule规则
    :param front_dependency_dex_dir_path:
    :param t_dvm:
    :param target_dex_file:
    :param base_kr_path:
    :return:
    """
    entry_point_method_full_name_list = set()

    target_method_full_name_list = []

    # 得到目标dex的所有方法名(全限定类名+方法信息)集合
    for method in t_dvm.get_methods():
        target_method_full_name_list.append(method.full_name)

    # 去除同一库多版本影响？去除小版本号的影响
    files = tools.list_all_files(front_dependency_dex_dir_path)

    # 通过依赖关系获取所有入口方法
    for file in files:
        file_name = file.split('\\')[-1]
        if file_name == target_dex_file:
            continue
        print(file)
        # 获取文件后缀
        file_ext = os.path.splitext(file)[-1]
        if file_ext == DOT_DEX:
            _, fd_dvm, fd_dx = AnalyzeDex(file)
            for class_x in fd_dx.get_classes():
                for method_x in class_x.get_methods():
                    if method_x.full_name in target_method_full_name_list:
                        entry_point_method_full_name_list.add(method_x)

    format_method_name_keep_rules = tools.format_method_keep_rule(entry_point_method_full_name_list)

    # write_file_flag为True时写入文件
    if write_file_flag:
        with open(r'%s\%s-keep-rule.cfg' % (base_kr_path, target_dex_file[:-4]), 'w') as f:
            for kr in format_method_name_keep_rules:
                f.write(kr + '\n')


# data = []
#
#
# def get_dependency_info(front_dependency_dex_dir_path, target_dex_file):
#     files = tools.list_all_files(front_dependency_dex_dir_path)
#     cnt1 = 0
#     tpl_names = set()
#
#     for file in files:
#         file_name = file.split('\\')[-1]
#         if file_name == target_dex_file:
#             continue
#         # 获取文件后缀
#         file_ext = os.path.splitext(file)[-1]
#         if file_ext == DOT_DEX:
#             cnt1 += 1
#             gavs = file.split('\\')[-1].split('@')
#             dex_file_name = gavs[0] + ':' + gavs[1]
#             tpl_names.add(dex_file_name)
#     cnt2 = len(tpl_names)
#     print(target_dex_file, cnt1, cnt2)
#     data.append([target_dex_file, cnt1, cnt2])


# def get_method_keep_rule(dependencies_dex_path, t_dvm, target_dex_file, b_keep_rule_path):
#     dex_files = tools.list_all_files(dependencies_dex_path)
#
#     target_method_full_name_list = []
#
#     # 得到目标dex的所有方法名(全限定类名+方法信息)集合
#     for method in t_dvm.get_methods():
#         target_method_full_name_list.append(method.full_name)
#
#     for file in dex_files:
#         file_name = file.split('\\')[-1]
#         if file_name == target_dex_file:
#             continue
#         # 获取文件后缀
#         file_ext = os.path.splitext(file)[-1]
#         if file_ext == DOT_DEX:
#             method_entry_list = []
#             _, fd_dvm, fd_dx = AnalyzeDex(file)
#             for class_x in fd_dx.get_classes():
#                 for method_x in class_x.get_methods():
#                     if method_x.full_name in target_method_full_name_list:
#                         method_entry_list.append(method_x)
#             if method_entry_list:
#                 format_method_keep_rules = tools.format_method_keep_rule(method_entry_list)
#                 base_output_path = os.path.join(b_keep_rule_path, target_dex_file[:-4])
#                 if not os.path.exists(base_output_path):
#                     os.makedirs(base_output_path)
#                 # 写入文件
#                 with open(r'%s\%s-keep-rule.cfg' % (base_output_path, file_name[:-4]), 'w') as f:
#                     for kr in format_method_keep_rules:
#                         f.write(kr + '\n')


if __name__ == '__main__':
    # dependencies_tree_path = r"D:\Android-exp\exp-example\faketraveler\faketraveler-dependency-tree.txt"
    dependencies_tree_path = r"D:\Android-exp\exp-example\haircomb\haircomb_dependencies.txt"
    apk_dependencies = tools.get_dependency_from_file(dependencies_tree_path)

    # dependency_path = r'D:\Android-exp\exp-example\faketraveler\dependency'
    # dependency_path = r"F:\maven-data\haircomb\dependencies"
    dependency_path = r'D:\Android-exp\exp-example\apk-haircomb'

    # base_keep_rule_path = r'D:\Android-exp\exp-example\faketraveler\keep-rules\union-new'
    # base_keep_rule_path = r"D:\Android-exp\exp-example\haircomb\keep-rules\union-new"
    base_keep_rule_path = r'D:\Android-exp\exp-example\apk-haircomb\union-keep-rule'

    if not os.path.exists(base_keep_rule_path):
        os.makedirs(base_keep_rule_path)

    write_file_flag = True

    for folder in os.listdir(dependency_path):
        if folder.replace('@', ':') in apk_dependencies:
            dex_file = folder + '.dex'
            dex_tmp_name = os.path.join('dex', dex_file)
            base_path = os.path.join(dependency_path, folder)
            dex_path = os.path.join(base_path, dex_tmp_name)
            print(dex_path)
            if os.path.exists(dex_path):
                _, target_dvm, target_dx = AnalyzeDex(dex_path)
                generate_method_keep_rule(os.path.join(base_path, 'dex'), target_dvm, dex_file, base_keep_rule_path)

    # base_rule_path = r"D:\Android-exp\exp-example\faketraveler\configuration.txt"
    base_rule_path = r"D:\Android-exp\exp-example\haircomb\configuration.txt"
    tools.keep_rule_file_add_base_rule(base_rule_path, base_keep_rule_path)

    # 写入excel
    # path1 = r"D:\zc\第三方库检测实验数据\2023-07-05-3.xlsx"
    # write_excel_xlsx(path1, '依赖数量统计', data)
