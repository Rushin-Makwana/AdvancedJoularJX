import os
import re
import csv
import statistics
import datetime
import matplotlib.pyplot as plt

TARGET_CLASS = "org.noureddine.joularjx.OverallEnergyValidationOverloads"

# Target metric to analyze: "TOTAL_PROGRAM" or a specific method name
#TARGET_METRIC = "org.noureddine.joularjx.PrimeUtils.isPrime(int)"  # Example method signature; adjust as needed
TARGET_METRIC = "TOTAL_PROGRAM"  # Analyze total program energy consumption

# If analyzing a method, specify which column to extract: "Self Energy (Joules)" or "Total Energy (Joules)"
METHOD_ENERGY_COLUMN = "Self Energy (Joules)"

# Run indexing
NUM_RUNS = 42
WARMUP_RUNS = 2

# EXTENDED_ROOT = "/Users/mac/Downloads/joularjx-3.1.0"
ORIGINAL_ROOT = "/Users/mac/Documents/RA/joularjx"

def sanitize_method_name(name):
    name = name.strip()
    if "(" in name:
        return name.split("(")[0].strip()
    return name

def get_total_program_energy(log_path):
    if not os.path.exists(log_path):
        return None
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"Program consumed ([\d\.,]+) joules", content)
        if match:
            return float(match.group(1).replace(",", "."))
        return None
    except Exception as e:
        return None

