from dask_jobqueue import HTCondorCluster
from dask.distributed import Client
import os

def runCondor(cores=1, memory="2 GB", disk="1 GB", death_timeout = '60', workers=4):

    os.environ["CONDOR_CONFIG"] = "/etc/condor/condor_config"
    #_x509_path = move_X509()

    cluster = HTCondorCluster(
        cores=cores,
        memory=memory,
        disk=disk,
        death_timeout = death_timeout,
        job_extra={
            "+JobFlavour": '"espresso"', # 20 minutes
            #"+JobFlavour": '"microcentury"' , # 1 hour
            #"+JobFlavour": '"longlunch"' , # 2 hours
            #"+JobFlavour": '"workday"' , # 8 hours
            #"+JobFlavour": '"tomorrow"' , # 1 day
            #"+JobFlavour": '"testmatch"' , # 3 days
            #"+JobFlavour": '"nextweek"' , # 1 week
            "log": "dask_job_output.$(PROCESS).$(CLUSTER).log",
            "output": "dask_job_output.$(PROCESS).$(CLUSTER).out",
            "error": "dask_job_output.$(PROCESS).$(CLUSTER).err",
            "should_transfer_files": "yes",
            "when_to_transfer_output": "ON_EXIT_OR_EVICT",
            #"+SingularityImage": '"/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask-almalinux8:2024.5.0-py3.11/"',
            #"Requirements": "HasSingularityJobStart",
            #"request_GPUs" : "1",
            #"InitialDir": f'/scratch/{os.environ["USER"]}',
            #"transfer_input_files": f'{_x509_path},{os.environ["EXTERNAL_BIND"]}/monoHbb'
            #"transfer_input_files": f'{os.environ["EXTERNAL_BIND"]}/processor_mHrecoil.py'
        },
        #job_script_prologue=[
        #    "export XRD_RUNFORKHANDLER=1",
            #f"export X509_USER_PROXY={_x509_path}",
        #]
)
    cluster.adapt(minimum=1, maximum=workers)
    #executor = processor.DaskExecutor(client=Client(cluster))
    return Client(cluster)


import dask.array as da

cluster = runCondor(cores=1, memory='10GB', disk='1GB')


x = da.random.random((10000, 10000), chunks=(1000, 1000))
y = x + x.T
z = y[::2, 5000:].mean(axis=1)
print(z.compute())
