import os
import re
import csv
import statistics
import datetime
import matplotlib.pyplot as plt

TARGET_CLASS = "org.noureddine.joularjx.org.noureddine.joularjx.OverloadTest"

# Path to the JoularJX root directory (can be relative or absolute)
JOULARJX_ROOT = "../"
JOULARJX_ROOT_ABS = os.path.abspath(JOULARJX_ROOT)

# Target metric to analyze: "TOTAL_PROGRAM" or a specific method name
# Example 1: TARGET_METRIC = "org.noureddine.joularjx.TestWorkload.methodA()"
# Example 2: TARGET_METRIC = "org.noureddine.joularjx.PerThreadTest.runWorkloadA()"
TARGET_METRIC = "org.noureddine.joularjx.org.noureddine.joularjx.OverloadTest.process(int)"

# If analyzing a method, specify which column to extract: "Self Energy (Joules)" or "Total Energy (Joules)"
METHOD_ENERGY_COLUMN = "Self Energy (Joules)"

# Run indexing (must match data collection script configurations)
NUM_RUNS = 40
WARMUP_RUNS = 2

def sanitize_method_name(name):
    """Removes parameters and parentheses to extract the base fully qualified method name."""
    name = name.strip()
    if "(" in name:
        return name.split("(")[0].strip()
    return name

def get_total_program_energy(log_path):
    """Parses total program energy from the saved console log file."""
    if not os.path.exists(log_path):
        print(f"Warning: Log file not found at {log_path}")
        return None
        
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        match = re.search(r"Program consumed ([\d\.,]+) joules", content)
        if match:
            # Replace comma with dot if locale formats it differently
            return float(match.group(1).replace(",", "."))
            
        print(f"Warning: 'Program consumed X joules' not found in log: {log_path}")
        return None
    except Exception as e:
        print(f"Error parsing log {log_path}: {e}")
        return None

def get_method_energy_from_csv(csv_path, method_name):
    """Parses a specific method's energy from the saved run CSV file."""
    if not os.path.exists(csv_path):
        print(f"Warning: CSV file not found at {csv_path}")
        return None
        
    try:
        has_parentheses = "(" in method_name
        target_trimmed = method_name.strip()
        sanitized_target = sanitize_method_name(method_name)
        
        with open(csv_path, mode='r', encoding='utf-8') as f:
            if has_parentheses:
                # Format A: Headered CSV (3 columns)
                reader = csv.DictReader(f)
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                
                for row in reader:
                    row_method = row.get("Method Name", "").strip()
                    if row_method == target_trimmed:
                        val_str = row.get(METHOD_ENERGY_COLUMN, "")
                        if val_str:
                            return float(val_str.strip())
            else:
                # Format B: Headerless CSV (2 columns: Method, Energy)
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    row_method = row[0].strip()
                    sanitized_row_method = sanitize_method_name(row_method)
                    if sanitized_row_method == sanitized_target:
                        val_str = row[1]
                        if val_str:
                            return float(val_str.strip())
                            
        print(f"Warning: Method '{method_name}' not found in CSV {csv_path}")
        return None
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {e}")
        return None

def get_raw_data_dir():
    """Resolve the raw data directory for the current JoularJX root layout."""
    class_name = TARGET_CLASS.split(".")[-1]
    root_label = "" if JOULARJX_ROOT == "../" else os.path.basename(os.path.normpath(JOULARJX_ROOT_ABS))

    new_style_dir = os.path.join("raw_data", root_label, class_name) if root_label else os.path.join("raw_data", class_name)
    legacy_dir = os.path.join("raw_data", re.sub(r"[^a-zA-Z0-9_]", "_", TARGET_CLASS))

    for candidate in [new_style_dir, legacy_dir]:
        if os.path.exists(candidate):
            return candidate

    return new_style_dir


def main():
    raw_data_dir = get_raw_data_dir()
    
    if not os.path.exists(raw_data_dir):
        print(f"Error: Raw data directory '{raw_data_dir}' does not exist. Please run collection first.")
        return

    energy_readings = []
    
    # Loop over the valid run indices (skipping warmup runs)
    start_run = WARMUP_RUNS + 1
    end_run = NUM_RUNS + WARMUP_RUNS
    
    print(f"Analyzing {NUM_RUNS} runs (runs {start_run} to {end_run}) for: {TARGET_METRIC}...")
    for i in range(start_run, end_run + 1):
        if TARGET_METRIC == "TOTAL_PROGRAM":
            log_path = os.path.join(raw_data_dir, f"run_{i}.log")
            val = get_total_program_energy(log_path)
        else:
            csv_path = os.path.join(raw_data_dir, f"run_{i}.csv")
            val = get_method_energy_from_csv(csv_path, TARGET_METRIC)
            
        if val is not None:
            energy_readings.append(val)

    if not energy_readings:
        print("Error: No energy readings could be extracted from saved data.")
        return

    # Calculate statistics
    n = len(energy_readings)
    mean_val = statistics.mean(energy_readings)
    variance_val = statistics.variance(energy_readings) if n > 1 else 0.0
    min_val = min(energy_readings)
    max_val = max(energy_readings)
    bin_width = (max_val - min_val) / 15.0

    # Generate unique timestamped filename for histogram
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    metric_sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", TARGET_METRIC)
    
    histograms_dir = "histograms"
    os.makedirs(histograms_dir, exist_ok=True)
    histogram_output = os.path.join(histograms_dir, f"{TARGET_METRIC}_{timestamp}.png")
    
    print(f"\nGenerating histogram and saving to {histogram_output}...")
    plt.figure(figsize=(10, 6))
    counts, bins, patches = plt.hist(energy_readings, bins=15, density=False, color='#4A90E2', edgecolor='#1F4E79', alpha=0.85, rwidth=0.9)
    plt.title(f"JoularJX Energy Distribution ({TARGET_METRIC})", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Energy Consumed (Joules)", fontsize=12, labelpad=10)
    plt.ylabel("Count (Number of Runs)", fontsize=12, labelpad=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add stats box to the plot
    stats_text = f"Runs: {n}\nMean: {mean_val:.3f} J\nVariance: {variance_val:.5f} J²"
    plt.gca().text(0.95, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=10,
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='#D3D3D3'))

    plt.tight_layout()
    plt.savefig(histogram_output, dpi=300)
    plt.close()
    print("Histogram generated successfully.")

    # Print the detailed Statistical Summary Report
    print("\n" + "="*55)
    print("              STATISTICAL SUMMARY REPORT")
    print("="*55)
    print(f"Target Class:           {TARGET_CLASS}")
    print(f"Target Metric Analyzed: {TARGET_METRIC}")
    print(f"Total Successful Runs:  {n} / {NUM_RUNS}")
    print(f"Minimum Energy:         {min_val:.4f} Joules")
    print(f"Maximum Energy:         {max_val:.4f} Joules")
    print(f"Energy Range:           {max_val - min_val:.4f} Joules")
    print(f"Sample Mean (x̄):        {mean_val:.4f} Joules")
    print(f"Sample Variance (s²):   {variance_val:.6f} Joules²")
    print(f"Sub-interval (Bin Width): {bin_width:.4f} Joules")
    print("="*55)

if __name__ == "__main__":
    main()
