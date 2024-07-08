from coffea.nanoevents import BaseSchema, NanoEventsFactory
from coffea import processor
from coffea.analysis_tools import PackedSelection
import dask_awkward as dak
import dask
import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import hist
import mplhep as hep
import numba
import vector
vector.register_awkward()


def index_mask(input_array, index_array):
    '''
    This function matches the given attribute of ReconstructedParticles (for example energy) to the particle index (for example Muon or Electron)
    '''
    # input_array = input_array.compute()
    # index_array = index_array.compute()
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
        
        # Filter out any event with no reconstructed particles
        Recon = events['ReconstructedParticles/ReconstructedParticles.energy']
        cut.add('No cuts', ak.all(Recon > 0, axis=1))
        useful_events = events[ak.num(Recon) > 0]
        
        
        # Generate Reconstructed Particle Attributes
        Reco_E = useful_events['ReconstructedParticles/ReconstructedParticles.energy'].compute()
        Reco_px = useful_events['ReconstructedParticles/ReconstructedParticles.momentum.x'].compute()
        Reco_py = useful_events['ReconstructedParticles/ReconstructedParticles.momentum.y'].compute()
        Reco_pz = useful_events['ReconstructedParticles/ReconstructedParticles.momentum.z'].compute()
        Reco_q = useful_events['ReconstructedParticles/ReconstructedParticles.charge'].compute()
        Reco_mass = useful_events['ReconstructedParticles/ReconstructedParticles.mass'].compute()
        cut.add('At least one Reco Particle', ak.all(Reco_E > 0, axis=1))

        # Generate Muon Attributes
        Muon_index = useful_events['Muon#0/Muon#0.index'].compute()
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
        sel0_list = ['At least one Reco Particle', 'Muon $p_T$ > 10 [GeV]', '$N_Z$', 'Opp charge muons' ]
        sel1_list = ['At least one Reco Particle', 'Muon $p_T$ > 10 [GeV]', '$N_Z$', 'Opp charge muons', '80 < $M_Z$ < 100']
        sel0 = cut.cutflow(*sel0_list)
        sel1 = cut.cutflow(*sel1_list)

        #Prepare output
        Output = {
            'histograms': {
                'sel0': {
                'Zm': hist.Hist.new.Regular(125,0,250).Double().fill(ak.flatten(Z_cand.mass)),
                'Zm_zoom' : hist.Hist.new.Regular(40,80,100).Double().fill(ak.flatten(Z_cand.mass)),
                'Recoilm': hist.Hist.new.Regular(100,0,200).Double().fill(ak.flatten(Recoil.mass)),
                'Recoilm_zoom' : hist.Hist.new.Regular(200,80,160).Double().fill(ak.flatten(Recoil.mass)),
                'Recoilm_zoom1' : hist.Hist.new.Regular(100,120,140).Double().fill(ak.flatten(Recoil.mass)),
                'Recoilm_zoom2' : hist.Hist.new.Regular(200,120,140).Double().fill(ak.flatten(Recoil.mass)),
                'Recoilm_zoom3' : hist.Hist.new.Regular(400,120,140).Double().fill(ak.flatten(Recoil.mass)),
                'Recoilm_zoom4' : hist.Hist.new.Regular(800,120,140).Double().fill(ak.flatten(Recoil.mass)),
                'Recoilm_zoom5' : hist.Hist.new.Regular(2000,120,140).Double().fill(ak.flatten(Recoil.mass)),
                'Recoilm_zoom6' : hist.Hist.new.Regular(100,130.3,132.5).Double().fill(ak.flatten(Recoil.mass))
                },
                'sel1': {
                'Zm': hist.Hist.new.Regular(125,0,250).Double().fill(ak.flatten(Z_cand_sel1.mass)),
                'Zm_zoom' : hist.Hist.new.Regular(40,80,100).Double().fill(ak.flatten(Z_cand_sel1.mass)),
                'Recoilm': hist.Hist.new.Regular(100,0,200).Double().fill(ak.flatten(Recoil_sel1.mass)),
                'Recoilm_zoom' : hist.Hist.new.Regular(200,80,160).Double().fill(ak.flatten(Recoil_sel1.mass)),
                'Recoilm_zoom1' : hist.Hist.new.Regular(100,120,140).Double().fill(ak.flatten(Recoil_sel1.mass)),
                'Recoilm_zoom2' : hist.Hist.new.Regular(200,120,140).Double().fill(ak.flatten(Recoil_sel1.mass)),
                'Recoilm_zoom3' : hist.Hist.new.Regular(400,120,140).Double().fill(ak.flatten(Recoil_sel1.mass)),
                'Recoilm_zoom4' : hist.Hist.new.Regular(800,120,140).Double().fill(ak.flatten(Recoil_sel1.mass)),
                'Recoilm_zoom5' : hist.Hist.new.Regular(2000,120,140).Double().fill(ak.flatten(Recoil_sel1.mass)),
                'Recoilm_zoom6' : hist.Hist.new.Regular(100,130.3,132.5).Double().fill(ak.flatten(Recoil_sel1.mass))
                }
            },
            'cutflow': { #cutflow objects
                'sel0': sel0,
                'sel1': sel1
            }
        }

        return Output
            
    def postprocess(self, accumulator):
        pass








