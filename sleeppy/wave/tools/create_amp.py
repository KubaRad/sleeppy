import sys
import edftools.edf.edffile as edf
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
    ac = signal_amplitude(signal_ts, signal_sampf, max_dist=0.2)
    for a in ac:
        print("\t".join(a.to_strings()))
