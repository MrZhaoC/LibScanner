import os

from tools.tools import list_all_files

# source_path = r'F:\zc-data\apk-source\new-download-source\apks-source'
source_path = r'F:\zc-data\apk-source\success'


def decompress_dir(path):
    src_count = 0
    minify_enabled_true = []
    dontobfuscate = []
    dontoptimize = []
    dontshrink = []
    minify_enabled = []
    for file in os.listdir(path):

        if file.endswith('_src'):
            src_count += 1
            file_path = os.path.join(path, file)
            # for root, folders, f in os.walk(file_path):
            try:
                for f_path in list_all_files(file_path):
                    flag = False
                    # todo: build.gradle ==> minifyEnabled true
                    if f_path.endswith('build.gradle'):
                        with open(f_path, 'r') as c:
                            for line in c.readlines():
                                # if line.strip() == 'minifyEnabled true':
                                if 'minifyEnabled' in line.strip():
                                    minify_enabled.append(file)
                                if 'minifyEnabled' in line.strip() and 'true' in line.strip():
                                    flag = True
                                    minify_enabled_true.append(file)
                                    break

                    # todo: build.gradle.kts ==> isMinifyEnabled = true
                    if f_path.endswith('build.gradle.kts'):
                        with open(f_path, 'r') as c:
                            for line in c.readlines():
                                # if line.strip() == 'minifyEnabled true':
                                if 'isMinifyEnabled' in line.strip():
                                    minify_enabled.append(file)
                                if 'isMinifyEnabled' in line.strip() and 'true' in line.strip():
                                    flag = True
                                    minify_enabled_true.append(file)
                                    break

                    # todo: -dontobfuscate -dontoptimize -dontshrink
                    if f_path.endswith('-rules.pro') and flag:
                        with open(f_path, 'r') as c:
                            for line in c.readlines():
                                # print(line)
                                if line.strip() == '-dontobfuscate':
                                    dontobfuscate.append(file)
                                elif line.strip() == '-dontoptimize':
                                    dontoptimize.append(file)
                                elif line.strip() == '-dontshrink':
                                    dontshrink.append(file)

                    if flag:
                        break
            except:
                print('异常', file_path)

    print(src_count)
    print(len(minify_enabled))
    print(len(minify_enabled_true))

    print()

    print(len(set(dontobfuscate)))
    print(len(set(dontoptimize)))
    print(len(set(dontshrink)))


def application_call_external_code_analysis(path):
    result = []
    with open('./filter-dependency.txt', 'w') as fdf:
        for file in os.listdir(path):
            if file.endswith('_src'):
                file_path = os.path.join(path, file)
                # for root, folders, f in os.walk(file_path):
                try:
                    for f_path in list_all_files(file_path):
                        # print(f_path)
                        if f_path.endswith('.java') or f_path.endswith('.kt'):
                            with open(f_path, 'r') as f:
                                lines = f.readlines()
                                for line in lines:
                                    if line.startswith('import '):
                                        # print(line.split(' ')[1])
                                        class_name = line.split(' ')[1]
                                        if class_name.startswith('java.') or class_name.startswith('android.') or '_' in class_name:
                                            continue
                                        format_class_name = 'L' + class_name.replace('.', '/')
                                        result.append(format_class_name)
                                        fdf.write(format_class_name)
                                        print(format_class_name)

                except:
                    pass


if __name__ == '__main__':
    # decompress_dir(source_path)
    # Lai/h2o/mojos/runtime/lic/InvalidWatermarkException;
    application_call_external_code_analysis(source_path)
