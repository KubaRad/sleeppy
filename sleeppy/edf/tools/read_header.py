
import sys
from edf.edffile import create_header_from_file

__author__ = 'Kuba Radliński'


def read_file_header(f_name):
    print(f_name)
    header = create_header_from_file(f_name)
    print("Version        :%s" % header.version)
    print("Patient id     :%s" % header.patient_id)
    print("Record id      :%s" % header.record_id)
    print("Start date     :%s" % header.start_date)
    print("Start time     :%s" % header.start_time)
    print("Header bytes   :%d" % header.bytes_in_header)
    print("Records        :%d" % header.records_in_file)
    print("Record duration:%d" % header.record_duration)
    print("Signals        :%d" % header.signals_in_file)
    print("------------------------ SIGNAL DEFS ------------------------ ")
    i = 1
    for sd in header.signal_defs:
        print("    Signal no   :%d" % i)
        print("    Label       :%s" % sd.label)
        print("    Transducer  :%s" % sd.transducer)
        print("    Phys. min.  :%f" % sd.phys_min)
        print("    Phys. max.  :%f" % sd.phys_max)
        print("    Dig. min.   :%d" % sd.dig_min)
        print("    Dig. max.   :%d" % sd.dig_max)
        print("    Dimension   :%s" % sd.dimension)
        print("    Filter      :%s" % sd.filter)
        print("    N. samples  :%d" % sd.samples)
        print(" ")
        i += 1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: read_header.py file_name")
    else:
        file_name = sys.argv[1]

    read_file_header(file_name)
