universe=vanilla
executable=job_4.sh
+JobFlavour="espresso"
RequestCpus=1
should_transfer_files=YES
when_to_transfer_output=ON_EXIT_OR_EVICT
transfer_input_files=/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/Batch/job_4.py,/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/processor_mHrecoil.py
transfer_output_files=singularity.log.job_4, outputs_4
output=out-4.$(ClusterId).$(ProcId)
error=err-4.$(ClusterId).$(ProcId)
log=log-4.$(ClusterId).$(ProcId)
queue 1