def get_method_energy_from_csv(csv_path, method_name, strip_parameters=False):
    if not os.path.exists(csv_path):
        return None
    try:
        if strip_parameters:
            if "(" in method_name:
                method_name = method_name.split("(")[0].strip()
                
        with open(csv_path, mode='r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or "Method Name" in line:
                    continue
                parts = line.rsplit(",", 2)
                if len(parts) >= 3:
                    row_method = parts[0].strip()
                    if strip_parameters:
                        if "(" in row_method:
                            row_method = row_method.split("(")[0].strip()
                            
                    if method_name in row_method:
                        col_idx = -1 if METHOD_ENERGY_COLUMN == "Total Energy (Joules)" else -2
                        return float(parts[col_idx].strip())
                elif len(parts) == 2:
                    row_method = parts[0].strip()
                    if strip_parameters:
                        if "(" in row_method:
                            row_method = row_method.split("(")[0].strip()
                            
                    if method_name in row_method:
                        return float(parts[1].strip())
        return None
    except Exception as e:
        return None

def extract_readings(raw_data_dir, strip_parameters=False):
    readings = []
    if TARGET_METRIC == "TOTAL_PROGRAM":
        consolidated_csv = os.path.join(raw_data_dir, "total_energies.csv")
        if os.path.exists(consolidated_csv):
            with open(consolidated_csv, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    run_num = int(row["run_num"])
                    if run_num > WARMUP_RUNS and run_num <= (WARMUP_RUNS + NUM_RUNS):
                        readings.append(float(row["total_energy"]))
    else:
        start_run = WARMUP_RUNS + 1
        end_run = NUM_RUNS + WARMUP_RUNS
        for i in range(start_run, end_run + 1):
            csv_path = os.path.join(raw_data_dir, f"run_{i}.csv")
            val = get_method_energy_from_csv(csv_path, TARGET_METRIC, strip_parameters)
            if val is not None:
                readings.append(val)
    return readings

def main():
    class_basename = TARGET_CLASS.split(".")[-1]
    
    orig_dir = os.path.join("raw_data", "joularjx", class_basename)
    ext_dir = os.path.join("raw_data", "joularjx-3.1.0", class_basename)
    if not os.path.exists(ext_dir):
        ext_dir = os.path.join("raw_data", class_basename)
    
    orig_readings = extract_readings(orig_dir, strip_parameters=True)
    ext_readings = extract_readings(ext_dir, strip_parameters=False)
    
    if not orig_readings and not ext_readings:
        print("Error: No energy readings could be extracted from saved data. Please check raw_data directories.")
        return
        
    n_orig = len(orig_readings)
    n_ext = len(ext_readings)
    
    orig_mean = statistics.mean(orig_readings) if orig_readings else 0.0
    ext_mean = statistics.mean(ext_readings) if ext_readings else 0.0
    
    orig_var = statistics.variance(orig_readings) if n_orig > 1 else 0.0
    ext_var = statistics.variance(ext_readings) if n_ext > 1 else 0.0
    
    abs_diff = abs(ext_mean - orig_mean)
    diff_pct = (abs_diff / orig_mean) * 100 if orig_mean > 0 else 0.0
    
    # Print the detailed Statistical Summary Report
    print("\n" + "="*129)
    print("                                            STATISTICAL SUMMARY REPORT")
    print("="*129)
    print(f"Target Class:           {TARGET_CLASS}")
    print(f"Target Metric Analyzed: {TARGET_METRIC}")
    print(f"Total Successful Runs:  Original: {n_orig}/{NUM_RUNS} | Extended: {n_ext}/{NUM_RUNS}")
    print("-" * 129)
    print(f"{'Metric':<38} | {'Ext Value':<15} | {'Orig Value':<15} | {'Abs Diff (J)':<15} | {'Diff (%)':<10}")
    print("-" * 129)
    print(f"{'Sample Mean (x̄)':<38} | {ext_mean:<15.4f} | {orig_mean:<15.4f} | {abs_diff:<15.4f} | {diff_pct:.2f}%")
    print(f"{'Sample Variance (s²)':<38} | {ext_var:<15.6f} | {orig_var:<15.6f} | {'-':<15} | {'-':<10}")
    if orig_readings and ext_readings:
        print(f"{'Minimum Energy':<38} | {min(ext_readings):<15.4f} | {min(orig_readings):<15.4f} | {'-':<15} | {'-':<10}")
        print(f"{'Maximum Energy':<38} | {max(ext_readings):<15.4f} | {max(orig_readings):<15.4f} | {'-':<15} | {'-':<10}")
    print("="*129)

    # Generate comparative histograms
    if orig_readings and ext_readings:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        metric_sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", TARGET_METRIC)
        histograms_dir = "histograms"
        os.makedirs(histograms_dir, exist_ok=True)
        histogram_output = os.path.join(histograms_dir, f"{metric_sanitized}_{timestamp}.png")
        
        plt.figure(figsize=(12, 5))
        
        # Left: Original
        plt.subplot(1, 2, 1)
        plt.hist(orig_readings, bins=15, color='#E2844A', edgecolor='#B3541A', alpha=0.85, rwidth=0.9)
        plt.title(f"Original - {TARGET_METRIC}", fontsize=11, fontweight='bold')
        plt.xlabel("Energy Consumed (Joules)")
        plt.ylabel("Count (Runs)")
        orig_stats = f"Runs: {n_orig}\nMean: {orig_mean:.3f} J\nVar: {orig_var:.5f} J²"
        plt.gca().text(0.95, 0.95, orig_stats, transform=plt.gca().transAxes, fontsize=9,
                        verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8, edgecolor='#D3D3D3'))
        
        # Right: Extended
        plt.subplot(1, 2, 2)
        plt.hist(ext_readings, bins=15, color='#4A90E2', edgecolor='#1F4E79', alpha=0.85, rwidth=0.9)
        plt.title(f"Extended - {TARGET_METRIC}", fontsize=11, fontweight='bold')
        plt.xlabel("Energy Consumed (Joules)")
        plt.ylabel("Count (Runs)")
        ext_stats = f"Runs: {n_ext}\nMean: {ext_mean:.3f} J\nVar: {ext_var:.5f} J²"
        plt.gca().text(0.95, 0.95, ext_stats, transform=plt.gca().transAxes, fontsize=9,
                        verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8, edgecolor='#D3D3D3'))
        
        plt.tight_layout()
        plt.savefig(histogram_output, dpi=300)
        plt.close()
        print(f"\nComparative histogram saved successfully to {histogram_output}")

if __name__ == "__main__":
    main()
