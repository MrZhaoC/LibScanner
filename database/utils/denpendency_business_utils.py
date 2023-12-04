import time

from database.utils import database_utils_pool


# 注意不是同一个数据库
# def get_front_dependencies_from_mvn(requirement, version):
#     sql = "select package_name, package_version from package_info where requirement = '%s' and requirement_version = " \
#           "'%s'" % (
#               requirement, version)
#     dependencies = database_utils_pool.fetchall(sql)
#     print('查询依赖关系共 %s 条' % len(dependencies))
#     return dependencies


# 根据gav查询下游依赖关系
def get_front_dependencies_from_mvn_by_gav(group_id, artifact_id, version_num):
    st = time.perf_counter()
    sql = "select group_id, artifact_id, version from maven_dependencies where d_group_id = '%s' and d_artifact_id = " \
          "'%s' and d_version = '%s'" % (group_id, artifact_id, version_num)
    dependencies = database_utils_pool.fetchall(sql)
    et = time.perf_counter()
    print('mvn查询依赖关系共 %s 条, 用时 %s' % (len(dependencies), et - st))
    return dependencies


# 根据gav查询下游依赖关系 google
def get_front_dependencies_from_google_by_gav(group_id, artifact_id, version_num):
    st = time.perf_counter()
    sql = "SELECT group_id, artifact_id, version from google_maven_dependencies where d_group_id = '%s' and " \
          "d_artifact_id = '%s' and d_version = '%s'" % (group_id, artifact_id, version_num)
    dependencies = database_utils_pool.fetchall(sql)
    et = time.perf_counter()
    print('google_mvn查询依赖关系共 %s 条, 用时 %s' % (len(dependencies), et - st))
    return dependencies


def get_front_dependencies_cnt_from_mvn_by_gav(group_id, artifact_id, version_num):
    sql = "select count(*) as dep_cnt from maven_dependencies where d_group_id = '%s' and d_artifact_id = " \
          "'%s' and d_version = '%s'" % (group_id, artifact_id, version_num)
    dependencies = database_utils_pool.fetchall(sql)

    return dependencies


def get_front_dependencies_cnt_from_google_by_gav(group_id, artifact_id, version_num):
    sql = "SELECT count(*) as dep_cnt from google_maven_dependencies where d_group_id = '%s' and " \
          "d_artifact_id = '%s' and d_version = '%s'" % (group_id, artifact_id, version_num)
    dependencies = database_utils_pool.fetchall(sql)

    return dependencies


def get_all_google_mvn_tpl():
    sql = 'SELECT group_id, artifact_id, version FROM google_maven_infos'
    google_mvn_tpl_list = database_utils_pool.fetchall(sql)
    return google_mvn_tpl_list
