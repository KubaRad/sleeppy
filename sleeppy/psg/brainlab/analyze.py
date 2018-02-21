"""
Created on 30-09-2011

@author: jradlins
"""

import struct
from itertools import repeat
from brainlab.events import Event, RecordingEvent, get_selected_events, get_selected_events_4_types, \
    find_recording_event, read_events, read_event_descs
from brainlab.utils import string_trim_to_0, add_seconds_to_time, ms_to_events_seconds, decode_time_seconds


class AnalyzeFile:
    def __init__(self):
        self.header = AnalyzeHeader()
        self.inventory = []
        self.stage_defs = {}
        self.events = []
        self.registration_events = []
        self.stage_defs = {}
        self.stages = []
        self.events_desc = []
        self.sleep_stg_vals = []
        self.sleep_stg_rem_vals = []
        self.sleep_stg_non_rem_vals = []
        self.first_sleep_stage = None
        self.last_sleep_stage = None
        self.sleep_period_time_hrs = 0
        self.sleep_period_time = 0
        self.sleep_stages = []
        self.sleep_time = 0
        self.sleep_time_hrs = 0
        self.sleep_wake_time = 0
        self.sleep_wake_time_hrs = 0
        self.sleep_n1_time = 0
        self.sleep_n1_time_hrs = 0
        self.sleep_n2_time = 0
        self.sleep_n2_time_hrs = 0
        self.sleep_n3_time = 0
        self.sleep_n3_time_hrs = 0
        self.sleep_rem_time = 0
        self.sleep_rem_time_hrs = 0
        self.respiratory_events = []
        self.saturation_events = []
        self.arousal_events = []
        self.rdi = 0
        self.odi = 0
        self.ai = 0


def read_analyze_file(file_name):
    af = AnalyzeFile()
    sf = open(file_name, 'rb')
    try:
        af.header = read_analyze_header(sf)
        af.inventory = read_file_inventory(sf)
        stage_block = None
        event_block = None
        for inv in af.inventory:
            if inv.item_id == InventoryItem.ID_STAGES:
                stage_block = inv
            if inv.item_id == InventoryItem.ID_EVENTS:
                event_block = inv
        stgs = read_stages(sf, stage_block.offset, stage_block.size)
        af.stage_defs = read_stage_types(sf)

        af.events = read_events(sf, event_block.offset, event_block.size)
        af.registration_events = []
        for ev in get_selected_events_4_types(af.events, [Event.ET_SAVESKIPEVENT]):
            af.registration_events.append(
                RecordingEvent(ev.page, ev.page + int(ms_to_events_seconds(ev.duration_in_ms) / 30) - 1,
                               decode_time_seconds(ev.time), decode_time_seconds(ev.end_time)))

        af.stages = transform_stages(stgs, af.stage_defs, af.registration_events)

        af.events_desc = read_event_descs(sf)
        af.sleep_stg_vals = get_sleep_values(af.stage_defs)
        af.sleep_stg_rem_vals = get_rem_values(af.stage_defs)
        af.sleep_stg_non_rem_vals = get_non_rem_values(af.stage_defs)
        af.first_sleep_stage = find_first_sleep_epoch(af.stages, af.sleep_stg_non_rem_vals, af.sleep_stg_vals)
        af.last_sleep_stage = find_last_sleep_epoch(af.stages, af.sleep_stg_vals)
        if (af.last_sleep_stage >= af.first_sleep_stage) and (af.first_sleep_stage != 0):
            af.sleep_period_time = (af.last_sleep_stage - af.first_sleep_stage) * 30
        af.sleep_period_time_hrs = af.sleep_period_time / (60 * 60)
        af.sleep_stages = [x for x in af.stages if (x.val in af.sleep_stg_vals)]
        af.sleep_time = len(af.sleep_stages) * 30
        af.sleep_time_hrs = af.sleep_time / (60 * 60)
        af.sleep_wake_time = len([x for x in af.stages if (
            (x.label == "W") and (x.no > af.first_sleep_stage) and (x.no <= af.last_sleep_stage))]) * 30
        af.sleep_wake_time_hrs = af.sleep_wake_time / (60 * 60)
        af.sleep_n1_time = len([x for x in af.stages if x.label == "N1"]) * 30
        af.sleep_n1_time_hrs = af.sleep_n1_time / (60 * 60)
        af.sleep_n2_time = len([x for x in af.stages if x.label == "N2"]) * 30
        af.sleep_n2_time_hrs = af.sleep_n2_time / (60 * 60)
        af.sleep_n3_time = len([x for x in af.stages if x.label == "N3"]) * 30
        af.sleep_n3_time_hrs = af.sleep_n3_time / (60 * 60)
        af.sleep_rem_time = len([x for x in af.stages if x.label == "R"]) * 30
        af.sleep_rem_time_hrs = af.sleep_rem_time / (60 * 60)
        resp_subtypes = [Event.ST_NONCLASSIFIEDAPNEA, Event.ST_CENTRALAPNEA, Event.ST_OBSTRUCTIVEAPNEA,
                         Event.ST_MIXEDAPNEA, Event.ST_NONCLASSIFIEDHYPOPNEA, Event.ST_CENTRALHYPOPNEA,
                         Event.ST_OBSTRUCTIVEHYPOPNEA, Event.ST_MIXEDHYPOPNEA, Event.ST_NEUTRAL,
                         Event.ST_PARADOXYCALAPNEA, Event.ST_PARADOXYCALHYPOPNEA, Event.ST_PERIODICALBREATHING]
        af.respiratory_events = get_selected_events(af.events, [Event.ET_RESPIRATIONEVENTS], resp_subtypes)
        af.saturation_events = get_selected_events(af.events, [Event.ET_SATURATIONEVENTS],
                                                   [Event.ST_DIPSATURATION])
        af.arousal_events = get_selected_events(af.events, [Event.ET_AROUSALEVENTS], [Event.ST_AROUSAL])
        if af.sleep_time_hrs != 0:
            af.rdi = len(af.respiratory_events) / af.sleep_time_hrs
            af.odi = len(af.saturation_events) / af.sleep_time_hrs
            af.ai = len(af.arousal_events) / af.sleep_time_hrs
    finally:
        sf.close()
    return af


def find_first_sleep_epoch(stages, sleep_stg_nrem_vals, sleep_stg_vals):
    scount = len(stages)
    for i in range(scount):
        if len(sleep_stg_nrem_vals) < 2:
            if stages[i].val in sleep_stg_vals:
                return i + 1
        else:
            if i > 0:
                if stages[i].val in sleep_stg_nrem_vals[1:]:
                    return i + 1
    return 0


def find_last_sleep_epoch(stages, sleep_stg_vals):
    scount = len(stages)
    last_stage = 0
    for i in range(scount):
        if stages[i].val in sleep_stg_vals:
            last_stage = i
    if last_stage > 0:
        return last_stage + 1
    return 0


class AnalyzeHeader:
    PROGRAM_ID = 0x41545353
    TABLE_ID = 0x534C4254

    def __init__(self, program_id=0, table_id=0, version_id=0):
        self.program_id = program_id
        self.table_id = table_id
        self.version_id = version_id

    def check_program_id(self):
        return self.program_id == AnalyzeHeader.PROGRAM_ID

    def check_table_id(self):
        return self.table_id == AnalyzeHeader.TABLE_ID

    def check_header(self):
        return self.check_program_id() and self.check_table_id()


def read_analyze_header(sf):
    sf.seek(0)
    header_struct = struct.Struct("<2lh")
    hb = header_struct.unpack(sf.read(header_struct.size))
    return AnalyzeHeader(hb[0], hb[1], hb[2])


