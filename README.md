# COFFEA FCC Analyses

## Setup
Start a singularity shell with coffea with
```bash
./shell
```
## Examples
Example Analyses are separated into these files:
- processor_<example_name>.py
- runner_<example_name>.py
- plotter_<example_name>.py

To run the ZH Recoil example:

Step 0 : Clone this repository

1. Navigate to example folder
   ```bash
   cd examples/FCCee/higgs/mHrecoil/mumu/
   ```
2. Start the singularity shell
   ```bash
   ./shell
   ```
3. A] Local Execution
  Within the shell execute runner_mHrecoil.py with the desired parameters(--executor or -e set to dask by default). The output file would be saved at ./output/FCCee/higgs/mH-recoil/mumu/.
     ```bash
     python3 runner_mHrecoil.py -e dask
     ```
  One can also choose to split up the processing and results in chunks with the --chunks or -c argument
    ```bash
    python3 runner_mHrecoil.py -e dask -c 8
    ```
  B] Batch Execution with HTCondor
  Choosing the executor as condor one can generate job and submit files and a master submit file called condor.sh
    ```bash
    python3 runner_mHrecoil.py -e condor -c 8
    ```
  Now exit the container shell with exit , move to the directory where the files are created(by default Batch) and run condor.sh without getting into the shell
  ```bash
  singularity>exit
  cd Batch
  ./condor.sh
  ```
4. Generate plots with plotter_mHrecoil.py. The plots would be saved at ./output/FCCee/higgs/mH-recoil/mumu/plots/
   ```bash
   python3 plotter_mHrecoil.py
   ```
  If the plots are generated in a different folder than ./output/FCCee/higgs/mH-recoil/mumu/ , input it's path with the --input or -i keyword. For example for batch submission, the outputs are saved in Batch directory.
  ```bash
  python3 plotter_mHrecoil.py -i Batch
  ```
