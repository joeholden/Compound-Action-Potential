import pyabf
import matplotlib.pyplot as plt
import numpy as np
import os
import statistics
import itertools as it
from scipy import interpolate

abf_files = []
folder_path = 'C:/Users/joema/PycharmProjects/CAP/files/'
SAMPLING_FREQUENCY = 50000

for file in os.listdir(folder_path):
    abf = pyabf.ABF(folder_path + file)
    abf_files.append(abf)


def find_impulse(cap_file):
    """This function will return a 3-member tuple. The first
    element is a list containing the time indices of the delivered pulse.
    The second is the time-point in ms that the pulse was delivered. The
    last element is the stimulus duration"""

    cap_file.setSweep(sweepNumber=0, channel=1)
    max_pulse_value = max(cap_file.sweepY)
    time_indices_of_pulse = []

    for index, element in enumerate(cap_file.sweepY):
        if element > 0.1 * max_pulse_value:
            time_indices_of_pulse.append(index)

    pulse_duration_ms = len(time_indices_of_pulse) / (SAMPLING_FREQUENCY / 1000)
    time_of_spike_onset = (time_indices_of_pulse[0] / SAMPLING_FREQUENCY) * 1000
    return time_indices_of_pulse, time_of_spike_onset, pulse_duration_ms


def find_baseline_noise(cap_file):
    global time_indices_of_pulse, time_of_spike_onset, pulse_duration_ms, average_noise
    time_indices_of_pulse, time_of_spike_onset, pulse_duration_ms = find_impulse(cap_file)
    cap_file.setSweep(sweepNumber=0, channel=0)
    average_noise = statistics.mean(cap_file.sweepY[0:(time_indices_of_pulse[0] - 100)])
    return average_noise


def find_regions(cap_file):
    cap_file.setSweep(sweepNumber=0, channel=0)
    # time_points_past_pulse = list(np.arange(time_indices_of_pulse[-1] + 1, len(cap_file.sweepX), 1))
    above_baseline = [True if i > avg_noise else False for i in cap_file.sweepY[int(time_indices_of_pulse[-1]) + 1:]]

    def find_ranges(lst, n):
        """Return ranges for `n` or more repeated values."""
        groups = ((k, tuple(g)) for k, g in it.groupby(enumerate(lst), lambda x: x[-1]))
        repeated = (idx_g for k, idx_g in groups if len(idx_g) >= n)
        return ((sub[0][0], sub[-1][0]) for sub in repeated)

    regions = find_ranges(above_baseline, n=5)
    print(list(regions))

    # regions = [(start, stop, length, above/below)]
    # start searching for multiples of 5 in a row. If this occurs, start a region at the first occurance.
    # stop when there is a switch that is maintained for 5. Start a new region here.
    # If a region is short-

    with open('y.txt', 'w') as yy:
        for u in above_baseline:
            yy.write(str(u))


# /////////////////////////////////////////run below////////////////////////////////////////////
cap_file = abf_files[5]

avg_noise = find_baseline_noise(abf_files[5])
cap_file.setSweep(sweepNumber=0, channel=0)

plt.plot(cap_file.sweepX, cap_file.sweepY, color='k', linewidth=0.3)

plt.xlim(.327, .34)
plt.ylim(-10, 100)
avg_baseline_array = np.full(cap_file.sweepX.shape, avg_noise)
plt.plot(cap_file.sweepX, avg_baseline_array, color='k')

plt.fill_between(cap_file.sweepX, cap_file.sweepY, avg_baseline_array,
                 where=cap_file.sweepY - avg_baseline_array > 0, color='green', alpha=1)
plt.fill_between(cap_file.sweepX, cap_file.sweepY, avg_baseline_array,
                 where=cap_file.sweepY - avg_baseline_array < 0, color='maroon', alpha=1)

find_regions(cap_file)
plt.show()

# To find the CAP, start at the impulse delivery. Check the sign of the waveform. It should start +, cross 0, go -,
# then return to 0 (where 0 is the baseline noise). CAP top area goes from here to where it crosses back over 0.
# There is a possible bug if the signal is noisy.
