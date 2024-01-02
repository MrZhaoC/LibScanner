import os
import warnings
import zipfile

import tools

DOT_DEX = '.dex'
DOT_AAR = '.aar'
DOT_JAR = '.jar'

warnings.filterwarnings("ignore")


def preprocessing(tpl_file_path, output_path):
    print(tpl_file_path)
    files = tools.list_all_files(tpl_file_path)
    for file in files:
        parent_dir = os.path.dirname(file)

        file_name = file.split('\\')[-1][:-4]

        dex_file_name = file_name + '.dex'

        dex_file_path = os.path.join(output_path, dex_file_name)

        if os.path.exists(dex_file_path):
            print("文件已经存在 %s" % dex_file_name)
            continue

        if file.endswith(DOT_AAR):
            # 解压 提取classes.jar 文件
            arr_file = file.split("\\")[-1]
            aar_name = os.path.splitext(arr_file)[0]  # 分离文件名 和 后缀名
            zip_file = zipfile.ZipFile(file)

            for names in zip_file.namelist():
                if names == "classes.jar":
                    zip_file.extract(names, parent_dir)
                    old_path = os.path.join(parent_dir, names)
                    jar_path = os.path.join(parent_dir, aar_name) + DOT_JAR
                    try:
                        os.rename(old_path, jar_path)
                    except Exception as e:
                        os.remove(jar_path)
                        os.rename(old_path, jar_path)
                    jar_to_dex(jar_path, output_path, True)

        # jar处理
        if file.endswith(DOT_JAR):
            jar_to_dex(file, output_path, False)


def jar_to_dex(jar_file, output_path, aar_flag):
    # 转换jar to dex
    full_name = jar_file.split("\\")[-1]
    jar_name = os.path.splitext(full_name)[0]
    dex_file_name = jar_name + DOT_DEX

    # 所有 alpha beta rc版本跳过
    # if t_version_skip:
    #     version_num = jar_name.split('@')[-1]
    #     if '-' in version_num:
    #         return

    print(full_name)

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    try:
        # cmd = r"d8 {0} --release  --intermediate --output {1}".format(
        #     jar_file, output_path)

        cmd = r"d8 {0} " \
              r"--release  " \
              r"--intermediate " \
              r"--output {1} " \
              r"--min-api 26 "\
              r"--lib E:\android\sdk\platforms\android-33\android.jar".format(jar_file, output_path)
        os.system(cmd)

        # aar生成的jar使用完删除
        if aar_flag:
            try:
                os.remove(jar_file)
            except Exception:
                print("{} 文件删除失败".format(jar_file))

        if not os.path.exists(os.path.join(output_path, 'classes.dex')):
            return

        try:
            os.rename(os.path.join(output_path, 'classes.dex'), os.path.join(output_path, dex_file_name))
        except Exception as e:
            os.remove(os.path.join(output_path, dex_file_name))
            os.rename(os.path.join(output_path, 'classes.dex'), os.path.join(output_path, dex_file_name))
    except Exception as e:
        print(e)


def multiple_dependencies_dir(path, deps_tree_path):
    dependencies = tools.get_dependency_from_file(deps_tree_path)
    format_dependencies = []

    # format dependency
    for dep in sorted(set(dependencies)):
        format_dependencies.append(dep.replace(':', '@'))

    for filename in os.listdir(path):
        if filename in format_dependencies:
            tpl_path = os.path.join(path, filename)

            print(tpl_path)

            output_path = os.path.join(tpl_path, 'dex')

            if os.path.exists(output_path):
                continue
            #     shutil.rmtree(output_path)

            if not os.path.exists(output_path):
                os.makedirs(output_path)
            preprocessing(tpl_path, output_path, True)
    print("tpl to dex finished...")


if __name__ == '__main__':
    # input_library_path = r'D:\Android-exp\google_libraries'
    # output_dex_path = r'D:\Android-exp\google_dex'
    # test_version_skip = False
    # preprocessing(input_library_path, output_dex_path, test_version_skip)

    # 处理每个文件夹下面的aar/jar文件，转换成对应文件目录下 target_dex_folder/dex/...
    # tpl_dir = r'D:\Android-exp\exp-example\faketraveler\multi-dependency'
    # dependencies_tree_path = r'D:\Android-exp\exp-example\faketraveler\multi-version.txt'
    # multiple_dependencies_dir(tpl_dir, dependencies_tree_path)

    input_library_path = r'D:\mvn-library'
    output_dex_path = r'D:\mvn-dex'

    preprocessing(input_library_path, output_dex_path)
