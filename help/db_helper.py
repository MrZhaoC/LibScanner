import ast

from database.utils import feature_business_utils


def get_core_feature():
    data = feature_business_utils.get_all_tpl_feature()
    for tpl_info in data:
        tpl_info['course_feature'] = ast.literal_eval(tpl_info['course_feature'])
        tpl_info['fined_feature'] = ast.literal_eval(tpl_info['fined_feature'])
        if tpl_info['core_fined_feature']:
            tpl_info['core_fined_feature'] = ast.literal_eval(tpl_info['core_fined_feature'])
        else:
            tpl_info['core_fined_feature'] = []
    return data


if __name__ == '__main__':
    db_data = get_core_feature()
    for item in db_data:
        print('%-80s %s' % (item['tpl_name'], item['core_method_count']))
