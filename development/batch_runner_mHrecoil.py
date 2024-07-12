
if __name__=="__main__":
    import argparse
    from coffea import util
    from coffea.nanoevents import BaseSchema
    import numpy as np
    import yaml
    import os
    from processor_mHrecoil import mHrecoil
    from coffea.dataset_tools import apply_to_fileset,max_chunks,preprocess
    import dask
    from dask.distributed import Client, LocalCluster
    from dask_jobqueue import HTCondorCluster
    from dask.diagnostics import ProgressBar, Profiler
    #pgb = ProgressBar()
    #pgb.register()

    ###################################
    # Define functions and parameters #
    ###################################
    process = {
        'collider':'FCCee',
        'campaign':'spring2021',
        'detector':'IDEA',
        'samples':['p8_ee_ZZ_ecm240','p8_ee_WW_ecm240','p8_ee_ZH_ecm240']
    }
    fraction = {
        'p8_ee_ZZ_ecm240':0.005,
        'p8_ee_WW_ecm240':0.5,
        'p8_ee_ZH_ecm240':0.2
    }

    redirectors = {
        "eos":'root://eospublic.cern.ch/'
    }
    
    def load_yaml_fileinfo(process):
        '''
        Loads the yaml data for filesets
        '''
        onlinesystem_path = '/cvmfs/fcc.cern.ch'
        localsystem_path = './../../../../../filesets/'
        path = '/'.join(
            [
             'FCCDicts',
             'yaml',
             process['collider'],
             process['campaign'],
             process['detector']
            ])
        if os.path.exists(onlinesystem_path):
            print(f'Connected to {onlinesystem_path}')
            filesystem_path = onlinesystem_path
        else:
            print(onlinesystem_path+' is not available.\nTrying to find local copies of the yaml files ...')
            filesystem_path = localsystem_path
        yaml_dict = {}
        for sample in process['samples']:
            full_path = '/'.join([filesystem_path,path,sample,'merge.yaml'])
            try :
                with open(full_path) as f:
                    dict = yaml.safe_load(f)
                print('Loaded : '+full_path)
                # print(dict)
            except:
                raise f'Could not find yaml files at {filesystem_path} .'
            yaml_dict[sample] = dict
        return yaml_dict

    def get_fileset(yaml_dict, fraction, skipbadfiles=True, redirector=''):
        output_fileset_dictionary = {}
        print('_________Loading fileset__________')
        for key in yaml_dict.keys():
            output_fileset_dictionary[key] = {}
            # nbad = yaml_dict[key]['merge']['nbad']
            # ndone = yaml_dict[key]['merge']['ndone']
            nevents = yaml_dict[key]['merge']['nevents']
            outdir = yaml_dict[key]['merge']['outdir']
            outfiles = yaml_dict[key]['merge']['outfiles']
            outfilesbad = yaml_dict[key]['merge']['outfilesbad']
            proc = yaml_dict[key]['merge']['process']
            # size = yaml_dict[key]['merge']['size']
            # sumofweights = yaml_dict[key]['merge']['sumofweights']
            out = np.array(outfiles)
            bad = np.array(outfilesbad)
            
            # Remove bad files
            if (bad.size != 0) & skipbadfiles :
                filenames_bad = bad[:,0]
                y = out
                for row in range(out.shape[0]) :
                    file = out[row,0]
                    if file in filenames_bad:
                        y = np.delete(y , (row), axis=0)
                out = y
    
            filenames = out[:,0]
            file_events = out[:,1].astype('int32')
            cumulative_events = np.cumsum(file_events)
        
            frac = fraction[proc]
            needed_events = frac*nevents
    
            #get closest value and index to the needed events
            index = np.abs(cumulative_events - needed_events).argmin() 
            assigned_events = cumulative_events[index]
            assigned_files = filenames[:index+1]
    
            # Summary
            print('----------------------------------')
            print(f'----------{key}---------')
            print('----------------------------------')
            print(f'Total available events = {nevents}')
            print(f'Fraction needed = {frac}')
            print(f'Needed events = {needed_events}')
            print(f'Assigned events = {assigned_events}')
            print(f'Number of files = {len(assigned_files)}')
            print('Files:')
    
            # At the same time get the dictionary
            fileset_by_key = {}
            for file in assigned_files:
                print(f'\t {redirector+outdir+file}')
                fileset_by_key[redirector+outdir+file] = 'events'
            output_fileset_dictionary[key]['files'] = fileset_by_key
        return output_fileset_dictionary
    
    def runCondor(cores=1, memory="2 GB", disk="1 GB", death_timeout = '60', workers=4):

        os.environ["CONDOR_CONFIG"] = "/etc/condor/condor_config"
        #_x509_path = move_X509()

        cluster = HTCondorCluster(
            cores=cores,
            memory=memory,
            disk=disk,
            death_timeout = death_timeout,
            job_extra_directives={
                #"+JobFlavour": '"espresso"', # 20 minutes
                #"+JobFlavour": '"microcentury"' , # 1 hour
                "+JobFlavour": '"longlunch"' , # 2 hours
                #"+JobFlavour": '"workday"' , # 8 hours
                #"+JobFlavour": '"tomorrow"' , # 1 day
                #"+JobFlavour": '"testmatch"' , # 3 days
                #"+JobFlavour": '"nextweek"' , # 1 week
                "log": "dask_job_output.$(PROCESS).$(CLUSTER).log",
                "output": "dask_job_output.$(PROCESS).$(CLUSTER).out",
                "error": "dask_job_output.$(PROCESS).$(CLUSTER).err",
                "should_transfer_files": "yes",
                "when_to_transfer_output": "ON_EXIT_OR_EVICT",
                "+SingularityImage": '"/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask-almalinux8:2024.5.0-py3.11/"',
                "Requirements": "HasSingularityJobStart",
                #"request_GPUs" : "1",
                #"InitialDir": f'/scratch/{os.environ["USER"]}',
                #"transfer_input_files": f'{_x509_path},{os.environ["EXTERNAL_BIND"]}/monoHbb'
                "transfer_input_files": f'{os.environ["EXTERNAL_BIND"]}/processor_mHrecoil.py'
            },
            job_script_prologue=[
                "export XRD_RUNFORKHANDLER=1",
                #f"export X509_USER_PROXY={_x509_path}",
            ]
        )
        cluster.adapt(minimum=1, maximum=workers)
        #executor = processor.DaskExecutor(client=Client(cluster))
        return Client(cluster)
    
    ##############################
    # Define the terminal inputs #
    ##############################
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--executor",
        choices=["condor", "dask"],
        help="Enter where to run the file : dask(local) or condor (Note: Only dask(local) works at the moment)",
        default="dask",
        type=str
    )

    parser.add_argument(
        "-m",
        "--maxchunks",
        help="Enter the number of chunks to be processed; by default 10",
        type=int
        )
    
    inputs = parser.parse_args()

    raw_yaml = load_yaml_fileinfo(process)
    myfileset = get_fileset(raw_yaml, fraction, redirector='root://eospublic.cern.ch/')

    ###################
    # Run the process #
    ###################


    #For local dask execution
    if inputs.executor == "dask" :
        print("Executing locally with dask ...")
        dask.config.set(scheduler='processes')
        print('Preparing fileset before run...')
        dataset_runnable, dataset_updated = preprocess(
        myfileset,
        align_clusters=False,
        step_size=100_000,
        files_per_batch=1,
        skip_bad_files=True,
        save_form=False,
        )
        
        cluster = LocalCluster(n_workers=16)
        #cluster.adapt(minimum=1, maximum=10)
        print('Dashboard at ', cluster.dashboard_link)

        client = Client(cluster)

        print('Processing ...')
        with ProgressBar(), Profiler() as prof:
            to_compute = apply_to_fileset(
                        mHrecoil(),
                        max_chunks(dataset_runnable, inputs.maxchunks),
                        schemaclass=BaseSchema,
            )
            computed = client.compute(to_compute)
            computed = (computed.result(),)


    #For condor execution
    elif inputs.executor == "condor" :
        print('Executing with HTCondor ...')
        client = runCondor()
        with client:

            print('Preparing fileset before run...')
            dataset_runnable, dataset_updated = preprocess(
            myfileset,
            align_clusters=False,
            step_size=100_000,
            files_per_batch=1,
            skip_bad_files=True,
            save_form=False,
            )

            print('Processing ...')
            to_compute = apply_to_fileset(
                mHrecoil(),
                        max_chunks(dataset_runnable, inputs.maxchunks),
                        schemaclass=BaseSchema,
            )
            computed = dask.compute(to_compute)

    (Output,) = computed

    ###############
    # Run Summary #
    ###############
    #print('_______________________________________________')
    #print('        Summary of Resource Utilization        ')
    #print('_______________________________________________')
    #ntask = 0
    #for task in prof.results:
    #    print(f'Task {ntask}: {task}')
    #    ntask += 1
    #print('_______________________________________________')
    
    ##########################
    # Create the output file #
    ##########################
    output_file = f"mHrecoil_mumu.coffea"
    print("Saving the output to : " , output_file)
    path ="outputs/FCCee/higgs/mH-recoil/mumu/"
    if not os.path.exists(path):
        os.makedirs(path)
    util.save(output= Output, filename=path+output_file)
    print(f"File {output_file} saved at {path}")
    print("Execution completed.")