class InventoryItem:
    ID_INVALID = 0x0000  # unused or invalid
    ID_SELECTEDPAGES = 0x0100  # Selected Pages
    ID_STAGES = 0x0200  # Stages
    ID_CALCULATEDSTAGES = 0x0210  # Calculated Stages
    ID_CALCSTAGESPARAMETERS = 0x0220  # Calculated Stages parameters
    ID_EVENTS = 0x0300  # Events
    ID_NOTES = 0x0400  # Notes
    ID_ECGPARAMETERS = 0x0500  # ECG parameters
    ID_ECGRATE = 0x0510  # ECG rate
    ID_ECGWAVE = 0x0520  # ECG wave
    ID_ECGRHYTHM = 0x0530  # ECG rhythm
    ID_RESPIRATIONPARAMETERS = 0x0600  # Respiration parameters
    ID_THORAXOLDHISTOGRAM = 0x0610  # Thorax histogram old
    ID_ABDOMENOLDHISTOGRAM = 0x0611  # Abdomen histogram old
    ID_FLOWOLDHISTOGRAM = 0x0612  # Flow histogram old
    ID_THORAXHISTOGRAM = 0x0615  # Thorax histogram
    ID_ABDOMENHISTOGRAM = 0x0616  # Abdomen histogram
    ID_FLOWHISTOGRAM = 0x0617  # Flow histogram
    ID_RESPIRATIONRATE = 0x0620  # Respiration rate
    ID_SATURATIONPARAMETERS = 0x0700  # Saturation parameters
    ID_SATURATIONRATE = 0x0710  # Saturation rate
    ID_SATURATIONSIGNAL = 0x0720  # Saturation signal
    ID_EMGPARAMETERS = 0x0800  # EMG parameters
    ID_EMGCHINSIGNAL = 0x0810  # EMG chin signal
    ID_EMGTIBIALSIGNAL_01 = 0x0820  # EMG tibial signal 1
    ID_EMGTIBIALSIGNAL_02 = 0x0821  # EMG tibial signal 2
    ID_EMGTIBIALSIGNAL_03 = 0x0822  # EMG tibial signal 3
    ID_EMGTIBIALSIGNAL_04 = 0x0823  # EMG tibial signal 4
    ID_EMGTIBIALSIGNAL_05 = 0x0824  # EMG tibial signal 5
    ID_EMGTIBIALSIGNAL_06 = 0x0825  # EMG tibial signal 6
    ID_EMGTIBIALSIGNAL_07 = 0x0826  # EMG tibial signal 7
    ID_EMGTIBIALSIGNAL_08 = 0x0827  # EMG tibial signal 8
    ID_EMGTIBIALSIGNAL_09 = 0x0828  # EMG tibial signal 9
    ID_EMGTIBIALSIGNAL_10 = 0x0829  # EMG tibial signal 10
    ID_EMGTIBIALSIGNAL_11 = 0x082a  # EMG tibial signal 11
    ID_EMGTIBIALSIGNAL_12 = 0x082b  # EMG tibial signal 12
    ID_EMGTIBIALSIGNAL_13 = 0x082c  # EMG tibial signal 13
    ID_EMGTIBIALSIGNAL_14 = 0x082d  # EMG tibial signal 14
    ID_EMGTIBIALSIGNAL_15 = 0x082e  # EMG tibial signal 15
    ID_EMGTIBIALSIGNAL_16 = 0x082f  # EMG tibial signal 16
    ID_EMGTIBIALSIGNAL_17 = 0x0830  # EMG tibial signal 17
    ID_EMGTIBIALSIGNAL_18 = 0x0831  # EMG tibial signal 18
    ID_EMGTIBIALSIGNAL_19 = 0x0832  # EMG tibial signal 19
    ID_EMGTIBIALSIGNAL_20 = 0x0833  # EMG tibial signal 20
    ID_EMGTIBIALSIGNAL_21 = 0x0834  # EMG tibial signal 21
    ID_EMGTIBIALSIGNAL_22 = 0x0835  # EMG tibial signal 22
    ID_EMGTIBIALSIGNAL_23 = 0x0836  # EMG tibial signal 23
    ID_EMGTIBIALSIGNAL_24 = 0x0837  # EMG tibial signal 24
    ID_EMGTIBIALSIGNAL_25 = 0x0838  # EMG tibial signal 25
    ID_EMGTIBIALSIGNAL_26 = 0x0839  # EMG tibial signal 26
    ID_EMGTIBIALSIGNAL_27 = 0x083a  # EMG tibial signal 27
    ID_EMGTIBIALSIGNAL_28 = 0x083b  # EMG tibial signal 28
    ID_EMGTIBIALSIGNAL_29 = 0x083c  # EMG tibial signal 29
    ID_EMGTIBIALSIGNAL_30 = 0x083d  # EMG tibial signal 30
    ID_EMGTIBIALSIGNAL_31 = 0x083e  # EMG tibial signal 31
    ID_EMGTIBIALSIGNAL_32 = 0x083f  # EMG tibial signal 32
    ID_EEGDELTAPARAMETERS = 0x0900  # EEG Delta parameters
    ID_EEGDELTAHISTOGRAM_01 = 0x0910  # EEG Delta Histogram channel 1
    ID_EEGDELTAHISTOGRAM_02 = 0x0911  # EEG Delta Histogram channel 2
    ID_EEGDELTAHISTOGRAM_03 = 0x0912  # EEG Delta Histogram channel 3
    ID_EEGDELTAHISTOGRAM_04 = 0x0913  # EEG Delta Histogram channel 4
    ID_EEGDELTAHISTOGRAM_05 = 0x0914  # EEG Delta Histogram channel 5
    ID_EEGDELTAHISTOGRAM_06 = 0x0915  # EEG Delta Histogram channel 6
    ID_EEGDELTAHISTOGRAM_07 = 0x0916  # EEG Delta Histogram channel 7
    ID_EEGDELTAHISTOGRAM_08 = 0x0917  # EEG Delta Histogram channel 8
    ID_EEGDELTAHISTOGRAM_09 = 0x0918  # EEG Delta Histogram channel 9
    ID_EEGDELTAHISTOGRAM_10 = 0x0919  # EEG Delta Histogram channel 10
    ID_EEGDELTAHISTOGRAM_11 = 0x091a  # EEG Delta Histogram channel 11
    ID_EEGDELTAHISTOGRAM_12 = 0x091b  # EEG Delta Histogram channel 12
    ID_EEGDELTAHISTOGRAM_13 = 0x091c  # EEG Delta Histogram channel 13
    ID_EEGDELTAHISTOGRAM_14 = 0x091d  # EEG Delta Histogram channel 14
    ID_EEGDELTAHISTOGRAM_15 = 0x091e  # EEG Delta Histogram channel 15
    ID_EEGDELTAHISTOGRAM_16 = 0x091f  # EEG Delta Histogram channel 16
    ID_EEGDELTAHISTOGRAM_17 = 0x0920  # EEG Delta Histogram channel 17
    ID_EEGDELTAHISTOGRAM_18 = 0x0921  # EEG Delta Histogram channel 18
    ID_EEGDELTAHISTOGRAM_19 = 0x0922  # EEG Delta Histogram channel 19
    ID_EEGDELTAHISTOGRAM_20 = 0x0923  # EEG Delta Histogram channel 20
    ID_EEGDELTAHISTOGRAM_21 = 0x0924  # EEG Delta Histogram channel 21
    ID_EEGDELTAHISTOGRAM_22 = 0x0925  # EEG Delta Histogram channel 22
    ID_EEGDELTAHISTOGRAM_23 = 0x0926  # EEG Delta Histogram channel 23
    ID_EEGDELTAHISTOGRAM_24 = 0x0927  # EEG Delta Histogram channel 24
    ID_EEGDELTAHISTOGRAM_25 = 0x0928  # EEG Delta Histogram channel 25
    ID_EEGDELTAHISTOGRAM_26 = 0x0929  # EEG Delta Histogram channel 26
    ID_EEGDELTAHISTOGRAM_27 = 0x092a  # EEG Delta Histogram channel 27
    ID_EEGDELTAHISTOGRAM_28 = 0x092b  # EEG Delta Histogram channel 28
    ID_EEGDELTAHISTOGRAM_29 = 0x092c  # EEG Delta Histogram channel 29
    ID_EEGDELTAHISTOGRAM_30 = 0x092d  # EEG Delta Histogram channel 30
    ID_EEGDELTAHISTOGRAM_31 = 0x092e  # EEG Delta Histogram channel 31
    ID_EEGDELTAHISTOGRAM_32 = 0x092f  # EEG Delta Histogram channel 32
    ID_EEGDELTAPERCENTAGE_01 = 0x0930  # EEG Delta Percentage channel 1
    ID_EEGDELTAPERCENTAGE_02 = 0x0931  # EEG Delta Percentage channel 2
    ID_EEGDELTAPERCENTAGE_03 = 0x0932  # EEG Delta Percentage channel 3
    ID_EEGDELTAPERCENTAGE_04 = 0x0933  # EEG Delta Percentage channel 4
    ID_EEGDELTAPERCENTAGE_05 = 0x0934  # EEG Delta Percentage channel 5
    ID_EEGDELTAPERCENTAGE_06 = 0x0935  # EEG Delta Percentage channel 6
    ID_EEGDELTAPERCENTAGE_07 = 0x0936  # EEG Delta Percentage channel 7
    ID_EEGDELTAPERCENTAGE_08 = 0x0937  # EEG Delta Percentage channel 8
    ID_EEGDELTAPERCENTAGE_09 = 0x0938  # EEG Delta Percentage channel 9
    ID_EEGDELTAPERCENTAGE_10 = 0x0939  # EEG Delta Percentage channel 10
    ID_EEGDELTAPERCENTAGE_11 = 0x093a  # EEG Delta Percentage channel 11
    ID_EEGDELTAPERCENTAGE_12 = 0x093b  # EEG Delta Percentage channel 12
    ID_EEGDELTAPERCENTAGE_13 = 0x093c  # EEG Delta Percentage channel 13
    ID_EEGDELTAPERCENTAGE_14 = 0x093d  # EEG Delta Percentage channel 14
    ID_EEGDELTAPERCENTAGE_15 = 0x093e  # EEG Delta Percentage channel 15
    ID_EEGDELTAPERCENTAGE_16 = 0x093f  # EEG Delta Percentage channel 16
    ID_EEGDELTAPERCENTAGE_17 = 0x0940  # EEG Delta Percentage channel 17
    ID_EEGDELTAPERCENTAGE_18 = 0x0941  # EEG Delta Percentage channel 18
    ID_EEGDELTAPERCENTAGE_19 = 0x0942  # EEG Delta Percentage channel 19
    ID_EEGDELTAPERCENTAGE_20 = 0x0943  # EEG Delta Percentage channel 20
    ID_EEGDELTAPERCENTAGE_21 = 0x0944  # EEG Delta Percentage channel 21
    ID_EEGDELTAPERCENTAGE_22 = 0x0945  # EEG Delta Percentage channel 22
    ID_EEGDELTAPERCENTAGE_23 = 0x0946  # EEG Delta Percentage channel 23
    ID_EEGDELTAPERCENTAGE_24 = 0x0947  # EEG Delta Percentage channel 24
    ID_EEGDELTAPERCENTAGE_25 = 0x0948  # EEG Delta Percentage channel 25
    ID_EEGDELTAPERCENTAGE_26 = 0x0949  # EEG Delta Percentage channel 26
    ID_EEGDELTAPERCENTAGE_27 = 0x094a  # EEG Delta Percentage channel 27
    ID_EEGDELTAPERCENTAGE_28 = 0x094b  # EEG Delta Percentage channel 28
    ID_EEGDELTAPERCENTAGE_29 = 0x094c  # EEG Delta Percentage channel 29
    ID_EEGDELTAPERCENTAGE_30 = 0x094d  # EEG Delta Percentage channel 30
    ID_EEGDELTAPERCENTAGE_31 = 0x094e  # EEG Delta Percentage channel 31
    ID_EEGDELTAPERCENTAGE_32 = 0x094f  # EEG Delta Percentage channel 32
    ID_EEGDELTACOUNT_01 = 0x0950  # EEG Delta Count channel 1
    ID_EEGDELTACOUNT_02 = 0x0951  # EEG Delta Count channel 2
    ID_EEGDELTACOUNT_03 = 0x0952  # EEG Delta Count channel 3
    ID_EEGDELTACOUNT_04 = 0x0953  # EEG Delta Count channel 4
    ID_EEGDELTACOUNT_05 = 0x0954  # EEG Delta Count channel 5
    ID_EEGDELTACOUNT_06 = 0x0955  # EEG Delta Count channel 6
    ID_EEGDELTACOUNT_07 = 0x0956  # EEG Delta Count channel 7
    ID_EEGDELTACOUNT_08 = 0x0957  # EEG Delta Count channel 8
    ID_EEGDELTACOUNT_09 = 0x0958  # EEG Delta Count channel 9
    ID_EEGDELTACOUNT_10 = 0x0959  # EEG Delta Count channel 10
    ID_EEGDELTACOUNT_11 = 0x095a  # EEG Delta Count channel 11
    ID_EEGDELTACOUNT_12 = 0x095b  # EEG Delta Count channel 12
    ID_EEGDELTACOUNT_13 = 0x095c  # EEG Delta Count channel 13
    ID_EEGDELTACOUNT_14 = 0x095d  # EEG Delta Count channel 14
    ID_EEGDELTACOUNT_15 = 0x095e  # EEG Delta Count channel 15
    ID_EEGDELTACOUNT_16 = 0x095f  # EEG Delta Count channel 16
    ID_EEGDELTACOUNT_17 = 0x0960  # EEG Delta Count channel 17
    ID_EEGDELTACOUNT_18 = 0x0961  # EEG Delta Count channel 18
    ID_EEGDELTACOUNT_19 = 0x0962  # EEG Delta Count channel 19
    ID_EEGDELTACOUNT_20 = 0x0963  # EEG Delta Count channel 20
    ID_EEGDELTACOUNT_21 = 0x0964  # EEG Delta Count channel 21
    ID_EEGDELTACOUNT_22 = 0x0965  # EEG Delta Count channel 22
    ID_EEGDELTACOUNT_23 = 0x0966  # EEG Delta Count channel 23
    ID_EEGDELTACOUNT_24 = 0x0967  # EEG Delta Count channel 24
    ID_EEGDELTACOUNT_25 = 0x0968  # EEG Delta Count channel 25
    ID_EEGDELTACOUNT_26 = 0x0969  # EEG Delta Count channel 26
    ID_EEGDELTACOUNT_27 = 0x096a  # EEG Delta Count channel 27
    ID_EEGDELTACOUNT_28 = 0x096b  # EEG Delta Count channel 28
    ID_EEGDELTACOUNT_29 = 0x096c  # EEG Delta Count channel 29
    ID_EEGDELTACOUNT_30 = 0x096d  # EEG Delta Count channel 30
    ID_EEGDELTACOUNT_31 = 0x096e  # EEG Delta Count channel 31
    ID_EEGDELTACOUNT_32 = 0x096f  # EEG Delta Count channel 32
    ID_EEGSPINDLEPARAMETERS = 0x0a00  # EEG Spindle parameters
    ID_EEGSPINDLEHISTOGRAM_01 = 0x0a10  # EEG Spindle Histogram channel 1
    ID_EEGSPINDLEHISTOGRAM_02 = 0x0a11  # EEG Spindle Histogram channel 2
    ID_EEGSPINDLEHISTOGRAM_03 = 0x0a12  # EEG Spindle Histogram channel 3
    ID_EEGSPINDLEHISTOGRAM_04 = 0x0a13  # EEG Spindle Histogram channel 4
    ID_EEGSPINDLEHISTOGRAM_05 = 0x0a14  # EEG Spindle Histogram channel 5
    ID_EEGSPINDLEHISTOGRAM_06 = 0x0a15  # EEG Spindle Histogram channel 6
    ID_EEGSPINDLEHISTOGRAM_07 = 0x0a16  # EEG Spindle Histogram channel 7
    ID_EEGSPINDLEHISTOGRAM_08 = 0x0a17  # EEG Spindle Histogram channel 8
    ID_EEGSPINDLEHISTOGRAM_09 = 0x0a18  # EEG Spindle Histogram channel 9
    ID_EEGSPINDLEHISTOGRAM_10 = 0x0a19  # EEG Spindle Histogram channel 10
    ID_EEGSPINDLEHISTOGRAM_11 = 0x0a1a  # EEG Spindle Histogram channel 11
    ID_EEGSPINDLEHISTOGRAM_12 = 0x0a1b  # EEG Spindle Histogram channel 12
    ID_EEGSPINDLEHISTOGRAM_13 = 0x0a1c  # EEG Spindle Histogram channel 13
    ID_EEGSPINDLEHISTOGRAM_14 = 0x0a1d  # EEG Spindle Histogram channel 14
    ID_EEGSPINDLEHISTOGRAM_15 = 0x0a1e  # EEG Spindle Histogram channel 15
    ID_EEGSPINDLEHISTOGRAM_16 = 0x0a1f  # EEG Spindle Histogram channel 16
    ID_EEGSPINDLEHISTOGRAM_17 = 0x0a20  # EEG Spindle Histogram channel 17
    ID_EEGSPINDLEHISTOGRAM_18 = 0x0a21  # EEG Spindle Histogram channel 18
    ID_EEGSPINDLEHISTOGRAM_19 = 0x0a22  # EEG Spindle Histogram channel 19
    ID_EEGSPINDLEHISTOGRAM_20 = 0x0a23  # EEG Spindle Histogram channel 20
    ID_EEGSPINDLEHISTOGRAM_21 = 0x0a24  # EEG Spindle Histogram channel 21
    ID_EEGSPINDLEHISTOGRAM_22 = 0x0a25  # EEG Spindle Histogram channel 22
    ID_EEGSPINDLEHISTOGRAM_23 = 0x0a26  # EEG Spindle Histogram channel 23
    ID_EEGSPINDLEHISTOGRAM_24 = 0x0a27  # EEG Spindle Histogram channel 24
    ID_EEGSPINDLEHISTOGRAM_25 = 0x0a28  # EEG Spindle Histogram channel 25
    ID_EEGSPINDLEHISTOGRAM_26 = 0x0a29  # EEG Spindle Histogram channel 26
    ID_EEGSPINDLEHISTOGRAM_27 = 0x0a2a  # EEG Spindle Histogram channel 27
    ID_EEGSPINDLEHISTOGRAM_28 = 0x0a2b  # EEG Spindle Histogram channel 28
    ID_EEGSPINDLEHISTOGRAM_29 = 0x0a2c  # EEG Spindle Histogram channel 29
    ID_EEGSPINDLEHISTOGRAM_30 = 0x0a2d  # EEG Spindle Histogram channel 30
    ID_EEGSPINDLEHISTOGRAM_31 = 0x0a2e  # EEG Spindle Histogram channel 31
    ID_EEGSPINDLEHISTOGRAM_32 = 0x0a2f  # EEG Spindle Histogram channel 32
    ID_EEGALPHAOLDPARAMETERS = 0x0b00  # EEG Alpha old-style parameters
    ID_EEGALPHASIGNAL_01 = 0x0b10  # EEG Alpha Histogram channel 1
    ID_EEGALPHASIGNAL_02 = 0x0b11  # EEG Alpha Histogram channel 2
    ID_EEGALPHASIGNAL_03 = 0x0b12  # EEG Alpha Histogram channel 3
    ID_EEGALPHASIGNAL_04 = 0x0b13  # EEG Alpha Histogram channel 4
    ID_EEGALPHASIGNAL_05 = 0x0b14  # EEG Alpha Histogram channel 5
    ID_EEGALPHASIGNAL_06 = 0x0b15  # EEG Alpha Histogram channel 6
    ID_EEGALPHASIGNAL_07 = 0x0b16  # EEG Alpha Histogram channel 7
    ID_EEGALPHASIGNAL_08 = 0x0b17  # EEG Alpha Histogram channel 8
    ID_EEGALPHASIGNAL_09 = 0x0b18  # EEG Alpha Histogram channel 9
    ID_EEGALPHASIGNAL_10 = 0x0b19  # EEG Alpha Histogram channel 10
    ID_EEGALPHASIGNAL_11 = 0x0b1a  # EEG Alpha Histogram channel 11
    ID_EEGALPHASIGNAL_12 = 0x0b1b  # EEG Alpha Histogram channel 12
    ID_EEGALPHASIGNAL_13 = 0x0b1c  # EEG Alpha Histogram channel 13
    ID_EEGALPHASIGNAL_14 = 0x0b1d  # EEG Alpha Histogram channel 14
    ID_EEGALPHASIGNAL_15 = 0x0b1e  # EEG Alpha Histogram channel 15
    ID_EEGALPHASIGNAL_16 = 0x0b1f  # EEG Alpha Histogram channel 16
    ID_EEGALPHASIGNAL_17 = 0x0b20  # EEG Alpha Histogram channel 17
    ID_EEGALPHASIGNAL_18 = 0x0b21  # EEG Alpha Histogram channel 18
    ID_EEGALPHASIGNAL_19 = 0x0b22  # EEG Alpha Histogram channel 19
    ID_EEGALPHASIGNAL_20 = 0x0b23  # EEG Alpha Histogram channel 20
    ID_EEGALPHASIGNAL_21 = 0x0b24  # EEG Alpha Histogram channel 21
    ID_EEGALPHASIGNAL_22 = 0x0b25  # EEG Alpha Histogram channel 22
    ID_EEGALPHASIGNAL_23 = 0x0b26  # EEG Alpha Histogram channel 23
    ID_EEGALPHASIGNAL_24 = 0x0b27  # EEG Alpha Histogram channel 24
    ID_EEGALPHASIGNAL_25 = 0x0b28  # EEG Alpha Histogram channel 25
    ID_EEGALPHASIGNAL_26 = 0x0b29  # EEG Alpha Histogram channel 26
    ID_EEGALPHASIGNAL_27 = 0x0b2a  # EEG Alpha Histogram channel 27
    ID_EEGALPHASIGNAL_28 = 0x0b2b  # EEG Alpha Histogram channel 28
    ID_EEGALPHASIGNAL_29 = 0x0b2c  # EEG Alpha Histogram channel 29
    ID_EEGALPHASIGNAL_30 = 0x0b2d  # EEG Alpha Histogram channel 30
    ID_EEGALPHASIGNAL_31 = 0x0b2e  # EEG Alpha Histogram channel 31
    ID_EEGALPHASIGNAL_32 = 0x0b2f  # EEG Alpha Histogram channel 32
    ID_EEGALPHAPARAMETERS = 0x0b80  # EEG Alpha parameters
    ID_EEGALPHAHISTOGRAM_01 = 0x0b90  # EEG Alpha Histogram channel 1
    ID_EEGALPHAHISTOGRAM_02 = 0x0b91  # EEG Alpha Histogram channel 2
    ID_EEGALPHAHISTOGRAM_03 = 0x0b92  # EEG Alpha Histogram channel 3
    ID_EEGALPHAHISTOGRAM_04 = 0x0b93  # EEG Alpha Histogram channel 4
    ID_EEGALPHAHISTOGRAM_05 = 0x0b94  # EEG Alpha Histogram channel 5
    ID_EEGALPHAHISTOGRAM_06 = 0x0b95  # EEG Alpha Histogram channel 6
    ID_EEGALPHAHISTOGRAM_07 = 0x0b96  # EEG Alpha Histogram channel 7
    ID_EEGALPHAHISTOGRAM_08 = 0x0b97  # EEG Alpha Histogram channel 8
    ID_EEGALPHAHISTOGRAM_09 = 0x0b98  # EEG Alpha Histogram channel 9
    ID_EEGALPHAHISTOGRAM_10 = 0x0b99  # EEG Alpha Histogram channel 10
    ID_EEGALPHAHISTOGRAM_11 = 0x0b9a  # EEG Alpha Histogram channel 11
    ID_EEGALPHAHISTOGRAM_12 = 0x0b9b  # EEG Alpha Histogram channel 12
    ID_EEGALPHAHISTOGRAM_13 = 0x0b9c  # EEG Alpha Histogram channel 13
    ID_EEGALPHAHISTOGRAM_14 = 0x0b9d  # EEG Alpha Histogram channel 14
    ID_EEGALPHAHISTOGRAM_15 = 0x0b9e  # EEG Alpha Histogram channel 15
    ID_EEGALPHAHISTOGRAM_16 = 0x0b9f  # EEG Alpha Histogram channel 16
    ID_EEGALPHAHISTOGRAM_17 = 0x0ba0  # EEG Alpha Histogram channel 17
    ID_EEGALPHAHISTOGRAM_18 = 0x0ba1  # EEG Alpha Histogram channel 18
    ID_EEGALPHAHISTOGRAM_19 = 0x0ba2  # EEG Alpha Histogram channel 19
    ID_EEGALPHAHISTOGRAM_20 = 0x0ba3  # EEG Alpha Histogram channel 20
    ID_EEGALPHAHISTOGRAM_21 = 0x0ba4  # EEG Alpha Histogram channel 21
    ID_EEGALPHAHISTOGRAM_22 = 0x0ba5  # EEG Alpha Histogram channel 22
    ID_EEGALPHAHISTOGRAM_23 = 0x0ba6  # EEG Alpha Histogram channel 23
    ID_EEGALPHAHISTOGRAM_24 = 0x0ba7  # EEG Alpha Histogram channel 24
    ID_EEGALPHAHISTOGRAM_25 = 0x0ba8  # EEG Alpha Histogram channel 25
    ID_EEGALPHAHISTOGRAM_26 = 0x0ba9  # EEG Alpha Histogram channel 26
    ID_EEGALPHAHISTOGRAM_27 = 0x0baa  # EEG Alpha Histogram channel 27
    ID_EEGALPHAHISTOGRAM_28 = 0x0bab  # EEG Alpha Histogram channel 28
    ID_EEGALPHAHISTOGRAM_29 = 0x0bac  # EEG Alpha Histogram channel 29
    ID_EEGALPHAHISTOGRAM_30 = 0x0bad  # EEG Alpha Histogram channel 30
    ID_EEGALPHAHISTOGRAM_31 = 0x0bae  # EEG Alpha Histogram channel 31
    ID_EEGALPHAHISTOGRAM_32 = 0x0baf  # EEG Alpha Histogram channel 32
    ID_EEGALPHAPERCENTAGE_01 = 0x0bb0  # EEG Alpha Percentage channel 1
    ID_EEGALPHAPERCENTAGE_02 = 0x0bb1  # EEG Alpha Percentage channel 2
    ID_EEGALPHAPERCENTAGE_03 = 0x0bb2  # EEG Alpha Percentage channel 3
    ID_EEGALPHAPERCENTAGE_04 = 0x0bb3  # EEG Alpha Percentage channel 4
    ID_EEGALPHAPERCENTAGE_05 = 0x0bb4  # EEG Alpha Percentage channel 5
    ID_EEGALPHAPERCENTAGE_06 = 0x0bb5  # EEG Alpha Percentage channel 6
    ID_EEGALPHAPERCENTAGE_07 = 0x0bb6  # EEG Alpha Percentage channel 7
    ID_EEGALPHAPERCENTAGE_08 = 0x0bb7  # EEG Alpha Percentage channel 8
    ID_EEGALPHAPERCENTAGE_09 = 0x0bb8  # EEG Alpha Percentage channel 9
    ID_EEGALPHAPERCENTAGE_10 = 0x0bb9  # EEG Alpha Percentage channel 10
    ID_EEGALPHAPERCENTAGE_11 = 0x0bba  # EEG Alpha Percentage channel 11
    ID_EEGALPHAPERCENTAGE_12 = 0x0bbb  # EEG Alpha Percentage channel 12
    ID_EEGALPHAPERCENTAGE_13 = 0x0bbc  # EEG Alpha Percentage channel 13
    ID_EEGALPHAPERCENTAGE_14 = 0x0bbd  # EEG Alpha Percentage channel 14
    ID_EEGALPHAPERCENTAGE_15 = 0x0bbe  # EEG Alpha Percentage channel 15
    ID_EEGALPHAPERCENTAGE_16 = 0x0bbf  # EEG Alpha Percentage channel 16
    ID_EEGALPHAPERCENTAGE_17 = 0x0bc0  # EEG Alpha Percentage channel 17
    ID_EEGALPHAPERCENTAGE_18 = 0x0bc1  # EEG Alpha Percentage channel 18
    ID_EEGALPHAPERCENTAGE_19 = 0x0bc2  # EEG Alpha Percentage channel 19
    ID_EEGALPHAPERCENTAGE_20 = 0x0bc3  # EEG Alpha Percentage channel 20
    ID_EEGALPHAPERCENTAGE_21 = 0x0bc4  # EEG Alpha Percentage channel 21
    ID_EEGALPHAPERCENTAGE_22 = 0x0bc5  # EEG Alpha Percentage channel 22
    ID_EEGALPHAPERCENTAGE_23 = 0x0bc6  # EEG Alpha Percentage channel 23
    ID_EEGALPHAPERCENTAGE_24 = 0x0bc7  # EEG Alpha Percentage channel 24
    ID_EEGALPHAPERCENTAGE_25 = 0x0bc8  # EEG Alpha Percentage channel 25
    ID_EEGALPHAPERCENTAGE_26 = 0x0bc9  # EEG Alpha Percentage channel 26
    ID_EEGALPHAPERCENTAGE_27 = 0x0bca  # EEG Alpha Percentage channel 27
    ID_EEGALPHAPERCENTAGE_28 = 0x0bcb  # EEG Alpha Percentage channel 28
    ID_EEGALPHAPERCENTAGE_29 = 0x0bcc  # EEG Alpha Percentage channel 29
    ID_EEGALPHAPERCENTAGE_30 = 0x0bcd  # EEG Alpha Percentage channel 30
    ID_EEGALPHAPERCENTAGE_31 = 0x0bce  # EEG Alpha Percentage channel 31
    ID_EEGALPHAPERCENTAGE_32 = 0x0bcf  # EEG Alpha Percentage channel 32
    ID_EOGPARAMETERS = 0x0c00  # EOG parameters
    ID_EOGREMHISTOGRAM_01 = 0x0c10  # EOG REM Histogram channel 1
    ID_EOGREMHISTOGRAM_02 = 0x0c11  # EOG REM Histogram channel 2
    ID_EOGREMCOUNT_01 = 0x0c30  # EOG REM Count channel 1
    ID_EOGREMCOUNT_02 = 0x0c31  # EOG REM Count channel 2
    ID_EOGSEMHISTOGRAM = 0x0c50  # EOG SEM Histogram
    ID_EOGSEMCOUNT = 0x0c70  # EOG SEM Count
    ID_EOGBLINKCOUNT_01 = 0x0c90  # EOG Blink Count channel 1
    ID_EOGBLINKCOUNT_02 = 0x0c91  # EOG Blink Count channel 2
    ID_EEGTHETAPARAMETERS = 0x0d00  # EEG Theta parameters
    ID_EEGTHETASIGNAL_01 = 0x0d10  # EEG Theta Histogram channel 1
    ID_EEGTHETASIGNAL_02 = 0x0d11  # EEG Theta Histogram channel 2
    ID_EEGTHETASIGNAL_03 = 0x0d12  # EEG Theta Histogram channel 3
    ID_EEGTHETASIGNAL_04 = 0x0d13  # EEG Theta Histogram channel 4
    ID_EEGTHETASIGNAL_05 = 0x0d14  # EEG Theta Histogram channel 5
    ID_EEGTHETASIGNAL_06 = 0x0d15  # EEG Theta Histogram channel 6
    ID_EEGTHETASIGNAL_07 = 0x0d16  # EEG Theta Histogram channel 7
    ID_EEGTHETASIGNAL_08 = 0x0d17  # EEG Theta Histogram channel 8
    ID_EEGTHETASIGNAL_09 = 0x0d18  # EEG Theta Histogram channel 9
    ID_EEGTHETASIGNAL_10 = 0x0d19  # EEG Theta Histogram channel 10
    ID_EEGTHETASIGNAL_11 = 0x0d1a  # EEG Theta Histogram channel 11
    ID_EEGTHETASIGNAL_12 = 0x0d1b  # EEG Theta Histogram channel 12
    ID_EEGTHETASIGNAL_13 = 0x0d1c  # EEG Theta Histogram channel 13
    ID_EEGTHETASIGNAL_14 = 0x0d1d  # EEG Theta Histogram channel 14
    ID_EEGTHETASIGNAL_15 = 0x0d1e  # EEG Theta Histogram channel 15
    ID_EEGTHETASIGNAL_16 = 0x0d1f  # EEG Theta Histogram channel 16
    ID_EEGTHETASIGNAL_17 = 0x0d20  # EEG Theta Histogram channel 17
    ID_EEGTHETASIGNAL_18 = 0x0d21  # EEG Theta Histogram channel 18
    ID_EEGTHETASIGNAL_19 = 0x0d22  # EEG Theta Histogram channel 19
    ID_EEGTHETASIGNAL_20 = 0x0d23  # EEG Theta Histogram channel 20
    ID_EEGTHETASIGNAL_21 = 0x0d24  # EEG Theta Histogram channel 21
    ID_EEGTHETASIGNAL_22 = 0x0d25  # EEG Theta Histogram channel 22
    ID_EEGTHETASIGNAL_23 = 0x0d26  # EEG Theta Histogram channel 23
    ID_EEGTHETASIGNAL_24 = 0x0d27  # EEG Theta Histogram channel 24
    ID_EEGTHETASIGNAL_25 = 0x0d28  # EEG Theta Histogram channel 25
    ID_EEGTHETASIGNAL_26 = 0x0d29  # EEG Theta Histogram channel 26
    ID_EEGTHETASIGNAL_27 = 0x0d2a  # EEG Theta Histogram channel 27
    ID_EEGTHETASIGNAL_28 = 0x0d2b  # EEG Theta Histogram channel 28
    ID_EEGTHETASIGNAL_29 = 0x0d2c  # EEG Theta Histogram channel 29
    ID_EEGTHETASIGNAL_30 = 0x0d2d  # EEG Theta Histogram channel 30
    ID_EEGTHETASIGNAL_31 = 0x0d2e  # EEG Theta Histogram channel 31
    ID_EEGTHETASIGNAL_32 = 0x0d2f  # EEG Theta Histogram channel 32
    ID_EEGBETAPARAMETERS = 0x0e00  # EEG Beta parameters
    ID_EEGBETASIGNAL_01 = 0x0e10  # EEG Beta Histogram channel 1
    ID_EEGBETASIGNAL_02 = 0x0e11  # EEG Beta Histogram channel 2
    ID_EEGBETASIGNAL_03 = 0x0e12  # EEG Beta Histogram channel 3
    ID_EEGBETASIGNAL_04 = 0x0e13  # EEG Beta Histogram channel 4
    ID_EEGBETASIGNAL_05 = 0x0e14  # EEG Beta Histogram channel 5
    ID_EEGBETASIGNAL_06 = 0x0e15  # EEG Beta Histogram channel 6
    ID_EEGBETASIGNAL_07 = 0x0e16  # EEG Beta Histogram channel 7
    ID_EEGBETASIGNAL_08 = 0x0e17  # EEG Beta Histogram channel 8
    ID_EEGBETASIGNAL_09 = 0x0e18  # EEG Beta Histogram channel 9
    ID_EEGBETASIGNAL_10 = 0x0e19  # EEG Beta Histogram channel 10
    ID_EEGBETASIGNAL_11 = 0x0e1a  # EEG Beta Histogram channel 11
    ID_EEGBETASIGNAL_12 = 0x0e1b  # EEG Beta Histogram channel 12
    ID_EEGBETASIGNAL_13 = 0x0e1c  # EEG Beta Histogram channel 13
    ID_EEGBETASIGNAL_14 = 0x0e1d  # EEG Beta Histogram channel 14
    ID_EEGBETASIGNAL_15 = 0x0e1e  # EEG Beta Histogram channel 15
    ID_EEGBETASIGNAL_16 = 0x0e1f  # EEG Beta Histogram channel 16
    ID_EEGBETASIGNAL_17 = 0x0e20  # EEG Beta Histogram channel 17
    ID_EEGBETASIGNAL_18 = 0x0e21  # EEG Beta Histogram channel 18
    ID_EEGBETASIGNAL_19 = 0x0e22  # EEG Beta Histogram channel 19
    ID_EEGBETASIGNAL_20 = 0x0e23  # EEG Beta Histogram channel 20
    ID_EEGBETASIGNAL_21 = 0x0e24  # EEG Beta Histogram channel 21
    ID_EEGBETASIGNAL_22 = 0x0e25  # EEG Beta Histogram channel 22
    ID_EEGBETASIGNAL_23 = 0x0e26  # EEG Beta Histogram channel 23
    ID_EEGBETASIGNAL_24 = 0x0e27  # EEG Beta Histogram channel 24
    ID_EEGBETASIGNAL_25 = 0x0e28  # EEG Beta Histogram channel 25
    ID_EEGBETASIGNAL_26 = 0x0e29  # EEG Beta Histogram channel 26
    ID_EEGBETASIGNAL_27 = 0x0e2a  # EEG Beta Histogram channel 27
    ID_EEGBETASIGNAL_28 = 0x0e2b  # EEG Beta Histogram channel 28
    ID_EEGBETASIGNAL_29 = 0x0e2c  # EEG Beta Histogram channel 29
    ID_EEGBETASIGNAL_30 = 0x0e2d  # EEG Beta Histogram channel 30
    ID_EEGBETASIGNAL_31 = 0x0e2e  # EEG Beta Histogram channel 31
    ID_EEGBETASIGNAL_32 = 0x0e2f  # EEG Beta Histogram channel 32
    ID_BODYPOSPARAMETERS = 0x0f00  # Body position parameters
    ID_SOUNDPARAMETERS = 0x1000  # Sound parameters
    ID_SOUND = 0x1010  # Sound signal
    ID_CPAPPRESSUREPARAMETERS = 0x1100  # CPAPparameters
    ID_CPAPPRESSUREVALUES = 0x1110  # CPAP page values

    ID_DICT = {ID_INVALID: "ID_INVALID",
               ID_SELECTEDPAGES: "ID_SELECTEDPAGES",
               ID_STAGES: "ID_STAGES",
               ID_CALCULATEDSTAGES: "ID_CALCULATEDSTAGES",
               ID_CALCSTAGESPARAMETERS: "ID_CALCSTAGESPARAMETERS",
               ID_EVENTS: "ID_EVENTS",
               ID_NOTES: "ID_NOTES",
               ID_ECGPARAMETERS: "ID_ECGPARAMETERS",
               ID_ECGRATE: "ID_ECGRATE",
               ID_ECGWAVE: "ID_ECGWAVE",
               ID_ECGRHYTHM: "ID_ECGRHYTHM",
               ID_RESPIRATIONPARAMETERS: "ID_RESPIRATIONPARAMETERS",
               ID_THORAXOLDHISTOGRAM: "ID_THORAXOLDHISTOGRAM",
               ID_ABDOMENOLDHISTOGRAM: "ID_ABDOMENOLDHISTOGRAM",
               ID_FLOWOLDHISTOGRAM: "ID_FLOWOLDHISTOGRAM",
               ID_THORAXHISTOGRAM: "ID_THORAXHISTOGRAM",
               ID_ABDOMENHISTOGRAM: "ID_ABDOMENHISTOGRAM",
               ID_FLOWHISTOGRAM: "ID_FLOWHISTOGRAM",
               ID_RESPIRATIONRATE: "ID_RESPIRATIONRATE",
               ID_SATURATIONPARAMETERS: "ID_SATURATIONPARAMETERS",
               ID_SATURATIONRATE: "ID_SATURATIONRATE",
               ID_SATURATIONSIGNAL: "ID_SATURATIONSIGNAL",
               ID_EMGPARAMETERS: "ID_EMGPARAMETERS",
               ID_EMGCHINSIGNAL: "ID_EMGCHINSIGNAL",
               ID_EMGTIBIALSIGNAL_01: "ID_EMGTIBIALSIGNAL_01",
               ID_EMGTIBIALSIGNAL_02: "ID_EMGTIBIALSIGNAL_02",
               ID_EMGTIBIALSIGNAL_03: "ID_EMGTIBIALSIGNAL_03",
               ID_EMGTIBIALSIGNAL_04: "ID_EMGTIBIALSIGNAL_04",
               ID_EMGTIBIALSIGNAL_05: "ID_EMGTIBIALSIGNAL_05",
               ID_EMGTIBIALSIGNAL_06: "ID_EMGTIBIALSIGNAL_06",
               ID_EMGTIBIALSIGNAL_07: "ID_EMGTIBIALSIGNAL_07",
               ID_EMGTIBIALSIGNAL_08: "ID_EMGTIBIALSIGNAL_08",
               ID_EMGTIBIALSIGNAL_09: "ID_EMGTIBIALSIGNAL_09",
               ID_EMGTIBIALSIGNAL_10: "ID_EMGTIBIALSIGNAL_10",
               ID_EMGTIBIALSIGNAL_11: "ID_EMGTIBIALSIGNAL_11",
               ID_EMGTIBIALSIGNAL_12: "ID_EMGTIBIALSIGNAL_12",
               ID_EMGTIBIALSIGNAL_13: "ID_EMGTIBIALSIGNAL_13",
               ID_EMGTIBIALSIGNAL_14: "ID_EMGTIBIALSIGNAL_14",
               ID_EMGTIBIALSIGNAL_15: "ID_EMGTIBIALSIGNAL_15",
               ID_EMGTIBIALSIGNAL_16: "ID_EMGTIBIALSIGNAL_16",
               ID_EMGTIBIALSIGNAL_17: "ID_EMGTIBIALSIGNAL_17",
               ID_EMGTIBIALSIGNAL_18: "ID_EMGTIBIALSIGNAL_18",
               ID_EMGTIBIALSIGNAL_19: "ID_EMGTIBIALSIGNAL_19",
               ID_EMGTIBIALSIGNAL_20: "ID_EMGTIBIALSIGNAL_20",
               ID_EMGTIBIALSIGNAL_21: "ID_EMGTIBIALSIGNAL_21",
               ID_EMGTIBIALSIGNAL_22: "ID_EMGTIBIALSIGNAL_22",
               ID_EMGTIBIALSIGNAL_23: "ID_EMGTIBIALSIGNAL_23",
               ID_EMGTIBIALSIGNAL_24: "ID_EMGTIBIALSIGNAL_24",
               ID_EMGTIBIALSIGNAL_25: "ID_EMGTIBIALSIGNAL_25",
               ID_EMGTIBIALSIGNAL_26: "ID_EMGTIBIALSIGNAL_26",
               ID_EMGTIBIALSIGNAL_27: "ID_EMGTIBIALSIGNAL_27",
               ID_EMGTIBIALSIGNAL_28: "ID_EMGTIBIALSIGNAL_28",
               ID_EMGTIBIALSIGNAL_29: "ID_EMGTIBIALSIGNAL_29",
               ID_EMGTIBIALSIGNAL_30: "ID_EMGTIBIALSIGNAL_30",
               ID_EMGTIBIALSIGNAL_31: "ID_EMGTIBIALSIGNAL_31",
               ID_EMGTIBIALSIGNAL_32: "ID_EMGTIBIALSIGNAL_32",
               ID_EEGDELTAPARAMETERS: "ID_EEGDELTAPARAMETERS",
               ID_EEGDELTAHISTOGRAM_01: "ID_EEGDELTAHISTOGRAM_01",
               ID_EEGDELTAHISTOGRAM_02: "ID_EEGDELTAHISTOGRAM_02",
               ID_EEGDELTAHISTOGRAM_03: "ID_EEGDELTAHISTOGRAM_03",
               ID_EEGDELTAHISTOGRAM_04: "ID_EEGDELTAHISTOGRAM_04",
               ID_EEGDELTAHISTOGRAM_05: "ID_EEGDELTAHISTOGRAM_05",
               ID_EEGDELTAHISTOGRAM_06: "ID_EEGDELTAHISTOGRAM_06",
               ID_EEGDELTAHISTOGRAM_07: "ID_EEGDELTAHISTOGRAM_07",
               ID_EEGDELTAHISTOGRAM_08: "ID_EEGDELTAHISTOGRAM_08",
               ID_EEGDELTAHISTOGRAM_09: "ID_EEGDELTAHISTOGRAM_09",
               ID_EEGDELTAHISTOGRAM_10: "ID_EEGDELTAHISTOGRAM_10",
               ID_EEGDELTAHISTOGRAM_11: "ID_EEGDELTAHISTOGRAM_11",
               ID_EEGDELTAHISTOGRAM_12: "ID_EEGDELTAHISTOGRAM_12",
               ID_EEGDELTAHISTOGRAM_13: "ID_EEGDELTAHISTOGRAM_13",
               ID_EEGDELTAHISTOGRAM_14: "ID_EEGDELTAHISTOGRAM_14",
               ID_EEGDELTAHISTOGRAM_15: "ID_EEGDELTAHISTOGRAM_15",
               ID_EEGDELTAHISTOGRAM_16: "ID_EEGDELTAHISTOGRAM_16",
               ID_EEGDELTAHISTOGRAM_17: "ID_EEGDELTAHISTOGRAM_17",
               ID_EEGDELTAHISTOGRAM_18: "ID_EEGDELTAHISTOGRAM_18",
               ID_EEGDELTAHISTOGRAM_19: "ID_EEGDELTAHISTOGRAM_19",
               ID_EEGDELTAHISTOGRAM_20: "ID_EEGDELTAHISTOGRAM_20",
               ID_EEGDELTAHISTOGRAM_21: "ID_EEGDELTAHISTOGRAM_21",
               ID_EEGDELTAHISTOGRAM_22: "ID_EEGDELTAHISTOGRAM_22",
               ID_EEGDELTAHISTOGRAM_23: "ID_EEGDELTAHISTOGRAM_23",
               ID_EEGDELTAHISTOGRAM_24: "ID_EEGDELTAHISTOGRAM_24",
               ID_EEGDELTAHISTOGRAM_25: "ID_EEGDELTAHISTOGRAM_25",
               ID_EEGDELTAHISTOGRAM_26: "ID_EEGDELTAHISTOGRAM_26",
               ID_EEGDELTAHISTOGRAM_27: "ID_EEGDELTAHISTOGRAM_27",
               ID_EEGDELTAHISTOGRAM_28: "ID_EEGDELTAHISTOGRAM_28",
               ID_EEGDELTAHISTOGRAM_29: "ID_EEGDELTAHISTOGRAM_29",
               ID_EEGDELTAHISTOGRAM_30: "ID_EEGDELTAHISTOGRAM_30",
               ID_EEGDELTAHISTOGRAM_31: "ID_EEGDELTAHISTOGRAM_31",
               ID_EEGDELTAHISTOGRAM_32: "ID_EEGDELTAHISTOGRAM_32",
               ID_EEGDELTAPERCENTAGE_01: "ID_EEGDELTAPERCENTAGE_01",
               ID_EEGDELTAPERCENTAGE_02: "ID_EEGDELTAPERCENTAGE_02",
               ID_EEGDELTAPERCENTAGE_03: "ID_EEGDELTAPERCENTAGE_03",
               ID_EEGDELTAPERCENTAGE_04: "ID_EEGDELTAPERCENTAGE_04",
               ID_EEGDELTAPERCENTAGE_05: "ID_EEGDELTAPERCENTAGE_05",
               ID_EEGDELTAPERCENTAGE_06: "ID_EEGDELTAPERCENTAGE_06",
               ID_EEGDELTAPERCENTAGE_07: "ID_EEGDELTAPERCENTAGE_07",
               ID_EEGDELTAPERCENTAGE_08: "ID_EEGDELTAPERCENTAGE_08",
               ID_EEGDELTAPERCENTAGE_09: "ID_EEGDELTAPERCENTAGE_09",
               ID_EEGDELTAPERCENTAGE_10: "ID_EEGDELTAPERCENTAGE_10",
               ID_EEGDELTAPERCENTAGE_11: "ID_EEGDELTAPERCENTAGE_11",
               ID_EEGDELTAPERCENTAGE_12: "ID_EEGDELTAPERCENTAGE_12",
               ID_EEGDELTAPERCENTAGE_13: "ID_EEGDELTAPERCENTAGE_13",
               ID_EEGDELTAPERCENTAGE_14: "ID_EEGDELTAPERCENTAGE_14",
               ID_EEGDELTAPERCENTAGE_15: "ID_EEGDELTAPERCENTAGE_15",
               ID_EEGDELTAPERCENTAGE_16: "ID_EEGDELTAPERCENTAGE_16",
               ID_EEGDELTAPERCENTAGE_17: "ID_EEGDELTAPERCENTAGE_17",
               ID_EEGDELTAPERCENTAGE_18: "ID_EEGDELTAPERCENTAGE_18",
               ID_EEGDELTAPERCENTAGE_19: "ID_EEGDELTAPERCENTAGE_19",
               ID_EEGDELTAPERCENTAGE_20: "ID_EEGDELTAPERCENTAGE_20",
               ID_EEGDELTAPERCENTAGE_21: "ID_EEGDELTAPERCENTAGE_21",
               ID_EEGDELTAPERCENTAGE_22: "ID_EEGDELTAPERCENTAGE_22",
               ID_EEGDELTAPERCENTAGE_23: "ID_EEGDELTAPERCENTAGE_23",
               ID_EEGDELTAPERCENTAGE_24: "ID_EEGDELTAPERCENTAGE_24",
               ID_EEGDELTAPERCENTAGE_25: "ID_EEGDELTAPERCENTAGE_25",
               ID_EEGDELTAPERCENTAGE_26: "ID_EEGDELTAPERCENTAGE_26",
               ID_EEGDELTAPERCENTAGE_27: "ID_EEGDELTAPERCENTAGE_27",
               ID_EEGDELTAPERCENTAGE_28: "ID_EEGDELTAPERCENTAGE_28",
               ID_EEGDELTAPERCENTAGE_29: "ID_EEGDELTAPERCENTAGE_29",
               ID_EEGDELTAPERCENTAGE_30: "ID_EEGDELTAPERCENTAGE_30",
               ID_EEGDELTAPERCENTAGE_31: "ID_EEGDELTAPERCENTAGE_31",
               ID_EEGDELTAPERCENTAGE_32: "ID_EEGDELTAPERCENTAGE_32",
               ID_EEGDELTACOUNT_01: "ID_EEGDELTACOUNT_01",
               ID_EEGDELTACOUNT_02: "ID_EEGDELTACOUNT_02",
               ID_EEGDELTACOUNT_03: "ID_EEGDELTACOUNT_03",
               ID_EEGDELTACOUNT_04: "ID_EEGDELTACOUNT_04",
               ID_EEGDELTACOUNT_05: "ID_EEGDELTACOUNT_05",
               ID_EEGDELTACOUNT_06: "ID_EEGDELTACOUNT_06",
               ID_EEGDELTACOUNT_07: "ID_EEGDELTACOUNT_07",
               ID_EEGDELTACOUNT_08: "ID_EEGDELTACOUNT_08",
               ID_EEGDELTACOUNT_09: "ID_EEGDELTACOUNT_09",
               ID_EEGDELTACOUNT_10: "ID_EEGDELTACOUNT_10",
               ID_EEGDELTACOUNT_11: "ID_EEGDELTACOUNT_11",
               ID_EEGDELTACOUNT_12: "ID_EEGDELTACOUNT_12",
               ID_EEGDELTACOUNT_13: "ID_EEGDELTACOUNT_13",
               ID_EEGDELTACOUNT_14: "ID_EEGDELTACOUNT_14",
               ID_EEGDELTACOUNT_15: "ID_EEGDELTACOUNT_15",
               ID_EEGDELTACOUNT_16: "ID_EEGDELTACOUNT_16",
               ID_EEGDELTACOUNT_17: "ID_EEGDELTACOUNT_17",
               ID_EEGDELTACOUNT_18: "ID_EEGDELTACOUNT_18",
               ID_EEGDELTACOUNT_19: "ID_EEGDELTACOUNT_19",
               ID_EEGDELTACOUNT_20: "ID_EEGDELTACOUNT_20",
               ID_EEGDELTACOUNT_21: "ID_EEGDELTACOUNT_21",
               ID_EEGDELTACOUNT_22: "ID_EEGDELTACOUNT_22",
               ID_EEGDELTACOUNT_23: "ID_EEGDELTACOUNT_23",
               ID_EEGDELTACOUNT_24: "ID_EEGDELTACOUNT_24",
               ID_EEGDELTACOUNT_25: "ID_EEGDELTACOUNT_25",
               ID_EEGDELTACOUNT_26: "ID_EEGDELTACOUNT_26",
               ID_EEGDELTACOUNT_27: "ID_EEGDELTACOUNT_27",
               ID_EEGDELTACOUNT_28: "ID_EEGDELTACOUNT_28",
               ID_EEGDELTACOUNT_29: "ID_EEGDELTACOUNT_29",
               ID_EEGDELTACOUNT_30: "ID_EEGDELTACOUNT_30",
               ID_EEGDELTACOUNT_31: "ID_EEGDELTACOUNT_31",
               ID_EEGDELTACOUNT_32: "ID_EEGDELTACOUNT_32",
               ID_EEGSPINDLEPARAMETERS: "ID_EEGSPINDLEPARAMETERS",
               ID_EEGSPINDLEHISTOGRAM_01: "ID_EEGSPINDLEHISTOGRAM_01",
               ID_EEGSPINDLEHISTOGRAM_02: "ID_EEGSPINDLEHISTOGRAM_02",
               ID_EEGSPINDLEHISTOGRAM_03: "ID_EEGSPINDLEHISTOGRAM_03",
               ID_EEGSPINDLEHISTOGRAM_04: "ID_EEGSPINDLEHISTOGRAM_04",
               ID_EEGSPINDLEHISTOGRAM_05: "ID_EEGSPINDLEHISTOGRAM_05",
               ID_EEGSPINDLEHISTOGRAM_06: "ID_EEGSPINDLEHISTOGRAM_06",
               ID_EEGSPINDLEHISTOGRAM_07: "ID_EEGSPINDLEHISTOGRAM_07",
               ID_EEGSPINDLEHISTOGRAM_08: "ID_EEGSPINDLEHISTOGRAM_08",
               ID_EEGSPINDLEHISTOGRAM_09: "ID_EEGSPINDLEHISTOGRAM_09",
               ID_EEGSPINDLEHISTOGRAM_10: "ID_EEGSPINDLEHISTOGRAM_10",
               ID_EEGSPINDLEHISTOGRAM_11: "ID_EEGSPINDLEHISTOGRAM_11",
               ID_EEGSPINDLEHISTOGRAM_12: "ID_EEGSPINDLEHISTOGRAM_12",
               ID_EEGSPINDLEHISTOGRAM_13: "ID_EEGSPINDLEHISTOGRAM_13",
               ID_EEGSPINDLEHISTOGRAM_14: "ID_EEGSPINDLEHISTOGRAM_14",
               ID_EEGSPINDLEHISTOGRAM_15: "ID_EEGSPINDLEHISTOGRAM_15",
               ID_EEGSPINDLEHISTOGRAM_16: "ID_EEGSPINDLEHISTOGRAM_16",
               ID_EEGSPINDLEHISTOGRAM_17: "ID_EEGSPINDLEHISTOGRAM_17",
               ID_EEGSPINDLEHISTOGRAM_18: "ID_EEGSPINDLEHISTOGRAM_18",
               ID_EEGSPINDLEHISTOGRAM_19: "ID_EEGSPINDLEHISTOGRAM_19",
               ID_EEGSPINDLEHISTOGRAM_20: "ID_EEGSPINDLEHISTOGRAM_20",
               ID_EEGSPINDLEHISTOGRAM_21: "ID_EEGSPINDLEHISTOGRAM_21",
               ID_EEGSPINDLEHISTOGRAM_22: "ID_EEGSPINDLEHISTOGRAM_22",
               ID_EEGSPINDLEHISTOGRAM_23: "ID_EEGSPINDLEHISTOGRAM_23",
               ID_EEGSPINDLEHISTOGRAM_24: "ID_EEGSPINDLEHISTOGRAM_24",
               ID_EEGSPINDLEHISTOGRAM_25: "ID_EEGSPINDLEHISTOGRAM_25",
               ID_EEGSPINDLEHISTOGRAM_26: "ID_EEGSPINDLEHISTOGRAM_26",
               ID_EEGSPINDLEHISTOGRAM_27: "ID_EEGSPINDLEHISTOGRAM_27",
               ID_EEGSPINDLEHISTOGRAM_28: "ID_EEGSPINDLEHISTOGRAM_28",
               ID_EEGSPINDLEHISTOGRAM_29: "ID_EEGSPINDLEHISTOGRAM_29",
               ID_EEGSPINDLEHISTOGRAM_30: "ID_EEGSPINDLEHISTOGRAM_30",
               ID_EEGSPINDLEHISTOGRAM_31: "ID_EEGSPINDLEHISTOGRAM_31",
               ID_EEGSPINDLEHISTOGRAM_32: "ID_EEGSPINDLEHISTOGRAM_32",
               ID_EEGALPHAOLDPARAMETERS: "ID_EEGALPHAOLDPARAMETERS",
               ID_EEGALPHASIGNAL_01: "ID_EEGALPHASIGNAL_01",
               ID_EEGALPHASIGNAL_02: "ID_EEGALPHASIGNAL_02",
               ID_EEGALPHASIGNAL_03: "ID_EEGALPHASIGNAL_03",
               ID_EEGALPHASIGNAL_04: "ID_EEGALPHASIGNAL_04",
               ID_EEGALPHASIGNAL_05: "ID_EEGALPHASIGNAL_05",
               ID_EEGALPHASIGNAL_06: "ID_EEGALPHASIGNAL_06",
               ID_EEGALPHASIGNAL_07: "ID_EEGALPHASIGNAL_07",
               ID_EEGALPHASIGNAL_08: "ID_EEGALPHASIGNAL_08",
               ID_EEGALPHASIGNAL_09: "ID_EEGALPHASIGNAL_09",
               ID_EEGALPHASIGNAL_10: "ID_EEGALPHASIGNAL_10",
               ID_EEGALPHASIGNAL_11: "ID_EEGALPHASIGNAL_11",
               ID_EEGALPHASIGNAL_12: "ID_EEGALPHASIGNAL_12",
               ID_EEGALPHASIGNAL_13: "ID_EEGALPHASIGNAL_13",
               ID_EEGALPHASIGNAL_14: "ID_EEGALPHASIGNAL_14",
               ID_EEGALPHASIGNAL_15: "ID_EEGALPHASIGNAL_15",
               ID_EEGALPHASIGNAL_16: "ID_EEGALPHASIGNAL_16",
               ID_EEGALPHASIGNAL_17: "ID_EEGALPHASIGNAL_17",
               ID_EEGALPHASIGNAL_18: "ID_EEGALPHASIGNAL_18",
               ID_EEGALPHASIGNAL_19: "ID_EEGALPHASIGNAL_19",
               ID_EEGALPHASIGNAL_20: "ID_EEGALPHASIGNAL_20",
               ID_EEGALPHASIGNAL_21: "ID_EEGALPHASIGNAL_21",
               ID_EEGALPHASIGNAL_22: "ID_EEGALPHASIGNAL_22",
               ID_EEGALPHASIGNAL_23: "ID_EEGALPHASIGNAL_23",
               ID_EEGALPHASIGNAL_24: "ID_EEGALPHASIGNAL_24",
               ID_EEGALPHASIGNAL_25: "ID_EEGALPHASIGNAL_25",
               ID_EEGALPHASIGNAL_26: "ID_EEGALPHASIGNAL_26",
               ID_EEGALPHASIGNAL_27: "ID_EEGALPHASIGNAL_27",
               ID_EEGALPHASIGNAL_28: "ID_EEGALPHASIGNAL_28",
               ID_EEGALPHASIGNAL_29: "ID_EEGALPHASIGNAL_29",
               ID_EEGALPHASIGNAL_30: "ID_EEGALPHASIGNAL_30",
               ID_EEGALPHASIGNAL_31: "ID_EEGALPHASIGNAL_31",
               ID_EEGALPHASIGNAL_32: "ID_EEGALPHASIGNAL_32",
               ID_EEGALPHAPARAMETERS: "ID_EEGALPHAPARAMETERS",
               ID_EEGALPHAHISTOGRAM_01: "ID_EEGALPHAHISTOGRAM_01",
               ID_EEGALPHAHISTOGRAM_02: "ID_EEGALPHAHISTOGRAM_02",
               ID_EEGALPHAHISTOGRAM_03: "ID_EEGALPHAHISTOGRAM_03",
               ID_EEGALPHAHISTOGRAM_04: "ID_EEGALPHAHISTOGRAM_04",
               ID_EEGALPHAHISTOGRAM_05: "ID_EEGALPHAHISTOGRAM_05",
               ID_EEGALPHAHISTOGRAM_06: "ID_EEGALPHAHISTOGRAM_06",
               ID_EEGALPHAHISTOGRAM_07: "ID_EEGALPHAHISTOGRAM_07",
               ID_EEGALPHAHISTOGRAM_08: "ID_EEGALPHAHISTOGRAM_08",
               ID_EEGALPHAHISTOGRAM_09: "ID_EEGALPHAHISTOGRAM_09",
               ID_EEGALPHAHISTOGRAM_10: "ID_EEGALPHAHISTOGRAM_10",
               ID_EEGALPHAHISTOGRAM_11: "ID_EEGALPHAHISTOGRAM_11",
               ID_EEGALPHAHISTOGRAM_12: "ID_EEGALPHAHISTOGRAM_12",
               ID_EEGALPHAHISTOGRAM_13: "ID_EEGALPHAHISTOGRAM_13",
               ID_EEGALPHAHISTOGRAM_14: "ID_EEGALPHAHISTOGRAM_14",
               ID_EEGALPHAHISTOGRAM_15: "ID_EEGALPHAHISTOGRAM_15",
               ID_EEGALPHAHISTOGRAM_16: "ID_EEGALPHAHISTOGRAM_16",
               ID_EEGALPHAHISTOGRAM_17: "ID_EEGALPHAHISTOGRAM_17",
               ID_EEGALPHAHISTOGRAM_18: "ID_EEGALPHAHISTOGRAM_18",
               ID_EEGALPHAHISTOGRAM_19: "ID_EEGALPHAHISTOGRAM_19",
               ID_EEGALPHAHISTOGRAM_20: "ID_EEGALPHAHISTOGRAM_20",
               ID_EEGALPHAHISTOGRAM_21: "ID_EEGALPHAHISTOGRAM_21",
               ID_EEGALPHAHISTOGRAM_22: "ID_EEGALPHAHISTOGRAM_22",
               ID_EEGALPHAHISTOGRAM_23: "ID_EEGALPHAHISTOGRAM_23",
               ID_EEGALPHAHISTOGRAM_24: "ID_EEGALPHAHISTOGRAM_24",
               ID_EEGALPHAHISTOGRAM_25: "ID_EEGALPHAHISTOGRAM_25",
               ID_EEGALPHAHISTOGRAM_26: "ID_EEGALPHAHISTOGRAM_26",
               ID_EEGALPHAHISTOGRAM_27: "ID_EEGALPHAHISTOGRAM_27",
               ID_EEGALPHAHISTOGRAM_28: "ID_EEGALPHAHISTOGRAM_28",
               ID_EEGALPHAHISTOGRAM_29: "ID_EEGALPHAHISTOGRAM_29",
               ID_EEGALPHAHISTOGRAM_30: "ID_EEGALPHAHISTOGRAM_30",
               ID_EEGALPHAHISTOGRAM_31: "ID_EEGALPHAHISTOGRAM_31",
               ID_EEGALPHAHISTOGRAM_32: "ID_EEGALPHAHISTOGRAM_32",
               ID_EEGALPHAPERCENTAGE_01: "ID_EEGALPHAPERCENTAGE_01",
               ID_EEGALPHAPERCENTAGE_02: "ID_EEGALPHAPERCENTAGE_02",
               ID_EEGALPHAPERCENTAGE_03: "ID_EEGALPHAPERCENTAGE_03",
               ID_EEGALPHAPERCENTAGE_04: "ID_EEGALPHAPERCENTAGE_04",
               ID_EEGALPHAPERCENTAGE_05: "ID_EEGALPHAPERCENTAGE_05",
               ID_EEGALPHAPERCENTAGE_06: "ID_EEGALPHAPERCENTAGE_06",
               ID_EEGALPHAPERCENTAGE_07: "ID_EEGALPHAPERCENTAGE_07",
               ID_EEGALPHAPERCENTAGE_08: "ID_EEGALPHAPERCENTAGE_08",
               ID_EEGALPHAPERCENTAGE_09: "ID_EEGALPHAPERCENTAGE_09",
               ID_EEGALPHAPERCENTAGE_10: "ID_EEGALPHAPERCENTAGE_10",
               ID_EEGALPHAPERCENTAGE_11: "ID_EEGALPHAPERCENTAGE_11",
               ID_EEGALPHAPERCENTAGE_12: "ID_EEGALPHAPERCENTAGE_12",
               ID_EEGALPHAPERCENTAGE_13: "ID_EEGALPHAPERCENTAGE_13",
               ID_EEGALPHAPERCENTAGE_14: "ID_EEGALPHAPERCENTAGE_14",
               ID_EEGALPHAPERCENTAGE_15: "ID_EEGALPHAPERCENTAGE_15",
               ID_EEGALPHAPERCENTAGE_16: "ID_EEGALPHAPERCENTAGE_16",
               ID_EEGALPHAPERCENTAGE_17: "ID_EEGALPHAPERCENTAGE_17",
               ID_EEGALPHAPERCENTAGE_18: "ID_EEGALPHAPERCENTAGE_18",
               ID_EEGALPHAPERCENTAGE_19: "ID_EEGALPHAPERCENTAGE_19",
               ID_EEGALPHAPERCENTAGE_20: "ID_EEGALPHAPERCENTAGE_20",
               ID_EEGALPHAPERCENTAGE_21: "ID_EEGALPHAPERCENTAGE_21",
               ID_EEGALPHAPERCENTAGE_22: "ID_EEGALPHAPERCENTAGE_22",
               ID_EEGALPHAPERCENTAGE_23: "ID_EEGALPHAPERCENTAGE_23",
               ID_EEGALPHAPERCENTAGE_24: "ID_EEGALPHAPERCENTAGE_24",
               ID_EEGALPHAPERCENTAGE_25: "ID_EEGALPHAPERCENTAGE_25",
               ID_EEGALPHAPERCENTAGE_26: "ID_EEGALPHAPERCENTAGE_26",
               ID_EEGALPHAPERCENTAGE_27: "ID_EEGALPHAPERCENTAGE_27",
               ID_EEGALPHAPERCENTAGE_28: "ID_EEGALPHAPERCENTAGE_28",
               ID_EEGALPHAPERCENTAGE_29: "ID_EEGALPHAPERCENTAGE_29",
               ID_EEGALPHAPERCENTAGE_30: "ID_EEGALPHAPERCENTAGE_30",
               ID_EEGALPHAPERCENTAGE_31: "ID_EEGALPHAPERCENTAGE_31",
               ID_EEGALPHAPERCENTAGE_32: "ID_EEGALPHAPERCENTAGE_32",
               ID_EOGPARAMETERS: "ID_EOGPARAMETERS",
               ID_EOGREMHISTOGRAM_01: "ID_EOGREMHISTOGRAM_01",
               ID_EOGREMHISTOGRAM_02: "ID_EOGREMHISTOGRAM_02",
               ID_EOGREMCOUNT_01: "ID_EOGREMCOUNT_01",
               ID_EOGREMCOUNT_02: "ID_EOGREMCOUNT_02",
               ID_EOGSEMHISTOGRAM: "ID_EOGSEMHISTOGRAM",
               ID_EOGSEMCOUNT: "ID_EOGSEMCOUNT",
               ID_EOGBLINKCOUNT_01: "ID_EOGBLINKCOUNT_01",
               ID_EOGBLINKCOUNT_02: "ID_EOGBLINKCOUNT_02",
               ID_EEGTHETAPARAMETERS: "ID_EEGTHETAPARAMETERS",
               ID_EEGTHETASIGNAL_01: "ID_EEGTHETASIGNAL_01",
               ID_EEGTHETASIGNAL_02: "ID_EEGTHETASIGNAL_02",
               ID_EEGTHETASIGNAL_03: "ID_EEGTHETASIGNAL_03",
               ID_EEGTHETASIGNAL_04: "ID_EEGTHETASIGNAL_04",
               ID_EEGTHETASIGNAL_05: "ID_EEGTHETASIGNAL_05",
               ID_EEGTHETASIGNAL_06: "ID_EEGTHETASIGNAL_06",
               ID_EEGTHETASIGNAL_07: "ID_EEGTHETASIGNAL_07",
               ID_EEGTHETASIGNAL_08: "ID_EEGTHETASIGNAL_08",
               ID_EEGTHETASIGNAL_09: "ID_EEGTHETASIGNAL_09",
               ID_EEGTHETASIGNAL_10: "ID_EEGTHETASIGNAL_10",
               ID_EEGTHETASIGNAL_11: "ID_EEGTHETASIGNAL_11",
               ID_EEGTHETASIGNAL_12: "ID_EEGTHETASIGNAL_12",
               ID_EEGTHETASIGNAL_13: "ID_EEGTHETASIGNAL_13",
               ID_EEGTHETASIGNAL_14: "ID_EEGTHETASIGNAL_14",
               ID_EEGTHETASIGNAL_15: "ID_EEGTHETASIGNAL_15",
               ID_EEGTHETASIGNAL_16: "ID_EEGTHETASIGNAL_16",
               ID_EEGTHETASIGNAL_17: "ID_EEGTHETASIGNAL_17",
               ID_EEGTHETASIGNAL_18: "ID_EEGTHETASIGNAL_18",
               ID_EEGTHETASIGNAL_19: "ID_EEGTHETASIGNAL_19",
               ID_EEGTHETASIGNAL_20: "ID_EEGTHETASIGNAL_20",
               ID_EEGTHETASIGNAL_21: "ID_EEGTHETASIGNAL_21",
               ID_EEGTHETASIGNAL_22: "ID_EEGTHETASIGNAL_22",
               ID_EEGTHETASIGNAL_23: "ID_EEGTHETASIGNAL_23",
               ID_EEGTHETASIGNAL_24: "ID_EEGTHETASIGNAL_24",
               ID_EEGTHETASIGNAL_25: "ID_EEGTHETASIGNAL_25",
               ID_EEGTHETASIGNAL_26: "ID_EEGTHETASIGNAL_26",
               ID_EEGTHETASIGNAL_27: "ID_EEGTHETASIGNAL_27",
               ID_EEGTHETASIGNAL_28: "ID_EEGTHETASIGNAL_28",
               ID_EEGTHETASIGNAL_29: "ID_EEGTHETASIGNAL_29",
               ID_EEGTHETASIGNAL_30: "ID_EEGTHETASIGNAL_30",
               ID_EEGTHETASIGNAL_31: "ID_EEGTHETASIGNAL_31",
               ID_EEGTHETASIGNAL_32: "ID_EEGTHETASIGNAL_32",
               ID_EEGBETAPARAMETERS: "ID_EEGBETAPARAMETERS",
               ID_EEGBETASIGNAL_01: "ID_EEGBETASIGNAL_01",
               ID_EEGBETASIGNAL_02: "ID_EEGBETASIGNAL_02",
               ID_EEGBETASIGNAL_03: "ID_EEGBETASIGNAL_03",
               ID_EEGBETASIGNAL_04: "ID_EEGBETASIGNAL_04",
               ID_EEGBETASIGNAL_05: "ID_EEGBETASIGNAL_05",
               ID_EEGBETASIGNAL_06: "ID_EEGBETASIGNAL_06",
               ID_EEGBETASIGNAL_07: "ID_EEGBETASIGNAL_07",
               ID_EEGBETASIGNAL_08: "ID_EEGBETASIGNAL_08",
               ID_EEGBETASIGNAL_09: "ID_EEGBETASIGNAL_09",
               ID_EEGBETASIGNAL_10: "ID_EEGBETASIGNAL_10",
               ID_EEGBETASIGNAL_11: "ID_EEGBETASIGNAL_11",
               ID_EEGBETASIGNAL_12: "ID_EEGBETASIGNAL_12",
               ID_EEGBETASIGNAL_13: "ID_EEGBETASIGNAL_13",
               ID_EEGBETASIGNAL_14: "ID_EEGBETASIGNAL_14",
               ID_EEGBETASIGNAL_15: "ID_EEGBETASIGNAL_15",
               ID_EEGBETASIGNAL_16: "ID_EEGBETASIGNAL_16",
               ID_EEGBETASIGNAL_17: "ID_EEGBETASIGNAL_17",
               ID_EEGBETASIGNAL_18: "ID_EEGBETASIGNAL_18",
               ID_EEGBETASIGNAL_19: "ID_EEGBETASIGNAL_19",
               ID_EEGBETASIGNAL_20: "ID_EEGBETASIGNAL_20",
               ID_EEGBETASIGNAL_21: "ID_EEGBETASIGNAL_21",
               ID_EEGBETASIGNAL_22: "ID_EEGBETASIGNAL_22",
               ID_EEGBETASIGNAL_23: "ID_EEGBETASIGNAL_23",
               ID_EEGBETASIGNAL_24: "ID_EEGBETASIGNAL_24",
               ID_EEGBETASIGNAL_25: "ID_EEGBETASIGNAL_25",
               ID_EEGBETASIGNAL_26: "ID_EEGBETASIGNAL_26",
               ID_EEGBETASIGNAL_27: "ID_EEGBETASIGNAL_27",
               ID_EEGBETASIGNAL_28: "ID_EEGBETASIGNAL_28",
               ID_EEGBETASIGNAL_29: "ID_EEGBETASIGNAL_29",
               ID_EEGBETASIGNAL_30: "ID_EEGBETASIGNAL_30",
               ID_EEGBETASIGNAL_31: "ID_EEGBETASIGNAL_31",
               ID_EEGBETASIGNAL_32: "ID_EEGBETASIGNAL_32",
               ID_BODYPOSPARAMETERS: "ID_BODYPOSPARAMETERS",
               ID_SOUNDPARAMETERS: "ID_SOUNDPARAMETERS",
               ID_SOUND: "ID_SOUND",
               ID_CPAPPRESSUREPARAMETERS: "ID_CPAPPRESSUREPARAMETERS",
               ID_CPAPPRESSUREVALUES: "ID_CPAPPRESSUREVALUES"}

    def __init__(self, item_id=0, offset=0, size=0):
        self.item_id = item_id
        self.offset = offset
        self.size = size


