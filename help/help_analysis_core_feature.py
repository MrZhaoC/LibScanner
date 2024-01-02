import os

from androguard.misc import get_default_session, AnalyzeDex

dex_path = r'D:\Android-exp\public-dex'


def validate_apk_shrink_method(apk_dx, module_item_class_names, db_tpl_name):
    """
    对于给定shrink_apk,分析其中TPL方法集合的存在情况
    :param dex_path:
    :return:
    """
    # module_item_class_names = get_tpl_modules_in_apk()

    dex_file = os.path.join(dex_path, db_tpl_name.replace(':', '@')) + '.dex'
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

    # 根据APK方法名的集合，构建dex方法名的集合
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
    # print(
    #     '%-80s %-10s %10s %s' % (
    #         db_tpl_name, len(apk_method_names), len(dex_method_names), len(dex_d.get_methods())))

    # 清空session，减少内存占用
    session = get_default_session()
    session.reset()
    return len(apk_method_names), len(dex_method_names)
