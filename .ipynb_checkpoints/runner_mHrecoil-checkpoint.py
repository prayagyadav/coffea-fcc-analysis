
if __name__=="__main__":
    from coffea import processor
    import argparse
    from coffea import util
    from coffea.nanoevents import BaseSchema , NanoEventsFactory
    import awkward as ak
    import numba
    import json
    import rich
    import numpy as np
    import os
    import shutil
    import logging
    from processor_mHrecoil import mHrecoil
    from coffea.dataset_tools import apply_to_fileset,max_chunks,preprocess
    import dask

    ##############################
    # Define the terminal inputs #
    ##############################
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--executor",
        choices=["condor", "dask"],
        help="Enter where to run the file : dask(local) or condor (Note: Only dask(local) works at the moment)",
        default="futures",
        type=str
    )
    parser.add_argument(
        "-r",
        "--redirector",
        choices=["eos"],
        help="Enter the redirector to use, eg. eos",
        default="",
        type=str
    )
    parser.add_argument(
        "-m",
        "--maxchunks",
        help="Enter the number of chunks to be processed; by default None ie full dataset",
        type=int
        )
    inputs = parser.parse_args()

    def getraw(jsonfilename):
        '''
        Load the raw dictionary
        '''
        with open(jsonfilename) as f :
            full_fileset = json.load(f)
        return full_fileset

    def add_redirector(filesetname,redirector=""):
        '''
        Choose your redirector
        '''
        redirectors = {
            "eos":'root://eospublic.cern.ch/'
        }
        if len(redirector) != 0 :
            redirector_string = redirectors[redirector]
        else:
            redirector_string = ''
        
        raw_fileset = getraw(filesetname)
    
        # Expecting raw_fileset to be in {key1:{files:{filepath1:events, filepath2:events, ...}},key2:... } format
        new_fileset = {}
        for key in raw_fileset.keys():
            new_files = {}
            new_fileset[key] = {}
            for file_path in raw_fileset[key]["files"].keys():
                new_name = redirector_string+file_path
                new_files[new_name] = "events"
            new_fileset[key]["files"] = new_files
    
        return new_fileset

    myfileset = add_redirector(filesetname="./local_fileset.json", redirector=inputs.redirector)


    ###################
    # Run the process #
    ###################    
    dataset_runnable, dataset_updated = preprocess(
    myfileset,
    align_clusters=False,
    step_size=100_000,
    files_per_batch=1,
    skip_bad_files=True,
    save_form=False,
    )

    #For dask execution
    if inputs.executor == "dask" :
        print("Executing locally with dask ...")
        to_compute = apply_to_fileset(
                    mHrecoil(),
                    max_chunks(dataset_runnable, inputs.maxchunks),
                    schemaclass=BaseSchema,
        )
        (Output,) = dask.compute(to_compute)        
        
    #For condor execution
    elif inputs.executor == "condor" :
        raise('HTCondor execution is not available yet!')
        
    ##########################
    # Create the output file #
    ##########################
    output_file = f"mHrecoil_mumu.coffea"
    print("Saving the output to : " , output_file)
    path ="outputs/FCCee/higgs/mH-recoil/mumu/"
    if not os.path.exists(path):
        os.makedirs(path)
    util.save(output= Output, filename=path+output_file)
    print(f"File {output_file} saved.")
    print("Execution completed.")
