from coffea.util import load
import hist
import matplotlib.pyplot as plt
import mplhep as hep
import os
import numpy as np
import pandas as pd
import  collections


#########################
# Load the coffea files #
#########################
print("Loading coffea files...")
input_path = "outputs/FCCee/higgs/mH-recoil/mumu/"
filename = "mHrecoil_mumu.coffea"
input = load(input_path+filename)


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

cross_sections = { # Taken as is from https://github.com/HEP-FCC/FCCAnalyses/blob/master/examples/FCCee/higgs/mH-recoil/histmaker_mumu.py#L7
    'p8_ee_WW_ecm240': 0.25792,
    'p8_ee_ZZ_ecm240': 2 * 1.35899 * 0.034 * 0.152,
    'p8_ee_ZH_ecm240': 0.201868 * 0.034
}

##################################
# Choose the required plots here #
##################################
selections = ['sel0','sel1']
stack = [True, False]
log = [True, False]
formats = ['png','pdf']
req_plots = ['Zm', 'Zm_zoom', 'Recoilm', 'Recoilm_zoom', 'Recoilm_zoom1']
req_hists = {
    "ZH":{"datasets":['p8_ee_ZH_ecm240'],"color":'r'},
    "ZZ":{"datasets":['p8_ee_ZZ_ecm240'],"color":'g'},
    "WW":{"datasets":['p8_ee_WW_ecm240'],"color":'b'}
}
plot_path = 'outputs/FCCee/higgs/mH-recoil/mumu/plots/'
intLumi        = 5.0e+06 #in pb-1
ana_tex        = 'e^{+}e^{-} \\rightarrow ZH \\rightarrow \\mu^{+}\\mu^{-} + X'
delphesVersion = '3.4.2'
energy         = 240.0 #in GeV
collider       = 'FCC-ee'

#######################
# Plot the histograms #
#######################
print("Plotting...")
if not os.path.exists(plot_path):
    os.makedirs(plot_path)

def accumulate(dicts):
    """
    Merges an array of dictionaries and adds up the values of common keys.
    
    Parameters:
    dicts (list): A list of dictionaries to be merged.
    
    Returns:
    dict: A dictionary with combined keys and values summed for common keys.
    """
    dict = {}
    
    for dictionary in dicts:
        for key, value in dictionary.items():
            if key in dict:
                dict[key] += value  # Add values if the key is common
            else:
                dict[key] = value  # Otherwise, add the new key-value pair 
    return dict

def get_cutflow_props(object_list):
    '''
    Takes in a list of cutflow objects and returns the sum of their component arrays
    '''
    onecut_list = []
    cutflow_list = []
    labels_list = object_list[0].result().labels
    nevonecut_list = []
    nevcutflow_list = []
    for object in object_list:
        res = object.result()
        if res.labels == labels_list :
            nevonecut_list.append(np.array(res.nevonecut))
            nevcutflow_list.append(np.array(res.nevcutflow))
            onecut_hist, cutflow_hist,l = object.yieldhist() 
            onecut_list.append(onecut_hist)
            cutflow_list.append(cutflow_hist)
        else :
            raise "The labels of cutflow objects do not match."
    nevonecut = sum(nevonecut_list)
    nevcutflow = sum(nevcutflow_list)
    onecut = sum(onecut_list)
    cutflow = sum(cutflow_list)
    c = collections.namedtuple('Cutflow',['labels','onecut','nevonecut','cutflow','nevcutflow'])
    return c(labels_list, onecut, nevonecut, cutflow, nevcutflow)


