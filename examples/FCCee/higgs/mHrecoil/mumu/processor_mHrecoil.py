from coffea import processor
from coffea.analysis_tools import PackedSelection, Cutflow
import awkward as ak
import pandas as pd
import dask_awkward as dak
import hist.dask as hda
from collections import namedtuple
import hist
import vector
vector.register_awkward()

##########################
# Define plot properties #
##########################
plot_props = pd.DataFrame({
    'Zm':{'name':'Zm','title':'Z Candidate mass','xlabel':'$Z_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':0,'xmax':250},
    'Zm_zoom':{'name':'Zm_zoom','title':'Z Candidate mass','xlabel':'$Z_{mass}$ [GeV]','ylabel':'Events','bins':40,'xmin':80,'xmax':100},
    'Recoilm':{'name':'Recoilm','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':0,'xmax':200},
    'Recoilm_zoom':{'name':'Recoilm_zoom','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':200,'xmin':80,'xmax':160},
    'Recoilm_zoom1':{'name':'Recoilm_zoom1','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':120,'xmax':140},
    'Recoilm_zoom2':{'name':'Recoilm_zoom2','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':200,'xmin':120,'xmax':140},
    'Recoilm_zoom3':{'name':'Recoilm_zoom3','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':400,'xmin':120,'xmax':140},
    'Recoilm_zoom4':{'name':'Recoilm_zoom4','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':800,'xmin':120,'xmax':140},
    'Recoilm_zoom5':{'name':'Recoilm_zoom5','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':2000,'xmin':120,'xmax':140},
    'Recoilm_zoom6':{'name':'Recoilm_zoom6','title':'Leptonic Recoil mass','xlabel':'$Recoil_{mass}$ [GeV]','ylabel':'Events','bins':100,'xmin':130.3,'xmax':140}
})

def get_1Dhist(name, var, flatten=True):
    '''
    name: eg. Zm
    var: eg. variable containing array of mass of Z
    flatten: If to flatten var before fill; True by default
    Returns a histogram
    '''
    props = plot_props[name]
    if flatten : var = dak.ravel(var)
    return hda.Hist.new.Reg(props.bins, props.xmin, props.xmax).Double().fill(var)

def get(events,collection,attribute,*cut):
    '''
    Get an attribute from a branch with or without a base cut.
    '''
    if len(cut) != 0:
        return events[collection+'/'+collection+'.'+attribute][cut[0]]
    return events[collection+'/'+collection+'.'+attribute]

def get_all(events,Collection,*basecut):
    '''
    Collect all the attributes of a collection into a namedtuple named particle, with or without a base cut
    '''
    prefix = '/'.join([Collection]*2)+'.'
    list_of_attr = [field.replace(prefix,'') for field in events.fields if field.startswith(prefix)]
    replace_list = ['.','[',']']
    valid_attr = list_of_attr
    for rep in replace_list:
        valid_attr = [field.replace(rep, '_') for field in valid_attr ]
    part = namedtuple('particle', valid_attr)
    return part(*[get(events,Collection,attr,*basecut) for attr in list_of_attr])

def get_reco(Reconstr_branch, needed_particle, events):
    '''
    Match the Reconstructed collection to the desired particle collection.
    '''
    part = namedtuple('particle', list(Reconstr_branch._fields))
    return part(*[getattr(Reconstr_branch,attr)[get(events,needed_particle,'index')] for attr in Reconstr_branch._fields])

def Reso_builder(lepton,resonance):
    '''
    Builds Resonance candidates with two oppositely charged leptons
    Input:    lepton(var*[var*LorentzVector]),
              resonance(float)
    Output: Reso(var*[var*LorentzVecctor]) sorted best to worst in axis 1
    '''
    #Create all the combinations
    combs = dak.combinations(lepton,2)
    # Get dileptons
    lep1 , lep2 = dak.unzip(combs)
    di_lep = lep1 + lep2
    # Choose dilep pair which is made up of two oppositely charged lep
    q_sum_mask = dak.any((lep1.q + lep2.q) == 0, axis=1)
    di_lep = dak.mask(di_lep , q_sum_mask)
    # Sort by closest mass to the resonance value
    sort_mask = dak.argsort(abs(resonance-di_muon.mass), axis=1)
    Reso = di_lep[sort_mask]
    return Reso

