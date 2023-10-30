import mne
import numpy as np

from noise_rejction import asr_noise_rejection, reject_bad_segs


### Function to process raw data
def preprocessing_eeg(fname=None):
    """
    Preprocess raw edf data

    input: file name of raw data

    outputs:
         1. processed data with edf format,
         2. processed data of numpy array format (for absolute power calculating)
    ------------------

    Preprocessing pipline:

    Resampling to 250

    IIR filtering, (1-50), notch filtering

    Noise segment rejection with ASR algorith

    ECG noise segment makring and rejction

    Remove NaN data

    Stepforward ASR segment rejection

    """
    raw = mne.io.read_raw_edf(fname + '.edf', verbose=0)
    raw.resample(sfreq=250)
    # raw.info
    # raw.plot(duration=60, n_channels=len(raw.ch_names), remove_dc=False)

    # load data into memory
    raw.load_data()

    # Filtering
    # raw_filtered = raw.load_data().filter(l_freq=1, h_freq= 50)
    raw.notch_filter(freqs=60)
    raw.filter(l_freq=1, h_freq=50)
    # filtered data
    ## raw.plot(duration=10, start=0, n_channels=len(raw.ch_names), remove_dc=True)

    raw = asr_noise_rejection(raw)

    # data after ASR processing
    ## raw.plot(duration=10, start=0, title='with ASR auto rejection')

    # detect ECG noise in EEG data, create as events, use annotaion to mark as 'bad' duration to drop
    ecg_events = mne.preprocessing.find_ecg_events(raw, ch_name=raw.ch_names[2], tstart=0, return_ecg=True)

    # set boundary
    onsets = ecg_events[0][:, 0] / raw.info["sfreq"] - 0.05
    durations = [0.1] * len(ecg_events[0])
    descriptions = ['bad'] * len(ecg_events[0])

    # convert event to annotation
    ecg_annot = mne.Annotations(
        onsets, durations, descriptions, orig_time=raw.info["meas_date"]
    )

    raw.set_annotations(ecg_annot)

    # plot with annotation
    eeg_picks = mne.pick_types(raw.info, meg=False, eeg=True)

    # raw.plot(duration=10, start=50, events=ecg_events[0], order=eeg_picks)

    # len(raw.annotations)

    crop_raw = reject_bad_segs(raw)
    # data with bad duration exclueded
    ##crop_raw.plot(duration=10, start=50)
    # crop_raw.info

    # Remove NaN values
    raw_data_no_nan = crop_raw._data[:, ~np.isnan(crop_raw._data).any(axis=0)]

    # create a tem raw data to distinguish with orignial raw data
    tem_raw = mne.io.RawArray(raw_data_no_nan, crop_raw.info)

    # tem_raw.plot_psd()

    # tem_raw.plot()

    # use asr algorithm again after ECG noise rejection
    # with self defined rejecting power (higher than first time)

    tem_raw = asr_noise_rejection(data=tem_raw, cutoff=2.5, win_len=3)
    ##tem_raw.plot(duration=10, start=0, title='with ASR auto rejection')

    # return preprocessed raw data

    return tem_raw, raw_data_no_nan
