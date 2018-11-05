
from os.path import isfile


REPORT_FIELDS = [
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


def unicode_win_decoder(s):
    return s.replace('\\u260?', 'Ą'). \
        replace('\\u262?', 'Ć'). \
        replace('\\u280?', 'Ę'). \
        replace('\\u321?', 'Ł'). \
        replace('\\u323?', 'Ń'). \
        replace('\\u211?', 'Ó'). \
        replace('\\u346?', 'Ś'). \
        replace('\\u377?', 'Ź'). \
        replace('\\u379?', 'Ż'). \
        replace('\\u261?', 'ą'). \
        replace('\\u263?', 'ć'). \
        replace('\\u281?', 'ę'). \
        replace('\\u322?', 'ł'). \
        replace('\\u324?', 'ń'). \
        replace('\\u243?', 'ó'). \
        replace('\\u347?', 'ś'). \
        replace('\\u378?', 'ź'). \
        replace('\\u380?', 'ż').replace('\\uc1','')


def read_report_file(file_name, report_fields=REPORT_FIELDS):
    return_dict = {}
    if isfile(file_name):
        with open(file_name) as fin:
            lines = fin.readlines()
            lines = [unicode_win_decoder(x.replace('\r', '').replace('\n', '').replace('\"', '')) for x in lines]
        report_dict = {}
        for l in lines:
            el = l.split(',')
            if el[0]:
                report_dict[int(el[0])] = el[1].strip()
        for dd in report_fields:
            if dd[1] in report_dict:
                return_dict[dd[0]] = report_dict[dd[1]]
    return return_dict


def format_field(f, field_name, report_fields=REPORT_FIELDS):
    field_def = [x for x in report_fields if x[0] == field_name]
    if len(field_def) > 0:
        field_def = field_def[0]
        if field_def[2] == 'T':
            return "\"" + f + "\""
        else:
            if field_def[2] == 'DT':
                pass
            else:
                if field_def[2] == 'TM':
                    pass
                else:
                    if field_def[2] == 'N':
                        return str(f)

    return f
