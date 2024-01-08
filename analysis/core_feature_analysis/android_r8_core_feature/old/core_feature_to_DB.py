import os

from androguard.misc import AnalyzeDex

import generate_feature
from database.utils.feature_business_utils import update_core_feature
from tools import tools

"""
    intput_path: D:\\Android-exp\\exp-example\\faketraveler\\shrink-dex
                 D:\\Android-exp\\exp-example\\haircomb\\shrink-dex
"""

dex_dir_path = r'F:\zc-data\RQ\RQ1\small-scale\shrink-dex-output'


def dex_all_dependency_generate_core_feature():
    """
    根据dex的所有下游依赖生成的shrink_dex的方法特征的并集作为核心特征
    :return:
    """
    dex_dirs = os.listdir(dex_dir_path)

    for dex_folder in dex_dirs:
        dex_folder_name = dex_folder.replace('@', ':')
        files = tools.list_all_files(os.path.join(dex_dir_path, dex_folder))
        core_feature_union = set()
        core_class = set()
        for file in files:
            if file.endswith('.dex'):
                # filename = tools.get_filename_from_path(file).replace('@', ':')
                _, target_dvm, target_dx = AnalyzeDex(file)

                class_name_set = set()  # 收集每个dex中所有的class file name
                for class_name in target_dvm.get_classes():
                    class_name_set.add(class_name.name)
                    core_class.add(class_name.name)

                core_cla_count, core_fined_feature = generate_feature.generate_fined_feature_cfg(target_dx,
                                                                                                 class_name_set)
                # 取并集
                core_feature_union = core_feature_union.union(core_fined_feature)

        core_method_count = len(core_feature_union)
        core_cla_count = len(core_class)
        print(dex_folder_name, core_cla_count, core_method_count)

        # 非空，更新数据库
        if core_feature_union:
            update_core_feature(dex_folder_name, core_cla_count, core_method_count, core_feature_union)


if __name__ == '__main__':
    dex_all_dependency_generate_core_feature()
