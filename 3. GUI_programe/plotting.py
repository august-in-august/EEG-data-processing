import os
from matplotlib import pyplot as plt



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