# Simulation Output Verification Tool

This tool verifies if two OMNeT++ simulation runs (e.g., standard TraCI and a custom gRPC version) produce identical results. 

Directly hashing output files (using MD5/SHA-256) always fails because OMNeT++ generates unique metadata headers for each run (such as the datetime, process ID, and run execution ID). This script filters out those dynamic header lines, allowing you to hash only the actual simulation data and configs.

# Things that have been taken care of while hashing

Directly comparing OMNeT++ output vector (.vec) files using standard file diffs or basic cryptographic hashing (like MD5 or SHA-256 of the raw files) always fails due to three types of non-deterministic differences that do not affect the actual physical simulation results:

- Execution Metadata: Real-time run stamps, process IDs, and run IDs change on every execution.
- Line Interleaving (Write Order): Depending on slight thread scheduling differences or network delays (especially between a synchronous socket-based TraCI and a gRPC interface), OMNeT++ processes events in slightly different orders, writing lines to the file in a different sequence.
- Dynamic ID Assignment: OMNeT++ assigns sequential numeric IDs (e.g. 141 vs 143) to variables dynamically when vehicles spawn. Minor timing differences in spawning events shuffle these IDs.
Our custom comparison tool overcomes all three issues by parsing, sanitizing, sorting, and hashing the data streams by their hierarchical vector names rather than their arbitrary IDs or line numbers.

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
OR
python compare_simulation_outputs.py 200Accident_TraciGeneral-#0.vec 200Accident_grpcGeneral-#0.vec
OR
python compare_simulation_outputs.py grpcEvaluation_Seeds-#0.vec TraciEvaluation_Seeds-#0.vec
python compare_simulation_outputs.py grpcEvaluation_Seeds-#1.vec TraciEvaluation_Seeds-#1.vec
python compare_simulation_outputs.py grpcEvaluation_Seeds-#2.vec TraciEvaluation_Seeds-#2.vec
python compare_simulation_outputs.py grpcEvaluation_Seeds-#3.vec TraciEvaluation_Seeds-#3.vec
python compare_simulation_outputs.py grpcEvaluation_Seeds-#4.vec TraciEvaluation_Seeds-#4.vec
OR
python compare_simulation_outputs.py grpcGeneralZeroVehicle-#0.vec TraciGeneralZeroVehicle-#0.vec
```

---

## Author
* **MD AHSANUL BARI**