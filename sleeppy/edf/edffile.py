import struct
import numpy as np
import pandas as pd
from collections import namedtuple
from datetime import datetime

__author__ = 'Kuba Radliński'

_DEFAULT_DATE_FORMAT = "%d.%m.%y"
_DEFAULT_TIME_FORMAT = "%H.%M.%S"


def _encode_date(dtstr):
    return datetime.strptime(dtstr, _DEFAULT_DATE_FORMAT).date()


def _encode_time(tmstr):
    return datetime.strptime(tmstr, _DEFAULT_TIME_FORMAT).time()


def _string_trim0(s):
    ns = "".join([x if 32 <= ord(x) <= 126 else '' for x in s])
    return ns


StructDesc = namedtuple('StructDesc', 'fname ln type encoding input_f output_f')


def _prepare_float_string(sd, f):
    int_f = int(f)
    len_int_f = len(str(int_f))
    decimals = sd.ln - 1 - len_int_f
    return ('{' + ':<{}.{}f'.format(sd.ln, decimals) + '}').format(f).encode(sd.encoding)


def _prepare_int_string(sd, d):
    return ('{' + ':<{}d'.format(sd.ln) + '}').format(d).encode(sd.encoding)


def _prepare_time_string(sd, tm):
    return ('{' + ':<{}'.format(sd.ln) + '}').format(tm.strftime(_DEFAULT_TIME_FORMAT)[:sd.ln]).encode(sd.encoding)


def _prepare_date_string(sd, dt):
    return ('{' + ':<{}'.format(sd.ln) + '}').format(dt.strftime(_DEFAULT_DATE_FORMAT)[:sd.ln]).encode(sd.encoding)


def _prepare_string(sd, st):
    return ('{' + ':<{}'.format(sd.ln) + '}').format(st.strip()[:sd.ln]).encode(sd.encoding)


_HEADER_STRUCTURE = [StructDesc('version', 8, 's', 'ASCII', _string_trim0, _prepare_string),
                     StructDesc('patient_id', 80, 's', 'LATIN2', _string_trim0, _prepare_string),
                     StructDesc('record_id', 80, 's', 'LATIN2', _string_trim0, _prepare_string),
                     StructDesc('start_date', 8, 's', 'ASCII', _encode_date, _prepare_date_string),
                     StructDesc('start_time', 8, 's', 'ASCII', _encode_time, _prepare_time_string),
                     StructDesc('bytes_in_header', 8, 's', 'ASCII', int, _prepare_int_string),
                     StructDesc('reserved', 44, 's', 'ASCII', _string_trim0, _prepare_string),
                     StructDesc('records_in_file', 8, 's', 'ASCII', int, _prepare_int_string),
                     StructDesc('record_duration', 8, 's', 'ASCII', int, _prepare_int_string),
                     StructDesc('signals_in_file', 4, 's', 'ASCII', int, _prepare_int_string)]

_HEADER_FIELD_NAMES = ['version', 'patient_id', 'record_id', 'start_date', 'start_time', 'bytes_in_header',
                       'reserved', 'records_in_file', 'record_duration', 'signals_in_file', 'signal_defs']

_HEADER_SD_STRUCTURE = [StructDesc('label', 16, 's', 'ASCII', _string_trim0, _prepare_string),
                        StructDesc('transducer', 80, 's', 'ASCII', _string_trim0, _prepare_string),
                        StructDesc('dimension', 8, 's', 'ASCII', _string_trim0, _prepare_string),
                        StructDesc('phys_min', 8, 's', 'ASCII', float, _prepare_float_string),
                        StructDesc('phys_max', 8, 's', 'ASCII', float, _prepare_float_string),
                        StructDesc('dig_min', 8, 's', 'ASCII', int, _prepare_int_string),
                        StructDesc('dig_max', 8, 's', 'ASCII', int, _prepare_int_string),
                        StructDesc('filter', 80, 's', 'ASCII', _string_trim0, _prepare_string),
                        StructDesc('samples', 8, 's', 'ASCII', int, _prepare_int_string),
                        StructDesc('reserved', 32, 's', 'ASCII', _string_trim0, _prepare_string)]

_SD_FIELD_NAMES = [x.fname for x in _HEADER_SD_STRUCTURE]

SignalDefinition = namedtuple('SignalDefinition', _SD_FIELD_NAMES)

SignalReadInfo = namedtuple('SignalReadInfo', ['index', 'index_in_file', 'start_position', 'struct_def', 'samples'])


def _extract_field(sf, hds):
    hs = struct.Struct(str(hds.ln) + hds.type)
    hb = hs.unpack(sf.read(hs.size))
    try:
        s = hb[0].decode(hds.encoding).strip()
    except:
        print("Erorr in field {} decoding (probably wrong {} character): {}".format(hds.fname, hds.encoding, hb[0]))
        s = hds.fname
    if hds[3] is not None:
        try:
            value = hds.input_f.__call__(s)
        except:
            print("Erorr in processing field {}: {}".format(hds.fname, hb[0]))
            value = None
    else:
        value = s
    return value


