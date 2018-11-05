__author__ = 'Kuba Radliński'

import sys
from ..rmlfile import read_rml_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage printrml filename')
    else:
        file_name = sys.argv[1]
        rml = read_rml_file(file_name)
        print("start:", rml.recording_data.start_time)
        print("end:", rml.recording_data.end_time)
        print("duration:", rml.recording_data.duration.total_seconds())
        print("lights off:", rml.recording_data.lights_off_time)
        print("lights on:", rml.recording_data.lights_on_time)
        print("epochs start:", rml.recording_data.epochs_start)

        for s in rml.scoring_data.staging:
            print(s.start_time.time().isoformat(), (s.start_time - rml.recording_data.start_time).total_seconds(),
                  s.end_time.time().isoformat(), s.duration.total_seconds(), s.stage_type)
        print('===========================================================')
        for s in rml.scoring_data.block_staging:
            print(s.start_time, s.start_time.total_seconds(), s.end_time, s.duration.total_seconds(), s.stage_type)
