"""
Created on 02-10-2011

@author: Kuba Radliński
"""
import sys
import glob
from os.path import splitext, split
from psg.brainlab.analyze import read_analyze_file
from psg.brainlab.signal import read_signal_file
from psg.brainlab.utils import make_brainlab_filenames, decode_time


def surroud_text(txt, surrounder='"'):
    return surrounder + txt + surrounder


if __name__ == '__main__':
    if len(sys.argv)<2:
        print ('Usage: measurement_info [options] filename')
    else:
        file_name = sys.argv[1]
        if file_name == "--printheader":
            print(surroud_text("FILE_ID"), surroud_text("ID"), surroud_text("NAME"), surroud_text("SEX"), surroud_text("BIRTH_DATE"),
                  surroud_text("START_DATE"), surroud_text("PROTOCOL"), surroud_text("STORAGE"), surroud_text("CODE"),
                  surroud_text("AGE"), surroud_text("WEIGHT"), surroud_text("HEIGHT"), surroud_text("RDI"), surroud_text("ODI"),
                  surroud_text("AI"), surroud_text("TST"), surroud_text("TST_TIME"), surroud_text("TST_HRS"), surroud_text("SPT"),
                  surroud_text("SPT_TIME"), surroud_text("SPT_HRS"), sep='\t')
            file_name = sys.argv[2] if len(sys.argv)==3 else None

        if file_name is not None:
            fnames = make_brainlab_filenames(file_name)
            signalName = fnames[0]
            analyzeName = fnames[1]
            basename = splitext(file_name)[0]
            sigFileId = split(basename)[1]
            af = read_analyze_file(analyzeName)
            sf = read_signal_file(signalName, False)
            if sf is not None and sf.measurement is not None and af is not None:
                print(surroud_text(sigFileId), surroud_text(sf.measurement.id), surroud_text(sf.measurement.name),
                      surroud_text(sf.measurement.sex), sf.measurement.birthday, sf.measurement.start_date,
                      surroud_text(sf.measurement.protocol), sf.store_events, surroud_text(sf.measurement.class_code),
                      sf.measurement.age, sf.measurement.weight, sf.measurement.height, af.rdi, af.odi, af.ai, af.sleep_time,
                      decode_time(af.sleep_time * 1000), af.sleep_time_hrs, af.sleep_period_time,
                      decode_time(af.sleep_period_time * 1000), af.sleep_period_time_hrs, sep='\t')
            else:
                print(surroud_text(sigFileId), surroud_text("---"), surroud_text("---"),
                      surroud_text("---"), surroud_text("---"), surroud_text("---"),
                      surroud_text("---"), surroud_text("---"), surroud_text("---"),
                      surroud_text("---"), surroud_text("---"), surroud_text("---"), surroud_text("---"), surroud_text("---"),
                      surroud_text("---"), surroud_text("---"),
                      surroud_text("---"), surroud_text("---"), surroud_text("---"),
                      surroud_text("---"), surroud_text("---"), sep='\t')
