import os
import edf.edffile as edf
import pkg_resources
from datetime import datetime
from wave.amplitude import *


_FILE_NAME = "test_amp.edf"
_FILE_PATH = "data"


def _provide_test_stream():
    return pkg_resources.resource_stream(__name__, os.path.join(_FILE_PATH, _FILE_NAME))


if __name__ == '__main__':
    header = edf.create_header_from_stream(_provide_test_stream())
    edf_file = edf.EdfFile(header)
    i = edf_file.find_signal_index('Pleth')
    edf_file = edf.create_from_stream(_provide_test_stream(), [i])
    signal_ts = edf_file.signals[0]
    signal_sampf = edf_file.signal_sampf(0)
    print("fs:", signal_sampf, flush=True)
    execution_times = []
    for i in range(10):
        print("Statring calculatings, loop:", i+1, flush=True)
        start_time = datetime.utcnow()
        ac = signal_amplitude(signal_ts, signal_sampf, max_dist=0.2)
        calc_time = (datetime.utcnow()-start_time).total_seconds()
        print("Calc done. Time:", calc_time, flush=True)
        print("---------------------------------------------------", flush=True)
        execution_times.append(calc_time)
    print("==================================================")
    print("Total time:", sum(execution_times))
    print("Mean time:", sum(execution_times)/len(execution_times))
