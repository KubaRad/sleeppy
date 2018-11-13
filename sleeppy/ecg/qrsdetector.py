import time
import numpy as np
from wfdb import processing


def detect_qrs(ecg_measurements, fs, win_len_min=10, win_overlap_min=1):

    win_len = int(fs * 60 * win_len_min)
    win_overlap = int(fs * 60 * win_overlap_min)
    indices = set()
    win_skip = win_len - win_overlap
    wins = int((len(ecg_measurements) - win_len)/ win_skip)+2
    min_bpm = 20
    max_bpm = 230
    search_radius = int(fs * 60 / max_bpm)
    start_time_all = time.time()
    for i, w_start in enumerate([x * win_skip for x in range(wins)]):
        w_end = w_start + win_len
        start_time = time.time()
        calc_data = ecg_measurements[w_start:w_end]
        qrs_inds = processing.xqrs_detect(sig=calc_data, fs=fs, learn=True, verbose=False)
        corrected_peak_inds = processing.correct_peaks(calc_data, peak_inds=qrs_inds,
                                                       search_radius=search_radius, smooth_window_size=150)
        start_upd_dict_time = time.time()
        corrected_peak_inds = corrected_peak_inds + w_start
        indices.update(corrected_peak_inds)
        end_time = time.time()
        print("{:5} {:10} - {:10} czas wykonania: {:10.2} całkowity czas wykonania: {:10.2}  liczba probek: {} liczba qrs: {} liczba probek w zbiorze {}".format(i, w_start, w_end, end_time-start_time, end_time - start_time_all,  len(calc_data), len(corrected_peak_inds), len(indices)), flush=True)
    result = np.array(list(indices))
    np.ndarray.sort(result)
    return result
