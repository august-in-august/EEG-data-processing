import mne
import numpy as np
import pandas as pd


def power_computation(data=None, tem_raw=None):
    """
    Input: numpy Array
    Outputs: 1. absolute power,  2. Relative Power
    """
    raw_data_no_nan = data
    # Define EEG bands ( Specifing ranges)
    eeg_bands = {'Delta': (0, 4),
                 'Theta': (4, 8),
                 'Alpha': (9, 12),
                 'Smr': (13, 15),
                 'L-Beta': (16, 20),
                 'H-Beta': (21, 30),
                 'Gamma': (31, 50)}

    col = list(eeg_bands.keys())

    # create a dataframe to store abs power results
    power = pd.DataFrame(np.zeros((4, 7)), columns=col, index=['T7', 'T8', 'Fp1', 'Fp2'])

    # get accumulative power for each band
    for band in eeg_bands:
        psds, freqs = mne.time_frequency.psd_array_welch(raw_data_no_nan, sfreq=tem_raw.info['sfreq'],
                                                         fmin=eeg_bands[band][0], fmax=eeg_bands[band][1])
        for ch in range(0, len(psds)):
            # ch_avg.append(np.mean(psds[ch]))
            # print(len(psds[ch]))
            power[band][ch] = np.sum(psds[ch])

            # get sum of each rows ( To calculate relative power)
    power['Total'] = power.sum(axis=1)

    # Get relative power
    rel_power = np.zeros(power.shape)
    for i in range(0, power.shape[0]):
        for j in range(0, power.shape[1]):
            rel_power[i][j] = power.iloc[i][j] / power.iloc[i][7]

    # create a dataframe to store relative power
    rel_power = pd.DataFrame(data=rel_power, index=power.index, columns=power.columns)
    rel_power.drop(columns='Total', inplace=True)

    power.drop(columns='Total', inplace=True)

    return power, rel_power
