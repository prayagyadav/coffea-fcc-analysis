# Set up

## Requirements: 
1. Access to `/cvmfs`
2. Access to `/eos`
3. To have read access to the FCC pre-generated samples, one needs to be subscribed to the following e-group (with owner approval): `fcc-eos-access`.

## Workflow
`coffea-fcc-analyses` uses coffea 2024.5.0 with python 3.11 and dask in an almalinux 8 singularity container.

1. Clone the [coffea-ffc-analyses](https://github.com/prayagyadav/coffea-fcc-analyses.git) repository
2. `cd coffea-fcc-analyses`
3. The container shell could be started with executing `./shell` at the root of the [coffea-ffc-analyses](https://github.com/prayagyadav/coffea-fcc-analyses.git) repository.

Once can also modify `shell` by editing it. The current contents of `shell` are :
```bash
#!/usr/bin/env bash

if [ "$1" == "" ]; then
	export COFFEA_IMAGE=coffeateam/coffea-dask-almalinux8:2024.5.0-py3.11
else
	export COFFEA_IMAGE=$1
fi

echo "Coffea Image: ${COFFEA_IMAGE}"

EXTERNAL_BIND=${PWD}

singularity exec -B /etc/condor -B /eos -B /afs -B /cvmfs --pwd ${PWD} \
	/cvmfs/unpacked.cern.ch/registry.hub.docker.com/${COFFEA_IMAGE} \
	/bin/bash --rcfile /srv/.bashrc
```
