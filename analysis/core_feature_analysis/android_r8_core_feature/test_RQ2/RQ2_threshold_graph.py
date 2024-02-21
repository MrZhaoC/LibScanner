# import matplotlib.pyplot as plt
#
# # x轴数据
# x1 = [0.7, 0.8, 0.9, 1]
# # y轴数据
# y1 = [0.034, 0.016, 0.005, 0.00]
#
# plt.plot(x1, y1)  # 绘制曲线图
#
#
# # x轴数据
# x2 = [0.7, 0.8, 0.9, 1]
# # y轴数据
# y2 = [0.003, 0.0045, 0.0063, 0.012]
# #
# plt.plot(x2, y2)  # 绘制曲线图
#
# plt.show()  # 显示图形


t_fpr = 0
t_fnr = 0
data = [[16, 10, 3], [19, 18, 4], [24, 18, 7], [21, 28, 8], [17, 17, 7],
        [18, 10, 3], [27, 21, 13], [14, 16, 6], [17, 16, 5], [27, 33, 8], [27, 16, 4], [21, 20, 8]]
for d in data:
    N = d[0]
    M = d[1]
    C = d[2]
    FP = M - C  # 假阳性
    TN = N - FP  # 真阴性
    FN = N - C  # 假阴性
    TP = C  # 真阳性
    FPR = FP / (FP + TN)  # 假阳性率
    FNR = FN / (FN + TP)  # 假阴性率
    print(FPR, FNR)
    t_fpr += FPR
    t_fnr += FNR
print()
print(t_fpr / len(data), t_fnr / len(data))

# import matplotlib.pyplot as plt
#
# x1 = [0.7, 0.8, 0.9, 1]
# y1 = [0.034, 0.016, 0.005, 0.00]
#
# plt.plot(x1, y1, marker='o')  # 绘制曲线，使用圆点作为数据点标记
# plt.xlabel('X轴标签')  # 设置x轴标签
# plt.ylabel('Y轴标签')  # 设置y轴标签
# plt.title('曲线图示例')  # 设置标题
# plt.grid(True)  # 显示网格线
# plt.show()  # 显示图形


# import matplotlib.pyplot as plt
#
# x1 = [0.7, 0.8, 0.9, 1]
# y1 = [0.034, 0.016, 0.005, 0.00]
#
# plt.plot(x1, y1, '-o', linestyle='-')  # 绘制光滑的曲线图，使用圆点作为数据点标记
# plt.xlabel('X轴标签')  # 设置x轴标签
# plt.ylabel('Y轴标签')  # 设置y轴标签
# plt.title('曲线图示例')  # 设置标题
# plt.grid(True)  # 显示网格线
# plt.show()  # 显示图形


