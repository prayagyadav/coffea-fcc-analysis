universe=vanilla
executable=job_5.sh
+JobFlavour="espresso"
RequestCpus=1
should_transfer_files=YES
when_to_transfer_output=ON_EXIT_OR_EVICT
transfer_input_files=/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/Batch/job_5.py,/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/processor_mHrecoil.py
transfer_output_files=singularity.log.job_5, outputs_5
output=out-5.$(ClusterId).$(ProcId)
error=err-5.$(ClusterId).$(ProcId)
log=log-5.$(ClusterId).$(ProcId)
queue 1