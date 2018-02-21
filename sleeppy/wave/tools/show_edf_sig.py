import sys
import edftools.edf.edffile as edf
import matplotlib.pyplot as plt
from signaltools.wave.amplitude import *


if __name__ == '__main__':
    file_name = sys.argv[1]
    signal_name = sys.argv[2]
    header = edf.create_header_from_file(file_name)
    edf_file = edf.EdfFile(header)
    i = edf_file.find_signal_index(signal_name)
    edf_file = edf.create_from_file(file_name, [i])
    signal_ts = edf_file.signals[0]
    signal_sampf = edf_file.signal_sampf(0)
    print("fs:", signal_sampf)
    dx_test_s = derivative(signal_ts)
    tx = np.arange(len(signal_ts))
    ac = signal_amplitude(signal_ts, signal_sampf, max_dist=0.2)
    plt.plot(tx, signal_ts)

    minimas_t = []
    minimas_v = []
    maximas_t = []
    maximas_v = []
    maxslope_t = []
    maxslope_v = []
    slope25_t = []
    slope25_v = []
    slope50_t = []
    slope50_v = []
    for a in ac:
        minimas_t.append(a.min_ind)
        minimas_v.append(a.min_value)
        maximas_t.append(a.max_ind)
        maximas_v.append(a.max_value)
        maxslope_t.append(a.max_slope_ind)
        maxslope_v.append(a.max_slope_val)
        slope25_t.append(a.amp25_ind)
        slope25_v.append(a.amp25_val)
        slope50_t.append(a.amp50_ind)
        slope50_v.append(a.amp50_val)

    plt.plot(minimas_t, minimas_v, 'gv')
    plt.plot(maximas_t, maximas_v, 'r^')
    plt.plot(maxslope_t, maxslope_v, 'g+')
    plt.plot(slope25_t, slope25_v, 'r+')
    plt.plot(slope50_t, slope50_v, 'b+')
    ma, dicrot = separate_amplitude(ac, min_amp=0.7)
    for a in ma:
        plt.plot([a.min_ind, a.max_ind], [a.min_value, a.max_value], 'y')
    for a in dicrot:
        plt.plot([a.min_ind, a.max_ind], [a.min_value, a.max_value], 'r')

    plt.show()


