import pyabf
import matplotlib.pyplot as plt
import numpy as np
import os
import statistics

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
    time_indices_of_pulse, time_of_spike_onset, pulse_duration_ms = find_impulse(cap_file)
    cap_file.setSweep(sweepNumber=0, channel=0)
    average_noise = statistics.mean(cap_file.sweepY[0:(time_indices_of_pulse[0] - 100)])
    return average_noise


# /////////////////////////////////////////run below////////////////////////////////////////////
cap_file = abf_files[5]
avg_noise = find_baseline_noise(abf_files[5])
cap_file.setSweep(sweepNumber=0, channel=0)

plt.plot(cap_file.sweepX, cap_file.sweepY)
plt.xlim(.32, .360)
plt.ylim(-1, 130)
plt.plot(cap_file.sweepX, np.full(cap_file.sweepX.shape, avg_noise))

plt.show()

# To find the CAP, start at the impulse delivery. Check the sign of the waveform. It should start +, cross 0, go -,
# then return to 0 (where 0 is the baseline noise). CAP top area goes from here to where it crosses back over 0.
# There is a possible bug if the signal is noisy.
