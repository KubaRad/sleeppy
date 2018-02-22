import os
import pkg_resources

from unittest import TestCase
from sleeppy.psg.sleepwareg3.rmlfile import read_rml_file, RmlFile, ScoringData, Event, EventSaO2, EventChannelFail, ChannelConfig


_RML_ONLY_RESP_FILE_CHANNEL_CONFIG = [ChannelConfig(0, True, 'SpO2'), ChannelConfig(1, True, 'PulseRate')]

_FILE_PATH = "data"
_RML_ONLY_RESP_FILE = 'test-events.rml'


def _provide_test_filename(name):
    return pkg_resources.resource_filename(__name__, os.path.join(_FILE_PATH, name))


class TestRead_rml_file(TestCase):
    def test_read_rml_file(self):
        rml_file = read_rml_file(_provide_test_filename(_RML_ONLY_RESP_FILE))
        self.assertIsNotNone(rml_file)
        self.assertIsInstance(rml_file, RmlFile)
        self.assertIsInstance(rml_file.scoring_data, ScoringData)
        self.assertEqual(rml_file.scoring_data.staging, [])
        self.assertEqual(rml_file.scoring_data.block_staging, [])
        self.assertNotEqual(rml_file.scoring_data.events, [])
        self.assertEqual(rml_file.channels_config, _RML_ONLY_RESP_FILE_CHANNEL_CONFIG)
        o2_ev_cnt = 0
        channel_fail_ev_cnt = 0
        for ev in rml_file.scoring_data.events:
            self.assertTrue(type(ev) in [Event, EventSaO2, EventChannelFail])
            if type(ev) == EventSaO2:
                self.assertIsNotNone(ev.o2_before)
                self.assertIsNotNone(ev.o2_min)
                self.assertIsNotNone(ev.o2_drop)
                self.assertEqual(ev.o2_before-ev.o2_min, ev.o2_drop)
                self.assertIsNotNone(ev.hr_before)
                self.assertIsNotNone(ev.hr_extreme)
                o2_ev_cnt +=1
            if type(ev) == EventChannelFail:
                self.assertIsNotNone(ev.edf_signal)
                channel_fail_ev_cnt +=1
        self.assertGreater(o2_ev_cnt, 0)
        self.assertGreater(channel_fail_ev_cnt, 0)
