from __future__ import annotations

import csv
from pathlib import Path



def build_threshold_tradeoff_plot(summary_csv_path: str | Path, output_path: str | Path) -> Path:
    summary_path = Path(summary_csv_path)
    out = Path(output_path)

    thresholds: list[float] = []
    silence_rates: list[float] = []
    accepted_error_rates: list[float] = []
    accepted_precisions: list[float] = []

    with summary_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            thresholds.append(float(row["threshold"]))
            silence_rates.append(float(row["silence_rate"]))
            accepted_error_rates.append(float(row["accepted_error_rate"]))
            accepted_precisions.append(float(row["accepted_precision"]))

    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, silence_rates, marker="o", label="silence_rate")
    plt.plot(thresholds, accepted_error_rates, marker="o", label="accepted_error_rate")
    plt.plot(thresholds, accepted_precisions, marker="o", label="accepted_precision")
    plt.xlabel("PoR threshold")
    plt.ylabel("Rate")
    plt.title("SimpleQA PoR tradeoff: silence vs accepted error")
    plt.ylim(0.0, 1.0)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=200)
    plt.close()
    return out
