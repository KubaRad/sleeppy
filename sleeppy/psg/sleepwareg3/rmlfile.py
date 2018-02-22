__author__ = 'Kuba Radliński'

from xml.dom import minidom, Node
from datetime import datetime, timedelta
from collections import namedtuple


ChannelConfig = namedtuple('ChannelConfig', ('edf_signal', 'use_for_analysis', 'label'))


def _read_channel_config(xmldoc):
    channels = []
    chnln = xmldoc.getElementsByTagName('ChannelConfig')
    if len(chnln) > 0:
        chnlsn = chnln[0].getElementsByTagName('Channels')
        if len(chnlsn) > 0:
            for ch in chnlsn[0].getElementsByTagName('Channel'):
                if ch.nodeType == Node.ELEMENT_NODE:
                    edf_signal  = int(ch.getAttribute('EdfSignal'))
                    use_for_analysis = ch.getAttribute('UseForAnalysis') == "true"
                    nds = ch.getElementsByTagName('Label')
                    label = nds[0].firstChild.data if len(nds) > 0 else ''
                    channels.append(ChannelConfig(edf_signal, use_for_analysis, label))
    return channels


RecordingData = namedtuple('RecordingData', ['start_time', 'end_time', 'duration', 'lights_off_time', 'lights_on_time', 'epochs_start'])


