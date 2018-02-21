__author__ = 'Kuba Radliński'

from xml.dom import minidom, Node
from datetime import datetime, timedelta
from collections import namedtuple


RecordingData = namedtuple('RecordingData', ['start_time', 'end_time', 'duration', 'lights_off_time', 'lights_on_time', 'epochs_start'])


def read_recording_data(xmldoc):
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


def create_event_from_node(x, recording_start_time):
    duration = timedelta(milliseconds=int(float(x.getAttribute('Duration'))*1000))
    start_time = recording_start_time+timedelta(milliseconds=int(float(x.getAttribute('Start'))*1000))
    end_time = start_time + duration
    family = x.getAttribute('Family')
    event_type = x.getAttribute('Type')
    return Event(family, event_type, start_time, end_time, duration)


Stage = namedtuple('Stage',['stage_type', 'start_time', 'end_time', 'duration'])
ScoringData = namedtuple('ScoringData', ['events', 'staging', 'block_staging'])


def read_scoring_data(xmldoc, recording_start_time, recording_duration, epochs_start_time=timedelta(seconds=0), relative=True):
    events_data = [x for x in xmldoc.getElementsByTagName('ScoringData')[0].childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Events'][0]
    events_list = [create_event_from_node(x, recording_start_time) for x in events_data.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Event']

    staging_data = [x for x in xmldoc.getElementsByTagName('ScoringData')[0].childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'StagingData'][0]
    user_staging = [x for x in staging_data.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'UserStaging'][0]
    aasm_adult_staging = [x for x in user_staging.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'NeuroAdultAASMStaging'][0]
    g3_stages = [x for x in aasm_adult_staging.childNodes if x.nodeType == Node.ELEMENT_NODE and x.localName == 'Stage']

    previous_stage = 'NotScored'
    previous_end = 0
    epoch = 0
    stages = []
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
    block_stages = []
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


RmlFile = namedtuple('RmlFile', ['recording_data', 'scoring_data'])


def read_rml_file(filename):
    xmldoc = minidom.parse(filename)
    recording_data = read_recording_data(xmldoc)
    scoring_data = read_scoring_data(xmldoc, recording_data.start_time, recording_data.duration, recording_data.epochs_start)
    return RmlFile(recording_data, scoring_data)
