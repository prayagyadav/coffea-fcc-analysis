# Define the requirements

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
ecm = 240.0 # #\sqrt(s) in GeV

if __name__=="__main__":
    from coffea import util
    import argparse
    from coffea.nanoevents import BaseSchema
    import numpy as np
    import yaml
    import os
    import subprocess
    from processor_mHrecoil import mHrecoil
    from coffea.dataset_tools import apply_to_fileset,max_chunks,preprocess
    from coffea.analysis_tools import Cutflow
    import dask
    import copy
    import time
    from dask.diagnostics import ProgressBar
    pgb = ProgressBar()
    pgb.register()

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
        "-o",
        "--outfile",
        help="Enter the base-name of the coffea file to output with .coffea extension. By default: 'mHrecoil_mumu'",
        default="mHrecoil_mumu",
        type=str
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Enter the path to save the output files. By default 'outputs/FCCee/higgs/mH-recoil/mumu/')",
        default="outputs/FCCee/higgs/mH-recoil/mumu/",
        type=str
    )
    parser.add_argument(
        "-m",
        "--maxchunks",
        help="Enter the number of chunks to be processed; by default 10",
        default=10,
        type=int
        )
    parser.add_argument(
        "-c",
        "--chunks",
        help="Enter the number of parallel chunks to be processed; by default 1",
        type=int,
        default=1
        )

    inputs = parser.parse_args()

    ###################################
    # Define functions and parameters #
    ###################################
    output_file = inputs.outfile+".coffea"
    path = inputs.path

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
            except:
                raise FileNotFoundError('Could not find yaml files at {filesystem_path}')
            yaml_dict[sample] = dict
        return yaml_dict

    def get_fileset(yaml_dict, fraction, skipbadfiles=True, redirector=''):
        '''
        Returns fileset a fraction of fileset in the dask compatible format
        '''
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

    def break_into_many(input_fileset,n):
        '''
        Split a given fileset into n almost even filesets
        '''

        # Create an indexed fileset
        fileset = copy.deepcopy(input_fileset)
        index = 0
        for dataset in input_fileset.keys():
            for filename,treename in input_fileset[dataset]['files'].items():
                fileset[dataset]['files'][filename] = {'treename': treename, 'index': index}
                index += 1

        # Split the array as required
        nfiles = sum([len(fileset[dataset]['files']) for dataset in fileset.keys()])
        if n == 0 :
            return [input_fileset]
        elif n > 0 and n <= index:
            index_split = np.array_split(np.arange(nfiles),n)
        else :
            raise ValueError(f'Allowed values of n between 0 and {index}')

        # Choose the required indices for each split
        raw = [copy.deepcopy(input_fileset) for i in range(n)]
        for f in range(n):
            for dataset in fileset.keys():
                for event in fileset[dataset]['files'].keys():
                    if not fileset[dataset]['files'][event]['index'] in index_split[f]:
                        del raw[f][dataset]['files'][event]

        #remove empty fields
        out = copy.deepcopy(raw)
        for f in range(n):
            for dataset in raw[f].keys():
                if len(raw[f][dataset]['files']) == 0 :
                    del out[f][dataset]

        return out

    def create_job_python_file(ecm, dataset_runnable, maxchunks,filename, output_file):
        s = f'''
from coffea import util
from coffea.nanoevents import BaseSchema
import os
from processor_mHrecoil import mHrecoil
from coffea.dataset_tools import apply_to_fileset,max_chunks
import dask

dataset_runnable = {dataset_runnable}
maxchunks = {maxchunks}

to_compute = apply_to_fileset(
            mHrecoil(ecm={ecm}),
            max_chunks(dataset_runnable, maxchunks),
            schemaclass=BaseSchema,
)
computed = dask.compute(to_compute)
(Output,) = computed

print("Saving the output to : " , "{output_file}")
util.save(output= Output, filename="{output_file}")
print("File {output_file} saved")
print("Execution completed.")

        '''
        with open(filename,'w') as f:
            f.write(s)

    def create_job_shell_file(filename, python_job_file):
        s = f'''#!/usr/bin/bash
export COFFEA_IMAGE=coffeateam/coffea-dask-almalinux8:2024.5.0-py3.11
echo "Coffea Image: ${{COFFEA_IMAGE}}"
EXTERNAL_BIND=${{PWD}}
echo $(pwd)
echo $(ls)
singularity exec -B /etc/condor -B /eos -B /afs -B /cvmfs --pwd ${{PWD}} \
/cvmfs/unpacked.cern.ch/registry.hub.docker.com/${{COFFEA_IMAGE}} \
/usr/local/bin/python3 {python_job_file} -e dask >> singularity.log.{python_job_file.strip('.py')}
echo $(ls)'''
        with open(filename,'w') as f:
            f.write(s)

    def create_submit_file(filename, executable, input, output):
        s = f'''universe=vanilla
executable={executable}
+JobFlavour="espresso"
RequestCpus=1
should_transfer_files=YES
when_to_transfer_output=ON_EXIT_OR_EVICT
transfer_input_files={input}
transfer_output_files={output}
output=out-{executable.strip('job_').strip('.sh')}.$(ClusterId).$(ProcId)
error=err-{executable.strip('job_').strip('.sh')}.$(ClusterId).$(ProcId)
log=log-{executable.strip('job_').strip('.sh')}.$(ClusterId).$(ProcId)
queue 1'''
        with open(filename,'w') as f:
            f.write(s)

    def create_master_submit(submitfile_base_name, chunks, wait_time,):
        s = '#!/usr/bin/bash\n'
        for i in range(chunks):
            s += f'condor_submit {submitfile_base_name}_{i}.sh\nsleep {wait_time}\n'
        with open('condor.sh','w') as f:
            f.write(s)


    ###################
    # Run the process #
    ###################

    raw_yaml = load_yaml_fileinfo(process)
    myfileset = get_fileset(raw_yaml, fraction, redirector='root://eospublic.cern.ch/')
    fileset = break_into_many(input_fileset=myfileset,n=inputs.chunks)

    print('Preparing fileset before run...')

    pwd = os.getcwd()

    dataset_runnable, dataset_updated = zip(*[preprocess(
        fl,
        align_clusters=False,
        step_size=50_000,
        files_per_batch=1,
        skip_bad_files=True,
        save_form=False,
    ) for fl in fileset ]
                                           )

    #For local dask execution
    if inputs.executor == "dask" :
        if not os.path.exists(path):
            os.makedirs(path)
        Output = []
        print("Executing locally with dask ...")
        for i in range(len(dataset_runnable)):
            print('Chunk : ',i)
            to_compute = apply_to_fileset(
                        mHrecoil(ecm=ecm),
                        max_chunks(dataset_runnable[i], inputs.maxchunks),
                        schemaclass=BaseSchema,
            )
            computed = dask.compute(to_compute)
            (Out,) = computed
            Output.append(Out)
            if inputs.chunks > 1:
                output_filename = output_file.strip('.coffea')+f'-chunk{i}'+'.coffea'
            else:
                output_filename = output_file
            print("Saving the output to : " , output_filename)
            util.save(output= Out, filename=path+output_filename)
            print(f"File {output_filename} saved at {path}")
        print("Execution completed.")

    #For condor execution
    elif inputs.executor == "condor" :
        print("Executing with condor ...")
        batch_dir = 'Batch'
        if not os.path.exists(batch_dir):
            os.makedirs(batch_dir)
        os.chdir(batch_dir)

        for i in range(len(dataset_runnable)):

            if inputs.chunks > 1:
                output_filename = output_file.strip('.coffea')+f'-chunk{i}'+'.coffea'
            else:
                output_filename = output_file
            create_job_python_file(
                ecm,
                dataset_runnable[i],
                inputs.maxchunks,
                f'job_{i}.py',
                output_filename,

            )
            print(f'\tjob_{i}.py created')
            create_job_shell_file(
                filename=f'job_{i}.sh',
                python_job_file=f'job_{i}.py'
            )
            subprocess.run(['chmod','u+x',f'job_{i}.sh'])
            print(f'\tjob_{i}.sh created')
            create_submit_file(
                filename=f'submit_{i}.sh',
                executable=f'job_{i}.sh',
                input=f'{pwd}/{batch_dir}/job_{i}.py,{pwd}/processor_mHrecoil.py',
                output=f'singularity.log.job_{i},{output_filename}'
            )
            subprocess.run(['chmod','u+x',f'submit_{i}.sh'])
            print(f'\tsubmit_{i}.sh created')
        create_master_submit(submitfile_base_name='submit',chunks=inputs.chunks,wait_time=5)
        subprocess.run(['chmod','u+x','condor.sh'])
        print('condor.sh created')
        print(f'Action Needed: All the job files created; To submit them, move to the {batch_dir} directory and run ./condor.sh without getting into the singularity container shell.')

        os.chdir('../')