def read_file_inventory(sf):
    sf.seek(10)
    inventory = []
    append = inventory.append
    inv_struct = struct.Struct("<hlL")
    for i in range(1, 129):
        ib = inv_struct.unpack(sf.read(inv_struct.size))
        append(InventoryItem(ib[0], ib[1], ib[2]))
    return inventory


class StageType:
    def __init__(self, desc="", label="", value=0, value_type=0):
        self.desc = desc
        self.label = label
        self.value = value
        self.value_type = value_type


def decode_stage_type(val, stage_defs):
    if val in stage_defs:
        return stage_defs[val]
    return StageType("INVALID", "INVALID", 0, 0)


def read_stage_types(sf):
    types = {}
    ssize = 12
    int16 = struct.Struct("<h")
    tcount = int16.unpack(sf.read(int16.size))[0]

    ds = "".join(repeat("20s", ssize))
    ls = "".join(repeat("6s", ssize))
    vs = "<%dh" % ssize

    dstruct = struct.Struct(ds)
    descs = dstruct.unpack(sf.read(dstruct.size))
    lstruct = struct.Struct(ls)
    labels = lstruct.unpack(sf.read(lstruct.size))
    vstruct = struct.Struct(vs)
    values = vstruct.unpack(sf.read(vstruct.size))
    for i in range(tcount):
        valbytes = values[i].to_bytes(2, byteorder='big')
        val = valbytes[1]
        valtype = valbytes[0]
        types[val] = StageType(string_trim_to_0(descs[i]), string_trim_to_0(labels[i]), val, valtype)
    return types


