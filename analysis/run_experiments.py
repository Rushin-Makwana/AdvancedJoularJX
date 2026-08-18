import os
import re
import shutil
import time
import subprocess

NUM_RUNS = 40          # Number of valid runs for statistics
WARMUP_RUNS = 2        # Number of initial runs to discard
COOL_DOWN_SLEEP = 10   # Cool-down sleep in seconds between runs (mitigates thermal throttling)
TARGET_CLASS = "org.noureddine.joularjx.OverallEnergyValidationThreads"
SAMPLE_RATE_MS = 1000  # Will be written to config.properties

EXTENDED_ROOT = "/Users/mac/Downloads/joularjx-3.1.0"
ORIGINAL_ROOT = "/Users/mac/Documents/RA/joularjx"

def setup_environment(root_dir_abs):
    """Ensures agent configuration properties are set to read native hardware metrics."""
    config_file = os.path.join(root_dir_abs, "config.properties")
    print(f"Setting up profiling environment using root: {root_dir_abs}...")
    
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            content = f.read()
        
        content = re.sub(
            r"^stack-monitoring-sample-rate=.*",
            f"stack-monitoring-sample-rate={SAMPLE_RATE_MS}",
            content,
            flags=re.MULTILINE
        )
        content = re.sub(
            r"^vm-monitoring=.*",
            "vm-monitoring=false",
            content,
            flags=re.MULTILINE
        )
        with open(config_file, "w") as f:
            f.write(content)
        print(f"Updated {config_file} with sample rate: {SAMPLE_RATE_MS}ms and disabled VM monitoring (native mode enabled)")
    else:
        print(f"Warning: {config_file} not found. Using defaults in agent JAR.")

def get_newest_result_dir(root_dir_abs):
    """Identifies the newest result directory inside joularjx-result/ using folder timestamps."""
    results_dir = os.path.join(root_dir_abs, "joularjx-result")
    if not os.path.exists(results_dir):
        return None
    folders = [f for f in os.listdir(results_dir) if "-" in f and os.path.isdir(os.path.join(results_dir, f))]
    if not folders:
        return None
    try:
        newest_folder = max(folders, key=lambda f: int(f.split("-")[1]))
        return os.path.join(results_dir, newest_folder)
    except Exception as e:
        print(f"Error parsing folder timestamps: {e}")
        return None

def copy_csv_to_raw_data(result_dir, dest_path):
    """Finds the all-methods energy CSV inside the result directory and copies it."""
    methods_dir = os.path.join(result_dir, "all", "total", "methods")
    if not os.path.exists(methods_dir):
        return False
    csv_files = [f for f in os.listdir(methods_dir) if f.endswith(".csv")]
    if not csv_files:
        return False
    src_csv = os.path.join(methods_dir, csv_files[0])
    shutil.copy2(src_csv, dest_path)
    return True

def run_single_experiment(run_num, total_runs, raw_data_dir, root_dir_abs, jar_path, classpath):
    """Runs a single iteration of the Java workload with the agent and saves the logs and CSV."""
    cmd = [
        "sudo",
        "java",
        f"-javaagent:{jar_path}",
        "-cp", classpath,
        TARGET_CLASS
    ]
    
    run_label = f"Warm-up Run {run_num}" if run_num <= WARMUP_RUNS else f"Valid Run {run_num - WARMUP_RUNS}"
    print(f"[{run_num}/{total_runs}] [{run_label}] Executing target class: {TARGET_CLASS}...")
    
    result = subprocess.run(cmd, cwd=root_dir_abs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    combined_output = result.stdout + "\n" + result.stderr
    
    if result.returncode != 0:
        print(f"[{run_num}/{total_runs}] Error: Java process exited with non-zero code: {result.returncode}")
        return False

    # Parse and save overall program energy to a single consolidated CSV file
    match = re.search(r"Program consumed ([\d\.,]+) joules", combined_output)
    if match:
        val = float(match.group(1).replace(",", "."))
        consolidated_csv = os.path.join(raw_data_dir, "total_energies.csv")
        write_header = not os.path.exists(consolidated_csv)
        with open(consolidated_csv, "a", encoding="utf-8") as f:
            if write_header:
                f.write("run_num,total_energy\n")
            f.write(f"{run_num},{val}\n")

    newest_dir = get_newest_result_dir(root_dir_abs)
    if newest_dir:
        csv_dest = os.path.join(raw_data_dir, f"run_{run_num}.csv")
        if copy_csv_to_raw_data(newest_dir, csv_dest):
            print(f"[{run_num}/{total_runs}] Success. Saved output to run_{run_num}.csv")
            return True
            
    print(f"[{run_num}/{total_runs}] Warning: Could not locate result CSV files.")
    return False

def run_for_root(root_path, label):
    root_dir_abs = os.path.abspath(root_path)
    setup_environment(root_dir_abs)
    
    class_name = TARGET_CLASS.split(".")[-1]
    raw_data_dir = os.path.join("raw_data", label, class_name)
    os.makedirs(raw_data_dir, exist_ok=True)
    print(f"Output raw data directory: {os.path.abspath(raw_data_dir)}\n")
    
    # Remove old consolidated energy file if it exists
    consolidated_csv = os.path.join(raw_data_dir, "total_energies.csv")
    if os.path.exists(consolidated_csv):
        os.remove(consolidated_csv)
    
    total_runs = NUM_RUNS + WARMUP_RUNS
    jar_path = os.path.join(root_dir_abs, "target", "joularjx-3.1.0.jar")
    # Clean classpath pointing to Extended compiled tests to avoid namespace collision
    classpath = os.path.join(os.path.abspath(EXTENDED_ROOT), 'target', 'test-classes')
    
    print(f"Executing {WARMUP_RUNS} warm-up runs to eliminate OS disk caching bias...")
    for i in range(1, WARMUP_RUNS + 1):
        run_single_experiment(i, total_runs, raw_data_dir, root_dir_abs, jar_path, classpath)
        if COOL_DOWN_SLEEP > 0:
            print(f"Sleeping for {COOL_DOWN_SLEEP} seconds...")
            time.sleep(COOL_DOWN_SLEEP)
            
    print(f"\nExecuting {NUM_RUNS} valid runs for statistical analysis...")
    for i in range(WARMUP_RUNS + 1, total_runs + 1):
        success = run_single_experiment(i, total_runs, raw_data_dir, root_dir_abs, jar_path, classpath)
        if not success:
            print(f"Warning: Run {i} failed. Stopping loop.")
            break
        if COOL_DOWN_SLEEP > 0 and i < total_runs:
            print(f"Sleeping for {COOL_DOWN_SLEEP} seconds...")
            time.sleep(COOL_DOWN_SLEEP)

def main():
    print(">>> RUNNING EXPERIMENTS FOR ORIGINAL VERSION <<<")
    run_for_root(ORIGINAL_ROOT, "joularjx")
    
    print("\n\n>>> RUNNING EXPERIMENTS FOR EXTENDED VERSION <<<")
    run_for_root(EXTENDED_ROOT, "joularjx-3.1.0")
    
    print("\nData collection finished successfully for both versions.")

if __name__ == "__main__":
    main()
