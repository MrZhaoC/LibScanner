# from upsetplot import from_contents
# from upsetplot import UpSet
# from matplotlib import pyplot
#
# mammals = ['Cat', 'Dog', 'Horse', 'Sheep', 'Pig', 'Cattle', 'Rhinoceros', 'Moose']
# herbivores = ['Horse', 'Sheep', 'Cattle', 'Moose', 'Rhinoceros']
# domesticated = ['Dog', 'Chicken', 'Horse', 'Sheep', 'Pig', 'Cattle', 'Duck']
#
#
# animals = from_contents({'mammal': mammals, 'herbivore': herbivores, 'domesticated': domesticated})
#
# ax_dict = UpSet(animals, subset_size='count').plot()
#
#
# pyplot.show()

# from upsetplot import from_memberships
#
# animal_memberships = {
#     "Cat": "Mammal",
#     "Dog": "Mammal,Domesticated",
#     "Horse": "Mammal,Herbivore,Domesticated",
#     "Sheep": "Mammal,Herbivore,Domesticated",
#     "Pig": "Mammal,Domesticated",
#     "Cattle": "Mammal,Herbivore,Domesticated",
#     "Rhinoceros": "Mammal,Herbivore",
#     "Moose": "Mammal,Herbivore",
#     "Chicken": "Domesticated",
#     "Duck": "Domesticated",
# }
#
# # Turn this into a list of lists:
# animal_membership_lists = [categories.split(",") for categories in animal_memberships.values()]
#
# print(animal_membership_lists)
#
# animals = from_memberships(animal_membership_lists)

import matplotlib.pyplot as plt
import venn

# a = {'1', '2', '3'}
# b = {'1', '2', '3', '4', '5'}
# c = {'1', '2', '3', '5', '6'}
# e = {'11', '12', '13', '14', '15'}
# f = {'12', '14', '15', '17'}
# g = {'11', '10'}
#
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文
# plt.figure(figsize=(14, 8), dpi=200)  # 创建画布
#
# labels = venn.generate_petal_labels([a, b, c, e, f, g])
# venn.venn6(labels, names=list('abcefg'))
#
# plt.show()

import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]

y = [1, 4, 9, 16, 25]

plt.plot(x, y)

plt.show()