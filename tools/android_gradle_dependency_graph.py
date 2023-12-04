import networkx as nx


class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []


def format_input_dependency_file(file_path=r'F:\pythonProject\ATVHunter\tools\dependencies.txt'):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    result = [line.replace('+---', '#').replace('|    ', '#').replace('\\---', '#')
              .replace("     ", "#").replace("(*)", "").replace("(c)", "").strip()
              for line in lines]

    return result


def build_tree(data):
    root = TreeNode("root")
    current_nodes = [root]

    for line in data:
        depth = line.count("#")
        node_name = line.lstrip("#").strip()
        new_node = TreeNode(node_name)

        if depth == 0:
            root.children.append(new_node)
        else:
            while len(current_nodes) <= depth:
                current_nodes.append(None)

            parent = current_nodes[depth - 1]
            parent.children.append(new_node)
            current_nodes[depth] = new_node

    return root


def print_tree(node, indent=0):
    print("#" * indent + " " + node.name)

    for child in node.children:
        if child:
            print_tree(child, indent + 1)


dependency_graph = nx.DiGraph()
# dependency_graph = pgv.AGraph(directed=True, strict=True)
node_map = {}


def convert_dependency_tree_2_graph(root, indent=0):
    root_name = root.name

    if '->' in root_name:
        node_names = root_name.split('->')
        node_name1 = node_names[0].strip()
        root_name = node_names[1].strip()

        if ':' not in node_names[1]:
            gav = node_name1.split(":")
            ga = gav[0] + ":" + gav[1]
            root_name = ga + ":" + node_names[1].strip()

    for child in root.children:
        if child:
            child_name = child.name

            if '->' in child_name:
                child_names = child_name.split('->')
                child_name1 = child_names[0].strip()
                child_name = child_names[1].strip()

                if ':' not in child_names[1]:
                    c_gav = child_name1.split(":")
                    c_ga = c_gav[0] + ":" + c_gav[1]
                    child_name = c_ga + ":" + child_names[1].strip()

            value = f"{root.name}-->{child.name}"

            if node_map.get(child_name):
                value_list = node_map.get(child_name)
                value_list.append(value)
                node_map[child_name] = value_list
            else:
                node_map[child_name] = [value]

            if not dependency_graph.has_edge(root_name, child.name):
                dependency_graph.add_edge(root_name, child_name)

            convert_dependency_tree_2_graph(child, indent + 1)

    return dependency_graph


def print_format_dependency_tree(node, indent=0):
    print("#" * indent + " " + node.name)

    for child in node.children:
        if child:
            print(child.name)


def get_curr_parents(target_node_name):
    tree_root = build_tree(format_input_dependency_file())
    graph = convert_dependency_tree_2_graph(tree_root)
    curr_node_parents = []

    for node_name in graph.nodes():
        if target_node_name in graph.neighbors(node_name):
            curr_node_parents.append(node_name)

    return curr_node_parents


if __name__ == "__main__":

    target_gav = r'com.nononsenseapps:filepicker:4.2.1'

    # for dependency_chain in node_map.get(target_gav):
    #     print(dependency_chain)

    parents = get_curr_parents(target_gav)
    for parent in parents:
        print(parent)
    # path = r'D:\Android-exp\exp-example\apk-haircomb'
    #
    # dependencies_tree_path = r"D:\Android-exp\exp-example\haircomb\haircomb_dependencies.txt"
    # apk_dependencies = tools.get_dependency_from_file(dependencies_tree_path)
    #
    # apk_dependency_path = r'F:\maven-data\haircomb\dependencies'
    # files = tools.list_all_files(apk_dependency_path)
    #
    # for dep in apk_dependencies:
    #     dep_path = os.path.join(path, dep.replace(":", "@"))
    #     if not os.path.exists(dep_path):
    #         os.makedirs(dep_path)
    #     dep_file_name = dep.replace(":", "@")
    #     library_file_path = ''
    #     for file in files:
    #         file_name = file.split('\\')[-1]
    #         if dep_file_name + ".aar" == file_name:
    #             # print(file_name)
    #             library_file_path = file
    #             break
    #         elif dep_file_name + ".jar" == file_name:
    #             # print(file_name)
    #             library_file_path = file
    #             break
    #     # 创建文件件，复制文件
    #     library_path = os.path.join(dep_path, 'library')
    #     if not os.path.exists(library_path):
    #         os.makedirs(library_path)
    #     # 复制文件
    #     if library_file_path:
    #         shutil.copy(library_file_path, library_path)
    #     else:
    #         print("{}文件不存在".format(library_file_path))
    #
    #     dex_path = os.path.join(dep_path, 'dex')
    #     if not os.path.exists(dex_path):
    #         os.makedirs(dex_path)
    #     # 寻找符合条件的dex依赖
    #     parents = get_curr_parents(dependency_g, dep)
    #     parents.append(dep)
    #     for parent in parents:
    #         for file in files:
    #             file_name = file.split('\\')[-1]
    #             parent_file_name = parent.replace(":", "@")
    #             if parent_file_name + ".dex" == file_name:
    #                 # 复制文件
    #                 shutil.copy(file, dex_path)
    #                 break
