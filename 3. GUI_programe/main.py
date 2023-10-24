# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#### import self defined functions
from preprocessing import preprocessing_eeg
from power_compute import power_computation
from plotting import power_plot, power_plot_save
from save_results import power_saving, processed_file_saving


# matplotlib.use('TKAgg')

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
