from coffea import processor
from coffea.analysis_tools import PackedSelection
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


#################################
#Begin the processor definition #
#################################
class mHrecoil(processor.ProcessorABC):
    '''
    mHrecoil example: e^+ + e^- rightarrow ZH rightarrow mu^+ mu^- + X(Recoil)
    Note: Use only BaseSchema with this processor
    '''
    def __init__(self):
        pass
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
        
        # Produce all the combinations of Muon Pairs possible within an event
        combs = dak.combinations(Muon,2)
        
        # Get dimuons
        mu1 , mu2 = dak.unzip(combs)
        di_muon = mu1 + mu2
        
        # Selection 0 : Only one Z candidate in an event
        di_muon = dak.mask(di_muon, dak.num(di_muon) == 1)
        cut.add('$N_Z$',dak.num(Muon) == 2 ) #Having one Z candidate is same as having exactly two muons in an even
        
        # Choose dimuon which is made up of two oppositely charged muons
        q_sum = mu1.q + mu2.q
        q_sum_array = dak.mask(q_sum, ak.num(q_sum) == 1)
        q_sum_mask = dak.all(q_sum_array == 0, axis=1)
        Z_cand = dak.mask(di_muon , q_sum_mask)
        cut.add('Opp charge muons',q_sum_mask)
        
        
        #Recoil Calculation
        ecm = 240.0 #GeV # com energy
        Recoil = ak.zip({"px":0.0-Z_cand.px,"py":0.0-Z_cand.py,"pz":0.0-Z_cand.pz,"E":ecm-Z_cand.E},with_name="Momentum4D")
        
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
