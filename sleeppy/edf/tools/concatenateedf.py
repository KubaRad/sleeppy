import os
import sys
import numpy
from edf.edffile import create_from_file
from datetime import timedelta, datetime


def concatenate_edfs():
    print("Reading file: {}".format(input1_name), end=' ', flush=True)
    edf_file = create_from_file(input1_name, integers=True)
    start_time = datetime.combine(edf_file.header.start_date, edf_file.header.start_time)
    print("Start time:", start_time)
    print("Records in file:", edf_file.header.records_in_file)
    print("Record duration [s]:", edf_file.header.record_duration)
    signal_length = edf_file.header.records_in_file*edf_file.header.record_duration
    print("Signal length [s]:", signal_length)
    end_time = start_time+timedelta(seconds=signal_length)
    print("End time:", end_time)
    edf_file2 = create_from_file(input2_name, integers=True)
    start_time2 = datetime.combine(edf_file2.header.start_date, edf_file2.header.start_time)
    print("Start time2:", start_time2)
    time_delay = start_time2-end_time
    print("Delay [s]:", time_delay.seconds)
    print("Length old:", len(edf_file.signals[1])/edf_file.header.signal_defs[1].samples)
    for i in range(0, len(edf_file.header.signal_defs)):
        s = edf_file.header.signal_defs[i]
        new_length = s.samples*time_delay.seconds
        print(s.label, s.samples, s.samples*time_delay.seconds)
        new_data = numpy.zeros(new_length, dtype=int)
        edf_file.signals[i].extend(new_data)
        edf_file.signals[i].extend(edf_file2.signals[i])
    new_records = int(len(edf_file.signals[1])/edf_file.header.signal_defs[1].samples)
    print("New number of records:", new_records)
    print(" File read. Writing file to: {}".format(output_name), end=' ', flush=True)
    edf_file.header.records_in_file = new_records
    edf_file.write_to_file(output_name, edf_file, integers=True)
    print("Repair finished")


def _check_file(file_name):
    if not os.path.isfile(file_name):
        print("Unknown file: {}".format(file_name))
        sys.exit(1)
    return file_name


if __name__ == '__main__':
    input1_name = _check_file(sys.argv[1])
    input2_name = _check_file(sys.argv[2])
    output_name = _check_file(sys.argv[3])
    concatenate_edfs()
