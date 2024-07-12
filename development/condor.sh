universe = vanilla
executable = batchjob.sh

should_transfer_files = IF_NEEDED
when_to_transfer_output = ON_EXIT
transfer_input_files= batch_runner_mHrecoil.py,processor_mHrecoil.py
transfer_output_files= outputs

output = out.$(ClusterId).$(ProcId)
error = err.$(ClusterId).$(ProcId)
log = log.$(ClusterId).$(ProcId)

queue 1
