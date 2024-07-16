#!/usr/bin/bash
export COFFEA_IMAGE=coffeateam/coffea-dask-almalinux8:2024.5.0-py3.11
echo "Coffea Image: ${COFFEA_IMAGE}"
EXTERNAL_BIND=${PWD}
echo $(pwd)
echo $(ls)
singularity exec -B /etc/condor -B /eos -B /afs -B /cvmfs --pwd ${PWD} /cvmfs/unpacked.cern.ch/registry.hub.docker.com/${COFFEA_IMAGE} /usr/local/bin/python3 job_3.py -e dask >> singularity.log.job_3
echo $(ls)