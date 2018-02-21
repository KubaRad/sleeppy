"""
Created on 02-10-2011

@author: Kuba Radliński
"""

import struct
import os
import numpy
from datetime import date, time
from sleeppy.psg.brainlab.utils import string_trim_to_0,  decode_time, decode_date
from psg.brainlab.events import Event, read_events, read_event_descs, get_selected_events_4_types


class SignalFile:
    def __init__(self):
        self.header = SignalHeader()
        self.data_table = DataTable()
        self.measurement = Measurement()
        self.recorder_info = RecorderMontageInfo()
        self.events = []
        self.events_desc = []
        self.store_events = 0
        self.signal_pages = []
        self.signal_data = []


def read_signal_file(file_name, read_signal_data):
    file_size = os.path.getsize(file_name)
    sf = open(file_name, 'rb')
    signal = SignalFile()
    try:
        signal.header = read_signal_header(sf)
        signal.data_table = read_data_table(sf)
        signal.measurement = read_measurement(sf, signal.data_table.measurement_info.offset, signal.data_table.measurement_info.size)
        signal.recorder_info = read_recorder_info(sf, signal.data_table.recorder_montage_info.offset,
                                                  signal.data_table.recorder_montage_info.size)
        signal.events = read_events(sf, signal.data_table.events_info.offset, signal.data_table.events_info.size, 2048)

        signal.events_desc = read_event_descs(sf)
        store_events_list = get_selected_events_4_types(signal.events, [Event.ET_SAVESKIPEVENT])
        signal.store_events = len(store_events_list)
        spages = read_signal_pages(sf, read_signal_data, file_size, signal.data_table.signal_info.offset, signal.data_table.signal_info.size, 30,
                                   signal.recorder_info.numberOfChannelsUsed, signal.recorder_info.channels)
        signal.signal_pages = spages[0]
        signal.signal_data = spages[1]
    finally:
        sf.close()
    return signal


class Block:
    def __init__(self, offset=0, size=0, header_size=0):
        self.offset = offset
        self.size = size
        self.header_size = header_size


class DataTable:
    def __init__(self):
        self.measurement_info = Block()
        self.recorder_montage_info = Block()
        self.events_info = Block()
        self.notes_info = Block()
        self.impedance_info = Block()
        self.display_montages_info = Block()
        self.stimulator_info = Block()
        self.signal_info = Block()


def read_data_table(sf):
    sf.seek((struct.Struct("<2l2h")).size)
    data_table = DataTable()
    dt_struct = struct.Struct("<17l")
    dt = dt_struct.unpack(sf.read(dt_struct.size))
    data_table.measurement_info = Block(dt[0], dt[1])
    data_table.recorder_montage_info = Block(dt[2], dt[3])
    data_table.events_info = Block(dt[4], dt[5])
    data_table.notes_info = Block(dt[6], dt[7])
    data_table.impedance_info = Block(dt[8], dt[9])
    data_table.display_montages_info = Block(dt[10], dt[11])
    data_table.stimulator_info = Block(dt[12], dt[13])
    data_table.signal_info = Block(dt[14], dt[15], dt[16])
    return data_table


class SignalHeader:
    PROGRAM_ID = 0x41545353
    SIGNAL_ID = 0x47495352
    SIGNAL_DUMMY_ID = 0x53464445

    def __init__(self, program_id=0, signal_id=0, version_id=0, read_only=0):
        self.program_id = program_id
        self.signal_id = signal_id
        self.version_id = version_id
        self.read_only = read_only

    def check_program_id(self):
        return self.program_id == SignalHeader.PROGRAM_ID

    def check_signal_id(self):
        return self.signal_id in (SignalHeader.SIGNAL_ID, SignalHeader.SIGNAL_DUMMY_ID)

    def check_header(self):
        return self.check_program_id() and self.check_signal_id()


def read_signal_header(sf):
    sf.seek(0)
    hs = struct.Struct("<2l2h")
    hb = hs.unpack(sf.read(hs.size))
    return SignalHeader(hb[0], hb[1], hb[2], hb[3])


class Measurement:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.street = ""
        self.zip_code = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.birthday = date(1900, 1, 1)
        self.sex = ""
        self.start_date = date(1900, 1, 1)
        self.start_hour = time(0, 0, 0)
        self.room = ""
        self.doctor = ""
        self.technician = ""
        self.class_code = ""
        self.clin_info = ""
        self.backup_flag = ""
        self.status_flags = 0
        self.archive_flag = ""
        self.vcr_timing_correction = 0
        self.referring_doctor_name = ""
        self.referring_doctor_code = ""
        self.weight = 0
        self.height = 0
        self.weight_unit = 0
        self.height_unit = 0
        self.protocol = ""
        self.maximum_voltage = 0
        self.maximum_amplitude = 0


