
    universe = vanilla
    executable = job_7.sh
    
    should_transfer_files = IF_NEEDED
    when_to_transfer_output = ON_EXIT
    transfer_input_files= ../batch_runner_mHrecoil.py,../processor_mHrecoil.py
    transfer_output_files= outputs
    
    output = out-7.$(ClusterId).$(ProcId)
    error = err-7.$(ClusterId).$(ProcId)
    log = log-7.$(ClusterId).$(ProcId)
    
    queue 1
        
        