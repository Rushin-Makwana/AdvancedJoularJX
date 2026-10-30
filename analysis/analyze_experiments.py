import os
import re
import csv
import statistics
import datetime
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# USER EXPERIMENT CONFIGURATION
# Edit these variables to profile any application (JVector, test workloads, etc.)
TARGET_CLASS = "io.github.jbellis.jvector.example.tutorial.VectorIntro"

# Target Metric: "TOTAL_PROGRAM" or a specific fully-qualified method with parameter types
TARGET_METRIC = "TOTAL_PROGRAM"

# Metric Energy Column to analyze when TARGET_METRIC is a method:
# Options: "Total Energy (Joules)" or "Self Energy (Joules)"
METHOD_ENERGY_COLUMN = "Total Energy (Joules)"

# Run parameters
NUM_RUNS = 50        # Number of valid experimental runs
WARMUP_RUNS = 2      # Number of initial warmup runs to discard

# Sample timing labels for display (matches JoularJX runtime settings)
SAMPLE_PERIOD_MS = 1000
SUB_SAMPLE_RATE_MS = 10

# ==============================================================================
# DIRECTORY RESOLUTION (Application-Agnostic)
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HISTOGRAMS_DIR = os.path.join(SCRIPT_DIR, "histograms")
MERGED_RESULTS_DIR = os.path.join(SCRIPT_DIR, "merged_results")
RAW_DATA_DIR = os.path.join(SCRIPT_DIR, "raw_data")

EXTENDED_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
ORIGINAL_ROOT = "/Users/mac/Documents/RA/joularjx"

def shorten_method_signature(full_signature):
    """
    Dynamically converts a fully qualified method signature into a readable short title.
    Example:
      'io.github.jbellis.jvector.graph.GraphIndexBuilder.addGraphNode(int,io.github.jbellis.jvector.vector.types.VectorFloat)'
      -> 'GraphIndexBuilder.addGraphNode(int, VectorFloat)'
    Works generically for any package and class without hardcoded rules.
    """
    if full_signature == "TOTAL_PROGRAM":
        return "Total Program Energy", "TOTAL_PROGRAM"

    # Match class.method(params)
    match = re.match(r"^(?:.*\.([a-zA-Z0-9_$]+))\s*\((.*)\)$", full_signature)
    if match:
        method_name = match.group(1)
        raw_params = match.group(2).strip()
        if raw_params:
            # Strip package qualifiers from parameter types generically
            clean_params = [re.sub(r"^.*[.$]", "", p.strip()) for p in raw_params.split(",")]
            params_str = ", ".join(clean_params)
            short_title = f"{method_name}({params_str})"
            tag_params = "_".join(re.sub(r"[^a-zA-Z0-9_]", "", p) for p in clean_params)
            file_tag = f"{method_name}_{tag_params}"
        else:
            short_title = f"{method_name}()"
            file_tag = f"{method_name}"
        return short_title, file_tag

    # Fallback if no parentheses
    short_name = full_signature.split(".")[-1]
    return short_name, re.sub(r"[^a-zA-Z0-9_]", "_", short_name)

def resolve_data_dirs(class_basename):
    """
    Locates raw_data directories for Extended and Original JoularJX runs.
    Searches standard candidate paths for the target class.
    """
    ext_candidates = [
        os.path.join(RAW_DATA_DIR, "joularjx-3.1.0", class_basename),
        os.path.join(RAW_DATA_DIR, class_basename),
        os.path.join(SCRIPT_DIR, "..", "raw_data", "joularjx-3.1.0", class_basename),
        os.path.join(SCRIPT_DIR, "..", "raw_data", class_basename),
    ]
    ext_dir = None
    for c in ext_candidates:
        if os.path.exists(c):
            csvs = [f for f in os.listdir(c) if f.startswith("run_") and f.endswith(".csv")]
            if csvs:
                ext_dir = c
                break

    orig_candidates = [
        os.path.join(RAW_DATA_DIR, "joularjx", class_basename),
        os.path.join(SCRIPT_DIR, "..", "raw_data", "joularjx", class_basename),
        os.path.join(ORIGINAL_ROOT, "raw_data", "joularjx", class_basename),
    ]
    orig_dir = None
    for c in orig_candidates:
        if os.path.exists(c):
            csvs = [f for f in os.listdir(c) if f.startswith("run_") and f.endswith(".csv")]
            if csvs:
                orig_dir = c
                break

    return ext_dir, orig_dir