def read_measurement(sf, offset, size):
    def sexc(x):
        return {
            1: 'M',
            0: 'F'}.get(x)

    sf.seek(offset)
    meas_struct = struct.Struct("<17s33s33s17s33s33s33slh2l9s33s33s9s1963s1sh1sd33s33s4h33s2h")
    if meas_struct.size > size:
        pass
    ms = meas_struct.unpack(sf.read(meas_struct.size))
    measurement = Measurement()
    measurement.id = string_trim_to_0(ms[0])
    measurement.name = string_trim_to_0(ms[1])
    measurement.street = string_trim_to_0(ms[2])
    measurement.zip_code = string_trim_to_0(ms[3])
    measurement.city = string_trim_to_0(ms[4])
    measurement.state = string_trim_to_0(ms[5])
    measurement.country = string_trim_to_0(ms[6])
    measurement.birthday = decode_date(ms[7])
    measurement.sex = sexc(ms[8])
    measurement.start_date = decode_date(ms[9])
    measurement.start_hour = decode_time(ms[10])
    measurement.room = string_trim_to_0(ms[11])
    measurement.doctor = string_trim_to_0(ms[12])
    measurement.technician = string_trim_to_0(ms[13])
    measurement.class_code = string_trim_to_0(ms[14])
    measurement.clin_info = string_trim_to_0(ms[15])
    measurement.backup_flag = string_trim_to_0(ms[16])
    measurement.status_flags = ms[17]
    measurement.archive_flag = string_trim_to_0(ms[18])
    measurement.vcr_timing_correction = ms[19]
    measurement.referring_doctor_name = string_trim_to_0(ms[20])
    measurement.referring_doctor_code = string_trim_to_0(ms[21])
    measurement.weight = ms[22] / 10
    measurement.height = ms[23] / 100
    measurement.weight_unit = ms[24]
    measurement.height_unit = ms[25]
    measurement.protocol = string_trim_to_0(ms[26])
    measurement.maximum_voltage = ms[27]
    measurement.maximum_amplitude = ms[28]
    td_age = measurement.start_date - measurement.birthday
    measurement.age = td_age.days / 365.25

    return measurement


def create_fmt_strings(cl):
    return ['%'+str(cl.field_size[i])+(('.'+str(cl.field_decimal[i])) if cl.field_decimal[i]>0 else '')+cl.field_type[i] for i in range(len(cl.field_name))]


def create_title_fmts(cl):
    return ['%'+str(cl.field_size[i])+'s' for i in range(len(cl.field_name))]


def create_table_title(cl):
    return ('|'+'|'.join(create_title_fmts(cl))+'|') % tuple(cl.field_name)


def create_row_breaker(cl):
    return ('|'+'|'.join(create_title_fmts(cl))+'|') % tuple(['-'*x for x in cl.field_size])


def create_row(cl, data_tuple):
    return ('|'+'|'.join(create_fmt_strings(cl))+'|') % data_tuple


class RecorderChannel:
    field_name = ['Samp.', 'Type', 'Subtype', 'Desc', 'Sens', 'LF', 'HF', 'Delay', 'Unit', 'ArLv', 'Cal Type', 'Cal Fct.', 'Cal Off.', 'B.Size']
    field_type = ['d', 's', 's', 's', 'f', 'f', 'f', 'd', 's', 'd', 'd', 'f', 'f', 'd']
    field_size = [5, 8, 8, 8, 6, 6, 6, 5, 5, 5, 8, 10, 8, 6]
    field_decimal = [0, 0, 0, 0, 1, 3, 1, 0, 0, 0, 0, 8, 1, 0]

    def __init__(self, sampling_rate, signal_type, signal_sub_type, channel_desc, sensitivity_index, low_filter_index, high_filter_index, delay,
                 unit, artefact_level, cal_type, cal_factor, cal_offset, save_buffer_size):
        self.sampling_rate = sampling_rate
        self.signal_type = signal_type
        self.signal_sub_type = signal_sub_type
        self.channel_desc = channel_desc
        self.sensitivity_index = sensitivity_index
        self.low_filter_index = low_filter_index
        self.high_filter_index = high_filter_index
        self.delay = delay
        self.unit = unit
        self.artefact_level = artefact_level
        self.cal_type = cal_type
        self.cal_factor = cal_factor
        self.cal_offset = cal_offset
        self.save_buffer_size = save_buffer_size

    def create_data_tuple(self,sensitivity=None, low_filter=None, high_filter=None):
        return (self.sampling_rate, self.signal_type, self.signal_sub_type, self.channel_desc,
                sensitivity[self.sensitivity_index] if sensitivity is not None else self.sensitivity_index,
                low_filter[self.low_filter_index] if low_filter is not None else self.low_filter_index,
                high_filter[self.high_filter_index] if high_filter is not None else self.high_filter_index, self.delay,
                self.unit, self.artefact_level, self.cal_type, self.cal_factor, self.cal_offset, self.save_buffer_size)


class RecorderMontageInfo:
    def __init__(self):
        self.name = ""
        self.nRecChannels = 0
        self.invertedACChannels = 0
        self.maximumVoltage = 0
        self.normalVoltage = 0
        self.calibrationSignal = 0
        self.calibrationScale = 0
        self.videoControl = 0
        self.nSensitivities = 0
        self.nLowFilters = 0
        self.nHighFilters = 0
        self.sensitivity = []
        self.lowFilter = []
        self.highFilter = []
        self.montageName = ""
        self.numberOfChannelsUsed = 0
        self.globalSens = 0
        self.epochLengthInSamples = 0
        self.highestRate = 0
        self.channels = []
        self.parameter = 0
        self.displayMontageName = ""
        self.dispCh = []
        self.dispChScale = []
        self.electrode = []
        self.lead = []
        self.gain = []
        self.offset = []
        self.nChannelsOnDisplay = 0
        self.sampleMap = []
        self.dummy = []