def _extract_composed_field(sf, hds, ln):
    hs = struct.Struct(ln * (str(hds.ln) + hds.type))
    hb = hs.unpack(sf.read(hs.size))
    try:
        s = [x.decode(hds.encoding).strip() for x in hb]
    except:
        print("Erorr in field {} decoding : {}".format(hds.fname, hds.encoding))
        s = ln * (hds.fname if hds.input_f is None else '0')
    if hds.input_f is not None:
        try:
            values = [hds.input_f.__call__(x) for x in s]
        except:
            print("Erorr in processing field {}".format(hds.fname))
            values = None
    else:
        values = s
    return values


class Header(namedtuple('Header', _HEADER_FIELD_NAMES)):
    def duration(self):
        return self.records_in_file * self.record_duration

    def to_bytes(self):
        sdict = {x.fname: [] for x in _HEADER_SD_STRUCTURE}
        for s in self.signal_defs:
            sd = s._asdict()
            for sg in _HEADER_SD_STRUCTURE:
                ss = struct.Struct(str(sg.ln) + sg.type)
                sdict[sg.fname].append(ss.pack(sg.output_f.__call__(sg, sd[sg.fname])))

        sb = b''.join([x for x in [b''.join(sdict[y.fname]) for y in _HEADER_SD_STRUCTURE]])
        header_len = 256 + len(sb)
        hs = struct.Struct(''.join([str(x.ln) + x.type for x in _HEADER_STRUCTURE]))
        hdict = self._asdict()
        if hdict['bytes_in_header'] != header_len:
            hdict['bytes_in_header'] = header_len
        hb = hs.pack(*[x.output_f.__call__(x, hdict[x.fname]) for x in _HEADER_STRUCTURE])
        return b''.join([hb, sb])

    def find_signal_index(self, signal_label):
        labels = [x.label for x in self.signal_defs]
        return labels.index(signal_label) if signal_label in labels else None


def create_header_from_stream(sf):
    dheader = {}
    for hds in _HEADER_STRUCTURE:
        value = _extract_field(sf, hds)
        dheader[hds[0]] = value

    signals_in_file = dheader['signals_in_file']
    dsignals = {}
    for hds in _HEADER_SD_STRUCTURE:
        values = _extract_composed_field(sf, hds, signals_in_file)
        dsignals[hds[0]] = values

    signal_defs = [SignalDefinition(**{x[0]: dsignals[x[0]][i] for x in _HEADER_SD_STRUCTURE}) for i in
                   range(0, signals_in_file)]
    dheader['signal_defs'] = signal_defs
    return Header(**dheader)


def create_header_from_file(file_name):
    with open(file_name, mode='rb') as ifile:
        instance = create_header_from_stream(ifile)
    return instance


class EdfFile(object):
    def __init__(self, header, integers=False):
        self.filename = None
        self._integers = integers
        self._data_start = 0
        self._nrecords = 0
        self._signal_infos = []
        self._record_size = 0
        self.header = header

    def _prepare_to_read(self, sf, signals_to_read):
        sf.seek(0, 2)
        file_size = sf.tell()
        self._data_start = 256 + 256 * self.header.signals_in_file
        self._record_size = sum([x.samples for x in self.header.signal_defs]) * 2
        estimated_records = (file_size - self._data_start) / self._record_size
        self._nrecords = self.header.records_in_file if self.header.records_in_file != -1 else estimated_records
        if estimated_records < self._nrecords:
            print("Estimated records number (%d) lower than stored records (%d)" % (estimated_records, self._nrecords))
            print("Assuming %d" % estimated_records)
            self._nrecords = estimated_records
        before = 0
        orig_start_positions = []
        for s in self.header.signal_defs:
            orig_start_positions.append(before)
            before += s.samples * 2
        sigs = [x for x in (signals_to_read if signals_to_read is not None else range(0, self.header.signals_in_file))]
        for i, s in enumerate(sigs):
            st = struct.Struct("%dh" % self.header.signal_defs[s].samples)
            self._signal_infos.append(
                SignalReadInfo(i, s, orig_start_positions[s], st, self.header.signal_defs[s].samples))

    @staticmethod
    def _read_signal_record(sf, s, record_start):
        sf.seek(record_start + s.start_position)
        ssize = s.struct_def.size
        rbytes = sf.read(ssize)
        rbytes_len = len(rbytes)
        if rbytes_len < ssize:
            rbytes = rbytes + bytes(ssize - rbytes_len)
        return s.struct_def.unpack(rbytes)

    def _read_record(self, sf, r, signals):
        record_start = self._data_start + r * self._record_size
        for s in self._signal_infos:
            buf = self._read_signal_record(sf, s, record_start)
            start_pos = r * s.samples
            signals[s.index].put(range(start_pos, start_pos + len(buf)), buf, mode='clip')

    def read_signals(self, sf, signals_to_read=None):
        self._prepare_to_read(sf, signals_to_read)
        # npsignals = len(self._signal_infos)*[np.array([], dtype=int)]
        npsignals = []
        for s in self._signal_infos:
            npsignals.append(np.zeros(self._nrecords * s.samples, dtype=int))
        for r in range(0, self._nrecords):
            self._read_record(sf, r, npsignals)
        if not self._integers:
            for s in self._signal_infos:
                dig_min = self.header.signal_defs[s.index_in_file].dig_min
                dig_max = self.header.signal_defs[s.index_in_file].dig_max
                phys_min = self.header.signal_defs[s.index_in_file].phys_min
                phys_max = self.header.signal_defs[s.index_in_file].phys_max
                phys_dig = (phys_max - phys_min) / (dig_max - dig_min)
                npsignals[s.index] = (npsignals[s.index] - dig_min) * phys_dig + phys_min
        return npsignals

    def find_signal_index(self, signal_label):
        return self.header.find_signal_index(signal_label)

    def __eq__(self, other):
        return self.header == other.header if other is not None else False


