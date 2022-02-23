import matplotlib.pyplot as plt
import numpy as np
plt.style.use('ggplot')

scenarios = [1,2,3]

start = ':'
end = '\n'

avarage_list = []
std_list = []

for x in scenarios:
    f = open("results/results_"+str(x)+"_vnfs.txt", "r")
    lines = f.readlines()[-2:] # getting only mean and standard deviation from result files
    lines = [float(line[line.find(start)+len(start):line.rfind(end)]) for line in lines]
    
    print(lines)
    print('-------------')
    avarage_list.append(lines[0])
    std_list.append(lines[1])

x_pos = np.arange(len(scenarios))

fig, ax = plt.subplots()
ax.bar(x_pos, avarage_list, yerr=std_list, align='center', alpha=0.5, ecolor='black', capsize=10)
ax.set_ylabel('Placemente runtime (seconds)')
ax.set_xlabel('Scenarios')
ax.set_xticks(x_pos)
ax.set_xticklabels(scenarios)
# ax.set_title('Coefficent of Thermal Expansion (CTE) of Three Metals')
ax.yaxis.grid(True)

# Save the figure and show
plt.tight_layout()
plt.savefig('results/runtime-results.png')
# plt.show()
