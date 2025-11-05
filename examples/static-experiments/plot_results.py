#!/usr/bin/env python3
"""
Script to aggregate and plot results from static experiment output files.
Parses output files, aggregates data to CSV, and creates throughput plots.
"""

import re
import csv
import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


def parse_output_file(filepath: str) -> List[Dict[str, float]]:
    """
    Parse an output file and extract processed counts, percentages, and batch times.

    Args:
        filepath: Path to the output file

    Returns:
        List of dictionaries with keys: 'processed', 'percentage', 'batch_time_ms'
    """
    data = []
    pattern = r"Processed: (\d+) \(([\d.]+)%\)\s+Batch time: (\d+) ms"

    try:
        with open(filepath, "r") as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    processed = int(match.group(1))
                    percentage = float(match.group(2))
                    batch_time_ms = int(match.group(3))

                    data.append({"processed": processed, "percentage": percentage, "batch_time_ms": batch_time_ms})
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return []

    return data


def calculate_throughput(data: List[Dict[str, float]]) -> List[Dict[str, float]]:
    """
    Calculate throughput for each data point.
    Throughput = tuples_in_batch / batch_time_ms * 1000 (tuples per second)

    Args:
        data: List of parsed data points

    Returns:
        List with added 'throughput' field
    """
    result = []
    prev_processed = None

    for point in data:
        if point["batch_time_ms"] > 0:  # Skip if batch time is 0
            if prev_processed is not None:
                tuples_in_batch = point["processed"] - prev_processed
                if tuples_in_batch > 0:
                    throughput = (tuples_in_batch / point["batch_time_ms"]) * 1000  # tuples per second
                    point["throughput"] = throughput
                    result.append(point)
            # Update prev_processed even if we skipped this point
            prev_processed = point["processed"]
        else:
            # If batch time is 0, update prev_processed but don't add to result
            prev_processed = point["processed"]

    return result


def extract_file_info(filename: str, experiment_name: str, method: str) -> Optional[Tuple[str, str, str]]:
    """
    Extract query, vo, and dataset_version from filename.

    Expected format: {experiment_name}-{query}-{method}-{dataset_version}_BATCH_1000.txt
    Example: static-tpch_query03_vo1-FIVM-jcch_unordered10_BATCH_1000.txt

    Args:
        filename: Name of the file
        experiment_name: Name of the experiment (e.g., 'static')
        method: Method name (e.g., 'FIVM')

    Returns:
        Tuple of (query_base, vo, dataset_version) or None if parsing fails
    """
    # Remove extension
    basename = filename.replace(".txt", "")

    # Pattern: {experiment_name}-{query}-{method}-{dataset_version}_BATCH_1000
    pattern = rf"{re.escape(experiment_name)}-(.+?)-{re.escape(method)}-(.+?)_BATCH_1000"
    match = re.match(pattern, basename)

    if match:
        query_full = match.group(1)  # e.g., 'tpch_query03_vo1'
        dataset_version = match.group(2)  # e.g., 'jcch_unordered10'

        # Extract VO from query name (assuming format like 'tpch_query03_vo1')
        vo_match = re.search(r"vo(\d+)", query_full)
        if vo_match:
            vo = f"vo{vo_match.group(1)}"
            query_base = query_full.rsplit("_vo", 1)[0]  # e.g., 'tpch_query03'
            return (query_base, vo, dataset_version)

    return None


