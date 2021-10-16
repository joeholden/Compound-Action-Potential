import pyabf
import matplotlib.pyplot as plt
import numpy as np
import os
import statistics
import itertools as it
from scipy import interpolate
import operator

# abf_files = []
# folder_path = 'C:/Users/joema/PycharmProjects/CAP/files/'
# SAMPLING_FREQUENCY = 50000
#
# for file in os.listdir(folder_path):
#     abf = pyabf.ABF(folder_path + file)
#     abf_files.append(abf)


abf_files = []
folder_path = 'C:/Users/joema/Desktop/CAP files/'
SAMPLING_FREQUENCY = 50000

for file in os.listdir(folder_path):
    if '21o14' in file:
        abf = pyabf.ABF(folder_path + file)
        abf_files.append(abf)
cap_file = abf_files[114]


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
    global time_indices_of_pulse, time_of_spike_onset, pulse_duration_ms, average_noise, average_spread_from_mean, standard_dev
    time_indices_of_pulse, time_of_spike_onset, pulse_duration_ms = find_impulse(cap_file)
    cap_file.setSweep(sweepNumber=0, channel=0)
    average_noise = statistics.mean(cap_file.sweepY[0:(time_indices_of_pulse[0] - 100)])

    standard_dev = np.std(cap_file.sweepY[0:(time_indices_of_pulse[0] - 100)])

    print(standard_dev)
    baseline_peaks = []
    baseline_troughs = []

    for value in cap_file.sweepY[0:(time_indices_of_pulse[0] - 100)]:
        if value < average_noise:
            baseline_troughs.append(value)
        else:
            baseline_peaks.append(value)
    average_of_baseline_peaks = statistics.mean(baseline_peaks)
    average_of_baseline_troughs = statistics.mean(baseline_troughs)
    average_spread_from_mean = statistics.mean((average_of_baseline_peaks - average_noise,
                                                average_noise - average_of_baseline_troughs))
    return average_noise, standard_dev


def find_regions(cap_file):
    cap_file.setSweep(sweepNumber=0, channel=0)

    # classify non-noise as 4 sigma... ~100% of all true noise.
    # indices are still original

    non_noise = []
    for index, mv in enumerate(cap_file.sweepY):
        if mv > avg_noise + (4 * standard_dev) or mv < avg_noise - (4 * standard_dev):
            non_noise.append((index, mv))

    # Dynamically re-type non_noise to remove pre-pulse entries and most post-CAP entries. Reduces chance or error
    non_noise = [(index, t) for (index, t) in non_noise if time_indices_of_pulse[-1] < index < 30000]

    # Boolean list if point in non_noise is above or below noise level average. This lets us separate groups
    above_baseline = [True if j > avg_noise else False for i, j in non_noise]

    # Find regions of 5 sign-contiguous neighbors as a criteria for a real signal
    # Returned is a list of tuples. The first is an index value that is from the enumeratiion of list
    def find_ranges(lst, n):
        """Return ranges for `n` or more repeated values. (index, # repeated adjacent)"""
        groups = ((k, tuple(g)) for k, g in it.groupby(enumerate(lst), lambda x: x[-1]))
        repeated = (idx_g for k, idx_g in groups if len(idx_g) >= n)
        return ((sub[0][0], sub[-1][0]) for sub in repeated)

    regions = list(find_ranges(above_baseline, n=5))

    region_left_index = []
    for (m, n) in regions:
        region_left_index.append(non_noise[m][0])

    # //////////////////////////////////////////////////

    # Walk down a peak group to find the boundary points

    ops = {
        "<=": operator.le,
        ">=": operator.ge
    }

    def walk_down_to_baseline(op_function):
        """ Starts at the left point mid-peak/trough that triggered the 4 sigma condition.
        It then walks up/down in both directions until it reaches the baseline noise spot.
        Returns the boundary points. """

        global boundary_1, boundary_2
        at_boundary_1 = False
        at_boundary_2 = False

        current_coordinate = point
        while not at_boundary_1:
            test = cap_file.sweepY[current_coordinate]
            if op_function(test, avg_noise):
                at_boundary_1 = True
                boundary_1 = current_coordinate
            else:
                current_coordinate -= 1

        current_coordinate = point
        while not at_boundary_2:
            test = cap_file.sweepY[current_coordinate]
            if op_function(test, avg_noise):
                at_boundary_2 = True
                boundary_2 = current_coordinate
            else:
                current_coordinate += 1

        return boundary_1, boundary_2

    # Use the walk_down_to_baseline function
    boundaries = []
    for point in region_left_index:
        if cap_file.sweepY[point] > avg_noise:
            peak_identity = 'peak'
            operator_function = ops["<="]
        else:
            peak_identity = 'trough'
            operator_function = ops[">="]
        (t1, t2) = walk_down_to_baseline(operator_function)
        boundaries.append((t1, t2))

    return boundaries


# /////////////////////////////////////////run below////////////////////////////////////////////

avg_noise, avg_spread_from_mean = find_baseline_noise(cap_file)

cap_file.setSweep(sweepNumber=0, channel=0)

plt.plot(cap_file.sweepX, cap_file.sweepY, color='k', linewidth=0.3)

plt.xlim(.325, .335)
plt.ylim(-20, 300)
avg_baseline_array = np.full(cap_file.sweepX.shape, avg_noise)
plt.plot(cap_file.sweepX, avg_baseline_array, color='k')



b = find_regions(cap_file)

plt.fill_between(cap_file.sweepX, cap_file.sweepY, avg_baseline_array,
                 where=cap_file.sweepY - avg_baseline_array > 0, color='turquoise', alpha=.8)
plt.fill_between(cap_file.sweepX, cap_file.sweepY, avg_baseline_array,
                 where=cap_file.sweepY - avg_baseline_array < 0, color='maroon', alpha=.8)



for i, j in find_regions(cap_file):
    plt.axvline(x=i / 50000)
    plt.axvline(x=j / 50000)

plt.show()

# To find the CAP, start at the impulse delivery. Check the sign of the waveform. It should start +, cross 0, go -,
# then return to 0 (where 0 is the baseline noise). CAP top area goes from here to where it crosses back over 0.
# There is a possible bug if the signal is noisy.
