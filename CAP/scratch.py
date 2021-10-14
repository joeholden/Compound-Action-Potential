import pyabf
import matplotlib.pyplot as plt
import numpy as np

SAMPLING_FREQUENCY = 50000
folder_path = 'C:/Users/joema/PycharmProjects/CAP/files/'
abf = pyabf.ABF(folder_path + '/21o12007.abf')
abf.setSweep(sweepNumber=0, channel=1)

max_pulse_value = max(abf.sweepY)
time_indices_of_pulse = []

for index, element in enumerate(abf.sweepY):
    if element > 0.1 * max_pulse_value:
        time_indices_of_pulse.append(index)

pulse_duration_ms = len(time_indices_of_pulse) / 50

print(pulse_duration_ms)


