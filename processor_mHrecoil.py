from coffea.nanoevents import BaseSchema, NanoEventsFactory
from coffea import processor
import dask_awkward as dak
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
    if len(input_array) != len(index_array) :
        raise Exception('Length of Input_array and index_array does not match!')
    counts = len(ak.count(input_array, axis = 1))
    @numba.jit
    def numba_wrap(input_array, index_array,counts):
        output_array = []
        for event_index in range(counts):
            event_mask = index_array[event_index]
            reco_list = input_array[event_index]
            output_array.append([reco_list[i] for i in  event_mask])
        return output_array
    return ak.Array(numba_wrap(input_array,index_array,counts))

#Begin the processor definition
class mHrecoil(processor.ProcessorABC):
    '''
    mHrecoil example: e^+ + e^- \rightarrow ZH \rightarrow \mu^+ \mu^- + X(Recoil)
    Note: Use only BaseSchema with this processor
    '''
    def __init__(self):
        
        pass
    def process(self,events):
        # Filter out any events which no reconstructed particles
        Recon = events['ReconstructedParticles/ReconstructedParticles.energy'].compute()
        useful_events = events[ak.num(Recon) > 0]
        
        Muon_index = useful_events['Muon#0/Muon#0.index'].compute()

        # Generate Reconstructed Particle Attributes
        Reco_E = useful_events['ReconstructedParticles/ReconstructedParticles.energy'].compute()
        Reco_px = useful_events['ReconstructedParticles/ReconstructedParticles.momentum.x'].compute()
        Reco_py = useful_events['ReconstructedParticles/ReconstructedParticles.momentum.y'].compute()
        Reco_pz = useful_events['ReconstructedParticles/ReconstructedParticles.momentum.z'].compute()
        Reco_q = useful_events['ReconstructedParticles/ReconstructedParticles.charge'].compute()
        Reco_mass = useful_events['ReconstructedParticles/ReconstructedParticles.mass'].compute()

        # Generate Muon Attributes
        Muon_E = index_mask(Reco_E,Muon_index)
        Muon_px = index_mask(Reco_px,Muon_index)
        Muon_py = index_mask(Reco_py,Muon_index)
        Muon_pz = index_mask(Reco_pz,Muon_index)
        Muon_q = index_mask(Reco_q,Muon_index)
        Muon_mass = index_mask(Reco_mass,Muon_index)

        # Create Array of Muon Lorentz Vector 
        Muon = ak.zip({"px":Muon_px,"py":Muon_py,"pz":Muon_pz,"E":Muon_E,"q":Muon_q,}, with_name="Momentum4D")

        # Produce combinations of Muon Pairs possible within an event
        combs = ak.combinations(Muon,2)

        # Get DiMuons
        mu1 , mu2 = ak.unzip(combs)
        di_muon = mu1 + mu2

        # Choose the dimuon with highest mass
        di_muon = di_muon[ak.num(di_muon) > 0]
        di_muon_mass = ak.Array([i[0] for i in ak.sort(di_muon.mass, ascending=False)])

        # Choose dimuon which is made up of two oppositely charged muons
        q_sum = mu1.q + mu2.q
        q_sum_array = q_sum[ak.num(q_sum)>0]
        q_sum_mask = ak.all(q_sum_array == 0, axis=1)
        Z_cand_m = di_muon_mass[q_sum_mask]
        Z_cand = di_muon[q_sum_mask]

        # Create Z-Candidate mass histogram
        hist_Zm = hist.Hist.new.Regular(100,0,150).Double().fill(Z_cand_m)

        #Recoil Calculation
        ecm = 240 #GeV # com energy
        initial = ak.zip({"px":0,"py":0,"pz":0,"E":ecm}, with_name="Momentum4D")
        Recoil = initial - Z_cand

        # Create Recoil mass histogram
        hist_Recoilm = hist.Hist.new.Regular(100,60,160).Double().fill(ak.flatten(Recoil.mass))


        #Prepare output
        Output = {
            'histograms': {
                'Z_mass': hist_Zm,
                'Recoil_mass':hist_Recoilm
            }
        }

        return Output
            
    def postprocess(self, accumulator):
        pass