def read_recorder_info(sf, offset, size):
    sf.seek(offset)
    recorder_struct = struct.Struct("<33s2b5h3H")
    if recorder_struct.size > size:
        pass
    rs = recorder_struct.unpack(sf.read(recorder_struct.size))

    recorder_info = RecorderMontageInfo()
    recorder_info.name = string_trim_to_0(rs[0])
    recorder_info.nRecChannels = rs[1]
    recorder_info.invertedACChannels = rs[2]
    recorder_info.maximumVoltage = rs[3]
    recorder_info.normalVoltage = rs[4]
    recorder_info.calibrationSignal = rs[5]
    recorder_info.calibrationScale = rs[6]
    recorder_info.videoControl = rs[7]
    recorder_info.nSensitivities = rs[8]
    recorder_info.nLowFilters = rs[9]
    recorder_info.nHighFilters = rs[10]

    recorder_struct = struct.Struct("20f")
    recorder_info.sensitivity = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_info.lowFilter = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_info.highFilter = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<33s2bhH")
    rs = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_info.montageName = string_trim_to_0(rs[0])
    recorder_info.numberOfChannelsUsed = rs[1]
    recorder_info.globalSens = rs[2]
    recorder_info.epochLengthInSamples = rs[3]
    recorder_info.highestRate = rs[4]

    recorder_struct = struct.Struct("<32H")
    sampling_rate = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct(32 * "9s")
    signal_type = [string_trim_to_0(x) for x in recorder_struct.unpack(sf.read(recorder_struct.size))]
    recorder_struct = struct.Struct(32 * "9s")
    signal_sub_type = [string_trim_to_0(x) for x in recorder_struct.unpack(sf.read(recorder_struct.size))]
    recorder_struct = struct.Struct(32 * "13s")
    channel_desc = [string_trim_to_0(x) for x in recorder_struct.unpack(sf.read(recorder_struct.size))]
    recorder_struct = struct.Struct("<32H")
    sensitivity_index = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<32H")
    low_filter_index = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<32H")
    high_filter_index = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<32H")
    delay = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct(32 * "5s")
    unit = [string_trim_to_0(x) for x in recorder_struct.unpack(sf.read(recorder_struct.size))]
    recorder_struct = struct.Struct("<32h")
    artefact_level = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<32h")
    cal_type = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<32f")
    cal_factor = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<32f")
    cal_offset = recorder_struct.unpack(sf.read(recorder_struct.size))
    recorder_struct = struct.Struct("<32H")
    save_buffer_size = recorder_struct.unpack(sf.read(recorder_struct.size))

    for i in range(32):
        rc = RecorderChannel(sampling_rate[i], signal_type[i], signal_sub_type[i], channel_desc[i], sensitivity_index[i],
                             low_filter_index[i], high_filter_index[i], delay[i], unit[i], artefact_level[i], cal_type[i], cal_factor[i],
                             cal_offset[i], save_buffer_size[i])
        recorder_info.channels.append(rc)

    return recorder_info


class SignalPage:
    def __init__(self):
        self.filling = 0
        self.time = time(0, 0, 0)


def eof(f):
    return f.tell() == os.fstat(f.fileno()).st_size


def read_signal_pages(sf, read_signal_data, file_size, offset, page_size, epoch_length, channels_used, channels):
    header_length = 6
    num_pages = int((file_size-offset)/page_size)
    pages=[None]*num_pages
    signals = [numpy.zeros(channels[i].save_buffer_size*num_pages) if read_signal_data else [] for i in range(channels_used)]
    current_offset = offset
    header_struct = struct.Struct("<Hl")
    stop = False
    sf.seek(current_offset)
    curr_page = -1
    while not stop and (not eof(sf)):
        curr_page += 1
        rs = header_struct.unpack(sf.read(header_struct.size))
        page = SignalPage()
        page.filling = rs[0]
        page.time = decode_time(rs[1])
        pages[curr_page]=page
        if page.filling != 0:
            stop = True
        else:
            data_size = page_size - header_length
        if not stop:
            current_offset += page_size
            if read_signal_data:
                for i in range(channels_used):
                    buffer_struct = struct.Struct(channels[i].save_buffer_size * "h")
                    b = buffer_struct.unpack(sf.read(buffer_struct.size))
                    start_index=curr_page*channels[i].save_buffer_size
                    numpy.put(signals[i], numpy.arange(start_index,start_index+channels[i].save_buffer_size), b)
            else:
                sf.seek(current_offset)
    if read_signal_data:
        for i in range(channels_used):
            signals[i] = signals[i] * channels[i].cal_factor + channels[i].cal_offset
    return pages, signals
