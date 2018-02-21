import os
from collections import namedtuple
from datetime import timedelta
from wfdb.basics import run_wfdb_app
from wfdb.signalfiles import export_signal


def extract_r_positions(record_name, working_dir, use_gqpost=False):
    run_wfdb_app('gqrs.exe', ['-r', record_name], working_dir)
    annotator = 'qrs'
    if use_gqpost:
        annotator = 'gqp'
        run_wfdb_app('gqpost.exe', ['-r', record_name, '-o', annotator], working_dir)
    out_file_name = os.path.join(working_dir, record_name + '.tmpqrs')
    with open(out_file_name, 'w') as fo:
        run_wfdb_app('rdann.exe', ['-r', record_name, '-a', annotator, '-p', 'N'], working_dir, stdout=fo)
    out_file_name2 = os.path.join(working_dir, record_name + '.tmpqrs.dat')
    with open(out_file_name2, 'w') as fo:
        run_wfdb_app('gawk.exe', ['\'{print', '$1', '}\'', out_file_name], working_dir, stdout=fo)
    r_pos = []
    with open(out_file_name2, 'r') as fi:
        for l in fi:
            l.strip()
            splitted = l.split(':')
            if len(splitted) < 3:
                h = 0
                m = int(splitted[0])
                spl2 = splitted[1].split('.')
            else:
                h = int(splitted[0])
                m = int(splitted[1])
                spl2 = splitted[2].split('.')
            s = int(spl2[0])
            ms = int(spl2[1])
            r_pos.append(timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms))
    return r_pos


EcgRR = namedtuple('EcgRR', ['time', 'interval'])


def analize_ecg(signal, signal_sampf, rec_name, working_dir, use_gqpost=False,
                min_rr=timedelta(seconds=0, milliseconds=540), max_rr=timedelta(milliseconds=400, seconds=2)):
    export_signal(signal, signal_sampf, rec_name, working_dir)
    r_pos = extract_r_positions(rec_name, working_dir, use_gqpost=use_gqpost)
    rr = []
    for r1, r2 in zip(r_pos[0:-2], r_pos[1:]):
        tmp_rr = r2 - r1
        if min_rr <= tmp_rr <= max_rr:
            rr.append(EcgRR(time=r2, interval=tmp_rr.total_seconds()))
    return r_pos, rr
