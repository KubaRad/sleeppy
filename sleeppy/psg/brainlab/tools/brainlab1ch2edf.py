import sys
import os
import numpy
from psg.brainlab.utils import make_brainlab_filenames, decode_time
from psg.brainlab.signal import read_signal_file
from edf.edffile import EdfFile, Header, SignalDefinition

epoch_length = 1


def _calculate_records_num(signal, smpls):
    r = int(round(signal.size/smpls))
    return r if (r*smpls) >= signal.size else r+1


if __name__ == '__main__':

    input_name = sys.argv[1]
    dest_dir = sys.argv[2]
    signal_name = sys.argv[3]
    meas_id = os.path.splitext(os.path.split(input_name)[1])[0]
    print('Processing: {}'.format(input_name), end='', flush=True)

    dest_path = os.path.join(dest_dir, meas_id+'.EDF')
    if os.path.exists(dest_path):
        print(" !!!! File exists in dest dir ({}). Skipping!".format(dest_path))
    else:
        fnames = make_brainlab_filenames(input_name)
        sf = read_signal_file(fnames[0], True)
        ch_index=-1
        i=0
        for c in sf.recorder_info.channels:
            if c.signal_type == signal_name:
                ch_index=i
                break
            else:
                i+=1
        if ch_index <0:
            print(" Channel {} no found. Skipping!".format(signal_name))
        else:
            ch = sf.recorder_info.channels[ch_index]
            print(" Channel {} found. Sampling: {}. Saving to {}".format(ch.signal_type, ch.sampling_rate, dest_path), end="", flush=True)
            samples = epoch_length*ch.sampling_rate
            ch_signal = sf.signal_data[ch_index]*100
            signal_defs = [SignalDefinition("ECG", "ECG", "uV", -2560.0, 2560.0, -32767, 32767, "", samples)]
            version = "0"
            patient_id = "Id:"+sf.measurement.id+" Name:"+sf.measurement.name+" Birthdate:"+sf.measurement.birthday.strftime("%d-%b-%Y").upper()
            record_id = "Id:"+meas_id+" Startdate:"+ sf.measurement.start_date.strftime("%d-%b-%Y").upper()+" Protocol:"+sf.measurement.protocol
            start_date = sf.measurement.start_date
            start_time = sf.signal_pages[0].time
            header_bytes = 0
            records = _calculate_records_num(ch_signal, samples)
            if ch_signal.size < (records*samples):
                ch_signal = numpy.append(ch_signal, numpy.zeros((records*samples)-ch_signal.size))

            record_duration = epoch_length
            signals_no = 1
            header = Header(version, patient_id, record_id , start_date, start_time, header_bytes, "", records, record_duration, signals_no, signal_defs)
            edf_file = EdfFile(header, [ch_signal])
            edf_file.write_to_file(dest_path)

            print(" Processing finished OK!")

