from coffea.util import load
import hist
import matplotlib.pyplot as plt
import mplhep as hep
import os
import numpy as np
import pandas as pd

#########################
# Load the coffea files #
#########################
print("Loading coffea files...")
input_path = "outputs/FCCee/higgs/mH-recoil/mumu/"
filename = "mHrecoil_mumu.coffea"
input = load(input_path+filename)
key = "p8_ee_ZH_ecm240"
dataset_keys = ["p8_ee_ZH_ecm240","p8_ee_ZZ_ecm240","p8_ee_WW_ecm240"]
selection_dictionary = input[key]['histograms']

###################
# Plot Properties #
###################
plot_props = {
    'Zm':{'name':'Zm','title':'Z Candidate mass','xlabel':'$Z_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':0,'xmax':250,'color':'g','histtype':'fill'},
    'Zm_zoom':{'name':'Zm_zoom','title':'Z Candidate mass','xlabel':'$Z_{mass}$ [GeV]','ylabel':'Events','bins':40,'xmin':80,'xmax':100,'color':'g','histtype':'fill'},
    'Recoilm':{'name':'Recoilm','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':0,'xmax':200,'color':'r','histtype':'fill'},
    'Recoilm_zoom':{'name':'Recoilm_zoom','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':200,'xmin':80,'xmax':160,'color':'r','histtype':'fill'},
    'Recoilm_zoom1':{'name':'Recoilm_zoom1','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':120,'xmax':140,'color':'r','histtype':'fill'},
    'Recoilm_zoom2':{'name':'Recoilm_zoom2','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':200,'xmin':120,'xmax':140,'color':'r','histtype':'fill'},
    'Recoilm_zoom3':{'name':'Recoilm_zoom3','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':400,'xmin':120,'xmax':140,'color':'r','histtype':'fill'},
    'Recoilm_zoom4':{'name':'Recoilm_zoom4','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':800,'xmin':120,'xmax':140,'color':'r','histtype':'fill'},
    'Recoilm_zoom5':{'name':'Recoilm_zoom5','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':2000,'xmin':120,'xmax':140,'color':'r','histtype':'fill'},
    'Recoilm_zoom6':{'name':'Recoilm_zoom6','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':130.3,'xmax':140,'color':'r','histtype':'fill'}
}
props = pd.DataFrame(plot_props)

#Choose the required plots here
selections = ['sel0','sel1']
stack = [True, False]
log = [True, False]
formats = ['png','pdf']
req_plots = ['Zm', 'Zm_zoom', 'Recoilm', 'Recoilm_zoom', 'Recoilm_zoom1']

#######################
# Plot the histograms #
#######################

print("Plotting...")
plot_path = 'outputs/FCCee/higgs/mH-recoil/mumu/plots/'
if not os.path.exists(plot_path):
    os.makedirs(plot_path)

def plots(selections, req_plots, stack, log, formats, path):
    '''
    Batch plot processor
    '''
    for sel in selections:
        print('_________________________________________________________________')
        print('---------------------','Selection:', sel ,'---------------------')
        hists = selection_dictionary[sel]
        plot_path_selection = path+sel+'/'
        if not os.path.exists(plot_path_selection):
            os.makedirs(plot_path_selection)
        for hist_name in req_plots:
            hist = hists[hist_name]
            print(hist_name, ' : ', props[hist_name].title)
            print('---------------------------------------------------------------')
            for log_mode in log :
                for stack_mode in stack:
                    makeplot(
                        hist=hist,
                        name=props[hist_name].name,
                        title=props[hist_name].title,
                        xlabel=props[hist_name].xlabel,
                        ylabel=props[hist_name].ylabel,
                        bins=props[hist_name].bins,
                        xmin=props[hist_name].xmin,
                        xmax=props[hist_name].xmax,
                        log=log_mode,
                        stack=stack_mode,
                        color=props[hist_name].color,
                        histtype=props[hist_name].histtype,
                        formats=formats, #is an array
                        path=plot_path_selection
                    )
            print('-------------------------------------------------------------------')
        print('_____________________________________________________________________\n')

def makeplot(hist, name, title, xlabel, ylabel, bins, xmin, xmax, log, stack, color, histtype, formats, path):
    '''
    Makes a single kinematic plot
    '''
    fig, ax = plt.subplots(figsize=(8,8))
    hep.histplot(
        hist,
        yerr=0,
        histtype=histtype,
        label=title,
        color=color,
        alpha=0.8,
        stack=stack,
        edgecolor='black',
        linewidth=1,
        ax=ax
    )

    # plt.text("Preliminary",0,0)
    ax.text(0.20, 1.02, 'FCC Analyses: FCC Simulation Delphes', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.92, 1.02, '$\\sqrt{s} = 240GeV$', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.84,0.54, 'FCCee', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.84,0.50, 'Sample = p8_ee_ZH_ecm240', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    n_xticks = 10
    per_bin = '/'+str((xmax-xmin)/bins)
    ax.set_ylabel(ylabel+per_bin+' [GeV]')
    ax.set_xlabel(xlabel)
    plt.xlim([xmin,xmax])
    plt.xticks(np.linspace(xmin,xmax,n_xticks+1))
    
    if log :
        ax.set_yscale('log')
        log_mode_text = 'log'
    else :
        log_mode_text = 'linear'

    if stack :
        stack_mode_text = 'stacked'
    else :
        stack_mode_text = 'unstacked'
    
    ax.set_title(title,pad=25,  fontsize= "15", color="#192655")
    # ax.axvline(91,label="91 GeV", color='r', linestyle='--')
    fig.legend(prop={"size":10},loc= (0.64,0.64) )

    for format in formats :
        filename = name+'_'+log_mode_text+'_'+stack_mode_text+'.'+format
        full_name = path+filename
        fig.savefig(full_name,dpi=240);
        print(filename, " saved at ", path)
    plt.close()



plots(selections, req_plots, stack, log, formats, plot_path)
