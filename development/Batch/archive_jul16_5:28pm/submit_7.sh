universe=vanilla
executable=job_7.sh
+JobFlavour="espresso"
RequestCpus=1
should_transfer_files=YES
when_to_transfer_output=ON_EXIT_OR_EVICT
transfer_input_files=/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/Batch/job_7.py,/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/processor_mHrecoil.py
transfer_output_files=singularity.log.job_7, outputs_7
output=out-7.$(ClusterId).$(ProcId)
error=err-7.$(ClusterId).$(ProcId)
log=log-7.$(ClusterId).$(ProcId)
queue 1