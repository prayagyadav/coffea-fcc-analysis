
    #!/usr/bin/env bash
    
    export COFFEA_IMAGE=coffeateam/coffea-dask-almalinux8:2024.5.0-py3.11
    
    echo "Coffea Image: ${COFFEA_IMAGE}"
    
    EXTERNAL_BIND=${PWD}
    
    
    singularity exec -B ${PWD}:/srv -B /etc/condor -B /eos -B /afs -B /cvmfs --pwd /srv     /cvmfs/unpacked.cern.ch/registry.hub.docker.com/${COFFEA_IMAGE}     /usr/local/bin/python3 job_1.py -e dask
        
        