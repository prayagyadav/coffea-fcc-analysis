# COFFEA FCC Analysis

## Setup
Start a singularity shell with coffea with
```bash
./shell
```
## Examples
Example Analyses are separated into 4 files: 
- processor_<example_name>.py
- runner_<example_name>.py
- plotter_<example_name>.py

To run the mHrecoil/mumu example:
Step 0 : Clone this repository

1. Navigate to example folder
   ```bash
   cd examples/mHrecoil/mumu/ 
   ```
2. Start the singularity shell
   ```bash
   ./shell
   ```
3. Within the shell execute runner_mHrecoil.py with the desired parameters. The output file would be saved at ./output/FCCee/higgs/mH-recoil/mumu/.
   ```bash
   python3 runner_mHrecoil.py -e dask
   ```
4. Generate plots with plotter_mHrecoil.py. The plots would be saved at ./output/FCCee/higgs/mH-recoil/mumu/plots/
   ```bash
   python3 plotter_mHrecoil.py
   ```
