"""
Created on 02-10-2011

@author: Borsuk
"""

import sys
from psg.brainlab.signal import read_signal_file, RecorderChannel, create_row_breaker, create_row, create_table_title
from psg.brainlab.events import *
from psg.brainlab.utils import make_brainlab_filenames, decode_time

if __name__ == '__main__':
    if len(sys.argv) < 2:
        #main('*.sig')
        fnames = make_brainlab_filenames('E:/Schwarzer/SIGNALS-ARCHIVE/A0000076.sig')
        print(fnames)
        sf = read_signal_file(fnames[0], True)
    else:
        arg = sys.argv[1]
        sf = read_signal_file(arg,False)

    print(hex(sf.header.version_id))
    print(hex(sf.data_table.measurement_info.offset), sf.data_table.measurement_info.size)
    print("%20s\t%s" % ("ID:", sf.measurement.id))
    print("%20s\t%s" % ("Name:", sf.measurement.name))
    print("%20s\t%s" % ("Start hour:", sf.measurement.start_hour))
    print("%20s\t%s" % ("Street:", sf.measurement.street))
    print("%20s\t%s" % ("City:", sf.measurement.city))
    print("%20s\t%s" % ("Zip code:", sf.measurement.zip_code))

    print("%20s\t%s" % ("Sex:", sf.measurement.sex))
    print("%20s\t%s" % ("Doctor:", sf.measurement.doctor))
    print("%20s\t%s" % ("Technician:", sf.measurement.technician))
    print("%20s\t%s" % ("Start date:", sf.measurement.start_date))
    print("%20s\t%s" % ("Birth date:", sf.measurement.birthday))
    print("%20s\t%s" % ("Age:", sf.measurement.age))
    print("%20s\t%s" % ("Protocol:", sf.measurement.protocol))
    print("%20s\t%s" % ("Clinical info:", sf.measurement.clin_info))
    print("%20s\t%s" % ("Ref. doctor name:", sf.measurement.referring_doctor_name))
    print("%20s\t%s" % ("Ref. doctor code:", sf.measurement.referring_doctor_code))

    print("====================")
    print("%20s\t%s" % ("Recorder name:", sf.recorder_info.name))
    print("%20s\t%d" % ("No rec. channels:", sf.recorder_info.nRecChannels))
    print("%20s\t%d" % ("Inverted AC channels:", sf.recorder_info.invertedACChannels))
    print("%20s\t%d" % ("Max voltage:", sf.recorder_info.maximumVoltage))
    print("%20s\t%d" % ("Normal voltage:", sf.recorder_info.normalVoltage))
    print("%20s\t%d" % ("Calibration signal:", sf.recorder_info.calibrationSignal))
    print("%20s\t%d" % ("Calibration scale:", sf.recorder_info.calibrationScale))
    print("%20s\t%d" % ("Video control:", sf.recorder_info.videoControl))
    print("%20s\t%d" % ("No sensitivities:", sf.recorder_info.nSensitivities))
    print("%20s\t%d" % ("No low filters:", sf.recorder_info.nLowFilters))
    print("%20s\t%d" % ("No high filters:", sf.recorder_info.nHighFilters))
    print("%20s" % ("Sensitivities:", ))
    for i in range(sf.recorder_info.nSensitivities):
        print("%20d:\t%f" % (i, sf.recorder_info.sensitivity[i]))

    print("%20s" % ("Low filters:", ))
    for i in range(sf.recorder_info.nLowFilters):
        print("%20d:\t%f" % (i, sf.recorder_info.lowFilter[i]))
    print("%20s" % ("High filters:", ))
    for i in range(sf.recorder_info.nHighFilters):
        print("%20d:\t%f" % (i, sf.recorder_info.highFilter[i]))
    print("%20s\t%s" % ("Montage name:", sf.recorder_info.montageName))
    print("%20s\t%d" % ("No channels used:", sf.recorder_info.numberOfChannelsUsed))
    print("%20s\t%d" % ("Global sensitivity:", sf.recorder_info.globalSens))
    print("%20s\t%d" % ("Epoch length:", sf.recorder_info.epochLengthInSamples))
    print("%20s\t%d" % ("Highets rate:", sf.recorder_info.highestRate))

    print(create_row_breaker(RecorderChannel))
    print(create_table_title(RecorderChannel))
    print(create_row_breaker(RecorderChannel))

    for rc in sf.recorder_info.channels:
        print(create_row(RecorderChannel, rc.create_data_tuple(sf.recorder_info.sensitivity, sf.recorder_info.lowFilter, sf.recorder_info.highFilter)))
    print("%20s\t%d" % ("Page buffor size:", sum([x.save_buffer_size for x in sf.recorder_info.channels])))



    print("====================")
    print("%20s\t%s" % ("Signal table offset:", sf.data_table.signal_info.offset))
    print("%20s\t%s" % ("First page size:", sf.data_table.signal_info.size))
    print("%20s\t%s" % ("Page header size:", sf.data_table.signal_info.header_size))


    print("====================")
    print("Events")
    for evt in sf.events:
        st = Event.ST_DICT.get((evt.ev_type, evt.sub_type))
        print(Event.ET_DICT.get(evt.ev_type), (st if st is not None else evt.sub_type), evt.page, evt.page_time,
              decode_time(evt.time).isoformat(), evt.duration, evt.duration_in_ms, hex(evt.channels), evt.info)
    print("====================")
    print("Events defs:")
    for evd in sf.events_desc:
        print(evd.label, evd.desc, EventDesc.DT_DICT.get(evd.d_type), evd.value)

    print("====================")
    print("Signal Pages:")
    i = 0
    for page in sf.signal_pages:
        print(i,page.filling, page.time)
        i += 1
