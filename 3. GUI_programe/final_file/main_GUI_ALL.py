# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#### import self defined functions
#from preprocessing import preprocessing_eeg
#from power_compute import power_computation
#from plotting import power_plot, power_plot_save
#from save_results import power_saving, processed_file_saving


# self defined functions and import statement
import mne
import numpy as np
#from noise_rejction import asr_noise_rejection, reject_bad_segs
import pandas as pd
import asrpy




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
    ecg_events = mne.preprocessing.find_ecg_events(raw, ch_name='EEG100C-1', tstart=0, return_ecg=True)

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

#############################################




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

#############################################



### MNE function to plot PSD of raw format data
def psd_plot(data=None):
    # plot processed data (PSD and Spectrogram)
    data = data
    data.plot_psd(fmin=1, fmax=60, spatial_colors=False)



### Function to plot abs power and rel power
def power_plot(power=None, rel_power=None, title=None):

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))

    fig.suptitle(title)

    # absolute  power plot
    ax1.plot(power.T)
    ax1.set_title('Absolute power')

    #relative power plot
    ax2.plot(rel_power.T)
    ax2.set_title('Relative power')
    #power.iloc[:, :-1].T.plot(title=)
    #rel_power.T.plot(title=)

    plt.show()



def power_plot_save(power=None, rel_power=None, title=None, path=os.getcwd()):


    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))

    fig.suptitle(title)

    # absolute  power plot
    ax1.plot(power.T)
    ax1.set_title('Absolute power')

    #relative power plot
    ax2.plot(rel_power.T)
    ax2.set_title('Relative power')
    #power.iloc[:, :-1].T.plot(title=)
    #rel_power.T.plot(title=)

    try:
        os.mkdir(title)
    except:
        pass
    os.chdir(path+'/'+title)

    plt.savefig(title+'.png', dpi=100)
    plt.close()
    os.chdir(path)

#############################################
#### use asr algorithm to handle big noise pattern



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


#############################################



### Function to save preprocessed data into edf and temporal eeglab set format
def processed_file_saving(data=None, fname=None, path=os.getcwd()):
    """
    input: raw data format, file name
    """
    try:
        os.chdir(path)
        os.mkdir(fname)
    except:
        pass
    os.chdir(path + '/' + fname)
    #os.chdir(os.path.join(path, fname))
    data = data
    # save processed data (raw data after filtering and ecg noise rejection, ars noise rejction
    data.export(fname=fname + '.edf', fmt='edf', overwrite=True)
    # save processed data to .set format, use for forther data process by eeglab (If necessray)
    data.export(fname=fname + '.set', fmt='eeglab', overwrite=True)

    os.chdir(path)


#### Function to save computed power (multiple files)

def power_saving(abs_power=None, rel_power=None, fnames=None):
    """
    input: Pandas dataframe of abs_power, rel_power
    """
    writer1 = pd.ExcelWriter('absolute_power.xlsx', engine='xlsxwriter')

    for index in range(0, len(abs_power)):
        abs_power[index].to_excel(writer1, sheet_name=fnames[index])
        # df.to_excel(writer, sheet_name=os.path.splitext(os.path.basename(f))[0], index=False)

    writer1.save()

    writer2 = pd.ExcelWriter('relative_power.xlsx', engine='xlsxwriter')

    for index in range(0, len(rel_power)):
        rel_power[index].to_excel(writer2, sheet_name=fnames[index])
        # df.to_excel(writer, sheet_name=os.path.splitext(os.path.basename(f))[0], index=False)

    writer2.save()

#############################################
#############################################
#############################################


# matplotlib.use('TKAgg')


