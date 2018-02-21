"""
Created on 12-08-2011

@author: Kuba Radliński
"""

import sys
from psg.brainlab.analyze import read_analyze_file
from psg.brainlab.events import Event, EventDesc, get_codes_4_label, get_selected_events, get_selected_events_4_types
from psg.brainlab.utils import decode_time, decode_time_seconds, ms_to_events_seconds, make_brainlab_filenames


if __name__ == '__main__':
    if len(sys.argv) < 2:
        #main('*.sig')
        fnames = make_brainlab_filenames('E:/Schwarzer/SIGNALS-ARCHIVE/A0000074.TBL')
        print(fnames)
        af = read_analyze_file(fnames[1])
    else:
        arg = sys.argv[1]
        af = read_analyze_file(arg)
    #print("Program ID:",hex(header.programId),header.checkProgramId())
    #print("Table ID:",hex(header.tableId),header.checkTableId())
    #print("VersionID:",hex(header.versionId))
    #i=0
    #for inv in af.inventory:
    #    i+=1
    #    print(i,hex(inv.id),FileInventory.ID_DICT.get(inv.id,"UNKNOWN"), inv.offset, inv.size)
    #print("Stages:", len(af.stages))
    #i=0
    #for stgs in af.stages:
    #    i+=1
    #    print("Stage:",i,stgs.no,stgs.relTime,stgs.val,stgs.label,stgs.valType);
    #print("Stage defs")
    #for stgdf in af.stageDefs.values():
    #    print(stgdf.value, stgdf.valueType, stgdf.label, stgdf.desc)
    #print("Sleep stages codes")
    #for ss in af.sleepStgVals:
    #    print (ss)
    #print("Sleep REM stages codes")
    #for ss in af.sleepStgRemVals:
    #    print (ss)
    #print("Sleep NON REM stages codes")
    #for ss in af.sleepStgNonRemVals:
    #    print (ss)
    #print("Events")
    #for evt in af.events:
    #    st=Event.ST_DICT.get((evt.evType,evt.subType));
    #    print(Event.ET_DICT.get(evt.evType),(st if not st == None else evt.subType),evt.page,evt.pageTime,decodeTime(evt.time).isoformat(),evt.duration,evt.durationInMs,hex(evt.channels),evt.info)
    print("Events defs:")
    for evd in af.events_desc:
        print(evd.label, evd.desc, EventDesc.DT_DICT.get(evd.d_type), evd.value)

    swevents = get_codes_4_label(af.events_desc, "swwyl")
    print("Swwyl events:", swevents)
    for evt in get_selected_events(af.events, {Event.ET_USEREVENT}, swevents):
        st = Event.ST_DICT.get((evt.ev_type, evt.sub_type))
        print(Event.ET_DICT.get(evt.ev_type), (st if st is not None else evt.sub_type), evt.page, evt.page_time,
              decode_time_seconds(evt.time).isoformat(), "-", decode_time_seconds(evt.end_time).isoformat(), evt.duration,
              ms_to_events_seconds(evt.duration_in_ms), hex(evt.channels), evt.info)
    print("-------")
    for evt in get_selected_events_4_types(af.events,
                                           {Event.ET_SAVESKIPEVENT, Event.ET_SYSTEMEVENT, Event.ET_USEREVENT, Event.ET_DIGINPEVENT,
                                            Event.ET_RECORDEREVENT}):
        st = Event.ST_DICT.get((evt.ev_type, evt.sub_type))
        print(Event.ET_DICT.get(evt.ev_type), (st if st is not None else evt.sub_type), evt.page, evt.page_time,
              decode_time_seconds(evt.time).isoformat(), "-", decode_time_seconds(evt.end_time).isoformat(), evt.duration,
              ms_to_events_seconds(evt.duration_in_ms), hex(evt.channels), evt.info)

    #for evt in af.respiratoryEvents:
    #    st=Event.ST_DICT.get((evt.evType,evt.subType));
    #    print(Event.ET_DICT.get(evt.evType),(st if not st == None else evt.subType),evt.page,evt.pageTime,decodeTimeSeconds(evt.time).isoformat(),"-",decodeTimeSeconds(evt.endTime).isoformat(),evt.duration,msToEventsSeconds(evt.durationInMs),hex(evt.channels),evt.info)
    #for evt in af.saturationEvents:
    #    st=Event.ST_DICT.get((evt.evType,evt.subType));
    #    print(Event.ET_DICT.get(evt.evType),(st if not st == None else evt.subType),evt.page,evt.pageTime,decodeTime(evt.time).isoformat(),evt.duration,evt.durationInMs,hex(evt.channels),evt.info)
    #for evt in af.arousalEvents:
    #    st=Event.ST_DICT.get((evt.evType,evt.subType));
    #    print(Event.ET_DICT.get(evt.evType),(st if not st == None else evt.subType),evt.page,evt.pageTime,decodeTime(evt.time).isoformat(),evt.duration,evt.durationInMs,hex(evt.channels),evt.info)

    print("Number of sleep stages:", len(af.sleep_stages), "Sleep time:", af.sleep_time, decode_time(af.sleep_time * 1000),
          af.sleep_time_hrs)
    print("First sleep stage:", af.first_sleep_stage)
    print("Last sleep stage:", af.last_sleep_stage)
    print("SPT:", af.sleep_period_time, decode_time(af.sleep_period_time * 1000), af.sleep_period_time_hrs)
    print("Wake in SPT:", af.sleep_wake_time, decode_time(af.sleep_wake_time * 1000), af.sleep_wake_time_hrs)
    print("N1 in SPT:", af.sleep_n1_time, decode_time(af.sleep_n1_time * 1000), af.sleep_n1_time_hrs)
    print("N2 in SPT:", af.sleep_n2_time, decode_time(af.sleep_n2_time * 1000), af.sleep_n2_time_hrs)
    print("N3 in SPT:", af.sleep_n3_time, decode_time(af.sleep_n3_time * 1000), af.sleep_n3_time_hrs)
    print("REM in SPT:", af.sleep_rem_time, decode_time(af.sleep_rem_time * 1000), af.sleep_rem_time_hrs)
    print("respiratory events:", len(af.respiratory_events), af.rdi)
    print("saturation events:", len(af.saturation_events), af.odi)
    print("arousal events:", len(af.arousal_events), af.ai)
