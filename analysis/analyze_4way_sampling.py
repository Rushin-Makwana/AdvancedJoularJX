import os
import re
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
from datetime import datetime

TARGET_CLASS = "OverallEnergyValidationSampling"

# Explicit target metric with parameter signature
TARGET_METRIC = "org.noureddine.joularjx.PrimeUtils.isPrime(int)"
TARGET_ENERGY_TYPE = "Self Energy"  # "Self Energy" or "Total Energy"

configs = [
    {
        "label": "Original\n(1000ms)",
        "dir": os.path.join("raw_data", "joularjx", TARGET_CLASS),
        "color": "#e07a5f",
        "sample_rate": "1000 ms",
        "sub_sample": "10 ms",
        "is_original": True
    },
    {
        "label": "Extended Config 1\n(1000ms / 10ms)",
        "dir": os.path.join("raw_data", "joularjx-3.1.0_1000_10", TARGET_CLASS),
        "color": "#3d85c6",
        "sample_rate": "1000 ms",
        "sub_sample": "10 ms",
        "is_original": False
    },
    {
        "label": "Extended Config 2\n(10000ms / 5000ms)",
        "dir": os.path.join("raw_data", "joularjx-3.1.0_10000_5000", TARGET_CLASS),
        "color": "#6aa84f",
        "sample_rate": "10000 ms",
        "sub_sample": "5000 ms",
        "is_original": False
    },
    {
        "label": "Extended Config 3\n(1000ms / 500ms)",
        "dir": os.path.join("raw_data", "joularjx-3.1.0_1000_500", TARGET_CLASS),
        "color": "#e69138",
        "sample_rate": "1000 ms",
        "sub_sample": "500 ms",
        "is_original": False
    }
]

