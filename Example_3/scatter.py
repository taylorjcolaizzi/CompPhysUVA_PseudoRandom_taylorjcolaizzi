import numpy as np
import matplotlib.pyplot as plt

# Reproducibility
np.random.seed(42)

# Generate N pairs of Uniform(0,1)
N = 8000
x = np.random.uniform(0, 1, N)
y = np.random.uniform(0, 1, N)

# Plot
plt.figure(figsize=(6, 6), dpi=160)
plt.scatter(x, y, s=6, c="#2979ff", alpha=0.55, edgecolors="none")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.gca().set_aspect("equal", adjustable="box")
plt.title("Uniform(0, 1) Random Pairs")
plt.xlabel("Uniform X")
plt.ylabel("Uniform Y")
plt.grid(True, color="#d0d0d0", linestyle="-", linewidth=0.6, alpha=0.5)
plt.tight_layout()
plt.show()
