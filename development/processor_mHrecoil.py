from coffea import processor
from coffea.analysis_tools import PackedSelection
import awkward as ak
import pandas as pd
import hist
import numba
import vector
vector.register_awkward()

##############################################
# Define plot properties
plot_props = pd.DataFrame({
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
})
def get_1Dhist(name, var, flatten=True):
    '''
    name: eg. Zm
    var: eg. variable containing array of mass of Z
    flatten: If to flatten var before fill; True by default
    Returns a histogram
    '''
    props = plot_props[name]
    if flatten : var = ak.flatten(var)
    return hist.Hist.new.Reg(props.bins, props.xmin, props.xmax).Double().fill(var)

##############################################
def index_mask(input_array, index_array):
    '''
    This function matches the given attribute of ReconstructedParticles (for example energy) to the particle index (for example Muon or Electron).
    Note: Input and output are both awkward.Array; dask_awkward is not supported at this moment
    '''
    if len(input_array) != len(index_array) :
        raise Exception(f'Length of input_array({len(input_array)}) and index_array({len(index_array)}) does not match!')
    counts = len(input_array)

    @numba.jit
    def numba_wrap(input_array, index_array,counts):
        output_array = []
        for event_index in range(counts):
            event_mask = index_array[event_index]
            reco_list = input_array[event_index]
            output_array.append([reco_list[i] for i in  event_mask])
        return output_array
    out = ak.Array(numba_wrap(input_array,index_array,counts))

    return out

###############################################
#Begin the processor definition
class mHrecoil(processor.ProcessorABC):
    '''
    mHrecoil example: e^+ + e^- rightarrow ZH rightarrow mu^+ mu^- + X(Recoil)
    Note: Use only BaseSchema with this processor
    '''
    def __init__(self):
        pass
    def process(self,events):
        # Create a Packed Selection object to get a cutflow later
        cut = PackedSelection()
        Recon = events['ReconstructedParticles/ReconstructedParticles.energy']
        cut.add('No cut', ak.all(Recon.compute() > 0, axis=1))

        # Filter out any event with no reconstructed particles and generate Reconstructed Particle Attributes
        #ak.mask preserves array length
        Reco_E = ak.mask(events['ReconstructedParticles/ReconstructedParticles.energy'],ak.num(Recon) > 0).compute()
        Reco_px = ak.mask(events['ReconstructedParticles/ReconstructedParticles.momentum.x'],ak.num(Recon) > 0).compute()
        Reco_py = ak.mask(events['ReconstructedParticles/ReconstructedParticles.momentum.y'],ak.num(Recon) > 0).compute()
        Reco_pz = ak.mask(events['ReconstructedParticles/ReconstructedParticles.momentum.z'],ak.num(Recon) > 0).compute()
        Reco_q = ak.mask(events['ReconstructedParticles/ReconstructedParticles.charge'],ak.num(Recon) > 0).compute()
        Reco_mass = ak.mask(events['ReconstructedParticles/ReconstructedParticles.mass'],ak.num(Recon) > 0).compute()
        cut.add('At least one Reco Particle', ak.all(Reco_E > 0, axis=1))

        # Generate Muon Attributes
        Muon_index = events['Muon#0/Muon#0.index'].compute()
        Muon_E = index_mask(Reco_E,Muon_index)
        Muon_px = index_mask(Reco_px,Muon_index)
        Muon_py = index_mask(Reco_py,Muon_index)
        Muon_pz = index_mask(Reco_pz,Muon_index)
        Muon_q = index_mask(Reco_q,Muon_index)
        Muon_mass = index_mask(Reco_mass,Muon_index)

        # Create Array of Muon Lorentz Vector
        Muon = ak.zip({"px":Muon_px,"py":Muon_py,"pz":Muon_pz,"E":Muon_E,"q":Muon_q,}, with_name="Momentum4D")

        # Muon pt > 10
        Muon_pt_cut = ak.all(Muon.pt > 10, axis=1)
        Muon = ak.mask(Muon, Muon_pt_cut) #ak.mask to preserve number of events
        cut.add('Muon $p_T$ > 10 [GeV]',Muon_pt_cut)

        # Produce all the combinations of Muon Pairs possible within an event
        combs = ak.combinations(Muon,2)

        # Get dimuons
        mu1 , mu2 = ak.unzip(combs)
        di_muon = mu1 + mu2

        # Selection 0 : Only one Z candidate in an event
        di_muon = ak.mask(di_muon, ak.num(di_muon) == 1)
        di_muon_mass = ak.flatten(di_muon.mass)
        cut.add('$N_Z$',ak.num(Muon) == 2 ) #Having one Z candidate is same as having exactly two muons in an even

        # Choose dimuon which is made up of two oppositely charged muons
        q_sum = mu1.q + mu2.q
        q_sum_array = ak.mask(q_sum, ak.num(q_sum) == 1)
        q_sum_mask = ak.all(q_sum_array == 0, axis=1)
        Z_cand = ak.mask(di_muon , q_sum_mask)
        cut.add('Opp charge muons',q_sum_mask)

        #Recoil Calculation
        ecm = 240 #GeV # com energy
        initial = ak.zip({"px":0,"py":0,"pz":0,"E":ecm}, with_name="Momentum4D")
        Recoil = initial - Z_cand

        # Selection 1 : Selection 0 + 80 < M_Z < 100
        zmassmask = (Z_cand.mass > 80) & (Z_cand.mass < 100)
        Z_cand_sel1 = Z_cand[zmassmask]
        Recoil_sel1 = Recoil[zmassmask]
        zmassmask = ak.fill_none(zmassmask,[False],axis=0) #Replace None values at axis 0 with [False]
        zmassmask = ak.flatten(zmassmask)
        cut.add('80 < $M_Z$ < 100',zmassmask)

        #Prepare cutflows
        sel0_list = ['No cut','At least one Reco Particle', 'Muon $p_T$ > 10 [GeV]', '$N_Z$', 'Opp charge muons' ]
        sel1_list = ['No cut','At least one Reco Particle', 'Muon $p_T$ > 10 [GeV]', '$N_Z$', 'Opp charge muons', '80 < $M_Z$ < 100']
        sel0 = cut.cutflow(*sel0_list)
        sel1 = cut.cutflow(*sel1_list)

        #Prepare output
        #Choose the required histograms and their assigned variables to fill
        names = ['Zm','Zm_zoom','Recoilm','Recoilm_zoom','Recoilm_zoom1','Recoilm_zoom2','Recoilm_zoom3','Recoilm_zoom4','Recoilm_zoom5','Recoilm_zoom6']
        vars_sel0 = ([Z_cand.mass]*2) + ([Recoil.mass]*8)
        vars_sel1 = ([Z_cand_sel1.mass]*2) + ([Recoil_sel1.mass]*8)
        Output = {
            'histograms': {
                'sel0':{name:get_1Dhist(name,var) for name,var in zip(names,vars_sel0)},
                'sel1':{name:get_1Dhist(name,var) for name,var in zip(names,vars_sel1)}
            },
            'cutflow': { #cutflow objects
                'sel0': sel0,
                'sel1': sel1
            }
        }

        return Output

    def postprocess(self, accumulator):
        pass
