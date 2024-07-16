
from coffea import util
from coffea.nanoevents import BaseSchema
import os
from processor_mHrecoil import mHrecoil
from coffea.dataset_tools import apply_to_fileset,max_chunks
import dask

dataset_runnable = {'p8_ee_WW_ecm240': {'files': {'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_073916792.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c8e6e9ac-aa7c-11eb-921f-6ac6b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_074962718.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'be1d7b6c-aa7c-11eb-9f88-89c18e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_076184375.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c44b39d4-aa7c-11eb-ac67-1c538e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_078174375.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c3d94cca-aa7c-11eb-8539-83458e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_081552316.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c87dc71a-aa7c-11eb-b7de-054f8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_087150860.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c1c02fe4-aa7c-11eb-aa7e-454e8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_087671235.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c2d42368-aa7c-11eb-aa7e-3d498e80beef'}}, 'form': None, 'metadata': None}, 'p8_ee_ZH_ecm240': {'files': {'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_ZH_ecm240/events_002125352.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'e03206c0-aa66-11eb-b728-24478e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_ZH_ecm240/events_004864728.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'df4890c6-aa66-11eb-af5e-464b8e80beef'}}, 'form': None, 'metadata': None}}
maxchunks = None

to_compute = apply_to_fileset(
            mHrecoil(),
            max_chunks(dataset_runnable, maxchunks),
            schemaclass=BaseSchema,
)
computed = dask.compute(to_compute)
(Output,) = computed

print("Saving the output to : " , "mHrecoil_mumu-chunk5.coffea")
#if not os.path.exists("outputs/FCCee/higgs/mH-recoil/mumu/"):
#    os.makedirs("outputs/FCCee/higgs/mH-recoil/mumu/")
#util.save(output= Output, filename="outputs/FCCee/higgs/mH-recoil/mumu/"+"/"+"mHrecoil_mumu-chunk5.coffea")
util.save(output= Output, filename="mHrecoil_mumu-chunk5.coffea")
print("File mHrecoil_mumu-chunk5.coffea saved")# at outputs/FCCee/higgs/mH-recoil/mumu/")
print("Execution completed.")

        