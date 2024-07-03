from coffea.util import load
import hist
import matplotlib.pyplot as plt
import mplhep as hep
import os
import numpy as np

#########################
# Load the coffea files #
#########################
print("Loading coffea files...")
input_path = "outputs/FCCee/higgs/mH-recoil/mumu/"
filename = "mHrecoil_mumu.coffea"
input = load(input_path+filename)
key = "p8_ee_ZZ_ecm240"
hists = input[key]['histograms']
Z_mass = hists['Z_mass']
Recoil_mass = hists['Recoil_mass']

#######################
# Plot the histograms #
#######################

print("Plotting...")
plot_path = 'outputs/FCCee/higgs/mH-recoil/mumu/plots/'

fig, ax = plt.subplots(figsize=(8,8))
hep.histplot(
    Z_mass,
    yerr=0,
    histtype='fill',
    label='$Z_{mass}$',
    color='g',
    ax=ax
)
hep.histplot(
    Recoil_mass,
    yerr=0,
    histtype='fill',
    label='$Recoil$',
    color='r',
    ax=ax
)
xlims = [60,160]
# plt.text("Preliminary",0,0)
ax.text(0.20, 1.02, 'FCC Analyses: FCC Simulation Delphes', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
ax.text(0.92, 1.02, '$\\sqrt{s} = 240GeV$', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
ax.text(0.84,0.54, 'FCCee', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
ax.text(0.84,0.50, 'Sample = p8_ee_ZH_ecm240', fontsize=9, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
ax.set_ylabel("Events")
ax.set_xlabel("$Z_{mass}$ [GeV]")
plt.xlim(xlims)
plt.xticks(np.arange(xlims[0],xlims[1],10))
ax.set_title(r"Z Candidate Mass",pad=25,  fontsize= "15", color="#192655")
ax.axvline(91,label="91 GeV", color='r', linestyle='--')
ax.axvline(125,label="125 GeV", color='g', linestyle='--')
fig.legend(prop={"size":15},loc= (0.70,0.64) )

if not os.path.exists(plot_path):
    os.makedirs(plot_path)

print("Saving plots ...")
plotname = 'Z_Peak_with_recoil.png'
fig.savefig(plot_path+plotname,dpi=240);
print(plotname, " saved at ", plot_path, ".\n")