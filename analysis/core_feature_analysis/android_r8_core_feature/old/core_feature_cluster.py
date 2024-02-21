import os
import warnings

import matplotlib.pyplot as plt
import networkx as nx
import venn
from androguard.misc import AnalyzeDex, get_default_session

import generate_feature
import tools.tools

warnings.filterwarnings("ignore")

"""
    dex_dir_path: D:\\Android-exp\\exp-example\\faketraveler\\shrink-dex
                  D:\\Android-exp\\exp-example\\haircomb\\shrink-dex
"""

# dex_dir_path = r'D:\Android-exp\shrink-dex-output'
dex_dir_path = r'F:\zc-data\RQ\RQ1\shrink-dex-output'

def get_current_dex_core_feature_clusters(dex_name):
    """
    根据给定dex，返回当前dex核心特征划分后的集合
    :param dex_name:
    :return:
    """
    dex_dirs = os.listdir(dex_dir_path)

    sets = []
    for dex_folder in dex_dirs:
        dex_folder_name = dex_folder.replace('@', ':')
        # 只寻找符合条件的dex
        if dex_folder_name != dex_name:
            continue
        files = tools.tools.list_all_files(os.path.join(dex_dir_path, dex_folder))
        tpl_set = set()
        for file in files:
            if file.endswith('.dex'):
                gav = file.split('\\')[-1][:-4].split('@')
                ga = gav[0] + '@' + gav[1]
                tpl_set.add(ga)
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
                sets.append(set(core_fined_feature))
    # 调用
    return format_core_feature_clusters(sets)


def get_current_dex_core_feature_clusters_():
    """
    根据给定dex，返回当前dex核心特征划分后的集合
    :param dex_name:
    :return:
    """
    dex_dirs = os.listdir(dex_dir_path)

    for dex_folder in dex_dirs:
        # dex_folder_name = dex_folder.replace('@', ':')
        # 只寻找符合条件的dex
        # if dex_folder_name != dex_name:
        #     continue

        files = tools.tools.list_all_files(os.path.join(dex_dir_path, dex_folder))

        tpl_set = []
        sets = []

        for file in files:
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
                sets.append(set(core_fined_feature))

                # 清空session，减少内存占用
                session = get_default_session()
                session.reset()
        # 调用
        set_num, feature_set = format_core_feature_clusters(sets)

        draw_venn(feature_set)

        print('%-80s %-20s %-20s' % (dex_folder, len(files), set_num))


def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


def set_similarity(set1, set2):
    min_len = len(set1) if len(set1) < len(set2) else len(set2)
    intersection_len = len(set1.intersection(set2))
    return intersection_len / min_len


def build_similarity_graph(sets, threshold):
    """
    Build similarity graph based on Jaccard similarity
    :param sets:
    :param threshold:
    :return:
    """
    G = nx.Graph()
    for i, set1 in enumerate(sets):
        G.add_node(i)
        for j, set2 in enumerate(sets):
            if j <= i:  # Avoid duplicate computation
                continue
            similarity = jaccard_similarity(set1, set2)
            # similarity = set_similarity(set1, set2)
            if similarity > threshold:
                G.add_edge(i, j, weight=similarity)
    return G


def cluster_sets(similarity_graph):
    clusters = list(nx.connected_components(similarity_graph))
    return clusters


def format_core_feature_clusters(sets):
    threshold = 0.7
    similarity_graph = build_similarity_graph(sets, threshold)
    clusters = cluster_sets(similarity_graph)

    feature_clusters = []

    for component in clusters:
        f_clusters = set()
        for index in component:
            for feature in sets[index]:
                f_clusters.add(feature)
        feature_clusters.append(f_clusters)

    return len(clusters), feature_clusters


def draw_venn(feature_set):
    feature_set_size = len(feature_set)

    # print(feature_set_size, len(tpl_set))

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文
    plt.figure(figsize=(14, 8), dpi=200)  # 创建画布

    # labels = venn.get_labels(feature_set)

    print(feature_set_size)
    if feature_set_size == 2:
        labels = venn.generate_petal_labels(feature_set)
        venn.venn2(labels, names=list('ab'))
    elif feature_set_size == 3:
        labels = venn.generate_petal_labels(feature_set)
        venn.venn3(labels, names=list('abc'))
    elif feature_set_size == 4:
        labels = venn.generate_petal_labels(feature_set)
        venn.venn4(labels, names=list('abcd'))
    elif feature_set_size == 5:
        labels = venn.generate_petal_labels(feature_set)
        venn.venn5(labels, names=list('abcde'))
    elif feature_set_size == 6:
        labels = venn.generate_petal_labels(feature_set)
        venn.venn6(labels, names=list('abcdef'))
    else:
        pass
    plt.show()


if __name__ == '__main__':
    get_current_dex_core_feature_clusters_()
