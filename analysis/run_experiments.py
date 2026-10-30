import os
import re
import shutil
import time
import subprocess

NUM_RUNS = 50          # Number of valid runs for statistics
WARMUP_RUNS = 2        # Number of initial runs to discard
COOL_DOWN_SLEEP = 1    # Cool-down sleep in seconds between runs
TARGET_CLASS = "io.github.jbellis.jvector.example.tutorial.VectorIntro"

EXTENDED_ROOT = "/Users/mac/Downloads/joularjx-3.1.0"
ORIGINAL_ROOT = "/Users/mac/Documents/RA/joularjx"

def setup_environment(root_dir_abs, sub_sample_rate_ms=10):
    """Ensures agent configuration properties are set to read native hardware metrics."""
    config_file = os.path.join(root_dir_abs, "config.properties")
    print(f"Setting up profiling environment using root: {root_dir_abs} (Sub-sample Rate: {sub_sample_rate_ms}ms)...")
    
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            content = f.read()
        
        # Remove custom property key if present
        content = re.sub(r"^stack-monitoring-sample-period=.*\n?", "", content, flags=re.MULTILINE)

        if "stack-monitoring-sample-rate=" in content:
            content = re.sub(
                r"^stack-monitoring-sample-rate=.*",
                f"stack-monitoring-sample-rate={sub_sample_rate_ms}",
                content,
                flags=re.MULTILINE
            )
        else:
            content += f"\nstack-monitoring-sample-rate={sub_sample_rate_ms}\n"

        with open(config_file, "w") as f:
            f.write(content)

        print(f"Updated {config_file} with sub-sample rate: {sub_sample_rate_ms}ms")
    else:
        print(f"Warning: {config_file} not found. Using defaults in agent JAR.")

def get_newest_result_dir(root_dir_abs):
    """Identifies the newest result directory inside joularjx-result/ using folder timestamps."""
    results_dir = os.path.join(root_dir_abs, "joularjx-result")
    if not os.path.exists(results_dir):
        return None

    try:
        subdirs = [os.path.join(results_dir, d) for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
        if not subdirs:
            return None
        subdirs.sort(key=lambda d: os.path.getmtime(d), reverse=True)
        return subdirs[0]
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

JVECTOR_JAR = "/Users/mac/Developer/jvector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar"
JAVA_BIN = "/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java"

def run_single_experiment(run_num, total_runs, raw_data_dir, root_dir_abs, jar_path, classpath, sample_period_ms=1000):
    """Runs a single iteration of the Java workload with the agent and saves the logs and CSV."""
    cmd = [
        JAVA_BIN,
        "-XX:CompileCommand=dontinline,io.github.jbellis.jvector.*::*",
        "--add-modules=jdk.incubator.vector",
        f"-Djoularjx.sampleTime={sample_period_ms}",
        f"-Djoularjx.config={os.path.join(root_dir_abs, 'config.properties')}",
        f"-javaagent:{jar_path}",
        "-cp", JVECTOR_JAR if "jvector" in TARGET_CLASS.lower() else classpath,
        TARGET_CLASS
    ]
    
    run_label = f"Warm-up Run {run_num}" if run_num <= WARMUP_RUNS else f"Valid Run {run_num - WARMUP_RUNS}"
    print(f"[{run_num}/{total_runs}] [{run_label}] Executing target class: {TARGET_CLASS} (Sample Period: {sample_period_ms}ms)...")
    
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

def run_for_root(root_path, label, sample_period_ms=1000, sub_sample_rate_ms=10):
    root_dir_abs = os.path.abspath(root_path)
    setup_environment(root_dir_abs, sub_sample_rate_ms)
    
    class_name = TARGET_CLASS.split(".")[-1]
    raw_data_dir = os.path.join("raw_data", label, class_name)
    os.makedirs(raw_data_dir, exist_ok=True)
    print(f"Output raw data directory: {os.path.abspath(raw_data_dir)}\n")
    
    # Remove old consolidated energy file if it exists
    consolidated_csv = os.path.join(raw_data_dir, "total_energies.csv")
    if os.path.exists(consolidated_csv):
        os.remove(consolidated_csv)
    
    total_runs = NUM_RUNS + WARMUP_RUNS
    jar_path = os.path.join(root_dir_abs, "target", "joularjx-3.1.0.jar") if "3.1.0" in root_path else os.path.join(root_dir_abs, "target", "joularjx-3.0.0.jar")
    if not os.path.exists(jar_path):
        jar_path = os.path.join(root_dir_abs, "target", "joularjx-3.1.0.jar")
    
    classpath = os.path.join(root_dir_abs, 'target', 'test-classes') + ":" + os.path.join(root_dir_abs, 'target', 'classes')
    
    print(f"Executing {WARMUP_RUNS} warm-up runs to eliminate OS disk caching bias...")
    for i in range(1, WARMUP_RUNS + 1):
        run_single_experiment(i, total_runs, raw_data_dir, root_dir_abs, jar_path, classpath, sample_period_ms)
        if COOL_DOWN_SLEEP > 0:
            time.sleep(COOL_DOWN_SLEEP)
            
    print(f"\nExecuting {NUM_RUNS} valid runs for statistical analysis...")
    for i in range(WARMUP_RUNS + 1, total_runs + 1):
        success = run_single_experiment(i, total_runs, raw_data_dir, root_dir_abs, jar_path, classpath, sample_period_ms)
        if not success:
            print(f"Warning: Run {i} failed. Stopping loop.")
            break
        if COOL_DOWN_SLEEP > 0 and i < total_runs:
            time.sleep(COOL_DOWN_SLEEP)

def main():
    global JVECTOR_JAR
    print(">>> 1. RUNNING EXPERIMENTS FOR ORIGINAL JVECTOR BASELINE (50 Valid Runs) <<<")
    JVECTOR_JAR = "/Users/mac/Developer/jvector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar"
    run_for_root(EXTENDED_ROOT, "joularjx", sample_period_ms=1000, sub_sample_rate_ms=10)
    
    print("\n\n>>> 2. RUNNING EXPERIMENTS FOR OPTIMIZED JVECTOR (50 Valid Runs) <<<")
    JVECTOR_JAR = "/Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar"
    run_for_root(EXTENDED_ROOT, "joularjx-3.1.0", sample_period_ms=1000, sub_sample_rate_ms=10)
    
    print("\nData collection finished successfully for both versions.")

if __name__ == "__main__":
    main()
