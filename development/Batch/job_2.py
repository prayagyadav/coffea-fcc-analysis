
from coffea import util
from coffea.nanoevents import BaseSchema
import os
from processor_mHrecoil import mHrecoil
from coffea.dataset_tools import apply_to_fileset,max_chunks
import dask

dataset_runnable = {'p8_ee_WW_ecm240': {'files': {'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_028807086.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c371e256-aa7c-11eb-bd39-05a9b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_028914696.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c6e1d464-aa7c-11eb-a3c3-d2478e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_030994453.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'bc37ffd4-aa7c-11eb-b11a-35478e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_031800883.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'ba1bf50c-aa7c-11eb-9485-4ea9b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_032306830.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'beca2574-aa7c-11eb-bbd6-754f8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_036566822.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '1f6b0264-aa7c-11eb-9643-1ec6b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_039767239.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'b66e8118-aa7c-11eb-ae0e-89518e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_040168535.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '20d06360-aa7c-11eb-9643-0b488e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_041868503.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c226306e-aa7c-11eb-a0f8-f8a9b8bcbeef'}}, 'form': None, 'metadata': None}}
maxchunks = None

to_compute = apply_to_fileset(
            mHrecoil(),
            max_chunks(dataset_runnable, maxchunks),
            schemaclass=BaseSchema,
)
computed = dask.compute(to_compute)
(Output,) = computed

print("Saving the output to : " , "mHrecoil_mumu-chunk2.coffea")
#if not os.path.exists("outputs/FCCee/higgs/mH-recoil/mumu/"):
#    os.makedirs("outputs/FCCee/higgs/mH-recoil/mumu/")
#util.save(output= Output, filename="outputs/FCCee/higgs/mH-recoil/mumu/"+"/"+"mHrecoil_mumu-chunk2.coffea")
util.save(output= Output, filename="mHrecoil_mumu-chunk2.coffea")
print("File mHrecoil_mumu-chunk2.coffea saved")# at outputs/FCCee/higgs/mH-recoil/mumu/")
print("Execution completed.")

        