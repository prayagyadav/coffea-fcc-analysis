universe=vanilla
executable=job_2.sh
+JobFlavour="espresso"
RequestCpus=1
should_transfer_files=YES
when_to_transfer_output=ON_EXIT_OR_EVICT
transfer_input_files=/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/Batch/job_2.py,/afs/cern.ch/user/p/pryadav/public/COFFEA-FCC/coffea-fcc-analyses/development/processor_mHrecoil.py
transfer_output_files=singularity.log.job_2,mHrecoil_mumu-chunk2.coffea
output=out-2.$(ClusterId).$(ProcId)
error=err-2.$(ClusterId).$(ProcId)
log=log-2.$(ClusterId).$(ProcId)
queue 1