import os

from androguard.misc import AnalyzeDex, get_default_session
from matplotlib import pyplot
from upsetplot import UpSet, from_memberships, plot
from upsetplot import from_contents

import generate_feature
import tools.tools

# def jaccard_similarity(set1, set2):
#     intersection = len(set1.intersection(set2))
#     union = len(set1.union(set2))
#     return intersection / union


# def set_similarity(set1, set2):
#     min_len = len(set1) if len(set1) < len(set2) else len(set2)
#     intersection_len = len(set1.intersection(set2))
#     return intersection_len / min_len

# example = from_memberships(
#     [[],
#      ['cat2'],
#      ['cat1'],
#      ['cat1', 'cat2'],
#      ['cat0'],
#      ['cat0', 'cat2'],
#      ['cat0', 'cat1'],
#      ['cat0', 'cat1', 'cat2'],
#      ],
#     data=[56, 283, 1279, 5882, 24, 90, 429, 1957]
# )
#
# plot(example)
# pyplot.show()

dex_dir_path = r'D:\Android-exp\shrink-dex-output-faketraveler'


def get_current_dex_core_feature_clusters_():
    """
    根据给定dex，返回当前dex核心特征划分后的集合
    :param dex_name:
    :return:
    """
    dex_dirs = set(os.listdir(dex_dir_path))

    for dex_folder in dex_dirs:
        # dex_folder_name = dex_folder.replace('@', ':')
        # 只寻找符合条件的dex
        # if dex_folder_name != dex_name:
        #     continue

        files = tools.tools.list_all_files(os.path.join(dex_dir_path, dex_folder))

        tpl_set = []
        set_dict = {}

        test_set = []

        for i, file in enumerate(files):
            if file.endswith('.dex'):
                gav = file.split('\\')[-1][:-4].split('@')
                ga = gav[0] + '@' + gav[1]
                tpl_set.append(ga)
                _, target_dvm, target_dx = AnalyzeDex(file)

                # method_set = set()
                # for method in target_dvm.get_methods():
                #     method_set.add(method.full_name)
                # sets.append(method_set)

                class_name_set = set()  # 收集每个dex中所有的class file name
                for class_name in target_dvm.get_classes():
                    class_name_set.add(class_name.name)

                core_cla_count, core_fined_feature = generate_feature.generate_fined_feature_cfg(target_dx,
                                                                                                 class_name_set)
                # 清空session，减少内存占用
                session = get_default_session()
                session.reset()

                set_dict['set' + str(i)] = set(core_fined_feature)
                test_set.append(set(core_fined_feature))
        if test_set:
            print(dex_folder)
            result = from_memberships(test_set)

            # print(result)

            # orientation='vertical'
            ax_dict = UpSet(result, subset_size='count', sort_by='cardinality', show_counts=True, show_percentages=True).plot()

            # pyplot.show()

            pyplot.savefig(r"F:\upsetpng\{}.png".format(dex_folder))


if __name__ == '__main__':
    get_current_dex_core_feature_clusters_()
