"""
Created on 06-12-2012

@author: jradlins
"""
import struct
from brainlab.utils import string_trim_to_0
from itertools import repeat


class Event:
    ET_SAVESKIPEVENT = 1
    ET_SYSTEMEVENT = 2
    ET_USEREVENT = 3
    ET_DIGINPEVENT = 4
    ET_RECORDEREVENT = 5
    ET_RESPIRATIONEVENTS = 6
    ET_SATURATIONEVENTS = 7
    ET_ECGEVENTS = 8
    ET_EMGEVENTS = 9
    ET_EEG_DELTAEVENTS = 10
    ET_EEG_SPINDLEEVENTS = 11
    ET_EEG_ALPHAEVENTS = 12
    ET_EOGEVENTS = 13
    ET_EEG_THETAEVENTS = 14
    ET_EEG_BETAEVENTS = 15
    ET_AROUSALEVENTS = 16
    ET_SOUNDEVENTS = 17
    ET_BODYPOSITIONEVENTS = 18
    ET_CPAPEVENTS = 19

    ET_DICT = {ET_SAVESKIPEVENT: "ET_SAVESKIPEVENT",
               ET_SYSTEMEVENT: "ET_SYSTEMEVENT",
               ET_USEREVENT: "ET_USEREVENT",
               ET_DIGINPEVENT: "ET_DIGINPEVENT",
               ET_RECORDEREVENT: "ET_RECORDEREVENT",
               ET_RESPIRATIONEVENTS: "ET_RESPIRATIONEVENTS",
               ET_SATURATIONEVENTS: "ET_SATURATIONEVENTS",
               ET_ECGEVENTS: "ET_ECGEVENTS",
               ET_EMGEVENTS: "ET_EMGEVENTS",
               ET_EEG_DELTAEVENTS: "ET_EEG_DELTAEVENTS",
               ET_EEG_SPINDLEEVENTS: "ET_EEG_SPINDLEEVENTS",
               ET_EEG_ALPHAEVENTS: "ET_EEG_ALPHAEVENTS",
               ET_EOGEVENTS: "ET_EOGEVENTS",
               ET_EEG_THETAEVENTS: "ET_EEG_THETAEVENTS",
               ET_EEG_BETAEVENTS: "ET_EEG_BETAEVENTS",
               ET_AROUSALEVENTS: "ET_AROUSALEVENTS",
               ET_SOUNDEVENTS: "ET_SOUNDEVENTS",
               ET_BODYPOSITIONEVENTS: "ET_BODYPOSITIONEVENTS",
               ET_CPAPEVENTS: "ET_CPAPEVENTS"}

    ST_ANALYSIS = 'A'
    ST_MONTAGECHANGE = 'M'
    ST_DIG_LOW_FILTER_INC = 'L'
    ST_DIG_LOW_FILTER_DEF = 'M'
    ST_DIG_LOW_FILTER_DEC = 'l'
    ST_DIG_HIGH_FILTER_INC = 'H'
    ST_DIG_HIGH_FILTER_DEF = 'I'
    ST_DIG_HIGH_FILTER_DEC = 'h'
    ST_SENSITIVITY_INC = 'S'
    ST_SENSITIVITY_DEF = 'T'
    ST_SENSITIVITY_DEC = 's'
    ST_LOW_FILTER_INC = 'L'
    ST_LOW_FILTER_DEF = 'M'
    ST_LOW_FILTER_DEC = 'l'
    ST_HIGH_FILTER_INC = 'H'
    ST_HIGH_FILTER_DEF = 'I'
    ST_HIGH_FILTER_DEC = 'h'
    ST_VIDEO_ON = 'V'
    ST_VIDEO_OFF = 'v'
    ST_VIDEO_ON_WHILE_MEASURING = 'Z'
    ST_VIDEO_OFF_WHILE_MEASURING = 'z'
    ST_STIMULUS_ON = 'X'
    ST_STIMULUS_OFF = 'x'
    ST_NONCLASSIFIEDAPNEA = 'A'
    ST_CENTRALAPNEA = 'C'
    ST_OBSTRUCTIVEAPNEA = 'O'
    ST_MIXEDAPNEA = 'M'
    ST_NONCLASSIFIEDHYPOPNEA = 'H'
    ST_CENTRALHYPOPNEA = 'D'
    ST_OBSTRUCTIVEHYPOPNEA = 'Q'
    ST_MIXEDHYPOPNEA = 'W'
    ST_NEUTRAL = 'N'
    ST_PARADOXYCALAPNEA = 'P'
    ST_PARADOXYCALHYPOPNEA = 'S'
    ST_PERIODICALBREATHING = 'R'
    ST_INVALIDFORRESPIRATIONS1 = 'I'
    ST_INVALIDFORRESPIRATIONS2 = 'J'
    ST_DIPSATURATION = 'D'
    ST_HYPOXYCALSATURATION = 'H'
    ST_INVALIDFORSATURATIONS1 = 'I'
    ST_INVALIDFORSATURATIONS2 = 'J'
    ST_TACHY = 'T'
    ST_BRADY = 'B'
    ST_INVALIDFORECGS1 = 'I'
    ST_INVALIDFORECGS2 = 'J'
    ST_MOVEMENT = 'M'
    ST_LEFTLEGMOVEMENT = 'L'
    ST_RIGHTLEGMOVEMENT = 'R'
    ST_INVALIDFOREMGS1 = 'I'
    ST_INVALIDFOREMGS2 = 'J'
    ST_K_COMPLEX = 'K'
    ST_INVALIDFOREEG_DELTAS1 = 'I'
    ST_INVALIDFOREEG_DELTAS2 = 'J'
    ST_SPINDLE = 'S'
    ST_INVALIDFOREEG_SPINDLES1 = 'I'
    ST_INVALIDFOREEG_SPINDLES2 = 'J'
    ST_ALPHA = 'A'
    ST_INVALIDFOREEG_ALPHAS1 = 'I'
    ST_INVALIDFOREEG_ALPHAS2 = 'J'
    ST_REM = 'R'
    ST_SEM = 'S'
    ST_BLINK = 'B'
    ST_INVALIDFOREOGREMS1 = 'I'
    ST_INVALIDFOREOGREMS2 = 'J'
    ST_INVALIDFOREOGSEMS1 = 'M'
    ST_INVALIDFOREOGSEMS2 = 'N'
    ST_THETA = 'T'
    ST_INVALIDFOREEG_THETAS1 = 'I'
    ST_INVALIDFOREEG_THETAS2 = 'J'
    ST_BETA = 'B'
    ST_INVALIDFOREEG_BETAS1 = 'I'
    ST_INVALIDFOREEG_BETAS2 = 'J'
    ST_AROUSAL = 'A'
    ST_INVALIDFORAROUSALS1 = 'I'
    ST_INVALIDFORAROUSALS2 = 'J'
    ST_SNORING = 'S'
    ST_PERIODICAL_SNORING = 'P'
    ST_INVALIDFORSOUNDS1 = 'I'
    ST_INVALIDFORSOUNDS2 = 'J'
    ST_LEFTSIDE = 'L'
    ST_RIGHTSIDE = 'R'
    ST_BACK = 'A'
    ST_BELLY = 'B'
    ST_STANDINGUP = 'U'
    ST_HEADDOWN = 'D'
    ST_INVALIDFORBODYPOSITIONS1 = 'I'
    ST_INVALIDFORBODYPOSITIONS2 = 'J'
    ST_CPAP = 'C'
    ST_INVALIDFORCPAPS1 = 'I'
    ST_INVALIDFORCPAPS2 = 'J'

    ST_DICT = {(ET_SYSTEMEVENT, ST_ANALYSIS): "ST_ANALYSIS",
               (ET_SYSTEMEVENT, ST_MONTAGECHANGE): "ST_MONTAGECHANGE",
               (ET_SYSTEMEVENT, ST_DIG_LOW_FILTER_INC): "ST_DIG_LOW_FILTER_INC",
               (ET_SYSTEMEVENT, ST_DIG_LOW_FILTER_DEF): "ST_DIG_LOW_FILTER_DEF",
               (ET_SYSTEMEVENT, ST_DIG_LOW_FILTER_DEC): "ST_DIG_LOW_FILTER_DEC",
               (ET_SYSTEMEVENT, ST_DIG_HIGH_FILTER_INC): "ST_DIG_HIGH_FILTER_INC",
               (ET_SYSTEMEVENT, ST_DIG_HIGH_FILTER_DEF): "ST_DIG_HIGH_FILTER_DEF",
               (ET_SYSTEMEVENT, ST_DIG_HIGH_FILTER_DEC): "ST_DIG_HIGH_FILTER_DEC",
               (ET_RECORDEREVENT, ST_SENSITIVITY_INC): "ST_SENSITIVITY_INC",
               (ET_RECORDEREVENT, ST_SENSITIVITY_DEF): "ST_SENSITIVITY_DEF",
               (ET_RECORDEREVENT, ST_SENSITIVITY_DEC): "ST_SENSITIVITY_DEC",
               (ET_RECORDEREVENT, ST_LOW_FILTER_INC): "ST_LOW_FILTER_INC",
               (ET_RECORDEREVENT, ST_LOW_FILTER_DEF): "ST_LOW_FILTER_DEF",
               (ET_RECORDEREVENT, ST_LOW_FILTER_DEC): "ST_LOW_FILTER_DEC",
               (ET_RECORDEREVENT, ST_HIGH_FILTER_INC): "ST_HIGH_FILTER_INC",
               (ET_RECORDEREVENT, ST_HIGH_FILTER_DEF): "ST_HIGH_FILTER_DEF",
               (ET_RECORDEREVENT, ST_HIGH_FILTER_DEC): "ST_HIGH_FILTER_DEC",
               (ET_RECORDEREVENT, ST_VIDEO_ON): "ST_VIDEO_ON",
               (ET_RECORDEREVENT, ST_VIDEO_OFF): "ST_VIDEO_OFF",
               (ET_RECORDEREVENT, ST_VIDEO_ON_WHILE_MEASURING): "ST_VIDEO_ON_WHILE_MEASURING",
               (ET_RECORDEREVENT, ST_VIDEO_OFF_WHILE_MEASURING): "ST_VIDEO_OFF_WHILE_MEASURING",
               (ET_RECORDEREVENT, ST_STIMULUS_ON): "ST_STIMULUS_ON",
               (ET_RECORDEREVENT, ST_STIMULUS_OFF): "ST_STIMULUS_OFF",
               (ET_RESPIRATIONEVENTS, ST_NONCLASSIFIEDAPNEA): "ST_NONCLASSIFIEDAPNEA",
               (ET_RESPIRATIONEVENTS, ST_CENTRALAPNEA): "ST_CENTRALAPNEA",
               (ET_RESPIRATIONEVENTS, ST_OBSTRUCTIVEAPNEA): "ST_OBSTRUCTIVEAPNEA",
               (ET_RESPIRATIONEVENTS, ST_MIXEDAPNEA): "ST_MIXEDAPNEA",
               (ET_RESPIRATIONEVENTS, ST_NONCLASSIFIEDHYPOPNEA): "ST_NONCLASSIFIEDHYPOPNEA",
               (ET_RESPIRATIONEVENTS, ST_CENTRALHYPOPNEA): "ST_CENTRALHYPOPNEA",
               (ET_RESPIRATIONEVENTS, ST_OBSTRUCTIVEHYPOPNEA): "ST_OBSTRUCTIVEHYPOPNEA",
               (ET_RESPIRATIONEVENTS, ST_MIXEDHYPOPNEA): "ST_MIXEDHYPOPNEA",
               (ET_RESPIRATIONEVENTS, ST_NEUTRAL): "ST_NEUTRAL",
               (ET_RESPIRATIONEVENTS, ST_PARADOXYCALAPNEA): "ST_PARADOXYCALAPNEA",
               (ET_RESPIRATIONEVENTS, ST_PARADOXYCALHYPOPNEA): "ST_PARADOXYCALHYPOPNEA",
               (ET_RESPIRATIONEVENTS, ST_PERIODICALBREATHING): "ST_PERIODICALBREATHING",
               (ET_RESPIRATIONEVENTS, ST_INVALIDFORRESPIRATIONS1): "ST_INVALIDFORRESPIRATIONS1",
               (ET_RESPIRATIONEVENTS, ST_INVALIDFORRESPIRATIONS2): "ST_INVALIDFORRESPIRATIONS2",
               (ET_SATURATIONEVENTS, ST_DIPSATURATION): "ST_DIPSATURATION",
               (ET_SATURATIONEVENTS, ST_HYPOXYCALSATURATION): "ST_HYPOXYCALSATURATION",
               (ET_SATURATIONEVENTS, ST_INVALIDFORSATURATIONS1): "ST_INVALIDFORSATURATIONS1",
               (ET_SATURATIONEVENTS, ST_INVALIDFORSATURATIONS2): "ST_INVALIDFORSATURATIONS2",
               (ET_ECGEVENTS, ST_TACHY): "ST_TACHY",
               (ET_ECGEVENTS, ST_BRADY): "ST_BRADY",
               (ET_ECGEVENTS, ST_INVALIDFORECGS1): "ST_INVALIDFORECGS1",
               (ET_ECGEVENTS, ST_INVALIDFORECGS2): "ST_INVALIDFORECGS2",
               (ET_EMGEVENTS, ST_MOVEMENT): "ST_MOVEMENT",
               (ET_EMGEVENTS, ST_LEFTLEGMOVEMENT): "ST_LEFTLEGMOVEMENT",
               (ET_EMGEVENTS, ST_RIGHTLEGMOVEMENT): "ST_RIGHTLEGMOVEMENT",
               (ET_EMGEVENTS, ST_INVALIDFOREMGS1): "ST_INVALIDFOREMGS1",
               (ET_EMGEVENTS, ST_INVALIDFOREMGS2): "ST_INVALIDFOREMGS2",
               (ET_EEG_DELTAEVENTS, ST_K_COMPLEX): "ST_K_COMPLEX",
               (ET_EEG_DELTAEVENTS, ST_INVALIDFOREEG_DELTAS1): "ST_INVALIDFOREEG_DELTAS1",
               (ET_EEG_DELTAEVENTS, ST_INVALIDFOREEG_DELTAS2): "ST_INVALIDFOREEG_DELTAS2",
               (ET_EEG_SPINDLEEVENTS, ST_SPINDLE): "ST_SPINDLE",
               (ET_EEG_SPINDLEEVENTS, ST_INVALIDFOREEG_SPINDLES1): "ST_INVALIDFOREEG_SPINDLES1",
               (ET_EEG_SPINDLEEVENTS, ST_INVALIDFOREEG_SPINDLES2): "ST_INVALIDFOREEG_SPINDLES2",
               (ET_EEG_ALPHAEVENTS, ST_ALPHA): "ST_ALPHA",
               (ET_EEG_ALPHAEVENTS, ST_INVALIDFOREEG_ALPHAS1): "ST_INVALIDFOREEG_ALPHAS1",
               (ET_EEG_ALPHAEVENTS, ST_INVALIDFOREEG_ALPHAS2): "ST_INVALIDFOREEG_ALPHAS2",
               (ET_EOGEVENTS, ST_REM): "ST_REM",
               (ET_EOGEVENTS, ST_SEM): "ST_SEM",
               (ET_EOGEVENTS, ST_BLINK): "ST_BLINK",
               (ET_EOGEVENTS, ST_INVALIDFOREOGREMS1): "ST_INVALIDFOREOGREMS1",
               (ET_EOGEVENTS, ST_INVALIDFOREOGREMS2): "ST_INVALIDFOREOGREMS2",
               (ET_EOGEVENTS, ST_INVALIDFOREOGSEMS1): "ST_INVALIDFOREOGSEMS1",
               (ET_EOGEVENTS, ST_INVALIDFOREOGSEMS2): "ST_INVALIDFOREOGSEMS2",
               (ET_EEG_THETAEVENTS, ST_THETA): "ST_THETA",
               (ET_EEG_THETAEVENTS, ST_INVALIDFOREEG_THETAS1): "ST_INVALIDFOREEG_THETAS1",
               (ET_EEG_THETAEVENTS, ST_INVALIDFOREEG_THETAS2): "ST_INVALIDFOREEG_THETAS2",
               (ET_EEG_BETAEVENTS, ST_BETA): "ST_BETA",
               (ET_EEG_BETAEVENTS, ST_INVALIDFOREEG_BETAS1): "ST_INVALIDFOREEG_BETAS1",
               (ET_EEG_BETAEVENTS, ST_INVALIDFOREEG_BETAS2): "ST_INVALIDFOREEG_BETAS2",
               (ET_AROUSALEVENTS, ST_AROUSAL): "ST_AROUSAL",
               (ET_AROUSALEVENTS, ST_INVALIDFORAROUSALS1): "ST_INVALIDFORAROUSALS1",
               (ET_AROUSALEVENTS, ST_INVALIDFORAROUSALS2): "ST_INVALIDFORAROUSALS2",
               (ET_SOUNDEVENTS, ST_SNORING): "ST_SNORING",
               (ET_SOUNDEVENTS, ST_PERIODICAL_SNORING): "ST_PERIODICAL_SNORING",
               (ET_SOUNDEVENTS, ST_INVALIDFORSOUNDS1): "ST_INVALIDFORSOUNDS1",
               (ET_SOUNDEVENTS, ST_INVALIDFORSOUNDS2): "ST_INVALIDFORSOUNDS2",
               (ET_BODYPOSITIONEVENTS, ST_LEFTSIDE): "ST_LEFTSIDE",
               (ET_BODYPOSITIONEVENTS, ST_RIGHTSIDE): "ST_RIGHTSIDE",
               (ET_BODYPOSITIONEVENTS, ST_BACK): "ST_BACK",
               (ET_BODYPOSITIONEVENTS, ST_BELLY): "ST_BELLY",
               (ET_BODYPOSITIONEVENTS, ST_STANDINGUP): "ST_STANDINGUP",
               (ET_BODYPOSITIONEVENTS, ST_HEADDOWN): "ST_HEADDOWN",
               (ET_BODYPOSITIONEVENTS, ST_INVALIDFORBODYPOSITIONS1): "ST_INVALIDFORBODYPOSITIONS1",
               (ET_BODYPOSITIONEVENTS, ST_INVALIDFORBODYPOSITIONS2): "ST_INVALIDFORBODYPOSITIONS2",
               (ET_CPAPEVENTS, ST_CPAP): "ST_CPAP",
               (ET_CPAPEVENTS, ST_INVALIDFORCPAPS1): "ST_INVALIDFORCPAPS1",
               (ET_CPAPEVENTS, ST_INVALIDFORCPAPS2): "ST_INVALIDFORCPAPS2"}

    def __init__(self, ev_type=0, sub_type=' ', page=0, page_time=0.0, time=0, duration=0, duration_in_ms=0, channels=0,
                 info=0):
        self.ev_type = ev_type
        self.sub_type = sub_type
        self.page = page
        self.page_time = page_time
        self.time = time
        self.duration = duration
        self.duration_in_ms = duration_in_ms
        self.end_time = time + duration_in_ms
        self.channels = channels
        self.info = info