def get_method_energy_from_csv(csv_path, target_metric, strip_parameters=False, energy_column=METHOD_ENERGY_COLUMN):
    """
    Extracts energy for a method from a run CSV.
    Matches exact method name (including parameter signature) when strip_parameters is False.
    If strip_parameters is True, strips parameter types to match unparameterized legacy CSVs.
    """
    if not os.path.exists(csv_path):
        return None
    try:
        target = target_metric.strip()
        if strip_parameters and "(" in target:
            target = target.split("(")[0].strip()

        with open(csv_path, mode='r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or "Method Name" in line:
                    continue
                parts = line.rsplit(",", 2)
                if len(parts) >= 3:
                    row_method = parts[0].strip()
                    if strip_parameters and "(" in row_method:
                        row_method = row_method.split("(")[0].strip()

                    if target == row_method:
                        col_idx = 2 if energy_column == "Total Energy (Joules)" else 1
                        return float(parts[col_idx].strip())
                elif len(parts) == 2:
                    row_method = parts[0].strip()
                    if strip_parameters and "(" in row_method:
                        row_method = row_method.split("(")[0].strip()

                    if target == row_method:
                        return float(parts[1].strip())
        return None
    except Exception:
        return None

def extract_readings(data_dir, target_metric, is_original=False, energy_column=METHOD_ENERGY_COLUMN):
    """
    Extracts readings across all valid runs (WARMUP_RUNS + 1 to WARMUP_RUNS + NUM_RUNS).
    If a method is unobserved in a given run, it receives 0.0 J.
    """
    readings = []
    occurrences = 0
    if not data_dir or not os.path.exists(data_dir):
        return readings, occurrences

    if target_metric == "TOTAL_PROGRAM":
        consolidated_csv = os.path.join(data_dir, "total_energies.csv")
        if os.path.exists(consolidated_csv):
            with open(consolidated_csv, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    run_num = int(row["run_num"])
                    if WARMUP_RUNS < run_num <= (WARMUP_RUNS + NUM_RUNS):
                        readings.append(float(row["total_energy"]))
                        occurrences += 1
        return readings, occurrences

    strip_parameters = is_original
    start_run = WARMUP_RUNS + 1
    end_run = NUM_RUNS + WARMUP_RUNS
    for i in range(start_run, end_run + 1):
        csv_path = os.path.join(data_dir, f"run_{i}.csv")
        val = get_method_energy_from_csv(csv_path, target_metric, strip_parameters=strip_parameters, energy_column=energy_column)
        if val is not None:
            readings.append(val)
            occurrences += 1
        else:
            readings.append(0.0)

    return readings, occurrences

def generate_merged_average_csv(data_dir, output_csv_path, warmup_runs=WARMUP_RUNS, max_runs=NUM_RUNS):
    """
    Computes the average self and total energy across all measured valid runs for each method
    and exports a clean, sortable CSV.
    """
    if not data_dir or not os.path.exists(data_dir):
        return None

    files = [f"run_{i}.csv" for i in range(warmup_runs + 1, warmup_runs + max_runs + 1)]
    valid_files = [os.path.join(data_dir, f) for f in files if os.path.exists(os.path.join(data_dir, f))]
    num_measured_runs = len(valid_files)

    if num_measured_runs == 0:
        return None

    method_data = {}
    for filepath in valid_files:
        with open(filepath, mode='r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or "Method Name" in line:
                    continue
                parts = line.rsplit(",", 2)
                if len(parts) == 3:
                    m_name = parts[0].strip()
                    try:
                        self_e = float(parts[1].strip())
                        total_e = float(parts[2].strip())
                    except ValueError:
                        continue
                    if m_name not in method_data:
                        method_data[m_name] = {"self_sum": 0.0, "total_sum": 0.0, "occurrences": 0}
                    method_data[m_name]["self_sum"] += self_e
                    method_data[m_name]["total_sum"] += total_e
                    method_data[m_name]["occurrences"] += 1
                elif len(parts) == 2:
                    m_name = parts[0].strip()
                    try:
                        val = float(parts[1].strip())
                    except ValueError:
                        continue
                    if m_name not in method_data:
                        method_data[m_name] = {"self_sum": 0.0, "total_sum": 0.0, "occurrences": 0}
                    method_data[m_name]["self_sum"] += val
                    method_data[m_name]["total_sum"] += val
                    method_data[m_name]["occurrences"] += 1

    records = []
    for m_name, d in method_data.items():
        records.append({
            "Method Name": m_name,
            "Average Self Energy (Joules)": d["self_sum"] / num_measured_runs,
            "Average Total Energy (Joules)": d["total_sum"] / num_measured_runs,
            "Runs Present": d["occurrences"],
            "Total Measured Runs": num_measured_runs
        })

    records.sort(key=lambda x: x["Average Total Energy (Joules)"], reverse=True)

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = [
            "Method Name",
            "Average Self Energy (Joules)",
            "Average Total Energy (Joules)",
            "Runs Present",
            "Total Measured Runs"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({
                "Method Name": r["Method Name"],
                "Average Self Energy (Joules)": f"{r['Average Self Energy (Joules)']:.8e}",
                "Average Total Energy (Joules)": f"{r['Average Total Energy (Joules)']:.8e}",
                "Runs Present": r["Runs Present"],
                "Total Measured Runs": r["Total Measured Runs"]
            })

    print(f"\nMerged average CSV saved successfully to:\n  {output_csv_path}\n  (Averaged over {num_measured_runs} runs, {len(records)} distinct methods)")
    return output_csv_path

def main():
    class_basename = TARGET_CLASS.split(".")[-1]
    ext_dir, orig_dir = resolve_data_dirs(class_basename)

    if not ext_dir and not orig_dir:
        print(f"Error: No raw_data directory found for {class_basename} under {RAW_DATA_DIR}")
        return

    short_title, file_tag = shorten_method_signature(TARGET_METRIC)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Destination directory for histograms
    target_hist_dir = os.path.join(HISTOGRAMS_DIR, "jvector") if "jvector" in TARGET_CLASS.lower() else HISTOGRAMS_DIR
    os.makedirs(target_hist_dir, exist_ok=True)
    histogram_output = os.path.join(target_hist_dir, f"{file_tag}_{timestamp}.png")

    # Extract readings
    ext_readings, ext_occ = extract_readings(ext_dir, TARGET_METRIC, is_original=False, energy_column=METHOD_ENERGY_COLUMN)
    orig_readings, orig_occ = extract_readings(orig_dir, TARGET_METRIC, is_original=True, energy_column=METHOD_ENERGY_COLUMN)

    n_ext = len(ext_readings)
    n_orig = len(orig_readings)

    # Determine execution mode: Comparative (both available) vs. Standalone Extended
    is_comparative = (orig_dir is not None and n_orig > 0 and n_ext > 0)

    print("=" * 105)
    print(f"               STATISTICAL SUMMARY REPORT: {short_title}")
    print("=" * 105)
    print(f"Target Class:           {TARGET_CLASS}")
    print(f"Target Metric:          {TARGET_METRIC}")
    if TARGET_METRIC != "TOTAL_PROGRAM":
        print(f"Energy Column:          {METHOD_ENERGY_COLUMN}")
    print(f"Data Source (Extended): {ext_dir}")
    if orig_dir:
        print(f"Data Source (Original): {orig_dir}")
    print("-" * 105)

    if is_comparative:
        ext_mean = statistics.mean(ext_readings) if n_ext > 0 else 0.0
        orig_mean = statistics.mean(orig_readings) if n_orig > 0 else 0.0
        ext_var = statistics.variance(ext_readings) if n_ext > 1 else 0.0
        orig_var = statistics.variance(orig_readings) if n_orig > 1 else 0.0
        abs_diff = abs(ext_mean - orig_mean)
        diff_pct = (abs_diff / orig_mean) * 100 if orig_mean > 0 else 0.0

        print(f"{'Metric':<35} | {'Extended':<18} | {'Original':<18} | {'Abs Diff (J)':<15} | {'Diff (%)':<10}")
        print("-" * 105)
        print(f"{'Sample Mean (x̄)':<35} | {ext_mean:<18.6f} | {orig_mean:<18.6f} | {abs_diff:<15.6f} | {diff_pct:.2f}%")
        print(f"{'Sample Variance (s²)':<35} | {ext_var:<18.6f} | {orig_var:<18.6f} | {'-':<15} | {'-':<10}")
        print(f"{'Minimum Energy':<35} | {min(ext_readings):<18.6f} | {min(orig_readings):<18.6f} | {'-':<15} | {'-':<10}")
        print(f"{'Maximum Energy':<35} | {max(ext_readings):<18.6f} | {max(orig_readings):<18.6f} | {'-':<15} | {'-':<10}")
        print(f"{'Detected Runs':<35} | {ext_occ}/{n_ext:<15} | {orig_occ}/{n_orig:<15} | {'-':<15} | {'-':<10}")
        print("=" * 105)

        # Plot Comparative Histogram (2 Panels)
        fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
        metric_label = f"{short_title} [{METHOD_ENERGY_COLUMN}]" if TARGET_METRIC != "TOTAL_PROGRAM" else "Total Program Energy"
        fig.suptitle(f"Comparative Energy Profile — {metric_label}", fontsize=12, fontweight='bold', y=0.98)

        # Left: Original
        ax0 = axes[0]
        ax0.hist(orig_readings, bins=15, color='#E2844A', edgecolor='#B3541A', alpha=0.85, rwidth=0.9)
        ax0.set_title("Original JoularJX", fontsize=11, fontweight='bold')
        ax0.set_xlabel("Energy Consumed (Joules)")
        ax0.set_ylabel("Count (Runs)")
        orig_stats = f"Runs: {n_orig} (Present: {orig_occ})\nMean: {orig_mean:.4f} J\nVar: {orig_var:.6f} J²\nMax: {max(orig_readings):.4f} J"
        ax0.text(0.95, 0.95, orig_stats, transform=ax0.transAxes, fontsize=8.5,
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#D3D3D3'))
        ax0.text(0.05, 0.95, f"Sample Rate: {SAMPLE_PERIOD_MS} ms\nSub-sample Rate: {SUB_SAMPLE_RATE_MS} ms",
                 transform=ax0.transAxes, fontsize=8.5, verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#D3D3D3'))

        # Right: Extended
        ax1 = axes[1]
        ax1.hist(ext_readings, bins=15, color='#4A90E2', edgecolor='#1F4E79', alpha=0.85, rwidth=0.9)
        ax1.set_title("Extended JoularJX", fontsize=11, fontweight='bold')
        ax1.set_xlabel("Energy Consumed (Joules)")
        ax1.set_ylabel("Count (Runs)")
        ext_stats = f"Runs: {n_ext} (Present: {ext_occ})\nMean: {ext_mean:.4f} J\nVar: {ext_var:.6f} J²\nMax: {max(ext_readings):.4f} J"
        ax1.text(0.95, 0.95, ext_stats, transform=ax1.transAxes, fontsize=8.5,
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#D3D3D3'))
        ax1.text(0.05, 0.95, f"Sample Rate: {SAMPLE_PERIOD_MS} ms\nSub-sample Rate: {SUB_SAMPLE_RATE_MS} ms",
                 transform=ax1.transAxes, fontsize=8.5, verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#D3D3D3'))

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(histogram_output, dpi=300)
        plt.close()

    else:
        # Standalone Extended Analysis
        if n_ext == 0:
            print(f"Error: No valid readings extracted from {ext_dir}")
            return

        mean_val = statistics.mean(ext_readings)
        var_val = statistics.variance(ext_readings) if n_ext > 1 else 0.0
        min_val = min(ext_readings)
        max_val = max(ext_readings)

        print(f"{'Metric':<40} | {'Value':<25}")
        print("-" * 105)
        print(f"{'Sample Mean (x̄)':<40} | {mean_val:<25.6f} Joules")
        print(f"{'Sample Variance (s²)':<40} | {var_val:<25.6f} Joules²")
        print(f"{'Minimum Energy':<40} | {min_val:<25.6f} Joules")
        print(f"{'Maximum Energy':<40} | {max_val:<25.6f} Joules")
        print(f"{'Detected Runs':<40} | {ext_occ}/{n_ext:<25}")
        print("=" * 105)

        # Plot Standalone Histogram
        plt.figure(figsize=(8.5, 5.2))
        metric_label = f"{short_title} [{METHOD_ENERGY_COLUMN}]" if TARGET_METRIC != "TOTAL_PROGRAM" else "Total Program Energy"
        plt.title(f"Extended JoularJX — {metric_label}", fontsize=11, fontweight='bold')
        plt.xlabel("Energy Consumed (Joules)")
        plt.ylabel("Frequency (Runs)")

        span = max_val - min_val
        if span == 0:
            bins = 10
        else:
            x_min = max(0.0, min_val - 0.05 * span)
            x_max = max_val + 0.05 * span
            bins = np.linspace(x_min, x_max, 16)

        plt.hist(ext_readings, bins=bins, color='#4A90E2', edgecolor='#1F4E79', alpha=0.85, rwidth=0.9)

        rates_text = f"Sample Rate: {SAMPLE_PERIOD_MS} ms\nSub-sample Rate: {SUB_SAMPLE_RATE_MS} ms\nMetric: {METHOD_ENERGY_COLUMN if TARGET_METRIC != 'TOTAL_PROGRAM' else 'Total Program'}"
        plt.gca().text(0.05, 0.95, rates_text, transform=plt.gca().transAxes, fontsize=8.5,
                       verticalalignment='top', horizontalalignment='left',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#D3D3D3'))

        ext_stats = f"Runs: {n_ext} (Present: {ext_occ})\nMean: {mean_val:.4f} J\nVar: {var_val:.6f} J²\nMax: {max_val:.4f} J"
        plt.gca().text(0.95, 0.95, ext_stats, transform=plt.gca().transAxes, fontsize=8.5,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#D3D3D3'))

        plt.tight_layout()
        plt.savefig(histogram_output, dpi=300)
        plt.close()

    print(f"Histogram saved successfully to:\n  {histogram_output}")

    # Generate non-overwriting timestamped merged average CSV
    if ext_dir:
        class_sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", class_basename)
        merged_csv_path = os.path.join(MERGED_RESULTS_DIR, f"{class_sanitized}_merged_average_energy_{timestamp}.csv")
        generate_merged_average_csv(ext_dir, merged_csv_path, warmup_runs=WARMUP_RUNS, max_runs=NUM_RUNS)

if __name__ == "__main__":
    main()
