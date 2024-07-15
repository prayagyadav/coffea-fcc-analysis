
    from coffea import util
    from coffea.nanoevents import BaseSchema
    import os
    from processor_mHrecoil import mHrecoil
    from coffea.dataset_tools import apply_to_fileset,max_chunks
    import dask
    
    dataset_runnable = {'p8_ee_WW_ecm240': {'files': {'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_042960849.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'bd10b2ac-aa7c-11eb-a7ec-58508e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_045685798.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c3c3c7b0-aa7c-11eb-9113-ab4a8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_046174706.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c3e21616-aa7c-11eb-bd39-ae4a8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_046854584.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'bc2b10f8-aa7c-11eb-8c83-d9468e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_049408485.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'bf14b404-aa7c-11eb-bbd6-8ca8b8bcbeef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_050421846.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '4cf2e76a-aa7c-11eb-b6bf-a34b8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_051087029.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': '8821c70c-aa7c-11eb-b1c5-3e488e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_051591218.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'c99bd2c2-aa7c-11eb-ae3a-4a4d8e80beef'}, 'root://eospublic.cern.ch:1094//eos/experiment/fcc/ee/generation/DelphesEvents/spring2021/IDEA/p8_ee_WW_ecm240/events_057156831.root': {'object_path': 'events', 'steps': [[0, 50000], [50000, 100000]], 'num_entries': 100000, 'uuid': 'b8e74966-aa7c-11eb-823c-d9c6b8bcbeef'}}, 'form': None, 'metadata': None}}
    maxchunks = None
    
    to_compute = apply_to_fileset(
                mHrecoil(),
                max_chunks(dataset_runnable, maxchunks),
                schemaclass=BaseSchema,
    )
    computed = dask.compute(to_compute)
    (Output,) = computed
    
    print("Saving the output to : " , "mHrecoil_mumu-chunk3.coffea")
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    util.save(output= Output, filename="outputs"+"mHrecoil_mumu-chunk3.coffea")
    print("File mHrecoil_mumu-chunk3.coffea saved at outputs")
    print("Execution completed.")
        
        