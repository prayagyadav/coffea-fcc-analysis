
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

    ##############################
    # Define the terminal inputs #
    ##############################
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--executor",
        choices=["futures","condor", "dask"],
        help="Enter where to run the file : futures(local) or dask(local) or condor (Note: Only futures works at the moment)",
        default="futures",
        type=str
    )
    parser.add_argument(
        "-k",
        "--keymap",
        choices=[
            "ZH", #p8_ee_ZH_ecm240
            "ZZ",
            "WW"
            ],
        help="Enter which dataset to run: example ZH, ZZ or WW etc. (Note: only ZH works at the moment)",
        type=str
    )
    parser.add_argument(
        "-c",
        "--chunk_size",
        help="Enter the chunksize; by default 100k",
        type=int ,
        default=100000
        )
    parser.add_argument(
        "-m",
        "--max_chunks",
        help="Enter the number of chunks to be processed; by default None ie full dataset",
        type=int
        )
    parser.add_argument(
        "-w",
        "--workers",
        help="Enter the number of workers to be employed for processing in local; by default 4",
        type=int ,
        default=4
        )
    inputs = parser.parse_args()

    def getraw(jsonfilename):
        '''
        Load the raw dictionary
        '''
        with open(jsonfilename) as f :
            full_fileset = json.load(f)
        return full_fileset

    def add_redirector(filesetname,redirector="root://eospublic.cern.ch/"):
        '''
        Choose your redirector
        '''
        raw_fileset = getraw(filesetname)

        # Expecting raw_fileset to be in {key1:file_list1,key2:file_list2,key3:file_list3 ... } format
        new_fileset = {}
        for key in raw_fileset.keys():
            new_list = []
            for file_path in raw_fileset[key]:
                new_name = redirector+file_path
                new_list.append(new_name)
            new_fileset[key] = new_list

        return new_fileset

    fileset = add_redirector(filesetname="./fileset.json")

    #For futures execution
    if inputs.executor == "futures" :
        futures_run = processor.Runner(
            executor = processor.FuturesExecutor(workers=inputs.workers),
            schema=BaseSchema,
            chunksize= inputs.chunk_size ,
            maxchunks= inputs.max_chunks,
            xrootdtimeout=120
        )
        Output = futures_run(
            fileset,
            "Events",
            processor_instance=mHrecoil()
        )
        
    #For dask execution
    elif inputs.executor == "dask" :
        raise('Dask execution is not available yet!')

    #For condor execution
    elif inputs.executor == "condor" :
        raise('HTCondor execution is not available yet!')
        
    #################################
    # Create the output file #
    #################################
    print("Output produced")
  
    output_file = f"mHrecoil_mumu_{inputs.keymap}.coffea"
    print("Saving the output to : " , output_file)
    util.save(output= Output, filename="outputs/FCCee/higgs/mH-recoil/mumu/"+output_file)
    print(f"File {output_file} saved.")
    print("Execution completed.")
