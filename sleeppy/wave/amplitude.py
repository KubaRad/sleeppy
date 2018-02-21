import numpy as np
from scipy.signal import argrelmax, argrelmin
from collections import namedtuple

_SIGNAL_AMP_POINTS_FIELD_NAMES = ['min_ind', 'min_value', 'max_ind', 'max_value', 'amplitude', 'amp_time',
                                  'max_slope_ind',
                                  'max_slope_val', 'amp25_ind', 'amp25_val', 'amp50_ind', 'amp50_val']

AmplitudeValue = namedtuple('AmplitudeValue', ['min_ind', 'min_value', 'max_ind', 'max_value', 'amplitude'])


class SignalAmpPoints(namedtuple('SignalAmpPoints', _SIGNAL_AMP_POINTS_FIELD_NAMES)):
    def to_strings(self):
        return [str(self.min_ind),
                str(self.min_value),
                str(self.max_ind),
                str(self.max_value),
                str(self.amplitude),
                str(self.amp_time),
                str(self.max_slope_ind),
                str(self.max_slope_val),
                str(self.amp25_ind),
                str(self.amp25_val),
                str(self.amp50_ind),
                str(self.amp50_val)]


def derivative(ts):
    dx = [0]
    dx.extend([x[1] - x[0] for x in zip(ts[:-2], ts[2:])])
    dx.append(0)
    return np.array(dx)


def delete_same(x):
    previous = x[0]
    previous_ind = 0
    result = []
    index = []
    for i, y in enumerate(x):
        if y != previous:
            result.append(previous)
            previous = y
            ind = previous_ind+int((i-previous_ind)/2)
            index.append(ind)
            previous_ind = i
    return np.array(index), np.array(result)


def find_amplitude_candidates(x):
    original_ind, simplified_x = delete_same(x)
    simplified_min_ind = argrelmin(simplified_x)[0]
    simplified_max_ind = argrelmax(simplified_x)[0]
    min_ind = original_ind[simplified_min_ind]
    max_ind = original_ind[simplified_max_ind]
    start_max = 0 if max_ind[0] > min_ind[0] else 1
    len_max = len(max_ind) - start_max
    len_min = len(min_ind)
    if len_max > len_min:
        len_max = len_min
    else:
        if len_min > len_max:
            len_min = len_max
    return [AmplitudeValue(min_ind, min_val, max_ind, max_val, max_val - min_val)  for min_ind, min_val, max_ind, max_val in zip(min_ind[:len_min], x[min_ind[:len_min]], max_ind[start_max:len_max], x[max_ind[start_max:len_max]])]


def _glue_candidates(ac, sampf, max_dist):
    sample_delta = 1/sampf
    glued = []
    previous = ac[0]
    nglues = 0
    for current in ac[1:]:
        td = (current.min_ind - previous.max_ind)*sample_delta
        if td < max_dist and current.min_value > previous.min_value and current.max_value > previous.max_value:
            previous = AmplitudeValue(previous.min_ind, previous.min_value, current.max_ind, current.max_value,
                                      current.max_value - previous.min_value)
            nglues += 1
        else:
            glued.append(previous)
            previous = current
    glued.append(previous)
    return nglues, glued


def separate_amplitude(amp, min_amp=0.1):
    mn = np.mean([x.amplitude for x in amp])
    main_amp = []
    additional_amp = []
    border = min_amp * mn
    for a in amp:
        if a.amplitude >= border:
            main_amp.append(a)
        else:
            additional_amp.append(a)
    return main_amp, additional_amp


def create_pulse_point(x, dx, a, sampf):
    adx = dx[a.min_ind:a.max_ind]
    dxmax_ind = a.min_ind+adx.argmax()
    ac25 = a.min_value + 0.25 * a.amplitude
    ac50 = a.min_value + 0.5 * a.amplitude
    ind = None
    tm25 = None
    tm50 = None
    tm25found = False
    tm50found = False
    selected_x = x[a.min_ind:a.max_ind]
    for i, xc in enumerate(selected_x):
        if not tm25found and ac25 < xc:
            tm25 = a.min_ind + ind + ((ac25 - selected_x[ind]) / (selected_x[ind + 1] - selected_x[ind])) if i < len(selected_x) - 1 else \
                a.min_ind + ind if ind else None
            tm25found = True
        if not tm50found and ac50 < xc:
            tm50 = a.min_ind + ind + (
                (ac50 - selected_x[ind]) / (selected_x[ind + 1] - selected_x[ind])) if i < len(selected_x) - 1 else \
                a.min_ind + ind if ind else None
            tm50found = True
        if tm25found and tm50found:
            break
        ind = i
    td = (a.max_ind - a.min_ind) * (1/sampf)
    return SignalAmpPoints(a.min_ind, a.min_value, a.max_ind, a.max_value, a.amplitude, td, dxmax_ind, x[dxmax_ind],
                           tm25, ac25, tm50, ac50)


def add_pulse_points(x, dx, amp, sampf):
    return [create_pulse_point(x, dx, a, sampf) for a in amp]


def signal_amplitude(x, sampf, max_dist=0.3, addpulse=True):
    dx = derivative(x)
    ac = find_amplitude_candidates(x)
    nglues = 1
    glued = ac
    while nglues > 0:
        nglues, glued = _glue_candidates(glued, sampf, max_dist)
    return add_pulse_points(x, dx, glued, sampf) if addpulse else glued
