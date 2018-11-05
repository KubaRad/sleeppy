import sys
import os
from os.path import join, isdir, isfile
from ..reportfile import REPORT_FIELDS, read_report_file, format_field

HEADERS = [x[0] for x in REPORT_FIELDS]


if __name__ == '__main__':
    if len(sys.argv) <2 :
        print("Usage: program acquisition_path")
        exit(1)
    main_dir = sys.argv[1]
    print("Acq_Id", '\t'.join(HEADERS), sep='\t')
    for entry in os.listdir(main_dir):
        acq_dir = join(main_dir, entry)
        if isdir(acq_dir):
            rml_file_name = join(acq_dir, entry + '.rml')
            report_file_name = join(acq_dir, entry + '-report.txt')
            rf = read_report_file(report_file_name)
            if rf and rf["ACQ_START_DATE"]:
                print("\"" + entry + "\"", '\t'.join([format_field(rf[x], x) if x in rf else "Na" for x in HEADERS]),
                      sep='\t')
