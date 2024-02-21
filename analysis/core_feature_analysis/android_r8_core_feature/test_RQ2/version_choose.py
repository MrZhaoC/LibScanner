def read_dependency_file(dependency_file_path):
    dependencies_list = []
    with open(dependency_file_path, 'r') as f:
        content = f.readlines()
        for line in content:
            if line.strip() == '':
                continue
            tpl = line.split('@')[0]
            # ext = line.split('@')[1]
            tpl = tpl.replace('|', '').replace('+', '').replace('---', '').replace('\\', '').lstrip()
            if '>' in tpl:
                tpl = tpl.split('->')
                gav = tpl[0].split(':')
                final_gav = gav[0] + ':' + gav[1] + ':' + tpl[1].strip().replace('(*)', '').replace('(c)', '').strip()
                dependencies_list.append(final_gav)
            else:
                _gav = tpl.replace('(*)', '').replace('(c)', '').strip()
                dependencies_list.append(_gav)
    print('原依赖树依赖项个数：', len(dependencies_list))
    print('去重之后依赖项个数：', len(set(dependencies_list)))
    return set(dependencies_list)


def read_all_version():
    all_tpl_info = []
    with open(r"F:\zc-data\RQ\RQ2\all-dependency.txt", 'r') as f:
        result = f.readlines()
        for line in result:
            all_tpl_info.append(line.strip())
    return all_tpl_info


def version_choose():
    dep_file_path = r"F:\zc-data\RQ\RQ1\all-dependency.txt"
    dependency_list = read_dependency_file(dep_file_path)

    result = set()

    all_version_dependency_list = read_all_version()
    for gav1 in dependency_list:
        gav1_list = gav1.split(':')
        if len(gav1_list) < 3:
            continue
        ga = gav1_list[0] + ':' + gav1_list[1]
        v = gav1_list[2]
        if len(v.split('.')) < 2:
            continue
        format_v = v.split('.')[0] + '.' + v.split('.')[1]
        format_gav = ga + ':' + format_v
        for gav2 in all_version_dependency_list:
            gav2_list = gav2.split(':')
            if len(gav2_list) < 3:
                continue
            v2 = gav2_list[2]

            if '-' in v2:
                continue
            if gav2.startswith(format_gav):
                print(gav2)
                result.add(gav2)
    print(len(result))
    with open(r"F:\zc-data\RQ\RQ2\filter-all-dependency.txt", 'w') as f:
        for x in sorted(result):
            f.write(x + '\n')


if __name__ == '__main__':
    version_choose()
