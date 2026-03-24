from pathlib import Path
import matplotlib.pyplot as plt

OUT_DIR = Path("reports")
OUT_DIR.mkdir(exist_ok=True)

# Data
labels = ["Baseline", "PoR 0.35", "PoR 0.43"]

coverage = [100.0, 53.5, 55.0]
accepted_precision = [54.8, 100.0, 98.36]
risk_capture = [0.0, 100.0, 98.01]  # baseline doesn't capture risk, so 0
silence_precision = [0.0, 93.76, 98.44]  # baseline has no silence

x = range(len(labels))

# Chart 1: Coverage / Accepted Precision / Risk Capture
plt.figure(figsize=(10, 6))
plt.plot(x, coverage, marker="o", linewidth=2, label="Coverage")
plt.plot(x, accepted_precision, marker="o", linewidth=2, label="Accepted Precision")
plt.plot(x, risk_capture, marker="o", linewidth=2, label="Risk Capture")

plt.xticks(list(x), labels)
plt.ylim(0, 105)
plt.ylabel("Percent")
plt.title("PoR Control Curve: Baseline vs Threshold 0.35 vs 0.43")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUT_DIR / "threshold_control_curve.png", dpi=200)
plt.close()

# Chart 2: Accepted failures
accepted_failures = [452, 0, 9]

plt.figure(figsize=(8, 5))
plt.bar(labels, accepted_failures)
plt.ylabel("Count")
plt.title("Accepted Failures: Baseline vs PoR")
plt.tight_layout()
plt.savefig(OUT_DIR / "accepted_failures_comparison.png", dpi=200)
plt.close()

# Chart 3: Drift separation
drift_success = [0.253, 0.253, 0.249]
drift_fail = [0.676, 0.676, 0.670]

plt.figure(figsize=(8, 5))
plt.plot(x, drift_success, marker="o", linewidth=2, label="Success Drift")
plt.plot(x, drift_fail, marker="o", linewidth=2, label="Fail Drift")

plt.xticks(list(x), labels)
plt.ylabel("Avg Drift")
plt.title("Drift Separation Across Modes")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUT_DIR / "drift_separation_comparison.png", dpi=200)
plt.close()

print("Saved:")
print("-", OUT_DIR / "threshold_control_curve.png")
print("-", OUT_DIR / "accepted_failures_comparison.png")
print("-", OUT_DIR / "drift_separation_comparison.png")