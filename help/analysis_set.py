from androguard.misc import AnalyzeDex, AnalyzeAPK

import tools.tools

dex_dir_path = r'F:\zc-data\mvn-dex'


def get_current_dex_core_feature_clusters_():
    """
    根据给定dex，返回当前dex核心特征划分后的集合
    :param dex_name:
    :return:
    """
    files = tools.tools.list_all_files(dex_dir_path)

    for i, file in enumerate(files):
        if file.endswith('.dex'):
            gav = file.split('\\')[-1][:-4].split('@')
            ga = gav[0] + '@' + gav[1]
            _, target_dvm, target_dx = AnalyzeDex(file)

            for field_x in target_dx.get_fields():
                # print(field_x.name)
                # print(field_x.get_field())
                # print(field_x.get_field().get_name())
                print(field_x.get_field().get_descriptor())

            # dx_class_list = []
            # d_class_list = []
            #
            # for clax in target_dx.get_classes():
            #     if clax.is_external():
            #         continue
            #     dx_class_list.append(clax.name)
            # for cla in target_dvm.get_classes():
            #     d_class_list.append(cla.name)
            #
            # dx_method_list = []
            # d_method_list = []
            #
            # for methodx in target_dx.get_methods():
            #     if methodx.is_external():
            #         continue
            #     dx_method_list.append(methodx.full_name)
            # for method in target_dvm.get_methods():
            #     d_method_list.append(method.full_name)
            #
            # print(len(dx_class_list), len(d_class_list), len(dx_method_list), len(d_method_list))


