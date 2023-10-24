# packages need for this script

# pip install mne
# pip install numpy
# pip install pandas
# pip install matplotlib
# pip install asrpy    #asr algorithm -> automatic noise rejection

# pip install EDFlib-Python  # export data to edf format
# pip install eeglabio # export data to .set format, which can be imported to eeglab
# pip install openpyxl   #convert results into excel
# pip install XlsxWriter  #write dataframe into excel


#### import packages
import os
# import mne
# import numpy as np
# import pandas as pd
# import asrpy
# import matplotlib.pyplot as plt

# interactive plot
# %matplotlib widget

# static plot
# %matplotlib inline


#### import self defined functions
from preprocessing import preprocessing_eeg
from power_compute import power_computation
from plotting import power_plot, power_plot_save
from save_results import power_saving, processed_file_saving

if __name__ == '__main__':

    path = os.getcwd()
    # os.chdir(path+'/multi data processing')
    path = os.getcwd()

    # get file names for further processing

    extensions = ('.edf')


    def get_edf(path, extensions):
        files = []
        for file in os.listdir(path):
            if file.endswith(extensions):
                files.append(file.strip('edf').strip('.'))
        return files


    list_files = get_edf(path, extensions)

    for each in list_files:
        print(each)

    #### Compute power and save files

    # Store computed power (Dataframe)
    abs_power_set = []
    rel_power_set = []
    files = []

    for each in list_files:
        files.append(each)
        # Preprocess
        tem_raw, raw_data_no_nan = preprocessing_eeg(fname=each)

        # Get power with FFT transform
        power, rel_power = power_computation(data=raw_data_no_nan, tem_raw=tem_raw)

        abs_power_set.append(power)
        rel_power_set.append(rel_power)

        # PSD plot
        # psd_plot(data=tem_raw)

        # Power plot
        power_plot(power=power, rel_power=rel_power, title=each)

        # Save each data into edf and .set under new directory named as data name
        processed_file_saving(data=tem_raw, fname=each, path=path)

        # Save power plot
        power_plot_save(power=power, rel_power=rel_power, title=each, path=path)

    # save dataframes into excel file, each dataframe as a separate TAB in Excel
    power_saving(abs_power=abs_power_set, rel_power=rel_power_set, fnames=files)
