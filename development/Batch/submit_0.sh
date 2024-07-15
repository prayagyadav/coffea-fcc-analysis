
    universe = vanilla
    executable = job_0.sh
    
    should_transfer_files = IF_NEEDED
    when_to_transfer_output = ON_EXIT
    transfer_input_files= ../batch_runner_mHrecoil.py,../processor_mHrecoil.py
    transfer_output_files= outputs
    
    output = out-0.$(ClusterId).$(ProcId)
    error = err-0.$(ClusterId).$(ProcId)
    log = log-0.$(ClusterId).$(ProcId)
    
    queue 1
        
        