import pyabf
import matplotlib.pyplot as plt
import os

abf_files = []
folder_path = 'C:/Users/joema/PycharmProjects/CAP/files/'

for file in os.listdir(folder_path):
    print(folder_path + file)
    abf = pyabf.ABF(folder_path + file)
    abf_files.append((abf, file))

plt.figure(figsize=(20, 12))
for f in abf_files:
    plt.plot(1000 * f[0].sweepX, f[0].sweepY, label=f[1][5:8])

plt.xlim(320, 360)
plt.ylim(-50, 175)
plt.ylabel('mV')
plt.xlabel('ms')
plt.title('Compound Action Potential')
plt.legend()

plt.show()
