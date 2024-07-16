
from coffea import util
from coffea.nanoevents import BaseSchema
import os
from processor_mHrecoil import mHrecoil
from coffea.dataset_tools import apply_to_fileset,max_chunks
import dask

dataset_runnable = {'p8_ee_WW_ecm240': {'files': {'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_014553223.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c2223626-aa7c-11eb-a0f8-88a8b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_015203393.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '715a857c-aa7c-11eb-ae18-54a8b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_016976279.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'bc288144-aa7c-11eb-a7ec-eca8b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_018665926.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '9bd28eb2-aa7c-11eb-972b-59c6b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_018713241.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c7225944-aa7c-11eb-bfd2-f5458e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_019837840.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '5693e62a-aa7c-11eb-9724-eb458e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_023471508.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c6b4ea6c-aa7c-11eb-a3c3-57448e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_026468529.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c65db0c6-aa7c-11eb-ac67-1e4c8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_027476245.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '1ea27b32-aa7c-11eb-bb0a-cda8b8bcbeef'}}, 'form': None, 'metadata': None}}
maxchunks = None

to_compute = apply_to_fileset(
            mHrecoil(),
            max_chunks(dataset_runnable, maxchunks),
            schemaclass=BaseSchema,
)
computed = dask.compute(to_compute)
(Output,) = computed

print("Saving the output to : " , "mHrecoil_mumu-chunk1.coffea")
if not os.path.exists("outputs_1"):
    os.makedirs("outputs_1")
util.save(output= Output, filename="outputs_1"+"/"+"mHrecoil_mumu-chunk1.coffea")
print("File mHrecoil_mumu-chunk1.coffea saved at outputs_1")
print("Execution completed.")

        