if __name__ == "__main__":
   
    # define window layout
    sg.set_options(font=('Arial Bold', 13))

    file_list_col = [
        [
            sg.Text('Data Folder'),
            sg.Input(size=(None, 10), enable_events=True, key='-FOLDER-'),
            sg.FolderBrowse(),
        ],

        [
            sg.Listbox(values=[], enable_events=True, size=(400, 400), key='-FILE LIST-'),
        ],

        # [sg.ProgressBar(max_value=100, size=(400,100))],
    ]


    # edf file processing UI

    psd_plot = []
    #psd_plot.append(sg.Text('FFT'))
    psd_plot.append(sg.Canvas(key='-PSD-'))

    abs_plot = []
    #abs_plot.append(sg.Text('Absolute Power'))
    abs_plot.append(sg.Canvas(key='-ABS-'))

    rel_plot = []
    #rel_plot.append(sg.Text('Relative Power'))
    rel_plot.append(sg.Canvas(key='-REL-'))


    psd_frame = sg.Frame('PSD plot', [psd_plot], size=(550, 160))
    abs_frame = sg.Frame('Absolute Power', [abs_plot], size=(550, 160))
    rel_frame = sg.Frame('Relative Power', [rel_plot], size=(550, 160))

    """
    plot_frame = sg.Frame('Plot Results',
                          [
                              #psd_plot,
                              abs_plot,
                              rel_plot],
                          size=(600, 500),
                          expand_x=True,
                          expand_y=True,
                          title_color='blue',
                          grab=True,
                          element_justification='top',
                          key='-PLOT-')

    """


    # create layout

    layout = [
        [sg.Titlebar('EEG preprocessing')],

        [

            sg.Column(file_list_col, size=(400, 500)),
            sg.VSeparator(),
            sg.Column([[psd_frame],[abs_frame],[rel_frame]], size=(600, 500))


        ],

        [
            sg.Button('Preview Selected'),
            sg.Button('Save Selected'),
            sg.Button('Process All Files', button_color='lightblue', ),
            sg.Button('Close', button_color='red'),
            # sg.Text('Path:', size=(100, 10)), sg.Text(key='-PATH-'),
            # sg.Text('File name:', size=(100, 10)), sg.Text(key='-FILE-'),
        ],
    ]

    # create the window

    window = sg.Window("EEG Processing", layout=layout, size=(1000, 600), resizable=True)

    # create an event loop, UI keep running

    while True:
        # read method use to collect the values entered in all input elements
        event, values = window.read()
        # end program if user clicks the button or closes window
        if event == 'Close' or event == sg.WINDOW_CLOSED:
            break

        # make a list of files with filled folder name
        if event == '-FOLDER-':
            folder = values['-FOLDER-']
            try:
                # get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                   and f.lower().endswith(('.edf'))
            ]

            window['-FILE LIST-'].update(fnames)


        # Select a file
        elif event == '-FILE LIST-':
            try:
                # save current work path as variable
                path = values['-FOLDER-']

                # name of selected file
                file = values['-FILE LIST-'][0]

                filename = os.path.join(
                    values['-FOLDER-'], values['-FILE LIST-'][0]
                )

                # debugging -- check path and file name
                # window['-SELECT-'].update(filename)
                # window['-PSD-'].update(filename=filename)
                # window['-IMAGE-'].update(filename=filename)

                # sg.Print(path)
                # sg.Print(filename)

            except:
                pass

        elif event == 'Preview Selected':
            
            try:
                sg.PopupAutoClose('Selected file:'+str(file), auto_close_duration=1)
            except NameError:
                sg.PopupError('Please select a specific file to process')
                continue

            file_name = file.strip('edf').strip('.')
            path_name = path

            # Print function for Debugging
            # sg.Print(path)
            # sg.Print(file)

            os.chdir(path_name)
            # sg.Print(os.getcwd())

            # Preprocess
            tem_raw, raw_data_no_nan = preprocessing_eeg(fname=file_name)

            # Get power with FFT transform
            power, rel_power = power_computation(data=raw_data_no_nan, tem_raw=tem_raw)

            # PSD plot
            # window['-PSD-'].update(sg.Canvas(psd_plot(data=tem_raw)))
            # psd_plot(data=tem_raw)

            # Power plot
            # power_plot(power=power, rel_power=rel_power, title=file_name)

            # Display matplotlib plot in program

            # power_plot(power=power, rel_power=rel_power, title=file_name)



            # function to add matplotlib figure to Canvas element
            def add_plot_to_canvas(fig, canvas):
                canvas = FigureCanvasTkAgg(fig, canvas)
                canvas.draw()
                canvas.get_tk_widget().pack()
                return canvas


            # PSD plot after FFT 
            try:
                canvas_psd.get_tk_widget().forget()
                plt.close(fig0)

            except NameError:
                # generate an empty plot for cold start
                fig0 = tem_raw.plot_psd()
                # plt.Figure(figsize=(6,2))
                fig0.add_subplot(111).plot()
                canvas_psd = window['-PSD-'].TKCanvas
                canvas_psd = add_plot_to_canvas(fig0, canvas_psd)
                canvas_psd.get_tk_widget().forget()
                plt.close(fig0)

            finally:
                
                fig0 = tem_raw.plot_psd(fmin=1, fmax=70, spatial_colors=False, verbose=None)
                canvas_psd = window['-PSD-'].TKCanvas
                
                canvas_psd = add_plot_to_canvas(fig0, canvas_psd)

            pass


            # Absolute power plot
            try:
                # fig1.clf()
                # ax1 = plt.gca()
                # ax1.cla()
                # plt.close(fig1)
                # !!! remove plot from canvas before plot a new figure
                canvas_abs.get_tk_widget().forget()
                plt.close(fig1)

            except NameError:
                fig1 = plt.figure(1)
                # plt.Figure(figsize=(6,2))
                fig1.add_subplot(111).plot()
                canvas_abs = window['-ABS-'].TKCanvas
                canvas_abs = add_plot_to_canvas(fig1, canvas_abs)
                canvas_abs.get_tk_widget().forget()
                plt.close(fig1)

            finally:
                fig1 = plt.figure(1)
                # plt.Figure(figsize=(6,2))
                fig1.add_subplot(111).plot(power.T)
                canvas_abs = window['-ABS-'].TKCanvas

                canvas_abs = add_plot_to_canvas(fig1, canvas_abs)

                # window['-ABS-'].update(visible=True)


            # Relative power plot
            try:
                canvas_rel.get_tk_widget().forget()
                plt.close(fig2)

            except NameError:
                fig2 = plt.figure(2)
                # plt.Figure(figsize=(6,2))
                fig2.add_subplot(111).plot()
                canvas_rel = window['-REL-'].TKCanvas
                canvas_rel = add_plot_to_canvas(fig2, canvas_rel)
                canvas_rel.get_tk_widget().forget()
                plt.close(fig2)

            finally:
                fig2 = plt.figure(2)
                fig2.add_subplot(111).plot(rel_power.T)
                canvas_rel = window['-REL-'].TKCanvas

                canvas_rel = add_plot_to_canvas(fig2, canvas_rel)

            pass

        # Handle single file
        elif event == 'Save Selected':
            try:
                """
                file_name = file.strip('edf').strip('.')
                path_name = path
                
                # Print function for Debugging
                #sg.Print(path)
                #sg.Print(file)
                
                os.chdir(path_name)
                #sg.Print(os.getcwd())
                # Preprocess
                tem_raw, raw_data_no_nan = preprocessing_eeg(fname=file_name)
        
                # Get power with FFT transform
                power, rel_power = power_computation(data=raw_data_no_nan, tem_raw=tem_raw)
        
                # PSD plot
                #window['-PSD-'].update(sg.Canvas(psd_plot(data=tem_raw)))
                #psd_plot(data=tem_raw)
        
                # Power plot
                #power_plot(power=power, rel_power=rel_power, title=file_name)
                
                # Display matplotlib plot in program
                fig0 = matplotlib.figure.Figure(figsize=(5, 4))
                fig0 = tem_raw.plot_psd(fmin=1, fmax=60, spatial_colors=False)
                tkcanvas_psd = FigureCanvasTkAgg(fig0, window['-PSD-'].TKCanvas)
                tkcanvas_psd.draw()
                tkcanvas_psd.get_tk_widget().pack()
        
                #power_plot(power=power, rel_power=rel_power, title=file_name)
                fig1 = matplotlib.figure.Figure(figsize=(5, 4))
                fig1.add_subplot(111).plot(power.T)
                tkcanvas_abs = FigureCanvasTkAgg(fig1, window['-ABS-'].TKCanvas)
                tkcanvas_abs.draw()
                tkcanvas_abs.get_tk_widget().pack()
        
        
                fig2 = matplotlib.figure.Figure(figsize=(5, 4))
                fig2.add_subplot(111).plot(rel_power.T)
                tkcanvas_rel = FigureCanvasTkAgg(fig2, window['-REL-'].TKCanvas)
                tkcanvas_rel.draw()
                tkcanvas_rel.get_tk_widget().pack()
        
                # add popup alert when finished 
                """

                # Save each data into edf and .set under new directory named as data name
                processed_file_saving(data=tem_raw, fname=file_name, path=path_name)

                # Save power plot
                power_plot_save(power=power, rel_power=rel_power, title=file_name, path=path_name)

                sg.popup_ok('Results saved to current folder successfully')
                # sg.Print('file location: '+str(path_name))
                pass
            except:
                sg.popup_error('Please select an file and click preview before save')
                pass


        # Select all files in path = values['-FOLDER-']the list
        elif event == 'Process All Files':
            try:
                sg.PopupAutoClose('Selected path:'+str(path))
            except NameError:
                sg.PopupError('Please select a specific file to process')
                continue
            
            path = folder
            list_files = fnames

            list_files = [f.strip('edf').strip('.') for f in list_files]

            try:
                #### Compute power and save files

                # Store computed power (Dataframe)
                abs_power_set = []
                rel_power_set = []
                files = []

                for each in list_files:
                    sg.Print(each)

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
                    # power_plot(power=power, rel_power=rel_power, title=each)

                    # Save each data into edf and .set under new directory named as data name
                    processed_file_saving(data=tem_raw, fname=each, path=path)

                    # Save power plot
                    power_plot_save(power=power, rel_power=rel_power, title=each, path=path)

                    sg.Print(str(each) + ' Processed successfully')
                    sg.Print('---------------------------')

                # save dataframes into excel file, each dataframe as a separate TAB in Excel
                power_saving(abs_power=abs_power_set, rel_power=rel_power_set, fnames=files)

                sg.Print('All results saved to path: ' + str(path))
                sg.Print('---------------------------')

            except:
                sg.Print('Program went wrong, Please try again')

    window.close()




