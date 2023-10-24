#### use asr algorithm to handle big noise pattern
import asrpy
import mne


def asr_noise_rejection(data, freq=250, blocksize=200, cutoff=20, win_len=0.5, win_overlap=0.66):
    """
    ASR auto noise rejction
    Find big noise segment

    Artifact subspace reconstruction (ASR) is an automated, online,
    component-based artifact removal method for removing transient or
    large-amplitude artifacts in multi-channel EEG recordings [1]_.

    Parameters
    ----------
    cutoff: float
        Standard deviation cutoff for rejection. X portions whose variance
        is larger than this threshold relative to the calibration data are
        considered missing data and will be removed. The most aggressive value
        that can be used without losing too much EEG is 2.5. Recommended to
        use with more conservative values ranging from 20 - 30.
        Defaults to 20.
    blocksize : int
        Block size for calculating the robust data covariance and thresholds,
        in samples; allows to reduce the memory and time requirements of the
        robust estimators by this factor (down to Channels x Channels x Samples
        x 16 / Blocksize bytes) (default=100).
    win_len : float
        Window length (s) that is used to check the data for artifact content.
        This is ideally as long as the expected time scale of the artifacts but
        not shorter than half a cycle of the high-pass filter that was used
        (default=0.5).
    win_overlap : float
        Window overlap fraction. The fraction of two successive windows that
        overlaps. Higher overlap ensures that fewer artifact portions are going
        to be missed, but is slower (default=0.66).
    """

    asr = asrpy.ASR(
        sfreq=freq,
        blocksize=blocksize,
        cutoff=cutoff,
        win_len=win_len,
        win_overlap=win_overlap
    )

    asr.fit(data.load_data())
    data = asr.transform(data.load_data())

    return data



#### Function to do slicing to crop bad durations out
def reject_bad_segs(raw):
    """ This function rejects all time spans annotated as 'bad' and concatenates the rest"""
    container_list = []
    for index in range(len(raw.annotations) - 1):  # index start with 0
        copy = raw.copy()
        duration = 0.2

        if index == 0:
            try:
                cropped_raw = raw.copy().crop(tmin=0, tmax=raw.annotations[index]['onset'] - duration / 2)
            except ValueError:
                cropped_raw = raw.copy()

        else:
            try:
                cropped_raw = raw.copy().crop(tmin=raw.annotations[index]['onset'] + duration / 2,
                                              tmax=raw.annotations[index + 1]['onset'] - duration / 2)
            except ValueError:
                cropped_raw = raw.copy().crop()

        container_list.append(cropped_raw)

    concatenated_raw = mne.concatenate_raws(container_list)
    return concatenated_raw