#################################
#Begin the processor definition #
#################################
class mHrecoil(processor.ProcessorABC, ecm):
    '''
    mHrecoil example: e^+ + e^- rightarrow ZH rightarrow mu^+ mu^- + X(Recoil)
    Note: Use only BaseSchema with this processor
    '''
    def __init__(self):
        self.arg_ecm = ecm #\sqrt(s) in GeV
        self.arg_zmass = 91.0 #GeV
        
    def process(self,events):
        
        #Create a Packed Selection object to get a cutflow later
        cut = PackedSelection()
        cut.add('No cut', dak.ones_like(dak.num(get(events,'ReconstructedParticles','energy'),axis=1),dtype=bool))
        
        # Filter out any event with no reconstructed particles and generate Reconstructed Particle Attributes
        #ak.mask preserves array length
        at_least_one_recon = dak.num(get(events,'ReconstructedParticles','energy'), axis=1) > 0
        good_events = dak.mask(events,at_least_one_recon)
        cut.add('At least one Reco Particle', at_least_one_recon)
        
        Reco = get_all(good_events,'ReconstructedParticles')
        Muons = get_reco(Reco,'Muon#0',good_events)
        
        # Create Array of Muon Lorentz Vector
        Muon = ak.zip({"px":Muons.momentum_x,"py":Muons.momentum_y,"pz":Muons.momentum_z,"E":Muons.energy,"q":Muons.charge,}, with_name="Momentum4D")
        
        # Muon pt > 10
        Muon_pt_cut = dak.any(Muon.pt > 10.0, axis=1)
        Muon = dak.mask(Muon, Muon_pt_cut) #ak.mask to preserve number of events
        cut.add('Muon $p_T$ > 10 [GeV]',Muon_pt_cut)
        
        Z_cand = Reso_builder(Muon, arg_zmass)
        
        # Selection 0 : only one Z candidate
        one_z = ak.num(Z_cand,axis=1) == 1
        Z_cand_sel0 = ak.mask(Z_cand, one_z)
        cut.add('$N_Z = 1$', one_z ) 
        sel0_ocl = cut.cutflow(*cut.names).yieldhist()
        
        # Selection 1 : 80 < M_Z < 100
        Z_mass_mask = (Z_cand_sel0.mass > 80.0) & (Z_cand_sel0.mass < 100.0)
        Z_mass_mask = dak.fill_none(Z_mass_mask,[False],axis=0)
        Z_mass_mask = dak.flatten(Z_mass_mask)
        Z_cand_sel1 = ak.mask(Z_cand_sel0, Z_mass_mask)
        cut.add('80 < $M_Z$ < 100',zmassmask)
        sel1_ocl = cut.cutflow(*cut.names).yieldhist()
        
        #Recoil Calculation
        Recoil_sel0 = ak.zip({"px":0.0-Z_cand_sel0.px,"py":0.0-Z_cand_sel0.py,"pz":0.0-Z_cand_sel0.pz,"E":arg_ecm-Z_cand_sel0.E},with_name="Momentum4D")
        Recoil_sel1 = ak.zip({"px":0.0-Z_cand_sel1.px,"py":0.0-Z_cand_sel1.py,"pz":0.0-Z_cand_sel1.pz,"E":arg_ecm-Z_cand_sel1.E},with_name="Momentum4D")
        
        #Prepare output
        #Choose the required histograms and their assigned variables to fill
        names = plot_props.columns.to_list()
        vars_sel0 = ([Z_cand_sel0.mass]*2) + ([Recoil_sel0.mass]*8)
        vars_sel1 = ([Z_cand_sel1.mass]*2) + ([Recoil_sel1.mass]*8)
        Output = {
            'histograms': {
                'sel0':{name:get_1Dhist(name,var) for name,var in zip(names,vars_sel0)},
                'sel1':{name:get_1Dhist(name,var) for name,var in zip(names,vars_sel1)}
            },
            'cutflow': {
                'sel0': {'Onecut':sel0_ocl[0],'Cutflow':sel0_ocl[1],'Labels':sel0_ocl[2]},
                'sel1': {'Onecut':sel1_ocl[0],'Cutflow':sel1_ocl[1],'Labels':sel1_ocl[2]}
            }
        }

        return Output

    def postprocess(self, accumulator):
        pass