def read_events(sf, offset, size, nevents=10240):
    sf.seek(offset)
    int16 = struct.Struct("<h")
    tcount = int16.unpack(sf.read(int16.size))[0]
    events = []
    evstruct = struct.Struct("<hB6I")
    currsize = int16.size + tcount*evstruct.size
    if currsize > size:
        pass
    for i in range(nevents):
        bts = sf.read(evstruct.size)
        if i < tcount:
            evd = evstruct.unpack(bts)
            events.append(
                Event(evd[0], chr(evd[1]), evd[2] >> 16, (evd[2] & 0x0000ffff) / 1000.0, evd[3], evd[4], evd[5],
                      evd[6], evd[7]))
    return events


class EventDesc:
    DT_MEASURE = 0
    DT_EXTERNAL = 1
    DT_SCAN = 2

    DT_DICT = {DT_MEASURE: "DT_MEASURE", DT_EXTERNAL: "DT_EXTERNAL", DT_SCAN: "DT_SCAN"}

    def __init__(self, desc="", label="", d_type=0, value=0):
        self.desc = desc
        self.label = label
        self.d_type = d_type
        self.value = value


def read_event_descs(sf):
    types = []
    ssize = 32
    int16 = struct.Struct("<h")
    tcount = int16.unpack(sf.read(int16.size))[0]
    ds = "".join(repeat("20s", ssize))
    ls = "".join(repeat("6s", ssize))
    ts = "<%dh" % ssize
    vs = "<%dh" % ssize
    dstruct = struct.Struct(ds)
    descs = dstruct.unpack(sf.read(dstruct.size))
    lstruct = struct.Struct(ls)
    labels = lstruct.unpack(sf.read(lstruct.size))
    tstruct = struct.Struct(ts)
    dtypes = tstruct.unpack(sf.read(tstruct.size))
    vstruct = struct.Struct(vs)
    values = vstruct.unpack(sf.read(vstruct.size))
    for i in range(tcount):
        types.append(EventDesc(string_trim_to_0(descs[i]), string_trim_to_0(labels[i]), dtypes[i], values[i]))
    return types


def get_codes_4_label(evds, label):
    return set(((chr(x.value)) for x in evds if x.label == label))


def get_selected_events(evlist, evtypes, evcode):
    return [x for x in evlist if (x.ev_type in evtypes) and (x.sub_type in evcode)]


def get_selected_events_4_types(evlist, evtypes):
    return [x for x in evlist if x.ev_type in evtypes]


class RecordingEvent:
    def __init__(self, start_page, end_page, start_time, end_time):
        self.start_page = start_page
        self.end_page = end_page
        self.start_time = start_time
        self.end_time = end_time


def find_recording_event(page, events):
    return next((x for x in events if (page >= x.start_page) and (page <= x.end_page)), None)