def yield_plot(name, title, keys, cutflow_obs, formats, path):
    '''
    Create yield plots
    '''
    fig, ax = plt.subplots(figsize=(8,8))
    ax.text(0.25, 1.02, 'FCC Analyses: FCC Simulation Delphes', fontsize=10, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.92, 1.02, '$\\sqrt{s} = '+str(energy)+' GeV$', fontsize=10, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.10, 0.90, collider, fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.10, 0.80,'Delphes Version: '+delphesVersion, fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.10, 0.70, 'Signal : $'+ana_tex+'$', fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.10, 0.60, '$L = '+str(intLumi/1e6)+' ab^{-1}$', fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)

    ax.text(0.10, 0.50, 'Sample', weight='bold', fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.40, 0.50, 'Yield', weight='bold', fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.70, 0.50, 'RawMC', weight='bold', fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)

    linespacing = 0.05
    for i in range(len(keys)):
        datasets = req_hists[list(keys)[i]]['datasets'] 
        color = req_hists[list(keys)[i]]['color']
        ax.text(0.10, 0.40-linespacing, datasets, fontsize=10, color=color,horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
        ax.text(0.40, 0.40-linespacing, cutflow_obs[i].nevcutflow[-1], color=color,fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
        ax.text(0.70, 0.40-linespacing, cutflow_obs[i].nevcutflow[0], color=color, fontsize=12, horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
        linespacing -= 0.05

    ax.set_title(title,pad=25,  fontsize= "15", color="#192655")
    for format in formats :
        filename = name+'.'+format
        full_name = path+filename
        fig.savefig(full_name,dpi=240);
        print(filename, " saved at ", path)
    

def cutflow(input_dict, req_hists, selections, stack, log, formats, path):
    '''
    Create cutflow and yield plots
    '''
    print('___________________________________________________________________')
    print('_____________________________Cutflows______________________________')
    for sel in selections:
        print('___________________________________________________________________')
        print('------------------------','Selection:', sel ,'--------------------------')

        cutflow_by_key = []
        # To create the yield summary
        for key in req_hists.keys():
            datasets = req_hists[key]['datasets']
            cutflow_object_list = []
            print('-------------------------------------------------------------------')
            print(f"Key: {key}            Sample:{datasets} ")
            print('-------------------------------------------------------------------')
            for i in datasets:
                object = input_dict[i]['cutflow'][sel]
                cutflow_object_list.append(object)
                object.print()
            cutflow = get_cutflow_props(cutflow_object_list)
            cutflow_by_key.append(cutflow) 

        hists = [cutflow_object.cutflow for cutflow_object in cutflow_by_key]
        ncuts = len(cutflow_by_key[0].labels)
        xticks = np.arange(ncuts)
        # print('xticks', xticks)
        color_list = [req_hists[key]['color'] for key in req_hists.keys()]
        plot_path_selection = path+sel+'/'
        if not os.path.exists(plot_path_selection):
            os.makedirs(plot_path_selection)

        #To create the cutflow plots
        print('-------------------------------------------------------------------')
        for log_mode in log:
            for stack_mode in stack:
                fig, ax = plt.subplots(figsize=(8,8))
                makeplot(
                    fig=fig,
                    ax=ax,
                    hist=hists,
                    name='Cutflow',
                    title=sel+' Cutflow',
                    label=req_hists.keys(),
                    xlabel='Cut Order',
                    ylabel='Events',
                    bins=len(xticks)+1,
                    xmin=xticks[0],
                    xmax=xticks[-1],
                    log=log_mode,
                    stack=stack_mode,
                    # color=props[hist_name].color,
                    color=color_list,
                    histtype='fill',
                    formats=formats, #is an array
                    path=plot_path_selection,
                    # xticks = xticks,
                    cutflow_mode=True
                )
                plt.close()
        yield_plot(
            name='Yield',
            title=f'{sel} Yield',
            keys=req_hists.keys(),
            cutflow_obs=cutflow_by_key,
            # rawstats= raw_nev,
            formats=formats,
            path=plot_path_selection
        )
        print('-------------------------------------------------------------------')
        print('_____________________________________________________________________\n')
        

def plots(input_dict, req_hists, req_plots, selections, stack, log, formats, path):
    '''
    Batch plot processor
    '''
    for sel in selections:
        print('_________________________________________________________________')
        print('---------------------','Selection:', sel ,'---------------------')

        #Get hist array for different backgrounds
        label_list = []
        dataset_list = []
        color_list = []
        hist_list = []
        for key in req_hists :
            label = key
            datasets = req_hists[key]['datasets']
            color = req_hists[key]['color']
            hists = []
            for i in datasets:
                hist = input_dict[i]['histograms'][sel]
                hists.append(hist)
            label_list.append(label)
            dataset_list.append(datasets)
            color_list.append(color)
            hist_list.append(accumulate(hists))

        plot_path_selection = path+sel+'/'
        if not os.path.exists(plot_path_selection):
            os.makedirs(plot_path_selection)
            
        for hist_name in req_plots:
            hist = [hists[hist_name] for hists in hist_list]
            
            print(hist_name, ' : ', props[hist_name].title)
            print('---------------------------------------------------------------')
            for log_mode in log :
                for stack_mode in stack:
                    fig, ax = plt.subplots(figsize=(8,8))
                    makeplot(
                        fig=fig,
                        ax=ax,
                        hist=hist,
                        name=props[hist_name].name,
                        title=props[hist_name].title,
                        label=label_list,
                        xlabel=props[hist_name].xlabel,
                        ylabel=props[hist_name].ylabel,
                        bins=props[hist_name].bins,
                        xmin=props[hist_name].xmin,
                        xmax=props[hist_name].xmax,
                        log=log_mode,
                        stack=stack_mode,
                        # color=props[hist_name].color,
                        color=color_list,
                        histtype=props[hist_name].histtype,
                        formats=formats, #is an array
                        path=plot_path_selection
                    )
                    plt.close()
            print('-------------------------------------------------------------------')
        print('_____________________________________________________________________\n')

def makeplot(fig, ax, hist, name, title, label, xlabel, ylabel, bins, xmin, xmax, log, stack, color, histtype, formats, path, xticks=10, cutflow_mode=False):
    '''
    Makes a single kinematic plot
    '''
    hep.histplot(
        hist,
        yerr=0,
        histtype=histtype,
        label=label,
        color=color,
        alpha=0.8,
        stack=stack,
        edgecolor='black',
        linewidth=1,
        ax=ax
    )

    # plt.text("Preliminary",0,0)
    ax.text(0.25, 1.02, 'FCC Analyses: FCC Simulation Delphes', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.text(0.92, 1.02, '$\\sqrt{s} = 240GeV$', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    #ax.text(0.84,0.54, 'FCCee', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    #ax.text(0.84,0.50, 'Sample = p8_ee_ZH_ecm240', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    # n_xticks = 10
    if  cutflow_mode:
        ax.set_ylabel(ylabel)
        # plt.xticks(xticks) #input xticks as an array for  cutflows
    else:
        per_bin = '/'+str((xmax-xmin)/bins)
        ax.set_ylabel(ylabel+per_bin+' [GeV]')
        plt.xlim([xmin,xmax])
        plt.xticks(np.linspace(xmin,xmax,xticks+1))
    ax.set_xlabel(xlabel)
    
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
    fig.legend(prop={"size":10},loc= (0.74,0.74) )

    for format in formats :
        filename = name+'_'+log_mode_text+'_'+stack_mode_text+'.'+format
        full_name = path+filename
        fig.savefig(full_name,dpi=240);
        print(filename, " saved at ", path)

###############################
# Call the plotting functions #
###############################
cutflow(input, req_hists, selections, stack, log, formats, plot_path)
# plots(input, req_hists, req_plots, selections, stack, log, formats, plot_path)
