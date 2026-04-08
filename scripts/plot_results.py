import matplotlib.pyplot as plt

labels = ["Success", "Failure"]
values = [0.238, 0.529]

plt.figure(figsize=(6,4))
bars = plt.bar(labels, values)

plt.title("Drift Separation (PoR Control)")
plt.ylabel("Average Drift")

# підпис значень
for bar in bars:
    y = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, y, f"{y:.3f}",
             ha='center', va='bottom')

plt.tight_layout()
plt.savefig("reports/drift_clean.png")