import os
import numpy as np
from wfdb.basics import run_wfdb_app


def export_signal(signal, sampf, record_name, working_dir):
    out_file_name = os.path.join(working_dir, record_name + '.txt')
    np.savetxt(out_file_name, signal)
    process_args = ['-F', str(sampf), '-i', out_file_name, '-o', record_name, '0']
    run_wfdb_app('wrsamp.exe', process_args, working_dir)