def get_all_methods(method_analysis, methods, result_set):
    if method_analysis in result_set:
        return result_set
    result_set.add(method_analysis)
    # to
    for _, callee_to, _ in method_analysis.get_xref_to():
        next_method_analysis = callee_to
        if next_method_analysis.full_name in methods:
            # print(next_method_analysis.full_name)
            get_all_methods(next_method_analysis, methods, result_set)
    return result_set

    # from
    # for _, callee_from, _ in method_analysis.get_xref_from():
    #     next_method_analysis = callee_from
    #     if next_method_analysis.full_name in methods:
    #         # print(next_method_analysis.full_name)
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
        # print((field.class_name, field.name, field.proto))
        filed_full_names.append((field.name, field.proto))
    class_names = []
    for cla in target_dvm2.get_classes():
        class_names.append(cla.name)
    print('---------------------------------')

    # match_method = []
    result_set = set()
    _, target_dvm1, target_dx1 = AnalyzeDex(q)
    for method_x1 in target_dx1.get_methods():
        for method2 in target_dx2.get_methods():
            if method2.is_external():
                continue
            if method_x1.full_name == method2.full_name:
                # match_method.append(method2)
                get_all_methods(method2, method_full_names, result_set)
    print(len(result_set))
    # 得到所有的调用方法 result_set

    field_list = []
    for method_x in target_dx1.get_methods():
        #     print(method_x.xrefto)
        #     print(method_x.xreffrom)
        # print(method_x.xrefread)
        # new_instance (class int)
        # new-instance v0, Lokhttp3/HttpUrl$Builder;
        # for new_instance_class, _ in method_x.get_xref_new_instance():
        #     class_name = new_instance_class.name
        #     if class_name in class_names:
        #         print(class_name)
        # const_class (class int)
        # const-class v0, Lokhttp3/internal/http2/Http2;
        # for const_class, _ in method_x.get_xref_const_class():
        #     class_name = const_class.name
        #     if class_name in class_names:
        #         print(class_name)

        for cla_x, field, _ in method_x.xrefread:
            # print(field.class_name, field.name, field.proto)
            field_list.append((field.name, field.proto))

        # print(method_x.xrefwrite)

        for cla_x, field, _ in method_x.xrefwrite:
            # print(field.class_name, field.name, field.proto)
            field_list.append((field.name, field.proto))

    for method_x in result_set:
        #     print(method_x.xrefto)
        #     print(method_x.xreffrom)
        # print(method_x.xrefread)
        # new_instance (class int)
        # new-instance v0, Lokhttp3/HttpUrl$Builder;
        # for new_instance_class, _ in method_x.get_xref_new_instance():
        #     class_name = new_instance_class.name
        #     if class_name in class_names:
        #         print(class_name)
        # const_class (class int)
        # const-class v0, Lokhttp3/internal/http2/Http2;
        # for const_class, _ in method_x.get_xref_const_class():
        #     class_name = const_class.name
        #     if class_name in class_names:
        #         print(class_name)

        for cla_x, field, _ in method_x.xrefread:
            # print(field.class_name, field.name, field.proto)
            field_list.append((field.name, field.proto))

        # print(method_x.xrefwrite)

        for cla_x, field, _ in method_x.xrefwrite:
            # print(field.class_name, field.name, field.proto)
            field_list.append((field.name, field.proto))

        # print(method_x.xrefnewinstance)
        # print(method_x.xrefconstclass)
    print('---------------------------')
    result = set()
    for field1 in field_list:
        if field1 in filed_full_names:
            result.add(field1)
            # print(field1)
    for item in result:
        print(item)
    print('---------------------------')

    # methods = []
    for method_x in target_dx2.get_methods():
        # for c_x, m_x, _ in method_x.xrefto:
        #     if m_x.full_name in method_full_names:
        #         methods.append(m_x)
        # for c_x, m_x, _ in method_x.xreffrom:
        #     if m_x.full_name in method_full_names:
        #         methods.append(m_x)
        for cla_x, field, _ in method_x.xrefread:
            if (field.name, field.proto) in result:
                print(method_x.full_name)
                result_set.add(method_x)
        for cla_x, field, _ in method_x.xrefwrite:
            if (field.name, field.proto) in result:
                print(method_x.full_name)
                result_set.add(method_x)

    print('-----------------------')
    format_method_keep_rules_temp = tools.tools.format_method_keep_rule(list(result_set))
    for f in format_method_keep_rules_temp:
        print(f)

    # for field1 in target_dx1.get_fields():
    #     field2 = field1.get_field()
    #     print(field2.class_name, field.name, field.proto)
    # if (field2.class_name, field2.name, field2.proto) in filed_full_names:
    #     print(field2.class_name, field2.name, field2.proto)

    #     self.xrefto = set()
    #     self.xreffrom = set()
    #
    #     self.xrefread = set()
    #     self.xrefwrite = set()
    #
    #     self.xrefnewinstance = set()
    #     self.xrefconstclass = set()
    #
    # field_list = []
    # for method_x in match:
    #     #     print(method_x.xrefto)
    #     #     print(method_x.xreffrom)
    #     # print(method_x.xrefread)
    #     for cla_x, field, _ in method_x.xrefread:
    #         # print(field.class_name, field.name, field.proto)
    #         field_list.append((field.class_name, field.name, field.proto))
    #     # print(method_x.xrefwrite)
    #     for cla_x, field, _ in method_x.xrefwrite:
    #         # print(field.class_name, field.name, field.proto)
    #         field_list.append((field.class_name, field.name, field.proto))
    #     print(method_x.xrefnewinstance)
    #     print(method_x.xrefconstclass)
    # for m in match:
    #     print(m.full_name)
    # print('---------------------------------')
    # for field in field_list:
    #     print(field)
    # print('----------------------------------------------')
    # for method_x in target_dx2.get_methods():
    #     if method_x.is_external():
    #         continue
    #     for cla_x, field, _ in method_x.xrefread:
    #         if (field.class_name, field.name, field.proto) in field_list:
    #             print(method_x.full_name)
    #     for cla_x, field, _ in method_x.xrefwrite:
    #         if (field.class_name, field.name, field.proto) in field_list:
    #             print(method_x.full_name)

    apk_path = r"F:\zc-data\RQ\RQ1\apks\cl.coders.faketraveler_9_src\app-debug-shrink.apk"
    app, d_list, app_dx = AnalyzeAPK(apk_path)
    for d in d_list:
        for method in d.get_methods():
            if 'Landroidx/activity/' in str(method.class_name):
                if method.full_name not in list3:
                    print(method.class_name, method.name)
