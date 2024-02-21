from androguard.misc import AnalyzeDex, AnalyzeAPK

import tools.tools

# result_set = set()


def get_all_methods(method_analysis, methods, result_set):
    if method_analysis in result_set:
        return
    result_set.add(method_analysis)
    # to
    for _, callee_to, _ in method_analysis.get_xref_to():
        next_method_analysis = callee_to
        if next_method_analysis.full_name in methods:
            print(next_method_analysis.full_name)
            get_all_methods(next_method_analysis, methods, result_set)

    # from
    # for _, callee_from, _ in method_analysis.get_xref_from():
    #     next_method_analysis = callee_from
    #     if next_method_analysis.full_name in methods:
    #         print(next_method_analysis.full_name)
    #         get_all_methods(next_method_analysis, methods)


if __name__ == '__main__':
    # get_current_dex_core_feature_clusters_()

    result = []

    p = r"F:\zc-data\RQ\RQ1\test\classes.dex"
    list3 = []
    _, target_dvm3, target_dx3 = AnalyzeDex(p)
    print(len(target_dvm3.get_methods()))

    for method in target_dvm3.get_methods():
        list3.append(method.full_name)

    q = r"F:\zc-data\RQ\RQ1\test\androidx.fragment@fragment@1.1.0.dex"
    z = r"F:\zc-data\RQ\RQ1\test\androidx.activity@activity@1.1.0.dex"

    _, target_dvm2, target_dx2 = AnalyzeDex(z)

    method_full_names = []
    for method in target_dvm2.get_methods():
        method_full_names.append(method.full_name)

    filed_full_names = []
    for field in target_dvm2.get_fields():
        filed_full_names.append((field.name, field.proto))

    class_names = []
    for cla in target_dvm2.get_classes():
        class_names.append(cla.name)

    print('---------------------------------')

    called_field_list = set()
    result_set = set()
    _, target_dvm1, target_dx1 = AnalyzeDex(q)
    for method_x1 in target_dx1.get_methods():
        for method2 in target_dx2.get_methods():
            if method2.is_external():
                continue
            if method_x1.full_name == method2.full_name:
                get_all_methods(method2, method_full_names, result_set)
        # 获取被外部tpl调用的字段
        for cla_x, field, _ in method_x1.xrefread:
            if (field.name, field.proto) in filed_full_names:
                called_field_list.add((field.name, field.proto))
        for cla_x, field, _ in method_x1.xrefwrite:
            if (field.name, field.proto) in filed_full_names:
                called_field_list.add((field.name, field.proto))

    print(len(result_set))

    for method_x in result_set:
        for cla_x, field, _ in method_x.xrefread:
            called_field_list.add((field.name, field.proto))
        for cla_x, field, _ in method_x.xrefwrite:
            called_field_list.add((field.name, field.proto))

    print('---------------------------')

    for method_x in target_dx2.get_methods():
        for cla_x, field, _ in method_x.xrefread:
            if (field.name, field.proto) in called_field_list:
                result_set.add(method_x)
        for cla_x, field, _ in method_x.xrefwrite:
            if (field.name, field.proto) in called_field_list:
                result_set.add(method_x)

    print('-----------------------')
    format_method_keep_rules_temp = tools.tools.format_method_keep_rule(list(result_set))
    for f in format_method_keep_rules_temp:
        print(f)

    apk_path = r"F:\zc-data\RQ\RQ1\apks\cl.coders.faketraveler_9_src\app-debug-shrink.apk"
    app, d_list, app_dx = AnalyzeAPK(apk_path)
    for d in d_list:
        for method in d.get_methods():
            if 'Landroidx/activity/' in str(method.class_name):
                if method.full_name not in list3:
                    print(method.class_name, method.name)
