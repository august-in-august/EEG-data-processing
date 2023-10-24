import os
import pandas as pd


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

#%%
