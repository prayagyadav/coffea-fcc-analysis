
from coffea import util
from coffea.nanoevents import BaseSchema
import os
from processor_mHrecoil import mHrecoil
from coffea.dataset_tools import apply_to_fileset,max_chunks
import dask

dataset_runnable = {'p8_ee_ZH_ecm240': {'files': {'../data/p8_ee_ZH_ecm240/events_082532938.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'e6d02516-aa66-11eb-97b7-c969b9bcbeef'}}, 'metadata': {'dataset': 'p8_ee_ZH_ecm240', 'generation': 'Spring2021'}, 'form': None}}
maxchunks = 10

to_compute = apply_to_fileset(
            mHrecoil(),
            max_chunks(dataset_runnable, maxchunks),
            schemaclass=BaseSchema,
)
computed = dask.compute(to_compute)
(Output,) = computed

print("Saving the output to : " , "mHrecoil_mumu-chunk0.coffea")
if not os.path.exists("outputs/FCCee/higgs/mH-recoil/mumu/"):
    os.makedirs("outputs/FCCee/higgs/mH-recoil/mumu/")
util.save(output= Output, filename="outputs/FCCee/higgs/mH-recoil/mumu/"+"mHrecoil_mumu-chunk0.coffea")
print("File mHrecoil_mumu-chunk0.coffea saved at outputs/FCCee/higgs/mH-recoil/mumu/")
print("Execution completed.")
    
    