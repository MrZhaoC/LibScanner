from typing import List

import tools.tools
from database.utils.denpendency_business_utils import get_front_dependencies_cnt_from_google_by_gav, \
    get_front_dependencies_cnt_from_mvn_by_gav, get_all_google_mvn_tpl


def get_google_mvn_tpl_from_db():
    google_mvn_tpl_list = get_all_google_mvn_tpl()
    result = []
    for item in google_mvn_tpl_list:
        group_id = item['group_id']
        artifact_id = item['artifact_id']
        version_num = item['version']
        # 排除测试版本的影响
        if '-' in version_num:
            continue
        result.append([group_id, artifact_id, version_num])
    return result


def query_current_dependency_from_mvn(gav: List[str]):
    return get_front_dependencies_cnt_from_mvn_by_gav(gav[0], gav[1], gav[2])


def query_current_dependency_from_google_mvn(gav: List[str]):
    return get_front_dependencies_cnt_from_google_by_gav(gav[0], gav[1], gav[2])


if __name__ == '__main__':
    db_data = get_google_mvn_tpl_from_db()

    dependency_result = []
    cnt = 0

    for gav in db_data:
        format_gav = gav[0] + ':' + gav[1] + ':' + gav[2]
        mvn_dependency = query_current_dependency_from_mvn(gav)
        google_mvn_dependency = query_current_dependency_from_google_mvn(gav)

        if mvn_dependency[0]['dep_cnt'] == 0 and google_mvn_dependency[0]['dep_cnt'] == 0:
            # print('{} google_mvn:{}'.format(format_gav, mvn_dependency[0]['dep_cnt'],
            #                                 google_mvn_dependency[0]['dep_cnt']))
            cnt += 1
        dependency_result.append([format_gav, mvn_dependency[0]['dep_cnt'], google_mvn_dependency[0]['dep_cnt']])

    print('total: {} mnv_and_google_mvn0: {}'.format(len(db_data), cnt))

    output_result = sorted(dependency_result, key=lambda x: x[1], reverse=True)

    more_ten_thousand = []
    more_thousand_and_less_ten_thousand = []
    more_hundred_and_less_thousand = []
    more_ten_and_less_hundred = []
    more_zero_and_less_ten = []
    zero = []
    _zero = []

    for name, mvn_cnt, google_mvn_cnt in output_result:
        sum = int(mvn_cnt) + int(google_mvn_cnt)
        if sum > 10000:
            more_ten_thousand.append(name)
        elif 10000 >= sum > 1000:
            more_thousand_and_less_ten_thousand.append(name)
        elif 1000 >= sum > 100:
            more_hundred_and_less_thousand.append(name)
        elif 100 >= sum > 10:
            more_ten_and_less_hundred.append(name)
        elif 10 >= sum > 0:
            more_zero_and_less_ten.append(name)
        else:
            zero.append(name)


    print(len(more_ten_thousand), len(more_thousand_and_less_ten_thousand), len(more_hundred_and_less_thousand),
          len(more_ten_and_less_hundred), len(more_zero_and_less_ten), len(zero))
    print(len(output_result))
    print(len(more_ten_thousand) / len(output_result))
    print(len(more_thousand_and_less_ten_thousand) / len(output_result))
    print(len(more_hundred_and_less_thousand) / len(output_result))
    print(len(more_ten_and_less_hundred) / len(output_result))
    print(len(more_zero_and_less_ten) / len(output_result))
    print(len(zero) / len(output_result))

    # tools.tools.write_excel_xlsx(r'D:\Desktop\2023-11-13.xlsx', 'google_dependency_count', output_result)

    # with open(r"D:\Desktop\dependency-count.txt", 'w') as f:
    #     for i in range(len(output_result)):
    #         f.write('{},{},{}\n'.format(output_result[i][0], output_result[i][1], output_result[i][2]))
