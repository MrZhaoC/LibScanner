import os

from analysis.core_feature_analysis.android_r8_core_feature.core_feature_pipeline import pre_main

# todo:项目依赖文件
dep_file_path = r"F:\zc-data\RQ\RQ1\all-dependency.txt"
# todo: shrink-dex输出文件夹
shrink_dex_output_path = r'F:\zc-data\RQ\RQ1\shrink-dex-output'
# todo: android config输出文件夹
base_rule_config_path = r'F:\zc-data\RQ\RQ1\r8-config'

if not os.path.exists(base_rule_config_path):
    os.makedirs(base_rule_config_path)

pre_main(dep_file_path, shrink_dex_output_path, base_rule_config_path)