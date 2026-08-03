import os
import re
import shutil
import time
import subprocess

NUM_RUNS = 40          # Number of valid runs for statistics
WARMUP_RUNS = 2        # Number of initial runs to discard
COOL_DOWN_SLEEP = 5   # Cool-down sleep in seconds between runs (thermal throttling mitigation)
TARGET_CLASS = "org.noureddine.joularjx.OverloadTest"
SAMPLE_RATE_MS = 1000  # Will be written to config.properties

# Path to the JoularJX root directory (can be relative or absolute)
JOULARJX_ROOT = "/Users/mac/Documents/RA/joularjx/"

# Dynamically resolve absolute paths based on the root directory
JOULARJX_ROOT_ABS = os.path.abspath(JOULARJX_ROOT)
CONFIG_FILE = os.path.join(JOULARJX_ROOT_ABS, "config.properties")
JAR_PATH = os.path.join(JOULARJX_ROOT_ABS, "target", "joularjx-3.1.0.jar")
CLASSPATH = f"{os.path.join(JOULARJX_ROOT_ABS, 'target', 'test-classes')}:{os.path.join(JOULARJX_ROOT_ABS, 'target', 'classes')}"

def setup_environment():
    """Ensures agent configuration properties are set to read native hardware metrics."""
    print(f"Setting up profiling environment using root: {JOULARJX_ROOT_ABS}...")
    
    # Ensure config.properties settings are correct
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            content = f.read()
        
        # Replace sample rate
        content = re.sub(
            r"^stack-monitoring-sample-rate=.*",
            f"stack-monitoring-sample-rate={SAMPLE_RATE_MS}",
            content,
            flags=re.MULTILINE
        )
        # Ensure vm-monitoring is disabled to read real hardware RAPL/powermetrics
        content = re.sub(
            r"^vm-monitoring=.*",
            "vm-monitoring=false",
            content,
            flags=re.MULTILINE
        )
        with open(CONFIG_FILE, "w") as f:
            f.write(content)
        print(f"Updated {CONFIG_FILE} with sample rate: {SAMPLE_RATE_MS}ms and disabled VM monitoring (native mode enabled)")
    else:
        print(f"Warning: {CONFIG_FILE} not found at {CONFIG_FILE}. Using defaults in agent JAR.")

def get_newest_result_dir():
    """Identifies the newest result directory inside joularjx-result/ using folder timestamps (Method 1)."""
    results_dir = os.path.join(JOULARJX_ROOT_ABS, "joularjx-result")
    if not os.path.exists(results_dir):
        return None
    folders = [f for f in os.listdir(results_dir) if "-" in f and os.path.isdir(os.path.join(results_dir, f))]
    if not folders:
        return None
    try:
        # Find folder with highest starting timestamp (Method 1)
        newest_folder = max(folders, key=lambda f: int(f.split("-")[1]))
        return os.path.join(results_dir, newest_folder)
    except Exception as e:
        print(f"Error parsing folder timestamps: {e}")
        return None

def copy_csv_to_raw_data(result_dir, dest_path):
    """Finds the all-methods energy CSV inside the result directory and copies it."""
    methods_dir = os.path.join(result_dir, "all", "total", "methods")
    if not os.path.exists(methods_dir):
        print(f"Warning: Methods directory not found at {methods_dir}")
        return False
    
    csv_files = [f for f in os.listdir(methods_dir) if f.endswith(".csv")]
    if not csv_files:
        print(f"Warning: No CSV file found in {methods_dir}")
        return False
    
    src_csv = os.path.join(methods_dir, csv_files[0])
    shutil.copy2(src_csv, dest_path)
    return True

def run_single_experiment(run_num, total_runs, raw_data_dir):
    """Runs a single iteration of the Java workload with the agent and saves the logs and CSV."""
    cmd = [
        "sudo",
        "java",
        f"-javaagent:{JAR_PATH}",
        "-cp", CLASSPATH,
        TARGET_CLASS
    ]
    
    # Warm-up indicator
    run_label = f"Warm-up Run {run_num}" if run_num <= WARMUP_RUNS else f"Valid Run {run_num - WARMUP_RUNS}"
    print(f"[{run_num}/{total_runs}] [{run_label}] Executing target class: {TARGET_CLASS}...")
    
    # Run the subprocess executing in the resolved root directory
    result = subprocess.run(cmd, cwd=JOULARJX_ROOT_ABS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    combined_output = result.stdout + "\n" + result.stderr
    
    
    # Check for process exit code failures
    if result.returncode != 0:
        print(f"[{run_num}/{total_runs}] Error: Java process exited with non-zero code: {result.returncode}")
        print("--- Output snippet ---")
        print(combined_output[-500:])
        print("----------------------")
        return False

    # Locate the newest result directory to copy the CSV file
    newest_dir = get_newest_result_dir()
    if newest_dir:
        csv_dest = os.path.join(raw_data_dir, f"run_{run_num}.csv")
        if copy_csv_to_raw_data(newest_dir, csv_dest):
            print(f"[{run_num}/{total_runs}] Success. Saved output to run_{run_num}.csv")
            return True
            
    print(f"[{run_num}/{total_runs}] Warning: Could not locate result CSV files.")
    return False

def main():
    setup_environment()
    
    class_name = TARGET_CLASS.split(".")[-1]
    root_label = "" if JOULARJX_ROOT == "../" else os.path.basename(os.path.normpath(JOULARJX_ROOT_ABS))
    raw_data_dir = os.path.join("raw_data", root_label, class_name) if root_label else os.path.join("raw_data", class_name)
    os.makedirs(raw_data_dir, exist_ok=True)
    print(f"Output raw data directory: {os.path.abspath(raw_data_dir)}\n")
    
    total_runs = NUM_RUNS + WARMUP_RUNS
    
    # Warm-up runs loop
    print(f"Executing {WARMUP_RUNS} warm-up runs to eliminate OS disk caching bias...")
    for i in range(1, WARMUP_RUNS + 1):
        run_single_experiment(i, total_runs, raw_data_dir)
        if COOL_DOWN_SLEEP > 0:
            print(f"Sleeping for {COOL_DOWN_SLEEP} seconds to allow CPU to cool down...")
            time.sleep(COOL_DOWN_SLEEP)
            
    # Valid runs loop
    print(f"\nExecuting {NUM_RUNS} valid runs for statistical analysis...")
    for i in range(WARMUP_RUNS + 1, total_runs + 1):
        success = run_single_experiment(i, total_runs, raw_data_dir)
        if not success:
            print(f"Warning: Run {i} failed. Stopping experiment loop.")
            break
            
        if COOL_DOWN_SLEEP > 0 and i < total_runs:
            print(f"Sleeping for {COOL_DOWN_SLEEP} seconds to allow CPU to cool down...")
            time.sleep(COOL_DOWN_SLEEP)
            
    print("\nData collection finished successfully.")

if __name__ == "__main__":
    main()
