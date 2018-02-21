import pkg_resources
import os
from unittest import TestCase
import pandas as pd
import numpy as np
import edf.edffile as edf
import wave.amplitude as amp

_FILE_NAME = "test_amp.edf"
_FILE_EXTREMES_DATA_NAME = "test_extremes_data.txt"
_FILE_TEST_AMPLITUDE_DATA_NAME = "test_amplitude_data.txt"
_FILE_PATH = "data"


def _provide_test_stream():
    return pkg_resources.resource_stream(__name__, os.path.join(_FILE_PATH, _FILE_NAME))


def _provide_test_data_extremes_stream():
    return pkg_resources.resource_stream(__name__, os.path.join(_FILE_PATH, _FILE_EXTREMES_DATA_NAME))


def _provide_test_signal():
    header = edf.create_header_from_stream(_provide_test_stream())
    edf_file = edf.EdfFile(header)
    i = edf_file.find_signal_index('Pleth')
    edf_file = edf.create_from_stream(_provide_test_stream(), [i])
    return edf_file.signal_to_timeserie(0, relative=True)


def _provide_expected_extremes():
    with _provide_test_data_extremes_stream() as fin:
        lines = fin.readlines()
    exp_index = []
    exp_extr = []
    exp_values = []
    for l in lines:
        e = [x.strip() for x in l.decode('ASCII').replace('\r\n', '').split('\t')]
        exp_index.append(pd.Timedelta(e[0]))
        exp_extr.append(e[1])
        exp_values.append(float(e[2]))
    return pd.DataFrame({'type': exp_extr, 'value': exp_values}, index=exp_index)


def _round_extremes(ex):
    for i, v in enumerate(ex.value):
        ex.loc[ex.index[i], ('value',)] = np.round(v, decimals=6)


class TestAmplitude(TestCase):
    pass
