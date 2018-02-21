import os
import pkg_resources
import io
import numpy as np
import pandas as pd
from unittest import TestCase
from sleeppy.edf import edffile as edf
from datetime import date, time, datetime
from tempfile import NamedTemporaryFile

_FILE_NAME = "edf-test1.edf"
_FILE2_NAME = "edf-test2.edf"
_TXT_FILE_NAME = "edf-test2_data.txt"


_TF1_HEADER_DICT = {'version': "0",
                    'patient_id': "TEST1_PATIENT_ID",
                    'record_id': "TEST1_RECORD_ID",
                    'start_date': date(2016, 5, 9),
                    'start_time': time(19, 57, 15),
                    'bytes_in_header': 7936,
                    'reserved': '',
                    'records_in_file': 791,
                    'record_duration': 1,
                    'signals_in_file': 30,
                    'signal_defs': [
                        edf.SignalDefinition("EEG C3-A2", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EEG C4-A1", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EEG F3-A2", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EEG F4-A1", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EEG O1-A2", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EEG O2-A1", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EOG LOC-A2", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EOG ROC-A2", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EMG Chin", "", "uV", -78.000000, 78.000000, -32768, 32767, "HP:10Hz LP:180Hz N:50/60Hz", 500,
                                             ''),
                        edf.SignalDefinition("Leg 1", "", "uV", -78.000000, 78.000000, -32768, 32767, "HP:10Hz LP:180Hz N:50/60Hz", 500,
                                             ''),
                        edf.SignalDefinition("Leg 2", "", "uV", -78.000000, 78.000000, -32768, 32767, "HP:10Hz LP:180Hz N:50/60Hz", 500,
                                             ''),
                        edf.SignalDefinition("ECG I", "", "uV", -8333.000000, 8333.000000, -32768, 32767, "HP:0,04Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("RR", "", "", 0.000000, 200.000000, 0, 200, "", 10, ''),
                        edf.SignalDefinition("ECG II", "", "uV", -8333.000000, 8333.000000, -32768, 32767, "HP:0,04Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("Flow Patient", "Pressure", "", -100.000000, 100.000000, -32768, 32767, "", 100, ''),
                        edf.SignalDefinition("Flow Patient", "Thermistor", "", -100.000000, 100.000000, -32768, 32767, "", 100, ''),
                        edf.SignalDefinition("Snore", "Mic", "", -100.000000, 100.000000, -32768, 32767, "HP:10Hz LP:180Hz N:50/60Hz", 500,
                                             ''),
                        edf.SignalDefinition("Effort THO", "", "", -100.000000, 100.000000, -32768, 32767, "", 100, ''),
                        edf.SignalDefinition("Effort ABD", "", "", -100.000000, 100.000000, -32768, 32767, "", 100, ''),
                        edf.SignalDefinition("SpO2", "", "%", 0.000000, 102.300000, 0, 1023, "", 1, ''),
                        edf.SignalDefinition("Pleth", "", "", -100.000000, 100.000000, -32768, 32767, "Delay:343", 200, ''),
                        edf.SignalDefinition("Body", "", "", 0.000000, 255.000000, 0, 255, "", 1, ''),
                        edf.SignalDefinition("EEG A1-A2", "", "uV", -313.000000, 313.000000, -32768, 32767, "HP:0,3Hz LP:180Hz N:50/60Hz",
                                             500, ''),
                        edf.SignalDefinition("EMG Chin", "", "uV", -78.000000, 78.000000, -32768, 32767, "HP:10Hz LP:180Hz", 500, ''),
                        edf.SignalDefinition("Leg 1", "", "uV", -78.000000, 78.000000, -32768, 32767, "HP:10Hz LP:180Hz", 500, ''),
                        edf.SignalDefinition("Leg 2", "", "uV", -78.000000, 78.000000, -32768, 32767, "HP:10Hz LP:180Hz", 500, ''),
                        edf.SignalDefinition("Snore", "Mic", "", -100.000000, 100.000000, -32768, 32767, "HP:10Hz LP:180Hz", 500, ''),
                        edf.SignalDefinition("PressCheck", "", "", 0.000000, 65535.000000, -32768, 32767, "", 1, ''),
                        edf.SignalDefinition("ECG IIHF", "", "uV", -8333.000000, 8333.000000, -32768, 32767, "N:50/60Hz", 1000, ''),
                        edf.SignalDefinition("Technical", "RI_Diag_Device Alice_5", "", 0.000000, 65535.000000, -32768, 32767, "", 200,
                                             '')]}

_TF1_DURATION = 791

_FILE_PATH = "data"


def _provide_test_filename(name):
    return pkg_resources.resource_filename(__name__, os.path.join(_FILE_PATH, name))


def _provide_test_stream(name):
    return pkg_resources.resource_stream(__name__, os.path.join(_FILE_PATH, name))


def _provide_test_header():
    return edf.Header(**_TF1_HEADER_DICT)


class TestSignalDefinition(TestCase):
    def test___eq__(self):
        sd1 = edf.SignalDefinition("Technical", "RI_Diag_Device Alice_5", "", 0.000000, 65534.000000, -32768, 32767, "", 200, '')
        sd2 = edf.SignalDefinition("Technical", "RI_Diag_Device Alice_5", "", 0.000000, 65534.000000, -32768, 32767, "", 200, '')
        sd3 = edf.SignalDefinition("Technical", "RI_Diag_Device Alice_5", "", 0.000000, 65532.000000, -32768, 32767, "", 200, '')
        self.assertEqual(sd1, sd2)
        self.assertNotEqual(sd2, sd3)


class TestHeader(TestCase):
    def test___init__(self):
        instance = edf.Header(**_TF1_HEADER_DICT)
        self.assertIsNotNone(instance)

    def test_create_from_file(self):
        instance = edf.create_header_from_file(_provide_test_filename(_FILE_NAME))
        self.assertIsNotNone(instance)
        self.assertEqual(instance, _provide_test_header())

    def test_create_from_stream(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_header_from_stream(f)
        self.assertIsNotNone(instance)
        self.assertEqual(instance, _provide_test_header())

    def test_to_bytes(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_header_from_stream(f)
        with io.BytesIO(instance.to_bytes()) as f:
            instance2 = edf.create_header_from_stream(f)
        self.assertEqual(instance, instance2)

    def test_find_signal_index(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_header_from_stream(f)
        for i, sg in enumerate(_TF1_HEADER_DICT['signal_defs']):
            if i not in [15, 23, 24, 25, 26]:  # duplicate labels
                self.assertEqual(i, instance.find_signal_index(sg.label))


class TestEdfFile(TestCase):
    def test___init__(self):
        instance = edf.EdfFile(edf.Header(**_TF1_HEADER_DICT))
        self.assertIsNotNone(instance)
        self.assertEqual(instance.header, _provide_test_header())

    def test_find_signal_index(self):
        with _provide_test_stream(_FILE_NAME) as f:
            header = edf.create_header_from_stream(f)
        instance = edf.EdfFile(header)
        for i, sg in enumerate(_TF1_HEADER_DICT['signal_defs']):
            if i not in [15, 23, 24, 25, 26]:  # duplicate labels
                self.assertEqual(i, instance.find_signal_index(sg.label))


class TestEdfData(TestCase):
    _instance = None

    def provide_instance(self):
        if self._instance is None:
            print('creating new instance in test class:', self)
            self._instance = edf.create_from_stream(_provide_test_stream(_FILE_NAME))
        return self._instance

    def test_init(self):
        instance = edf.EdfData(edf.Header(**_TF1_HEADER_DICT), _TF1_HEADER_DICT['signals_in_file'] * [[]])
        self.assertIsNotNone(instance)
        self.assertIsNotNone(instance.header)
        self.assertEqual(len(instance.signals), _TF1_HEADER_DICT['signals_in_file'])

    def test_to_bytes(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_from_stream(f)
        with io.BytesIO(instance.to_bytes()) as f:
            instance2 = edf.create_from_stream(f)
        self.assertEqual(instance, instance2)

    def test_to_timeserie(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_from_stream(f)
        start_date_time = datetime.combine(instance.header.start_date, instance.header.start_time)
        for i, sg in enumerate(_TF1_HEADER_DICT['signal_defs']):
            sg_timeserie = instance.signal_to_timeserie(i)
            self.assertEqual(start_date_time, sg_timeserie.index[0])
            self.assertEqual(instance.header.record_duration * instance.header.records_in_file * sg.samples, len(sg_timeserie))
        pass

    def test_create_from_stream(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_from_stream(f)
        self.assertIsNotNone(instance)
        self.assertEqual(instance.header, _provide_test_header())

    def test_write_file(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_from_stream(f)
        self.assertIsNotNone(instance)
        with NamedTemporaryFile(delete=False) as write_stream:
            file4read = write_stream.name
            print("using file:", file4read)
            instance.write_to_stream(write_stream)
        instance2 = edf.create_from_file(file4read)
        os.remove(file4read)
        self.assertIsNotNone(instance2)
        self.assertEqual(instance, instance2)

    def test_create_from_stream_selected_signal(self):
        with _provide_test_stream(_FILE_NAME) as f:
            instance = edf.create_from_stream(f)
        self.assertIsNotNone(instance)
        self.assertEqual(instance.header, _provide_test_header())

    def test_data_decoding(self):
        with _provide_test_stream(_FILE2_NAME) as f:
            instance = edf.create_from_stream(f)
        self.assertIsNotNone(instance)
        buf = np.genfromtxt(_provide_test_filename(_TXT_FILE_NAME), delimiter=',', skip_header=1)
        signal = np.array([x[1] for x in buf])
        index_range = pd.timedelta_range(0, periods=len(signal), freq=str(int((buf[1][0] - buf[0][0]) * 1000)) + 'ms')
        expected_serie = pd.Series(signal, index=index_range)
        readed_serie = instance.signal_to_timeserie(0, relative=True).round(decimals=6)
        self.assertTrue(expected_serie.equals(readed_serie))
