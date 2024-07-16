universe=vanilla
executable=job_3.sh
+JobFlavour="espresso"
RequestCpus=1
should_transfer_files=YES
when_to_transfer_output=ON_EXIT_OR_EVICT
transfer_input_files=/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/Batch/job_3.py,/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/processor_mHrecoil.py
transfer_output_files=singularity.log.job_3, outputs_3
output=out-3.$(ClusterId).$(ProcId)
error=err-3.$(ClusterId).$(ProcId)
log=log-3.$(ClusterId).$(ProcId)
queue 1