class EdfData(EdfFile):
    def __init__(self, header, signals):
        super(EdfData, self).__init__(header)
        self.signals = signals
        if header.signals_in_file != len(signals):
            raise BaseException("Signals lenght different from no. signals in header")

    def _create_record_block(self, rec, signals_to_write):
        record_data = []
        for i in range(len(self.header.signal_defs)):
            start_index = rec * self.header.signal_defs[i].samples
            sig_data = signals_to_write[i][start_index:start_index + self.header.signal_defs[i].samples]
            if self._integers:
                buf = b''.join(struct.pack("<h", x) for x in sig_data)
            else:
                buf = b''.join(
                    (struct.pack("<h", int(x) if -32768.0 <= x <= 32767.0 else -32768 if x <= -32768.0 else 32767)
                     for x in sig_data))
            record_data.append(buf)
        return b''.join(record_data)

    def _signals_to_stream(self, sf):
        signals_to_write = self._prepare_signals_to_write()
        for i in range(self.header.records_in_file):
            rb = self._create_record_block(i, signals_to_write)
            sf.write(rb)

    def _signals_to_bytes(self):
        record_data = []
        signals_to_write = self._prepare_signals_to_write()
        for i in range(self.header.records_in_file):
            rb = self._create_record_block(i, signals_to_write)
            record_data.append(rb)
        return b''.join(record_data)

    def _prepare_signals_to_write(self):
        if self._integers:
            signals_to_write = self.signals
        else:
            signals_to_write = []
            for i in range(len(self.header.signal_defs)):
                dig_min = self.header.signal_defs[i].dig_min
                dig_max = self.header.signal_defs[i].dig_max
                phys_min = self.header.signal_defs[i].phys_min
                phys_max = self.header.signal_defs[i].phys_max
                dig_phys = (dig_max - dig_min) / (phys_max - phys_min)
                new_signal = (self.signals[i] - phys_min) * dig_phys + dig_min
                signals_to_write.append(np.rint(new_signal))
        return signals_to_write

    def to_bytes(self):
        return b''.join([self.header.to_bytes(), self._signals_to_bytes()])

    def signal_to_timeserie(self, signum, relative=False):
        signal_length = len(self.signals[signum])
        signal_frequency = (self.header.signal_defs[signum].samples / self.header.record_duration)
        if relative:
            signal_start = 0.0
            index_range = pd.timedelta_range(signal_start, periods=signal_length,
                                             freq=str(int(1000 / signal_frequency)) + 'ms')
        else:
            signal_start = datetime.combine(self.header.start_date, self.header.start_time)
            index_range = pd.date_range(signal_start, periods=signal_length,
                                        freq=str(int(1000 / signal_frequency)) + 'ms')
        return pd.Series(self.signals[signum], index=index_range)

    def signal_sampf(self, signum):
        return self.header.signal_defs[signum].samples / self.header.record_duration

    def __eq__(self, other):
        return (self.header == other.header and len(self.signals) == len(other.signals)) if other is not None else False

    def write_to_stream(self, sf):
        sf.write(self.header.to_bytes())
        self._signals_to_stream(sf)

    def write_to_file(self, file_name):
        with open(file_name, mode='wb') as ofile:
            self.write_to_stream(ofile)


def calculate_header_size(ns):
    return 256 * ns * 256


def create_from_stream(file_stream, signals_to_read=None, integers=False):
    header = create_header_from_stream(file_stream)
    edf2read = EdfFile(header, integers)
    signals = edf2read.read_signals(file_stream, signals_to_read)
    if signals_to_read is not None:
        hdict = header._asdict()
        sif = len(signals_to_read)
        hdict['signals_in_file'] = sif
        hdict['signal_defs'] = [header.signal_defs[x] for x in signals_to_read]
        hdict['bytes_in_header'] = calculate_header_size(sif)
        header = Header(**hdict)
    return EdfData(header, signals)


def create_from_file(file_name, signals_to_read=None, integers=False):
    with open(file_name, mode='rb') as ifile:
        instance = create_from_stream(ifile, signals_to_read, integers)
    if instance is not None:
        instance.filename = file_name
    return instance
