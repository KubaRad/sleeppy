from scipy import signal


def signal_resample(x, sf, new_sf):
    new_samplings= int((new_sf/sf)*len(x))
    new_signal_values = signal.resample(x, new_samplings)
    return new_signal_values