def aggregate_to_csv(output_dir: str, csv_output: str, experiment_name: str = "static", method: str = "FIVM"):
    """
    Aggregate all output files to a single CSV file.

    Args:
        output_dir: Directory containing output files
        csv_output: Path to output CSV file
        experiment_name: Name of the experiment
        method: Method name
    """
    all_data = []

    # Find all output files
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"Error: Output directory does not exist: {output_dir}")
        return

    for filename in sorted(output_path.glob("*.txt")):
        file_info = extract_file_info(filename.name, experiment_name, method)
        if file_info is None:
            print(f"Warning: Could not parse filename: {filename.name}")
            continue

        query_base, vo, dataset_version = file_info

        # Parse the file
        parsed_data = parse_output_file(str(filename))
        if not parsed_data:
            print(f"Warning: No data found in {filename.name}")
            continue

        # Calculate throughput
        data_with_throughput = calculate_throughput(parsed_data)

        # Add metadata
        for point in data_with_throughput:
            all_data.append(
                {
                    "query": query_base,
                    "vo": vo,
                    "dataset_version": dataset_version,
                    "percentage": point["percentage"],
                    "throughput": point["throughput"],
                }
            )

    # Write to CSV
    if all_data:
        with open(csv_output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["query", "vo", "dataset_version", "percentage", "throughput"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"CSV file created: {csv_output} ({len(all_data)} rows)")
    else:
        print("Error: No data to write to CSV")


def create_plots(csv_file: str, output_dir: str, query_base: str):
    """
    Create throughput plots for each dataset_version comparing vo1 and vo2.
    Creates both individual plots and a combined plot with tpch in one column and jcch in another.

    Args:
        csv_file: Path to CSV file with aggregated data
        output_dir: Directory to save plot files
        query_base: Base query name (e.g., 'tpch_query03')
    """
    # Read CSV data
    data_by_dataset = defaultdict(lambda: {"vo1": [], "vo2": []})

    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["query"] == query_base:
                dataset_version = row["dataset_version"]
                vo = row["vo"]
                percentage = float(row["percentage"])
                throughput = float(row["throughput"])

                if vo in ["vo1", "vo2"]:
                    data_by_dataset[dataset_version][vo].append({"percentage": percentage, "throughput": throughput})

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Sort data by percentage for each dataset
    for dataset_version, data in data_by_dataset.items():
        for vo in ["vo1", "vo2"]:
            data[vo].sort(key=lambda x: x["percentage"])

    # Create individual plots
    for dataset_version, data in data_by_dataset.items():
        if not data["vo1"] and not data["vo2"]:
            print(f"Warning: No data for {dataset_version}")
            continue

        # Create individual plot
        plt.figure(figsize=(10, 6))

        if data["vo1"]:
            vo1_percentages = [p["percentage"] for p in data["vo1"]]
            vo1_throughputs = [p["throughput"] for p in data["vo1"]]
            plt.plot(vo1_percentages, vo1_throughputs, marker="o", label="vo1", linewidth=2, markersize=4)

        if data["vo2"]:
            vo2_percentages = [p["percentage"] for p in data["vo2"]]
            vo2_throughputs = [p["throughput"] for p in data["vo2"]]
            plt.plot(vo2_percentages, vo2_throughputs, marker="s", label="vo2", linewidth=2, markersize=4)

        plt.xlabel("Percentage of Tuples Processed (%)", fontsize=14)
        plt.ylabel("Throughput (tuples/second)", fontsize=14)
        plt.title(f"{query_base} - {dataset_version}", fontsize=16)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)

        # Format y-axis with scientific notation (e.g., 1E7, 2E7)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.1e}" if x >= 1e6 else f"{x:.1e}"))
        ax.tick_params(axis="y", labelsize=12)

        plt.tight_layout()

        # Save individual plot
        plot_filename = output_path / f"{query_base}_{dataset_version}_throughput.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches="tight")
        print(f"Plot saved: {plot_filename}")
        plt.close()

    # Create combined plot with tpch in one column and jcch in another
    tpch_datasets = sorted([d for d in data_by_dataset.keys() if d.startswith("tpch")])
    jcch_datasets = sorted([d for d in data_by_dataset.keys() if d.startswith("jcch")])

    max_rows = max(len(tpch_datasets), len(jcch_datasets))

    if max_rows > 0:
        fig, axes = plt.subplots(max_rows, 2, figsize=(16, 5 * max_rows))

        # Handle case where there's only one row
        if max_rows == 1:
            axes = axes.reshape(1, -1)

        # First, calculate y-axis ranges for each row
        y_ranges = []
        for i in range(max_rows):
            tpch_dataset = tpch_datasets[i] if i < len(tpch_datasets) else None
            jcch_dataset = jcch_datasets[i] if i < len(jcch_datasets) else None

            all_throughputs = []

            if tpch_dataset:
                data = data_by_dataset[tpch_dataset]
                if data["vo1"]:
                    all_throughputs.extend([p["throughput"] for p in data["vo1"]])
                if data["vo2"]:
                    all_throughputs.extend([p["throughput"] for p in data["vo2"]])

            if jcch_dataset:
                data = data_by_dataset[jcch_dataset]
                if data["vo1"]:
                    all_throughputs.extend([p["throughput"] for p in data["vo1"]])
                if data["vo2"]:
                    all_throughputs.extend([p["throughput"] for p in data["vo2"]])

            if all_throughputs:
                y_min = min(all_throughputs)
                y_max = max(all_throughputs)
                # Add 5% padding
                y_range = y_max - y_min
                y_min = max(0, y_min - 0.05 * y_range)
                y_max = y_max + 0.05 * y_range
                y_ranges.append((y_min, y_max))
            else:
                y_ranges.append((0, 1))

        # Plot tpch datasets in left column
        for i, dataset_version in enumerate(tpch_datasets):
            data = data_by_dataset[dataset_version]
            ax = axes[i, 0] if max_rows > 1 else axes[0]

            if data["vo1"]:
                vo1_percentages = [p["percentage"] for p in data["vo1"]]
                vo1_throughputs = [p["throughput"] for p in data["vo1"]]
                ax.plot(vo1_percentages, vo1_throughputs, marker="o", label="vo1", linewidth=2, markersize=3)

            if data["vo2"]:
                vo2_percentages = [p["percentage"] for p in data["vo2"]]
                vo2_throughputs = [p["throughput"] for p in data["vo2"]]
                ax.plot(vo2_percentages, vo2_throughputs, marker="s", label="vo2", linewidth=2, markersize=3)

            ax.set_xlabel("Percentage of Tuples Processed (%)", fontsize=12)
            ax.set_ylabel("Throughput (tuples/second)", fontsize=12)
            ax.set_title(f"{dataset_version}", fontsize=14)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.1e}" if x >= 1e6 else f"{x:.1e}"))
            ax.tick_params(axis="y", labelsize=10)
            # Set y-axis range to match the row
            if i < len(y_ranges):
                ax.set_ylim(y_ranges[i])

        # Hide empty subplots in left column
        for i in range(len(tpch_datasets), max_rows):
            axes[i, 0].axis("off")

        # Plot jcch datasets in right column
        for i, dataset_version in enumerate(jcch_datasets):
            data = data_by_dataset[dataset_version]
            ax = axes[i, 1] if max_rows > 1 else axes[1]

            if data["vo1"]:
                vo1_percentages = [p["percentage"] for p in data["vo1"]]
                vo1_throughputs = [p["throughput"] for p in data["vo1"]]
                ax.plot(vo1_percentages, vo1_throughputs, marker="o", label="vo1", linewidth=2, markersize=3)

            if data["vo2"]:
                vo2_percentages = [p["percentage"] for p in data["vo2"]]
                vo2_throughputs = [p["throughput"] for p in data["vo2"]]
                ax.plot(vo2_percentages, vo2_throughputs, marker="s", label="vo2", linewidth=2, markersize=3)

            ax.set_xlabel("Percentage of Tuples Processed (%)", fontsize=12)
            ax.set_ylabel("Throughput (tuples/second)", fontsize=12)
            ax.set_title(f"{dataset_version}", fontsize=14)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.1e}" if x >= 1e6 else f"{x:.1e}"))
            ax.tick_params(axis="y", labelsize=10)
            # Set y-axis range to match the row
            if i < len(y_ranges):
                ax.set_ylim(y_ranges[i])

        # Hide empty subplots in right column
        for i in range(len(jcch_datasets), max_rows):
            axes[i, 1].axis("off")

        # Add column labels
        fig.text(0.25, 0.98, "TPCH", ha="center", fontsize=16, fontweight="bold")
        fig.text(0.75, 0.98, "JCCH", ha="center", fontsize=16, fontweight="bold")

        plt.suptitle(f"{query_base} - Throughput Comparison", fontsize=18, fontweight="bold", y=0.995)
        plt.tight_layout(rect=[0, 0, 1, 0.98])

        # Save combined plot
        combined_filename = output_path / f"{query_base}_combined_throughput.png"
        plt.savefig(combined_filename, dpi=300, bbox_inches="tight")
        print(f"Combined plot saved: {combined_filename}")
        plt.close()


def main():
    """Main function to run the script."""
    import argparse

    parser = argparse.ArgumentParser(description="Aggregate and plot experiment results")
    parser.add_argument("--experiment", default="static", help="Experiment name (default: static)")
    parser.add_argument("--method", default="FIVM", help="Method name (default: FIVM)")
    parser.add_argument("--query", required=True, help="Base query name (e.g., tpch_query03)")
    parser.add_argument("--input-dir", required=True, help="Directory containing output files")
    parser.add_argument("--output-dir", default="plots", help="Directory to save plots (default: plots)")
    parser.add_argument("--csv", help="CSV output file (default: {query}_results.csv)")

    args = parser.parse_args()

    # Set default CSV filename if not provided
    if args.csv is None:
        args.csv = f"{args.query}_results.csv"

    # Aggregate to CSV
    print(f"Aggregating data from {args.input_dir}...")
    aggregate_to_csv(args.input_dir, args.csv, args.experiment, args.method)

    # Create plots
    print(f"Creating plots for {args.query}...")
    create_plots(args.csv, args.output_dir, args.query)

    print("Done!")


if __name__ == "__main__":
    main()
