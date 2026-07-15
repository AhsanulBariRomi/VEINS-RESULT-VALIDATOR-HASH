"""
OMNeT++ Simulation Results Verification Tool
=============================================
This script compares OMNeT++ vector (.vec) or scalar (.sca) files from different
simulation runs (e.g., standard TraCI vs. gRPC implementation).

Since OMNeT++ inserts run-specific metadata (timestamps, process IDs, and run IDs)
into the header of every output file, direct file hashing (MD5/SHA256) will always
fail even if the simulation results are 100% identical.

This script solves this by:
1. Reading the files line-by-line.
2. Filtering out execution-specific metadata lines.
3. Hashing the remaining data points and static parameters.
4. Comparing the resulting hashes.
"""

import os
import sys
import hashlib

# Define the dynamic metadata prefixes to ignore (headers that change on every run)
METADATA_PREFIXES = (
    "run ",            # e.g., "run General-0-20260709-06:38:37-204799"
    "attr datetime",   # e.g., "attr datetime 20260709-06:38:37"
    "attr datetimef",  # e.g., "attr datetimef 20260709-063837"
    "attr processid"   # e.g., "attr processid 204799"
)

def compute_filtered_hash(file_path):
    """
    Reads a file, filters out transient execution metadata, and groups/sorts
    vector declarations and data points by their hierarchical vector names.
    This ensures that the computed hash is completely independent of:
    1. The writing/interleaving order of the lines.
    2. Any variations in dynamic vector ID assignment (e.g. ID 141 vs 143).
    """
    sha256_hash = hashlib.sha256()
    line_count = 0
    filtered_count = 0
    
    # Map: vector_id -> "module_path vector_name"
    vector_names = {}
    # Map: "module_path vector_name" -> list of event-time-value strings
    vector_data = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_count += 1
            stripped_line = line.strip()
            if not stripped_line:
                continue
                
            # Check if the line starts with any of our dynamic metadata prefixes
            if stripped_line.startswith(METADATA_PREFIXES):
                filtered_count += 1
                continue  # Skip this line and do not include it in the hash
            
            if stripped_line.startswith("vector "):
                parts = stripped_line.split()
                if len(parts) >= 4:
                    vec_id = int(parts[1])
                    name = " ".join(parts[2:])
                    vector_names[vec_id] = name
                    if name not in vector_data:
                        vector_data[name] = []
            elif stripped_line[0].isdigit():
                parts = stripped_line.split()
                if len(parts) == 4:
                    vec_id = int(parts[0])
                    name = vector_names.get(vec_id)
                    if name:
                        # Exclude the arbitrary vector ID, store only: event, time, value
                        event_time_val = f"{parts[1]}\t{parts[2]}\t{parts[3]}"
                        vector_data[name].append(event_time_val)
            else:
                # Store structural/meta metadata (like version or static attributes)
                name = f"__meta__:{stripped_line}"
                if name not in vector_data:
                    vector_data[name] = [""]

    # Compute a deterministic hash of the sorted vector data
    for name in sorted(vector_data.keys()):
        sha256_hash.update(f"vector_name:{name}\n".encode("utf-8"))
        for dp in sorted(vector_data[name]):
            sha256_hash.update(f"{dp}\n".encode("utf-8"))

    return sha256_hash.hexdigest(), line_count, filtered_count

def main():
    # Ensure proper command-line arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python compare_simulation_outputs.py <file1> <file2>")
        print("Example: python compare_simulation_outputs.py TraciGeneral-#0.vec grpcGeneral-#0.vec")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    # Validate that files exist
    for file_path in (file1, file2):
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            sys.exit(1)

    print("=" * 60)
    print(" OMNeT++ Simulation Output Comparer ")
    print("=" * 60)

    # Compute hashes and file stats
    print(f"Analyzing File 1: {file1}...")
    hash1, lines1, filtered1 = compute_filtered_hash(file1)
    
    print(f"Analyzing File 2: {file2}...")
    hash2, lines2, filtered2 = compute_filtered_hash(file2)
    
    print("-" * 60)
    print(f"File 1 ({os.path.basename(file1)}):")
    print(f"  Total Lines   : {lines1}")
    print(f"  Filtered Lines: {filtered1} (metadata)")
    print(f"  SHA-256 Hash  : {hash1}")
    print()
    print(f"File 2 ({os.path.basename(file2)}):")
    print(f"  Total Lines   : {lines2}")
    print(f"  Filtered Lines: {filtered2} (metadata)")
    print(f"  SHA-256 Hash  : {hash2}")
    print("-" * 60)

    # Compare results
    if hash1 == hash2:
        print("\nSUCCESS: The simulation outputs are 100% identical!")
        print("Both programs generated the exact same data points and configurations.")
    else:
        print("\nFAILURE: Hashes do not match!")
        print("There are differences in the simulation data points or configuration parameters.")
        
    print("=" * 60)

if __name__ == "__main__":
    main()