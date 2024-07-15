
    universe = vanilla
    executable = job_6.sh
    
    should_transfer_files = IF_NEEDED
    when_to_transfer_output = ON_EXIT
    transfer_input_files= ../batch_runner_mHrecoil.py,../processor_mHrecoil.py
    transfer_output_files= outputs
    
    output = out-6.$(ClusterId).$(ProcId)
    error = err-6.$(ClusterId).$(ProcId)
    log = log-6.$(ClusterId).$(ProcId)
    
    queue 1
        
        