def _read_recording_data(xmldoc):
    sessions_node = [x for x in xmldoc.getElementsByTagName('Acquisition')[0].childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Sessions'][0]
    first_session = [x for x in sessions_node.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Session'][0]
    _start_time = None
    _end_time = None
    _duration_delta = None
    _lights_off_delta = None
    _lights_on_delta = None
    _lights_off_time = None
    _lights_on_time = None
    for r in [x for x in first_session.childNodes if x.nodeType == Node.ELEMENT_NODE]:
        if r.localName == 'RecordingStart':
            _start_time = datetime.strptime(r.firstChild.data, "%Y-%m-%dT%H:%M:%S")
        elif r.localName == 'Duration':
            _duration_delta = timedelta(seconds=int(r.firstChild.data))
        elif r.localName == 'LightsOff':
            _lights_off_delta = timedelta(seconds=int(r.firstChild.data))
        elif r.localName == 'LightsOn':
            _lights_on_delta = timedelta(seconds=int(r.firstChild.data))
    if _start_time is not None and _duration_delta is not None:
        _end_time = _start_time + _duration_delta
    if _start_time is not None and _lights_off_delta is not None:
        _lights_off_time = _start_time + _lights_off_delta
    if _start_time is not None and _lights_on_delta is not None:
        _lights_on_time = _start_time + _lights_on_delta
    _epochs_start = _start_time
    return RecordingData(_start_time, _end_time, _duration_delta, _lights_off_time, _lights_on_time, _epochs_start)


Event = namedtuple('Event', ['family', 'event_type', 'start_time', 'end_time', 'duration'])
EventSaO2 = namedtuple('Event', ['family', 'event_type', 'start_time', 'end_time', 'duration', 'o2_before', 'o2_min', 'o2_drop', 'hr_before', 'hr_extreme'])
EventChannelFail = namedtuple('Event', ['family', 'event_type', 'start_time', 'end_time', 'duration', 'edf_signal'])


def _extract_value_from_nodes(nds):
    if nds is not None and len(nds)>0:
        return nds[0].firstChild.data


def _extract_float_value_from_nodes(nds):
    v = _extract_value_from_nodes(nds)
    return float(v) if v else None


def _extract_int_value_from_nodes(nds):
    v = _extract_value_from_nodes(nds)
    return int(v) if v else None


def _create_event_from_node(x, recording_start_time):
    duration = timedelta(milliseconds=int(float(x.getAttribute('Duration'))*1000))
    start_time = recording_start_time+timedelta(milliseconds=int(float(x.getAttribute('Start'))*1000))
    end_time = start_time + duration
    family = x.getAttribute('Family')
    event_type = x.getAttribute('Type')
    if family == 'SpO2':
        o2_before = _extract_float_value_from_nodes(x.getElementsByTagName('O2Before'))
        o2_min = _extract_float_value_from_nodes(x.getElementsByTagName('O2Min'))
        o2_drop = o2_before - o2_min
        hr_before = _extract_float_value_from_nodes(x.getElementsByTagName('HRBefore'))
        hr_extreme = _extract_float_value_from_nodes(x.getElementsByTagName('HRExtreme'))
        return EventSaO2(family, event_type, start_time, end_time, duration, o2_before, o2_min, o2_drop, hr_before, hr_extreme)
    if event_type == 'ChannelFail':
        nds = x.getElementsByTagName('ChannelFail')
        edf_signal = int(nds[0].getAttribute('EdfSignal')) if len(nds) > 0 else None
        return EventChannelFail(family, event_type, start_time, end_time, duration, edf_signal)
    return Event(family, event_type, start_time, end_time, duration)



Stage = namedtuple('Stage',['stage_type', 'start_time', 'end_time', 'duration'])
ScoringData = namedtuple('ScoringData', ['events', 'staging', 'block_staging'])


def _read_scoring_data(xmldoc, recording_start_time, recording_duration, epochs_start_time=timedelta(seconds=0), relative=True):
    evdl = [x for x in xmldoc.getElementsByTagName('ScoringData')[0].childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Events']
    if len(evdl) > 0:
        events_data = evdl[0]
        events_list = [_create_event_from_node(x, recording_start_time) for x in events_data.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Event']
    else:
        events_list = []

    stages = []
    block_stages = []

    stgd = [x for x in xmldoc.getElementsByTagName('ScoringData')[0].childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'StagingData']

    if len(stgd) > 0:
        staging_data = stgd[0]
        ustgd = [x for x in staging_data.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'UserStaging']
        if len(ustgd) > 0:
            user_staging = ustgd[0]
            aastgd = [x for x in user_staging.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'NeuroAdultAASMStaging']
            if len(aastgd) > 0:
                aasm_adult_staging = aastgd[0]
                g3_stages = [x for x in aasm_adult_staging.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Stage']
                previous_stage = 'NotScored'
                previous_end = 0
                epoch = 0
                for g3s in g3_stages:
                    start = int(g3s.getAttribute('Start'))
                    duration = timedelta
                    if previous_end is not None and start > previous_end:
                        while start > previous_end:
                            epoch += 1
                            start_time = epochs_start_time+timedelta(seconds=previous_end)
                            end_time = start_time+timedelta(seconds=30)
                            stages.append(Stage(previous_stage, start_time, end_time, timedelta(seconds=30)))
                            previous_end += 30
                    epoch += 1
                    start_time = epochs_start_time+timedelta(seconds=start)
                    stage = g3s.getAttribute('Type')
                    end_time = start_time+timedelta(seconds=30)
                    stages.append(Stage(stage, start_time, end_time, timedelta(seconds=30)))
                    previous_end += 30
                    previous_stage = stage
                while previous_end < recording_duration.total_seconds():
                    epoch += 1
                    start_time = epochs_start_time+timedelta(seconds=previous_end)
                    end_time = start_time+timedelta(seconds=30)
                    stages.append(Stage(previous_stage, start_time, end_time, timedelta(seconds=30)))
                    previous_end += 30
                previous_stage = g3_stages[0].getAttribute('Type')
                previous_start = timedelta(seconds=int(g3_stages[0].getAttribute('Start')))
                for g3s in g3_stages[1:]:
                    stage = g3s.getAttribute('Type')
                    start = timedelta(seconds=int(g3s.getAttribute('Start')))
                    block_stages.append(Stage(previous_stage, previous_start, start, start-previous_start))
                    previous_stage = stage
                    previous_start = start
                d = (recording_duration-previous_start).total_seconds()
                duration = timedelta(seconds=(d//30)*30)
                block_stages.append(Stage(previous_stage, previous_start, recording_duration, duration))
    return ScoringData(events_list, stages, block_stages)


RmlFile = namedtuple('RmlFile', ['channels_config','recording_data', 'scoring_data'])


def read_rml_file(filename):
    xmldoc = minidom.parse(filename)
    channels_config = _read_channel_config(xmldoc)
    recording_data = _read_recording_data(xmldoc)
    scoring_data = _read_scoring_data(xmldoc, recording_data.start_time, recording_data.duration, recording_data.epochs_start)
    return RmlFile(channels_config, recording_data, scoring_data)
