import sys
import os
from os.path import join, isdir, isfile

_REPORT_FIELDS = [
    ("ACQ_START_DATE", 62, "DT"),
    ("ACQ_START_TIME", 63, "TM"),
    ("ACQ_END_DATE", 64, "DT"),
    ("ACQ_END_TIME", 65, "TM"),
    ("ACQ_DUR_M", 61, "N"),
    ("ACQ_TYPE", 126, "N"),
    ("CPAP", 2810, "N"),
    ("OA_TIME", 152, "N"),
    ("PATIENT_ID", 108, "T"),
    ("FAMILY_NAME", 52, "T"),
    ("FIRST_NAME", 53, "T"),
    ("SEX", 54, "T"),
    ("BIRTH_DATE", 55, "DT"),
    ("AGE", 57, "N"),
    ("HEIGHT", 138, "N"),
    ("WEIGHT", 139, "N"),
    ("Department", 5003, "T"),
    ("TIB", 207, "N"),
    ("SPT", 208, "N"),
    ("TST", 209, "N"),
    ("SEFF", 230, "N"),
    ("LAT", 218, "N"),
    ("N1_T", 262, "N"),
    ("N1_P_PST", 265, "N"),
    ("N1_LAT", 220, "N"),
    ("N1_EP", 261, "N"),
    ("N2_T", 267, "N"),
    ("N2_P_PST", 270, "N"),
    ("N2_LAT", 222, "N"),
    ("N2_EP", 266, "N"),
    ("N3_T", 272, "N"),
    ("N3_P_PST", 275, "N"),
    ("N3_LAT", 224, "N"),
    ("N3_EP", 271, "N"),
    ("R_T", 257, "N"),
    ("R_P_PST", 260, "N"),
    ("R_LAT", 228, "N"),
    ("R_EP", 256, "N"),
    ("A_N", 690, "N"),
    ("A_I", 720, "N"),
    ("CA_N", 687, "N"),
    ("CA_I", 717, "N"),
    ("OA_N", 688, "N"),
    ("OA_I", 718, "N"),
    ("MA_N", 689, "N"),
    ("MA_I", 719, "N"),
    ("H_N", 691, "N"),
    ("H_I", 721, "N"),
    ("AH_N", 692, "N"),
    ("AH_I", 722, "N"),
    ("RERA_N", 6163, "N"),
    ("RERA_I", 6173, "N"),
    ("RD_N", 6164, "N"),
    ("RD_I", 6174, "N"),
    ("SaO2_MIN", 899, "N"),
    ("SaO2_AVG", 894, "N"),
    ("ODI", 1504, "N"),
    ("AR_N", 1415, "N"),
    ("AR_I", 9964, "N"),
    ("AW_N", 1420, "N"),
    ("AW_I", 9970, "N")
]

_HEADERS = [x[0] for x in _REPORT_FIELDS]

_FIELD_TYPES = {x[0]: x[2] for x in _REPORT_FIELDS}


def read_report_file(file_name):
    return_dict = {}
    if isfile(file_name):
        with open(file_name) as fin:
            lines = fin.readlines()
            lines = [x.replace('\r', '').replace('\n', '').replace('\"', '') for x in lines]
        report_dict = {}
        for l in lines:
            el = l.split(',')
            if el[0]:
                report_dict[int(el[0])] = el[1].strip()
        for dd in _REPORT_FIELDS:
            if dd[1] in report_dict:
                return_dict[dd[0]] = report_dict[dd[1]]
    return return_dict


def format_field(f, field_name):
    return "\"" + f + "\"" if field_name in _FIELD_TYPES and _FIELD_TYPES[field_name] == "T" else f


if __name__ == '__main__':
    main_dir = sys.argv[1] if len(sys.argv) >= 2 else 'X:\\'
    print("Acq_Id", '\t'.join(_HEADERS), sep='\t')
    for entry in os.listdir(main_dir):
        acq_dir = join(main_dir, entry)
        if isdir(acq_dir):
            rml_file_name = join(acq_dir, entry + '.rml')
            report_file_name = join(acq_dir, entry + '-report.txt')
            rf = read_report_file(report_file_name)
            if rf and rf["ACQ_START_DATE"]:
                print("\"" + entry + "\"", '\t'.join([format_field(rf[x], x) if x in rf else "Na" for x in _HEADERS]),
                      sep='\t')
