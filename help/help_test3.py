mvn_file_path = r"D:\Desktop\dependency-count.txt"


def get_popular_mvn_data():
    result = []
    with open(mvn_file_path, 'r', encoding='utf-8') as f:
        items = f.readlines()
    for item in items:
        result.append([item.split(",")[0], item.split(",")[1], item.split(",")[2]])
    return result


more_ten_thousand = []
more_thousand_and_less_ten_thousand = []
more_hundred_and_less_thousand = []
more_ten_and_less_hundred = []
more_zero_and_less_ten = []
zero = []


def statistic_mvn_google_mvn_dependency(result):
    for name, mvn_cnt, google_mvn_cnt in result:
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


if __name__ == '__main__':
    res = get_popular_mvn_data()
    statistic_mvn_google_mvn_dependency(res)
    print(len(more_ten_thousand), len(more_thousand_and_less_ten_thousand), len(more_hundred_and_less_thousand),
          len(more_ten_and_less_hundred), len(more_zero_and_less_ten), len(zero))
    print(len(res))
    print(len(more_ten_thousand) / len(res))
    print(len(more_thousand_and_less_ten_thousand) / len(res))
    print(len(more_hundred_and_less_thousand) / len(res))
    print(len(more_ten_and_less_hundred) / len(res))
    print(len(more_zero_and_less_ten) / len(res))
    print(len(zero) / len(res))
