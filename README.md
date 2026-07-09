# Simulation Output Verification Tool

This tool verifies if two OMNeT++ simulation runs (e.g., standard TraCI and a custom gRPC version) produce identical results. 

Directly hashing output files (using MD5/SHA-256) always fails because OMNeT++ generates unique metadata headers for each run (such as the datetime, process ID, and run execution ID). This script filters out those dynamic header lines, allowing you to hash only the actual simulation data and configs.

## Contents
* `compare_simulation_outputs.py`: The Python script that parses, cleans, and hashes the files.
* `TraciGeneral-#0.vec`: The legacy TraCI output vector file.
* `grpcGeneral-#0.vec`: The new gRPC output vector file.

---

## How to Run

Open your terminal or command prompt, navigate to this folder, and run:

```bash
cd "/mnt/f/4. Academic(MSc)/Thesis/PLOT_VEC_HASH"
python compare_simulation_outputs.py TraciGeneral-#0.vec grpcGeneral-#0.vec
```

---

## Author
* **MD AHSANUL BARI**