from typing import List

import tools.tools
from database.utils.denpendency_business_utils import get_front_dependencies_cnt_from_google_by_gav, \
    get_front_dependencies_cnt_from_mvn_by_gav

mvn_file_path = r"D:\Android-exp\gav_index_popular.txt"


def get_popular_mvn_data():
    result = []
    with open(mvn_file_path, 'r', encoding='utf-8') as f:
        items = f.readlines()
    for item in items:
        if int(item.split(";")[1]) < 5:
            continue
        # append gav
        result.append(item.split(";")[0])
    return result


def query_current_dependency_from_mvn(gav: List[str]):
    return get_front_dependencies_cnt_from_mvn_by_gav(gav[0], gav[1], gav[2])


def query_current_dependency_from_google_mvn(gav: List[str]):
    return get_front_dependencies_cnt_from_google_by_gav(gav[0], gav[1], gav[2])


if __name__ == '__main__':
    result = get_popular_mvn_data()

    dependency_result = []

    cnt = 0

    for i, item in enumerate(result):
        gav = item.split(':')
        mvn_dependency = query_current_dependency_from_mvn(gav)
        google_mvn_dependency = query_current_dependency_from_google_mvn(gav)

        if mvn_dependency[0]['dep_cnt'] == 0 and google_mvn_dependency[0]['dep_cnt'] == 0:
            # print('{} google_mvn:{}'.format(item, mvn_dependency[0]['dep_cnt'], google_mvn_dependency[0]['dep_cnt']))
            cnt += 1
        dependency_result.append([item, mvn_dependency[0]['dep_cnt'], google_mvn_dependency[0]['dep_cnt']])

    print('total: {} mnv_and_google_mvn0: {}'.format(len(result), cnt))

    output_result = sorted(dependency_result, key=lambda x: x[1], reverse=True)

    # excel_result = []
    # for i in range(1000000):
    #     excel_result.append(output_result[i])
    #
    # tools.tools.write_excel_xlsx(r'D:\Desktop\2023-11-13.xlsx', 'dependency_count', excel_result)

    # with open(r"D:\Desktop\dependency-count.txt", 'w') as f:
    #     for i in range(len(output_result)):
    #         f.write('{},{},{}\n'.format(output_result[i][0], output_result[i][1], output_result[i][2]))