def get_method_energy_from_csv(csv_path, target_metric, strip_parameters=False, energy_type="Self Energy"):
    """
    Extracts energy for a method from a run CSV.
    Matches exact method name (including signature) when strip_parameters is False.
    If strip_parameters is True, strips parentheses and arguments to match unparameterized entries (Original JoularJX).
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
                        col_idx = 2 if energy_type == "Total Energy" else 1
                        return float(parts[col_idx].strip())
                elif len(parts) == 2:
                    row_method = parts[0].strip()
                    if strip_parameters and "(" in row_method:
                        row_method = row_method.split("(")[0].strip()
                    if target == row_method:
                        return float(parts[1].strip())
        return None
    except Exception as e:
        return None

def extract_metric_readings(data_dir, target_metric, is_original=False, energy_type="Self Energy"):
    readings = []
    if not os.path.exists(data_dir):
        return readings

    if target_metric == "TOTAL_PROGRAM":
        consolidated_csv = os.path.join(data_dir, "total_energies.csv")
        if os.path.exists(consolidated_csv):
            with open(consolidated_csv, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    run_num = int(row["run_num"])
                    if 3 <= run_num <= 42:
                        readings.append(float(row["total_energy"]))
        return readings

    # Process run_3.csv to run_42.csv (ignoring run_1, run_2 warmups)
    strip_parameters = is_original
    for i in range(3, 43):
        filepath = os.path.join(data_dir, f"run_{i}.csv")
        val = get_method_energy_from_csv(filepath, target_metric, strip_parameters=strip_parameters, energy_type=energy_type)
        if val is not None:
            readings.append(val)
        else:
            readings.append(0.0)
    return readings

def main():
    print("=================================================================================================================")
    print("                    4-WAY SAMPLING EXPERIMENTAL ANALYSIS & METRIC COMPARISON")
    print(f"Target Metric Analyzed: {TARGET_METRIC} ({TARGET_ENERGY_TYPE})")
    print("=================================================================================================================")
    
    summary_data = []
    all_readings = {}
    
    for cfg in configs:
        readings = extract_metric_readings(
            cfg["dir"],
            TARGET_METRIC,
            is_original=cfg.get("is_original", False),
            energy_type=TARGET_ENERGY_TYPE
        )
        all_readings[cfg["label"]] = readings
        
        n = len(readings)
        mean_val = statistics.mean(readings) if n > 0 else 0.0
        var_val = statistics.variance(readings) if n > 1 else 0.0
        min_val = min(readings) if n > 0 else 0.0
        max_val = max(readings) if n > 0 else 0.0
        
        summary_data.append({
            "Configuration": cfg["label"].replace("\n", " "),
            "Runs": n,
            "Sample Rate": cfg["sample_rate"],
            "Sub-sample Rate": cfg["sub_sample"],
            "Mean (J)": round(mean_val, 4),
            "Variance (J²)": round(var_val, 4),
            "Min (J)": round(min_val, 4),
            "Max (J)": round(max_val, 4)
        })
    
    df_summary = pd.DataFrame(summary_data)
    print(df_summary.to_string(index=False))
    print("=================================================================================================================\n")
    
    # Generate 4-panel histogram figure with independent visible x-axis labels on all subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    
    metric_display = f"{TARGET_METRIC} [{TARGET_ENERGY_TYPE}]" if TARGET_METRIC != "TOTAL_PROGRAM" else "Total Program Energy"
    fig.suptitle(f"4-Way Sampling Comparison — Target Metric: {metric_display}", fontsize=13, fontweight='bold', y=0.98)
    
    flat_readings = [v for r_list in all_readings.values() for v in r_list]
    if flat_readings:
        x_min = max(0, min(flat_readings) - 5)
        x_max = max(flat_readings) + 5
    else:
        x_min, x_max = 0, 100

    for idx, cfg in enumerate(configs):
        ax = axes[idx]
        readings = all_readings[cfg["label"]]
        
        if readings:
            mean_v = statistics.mean(readings)
            var_v = statistics.variance(readings)
            n_v = len(readings)
            c_min = max(0, min(readings) - 5)
            c_max = max(readings) + 5
            bins = np.linspace(c_min, c_max, 15)
        else:
            mean_v, var_v, n_v = 0.0, 0.0, 0
            bins = 15
            
        ax.hist(readings, bins=bins, color=cfg["color"], edgecolor='black', alpha=0.85, rwidth=0.9)
        ax.set_title(cfg["label"].replace("\n", " "), fontsize=12, fontweight='bold')
        ax.set_xlabel("Energy Consumed (Joules)", fontsize=10)
        ax.set_ylabel("Count (Runs)", fontsize=10)
        ax.tick_params(labelbottom=True)  # Force bottom tick labels to be visible on all subplots
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        # Left Box (Sample Rates & Target Metric)
        cfg_metric_name = "Original JoularJX Energy" if cfg.get("is_original") else f"Extended {TARGET_ENERGY_TYPE}"
        ax.text(
            0.05, 0.93,
            f"Sample Rate: {cfg['sample_rate']}\nSub-sample Rate: {cfg['sub_sample']}\nMetric: {cfg_metric_name}",
            transform=ax.transAxes,
            fontsize=8.5,
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='lightgrey')
        )
        
        # Right Box (Stats)
        ax.text(
            0.95, 0.93,
            f"Runs: {n_v}\nMean: {mean_v:.3f} J\nVar: {var_v:.3f} J²",
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='lightgrey')
        )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    hist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "histograms")
    os.makedirs(hist_dir, exist_ok=True)
    from datetime import datetime
    import csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_img = os.path.join(hist_dir, f"sampling_4way_comparison_{timestamp}.png")
    plt.savefig(out_img, dpi=300)
    print(f"4-Way Sampling Comparison Histogram saved successfully to: {out_img}")

    # Generate timestamped, non-overwriting merged average CSVs for each config
    merged_results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "merged_results")
    os.makedirs(merged_results_dir, exist_ok=True)
    print("\n--- Generating Non-Overwriting Merged Average CSVs for all configurations ---")
    for cfg in configs:
        cfg_clean_tag = re.sub(r"[^a-zA-Z0-9_]", "_", cfg["label"])
        cfg_clean_tag = re.sub(r"_+", "_", cfg_clean_tag).strip("_")
        csv_filename = f"{TARGET_CLASS}_{cfg_clean_tag}_merged_average_energy_{timestamp}.csv"
        csv_path = os.path.join(merged_results_dir, csv_filename)
        generate_merged_average_csv(cfg["dir"], csv_path, warmup_runs=2, max_runs=40)

def generate_merged_average_csv(data_dir, output_csv_path, warmup_runs=2, max_runs=40):
    import csv
    if not os.path.exists(data_dir):
        print(f"Notice: Data directory not found: {data_dir}")
        return None
    files = [f"run_{i}.csv" for i in range(warmup_runs + 1, warmup_runs + max_runs + 1)]
    valid_files = [os.path.join(data_dir, f) for f in files if os.path.exists(os.path.join(data_dir, f))]
    num_runs = len(valid_files)
    if num_runs == 0:
        print(f"Notice: No valid run CSVs found in {data_dir}")
        return None

    method_data = {}
    for filepath in valid_files:
        with open(filepath, 'r', encoding='utf-8') as f:
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
            "Average Self Energy (Joules)": d["self_sum"] / num_runs,
            "Average Total Energy (Joules)": d["total_sum"] / num_runs,
            "Runs Present": d["occurrences"],
            "Total Measured Runs": num_runs
        })
    records.sort(key=lambda x: x["Average Total Energy (Joules)"], reverse=True)

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Method Name", "Average Self Energy (Joules)", "Average Total Energy (Joules)", "Runs Present", "Total Measured Runs"])
        writer.writeheader()
        for r in records:
            writer.writerow({
                "Method Name": r["Method Name"],
                "Average Self Energy (Joules)": f"{r['Average Self Energy (Joules)']:.8e}",
                "Average Total Energy (Joules)": f"{r['Average Total Energy (Joules)']:.8e}",
                "Runs Present": r["Runs Present"],
                "Total Measured Runs": r["Total Measured Runs"]
            })
    print(f"Saved merged average CSV -> {output_csv_path} ({len(records)} methods)")
    return output_csv_path

if __name__ == "__main__":
    import re
    main()