class Stage:
    def __init__(self, no, time, val, label, val_type):
        self.no = no
        self.time = time
        self.val = val
        self.label = label
        self.val_type = val_type


def get_wake_values(stage_defs):
    return [x.value for x in stage_defs.values() if (x.value_type == 1)]


def get_sleep_values(stage_defs):
    return [x.value for x in stage_defs.values() if (x.value_type in [2, 3])]


def get_rem_values(stage_defs):
    return [x.value for x in stage_defs.values() if (x.value_type == 2)]


def get_non_rem_values(stage_defs):
    return [x.value for x in stage_defs.values() if (x.value_type == 3)]


def read_stages(sf, offset, size):
    sf.seek(offset)
    int16 = struct.Struct("<h")
    tcount = int16.unpack(sf.read(int16.size))[0]
    currsize = int16.size + tcount
    if currsize > size:
        pass
    stgs = sf.read(tcount)
    return stgs


LBL_DICT = {"INVALID": "INVALID", "Wake": "W", "MT": "MT", "S 1": "N1", "S 2": "N2", "S 3": "N3", "S 4": "N4",
            "REM": "R"}


def transform_stages(stgs, stage_defs, recording_events):
    stages = []
    append = stages.append
    j = 0
    for i in stgs:
        j += 1
        stgdef = decode_stage_type(i, stage_defs)
        recording_event = find_recording_event(j, recording_events)
        if recording_event is not None:
            tm = add_seconds_to_time(recording_event.start_time, (j - recording_event.start_page) * 30)
            append(Stage(j, tm, i, LBL_DICT[stgdef.label], stgdef.value_type))
    return stages


def find_page_in_stages(page, stages):
    return next((x for x in stages if (x.no == page)), None)
