import os

import networkx as nx
from androguard.misc import AnalyzeDex

import generate_feature
import tools.tools

"""
    dex_dir_path: D:\\Android-exp\\exp-example\\faketraveler\\shrink-dex
                  D:\\Android-exp\\exp-example\\haircomb\\shrink-dex
"""

dex_dir_path = r'D:\Android-exp\exp-example\haircomb\shrink-dex'


def analysis_cluster_result():
    dex_dirs = os.listdir(dex_dir_path)
    for dex_folder in dex_dirs:
        files = tools.tools.list_all_files(os.path.join(dex_dir_path, dex_folder))
        sets = []
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
        cluster_num, cluster_feature = format_core_feature_clusters(sets)
        print(cluster_num, len(cluster_feature))


def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


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
            if similarity > threshold:
                G.add_edge(i, j, weight=similarity)
    return G


def cluster_sets(similarity_graph):
    clusters = list(nx.connected_components(similarity_graph))
    return clusters


def format_core_feature_clusters(sets):
    threshold = 0.9
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

    # # Visualization
    # pos = nx.spring_layout(similarity_graph)  # Layout algorithm
    # edges = [(u, v) for u, v, d in similarity_graph.edges(data=True)]
    # weights = [similarity_graph[u][v]['weight'] * 5 for u, v in edges]
    #
    # plt.figure(figsize=(10, 8))
    # nx.draw(similarity_graph, pos, edgelist=edges, width=weights, with_labels=True, font_size=10,
    #         node_color='lightblue', edge_color='gray', alpha=0.7, node_size=2000, font_weight='bold')
    #
    # plt.title("Similarity Graph of Sets")
    # plt.show()
    #
    # print('%-80s %-10s %-10s %s' % (dex_name, gav_cnt, ga_cnt, len(clusters)))
    # for i, cluster in enumerate(clusters):
    #     print(f"Cluster {i + 1}: {cluster}")


if __name__ == '__main__':
    analysis_cluster_result()
