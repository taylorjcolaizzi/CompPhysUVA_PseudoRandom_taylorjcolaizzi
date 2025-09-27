
"""
Generate 10,000 (configurable) correlated normal random pairs and plot a colormap.

Targets:
- X ~ N(0, 1^2)
- Y ~ N(0, 2^2)
- Corr(X, Y) = 0.5

Usage examples:
python norm2.py                      # generates one pair and prints it
python norm2.py --n 10000 --plot     # generates N pairs and saves a heatmap PNG
python norm2.py --n 10000 --plot --show  # also shows the plot window
python norm2.py --n 10000 --plot --outfile my_heatmap.png --seed 42
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt

def draw_samples(n: int, seed: int | None = None):
rng = np.random.default_rng(seed)
mean = np.array([0.0, 0.0])
std1, std2 = 1.0, 2.0
rho = 0.5
cov12 = rho * std1 * std2
cov = np.array([[std1**2,  cov12],
                [cov12,    std2**2]])
samples = rng.multivariate_normal(mean=mean, cov=cov, size=n)
return samples

def plot_colormap(samples: np.ndarray, outfile: str, bins: int = 60, show: bool = False):
x = samples[:, 0]
y = samples[:, 1]
corr_xy = float(np.corrcoef(x, y)[0, 1])

fig, ax = plt.subplots(figsize=(6.4, 5.4), constrained_layout=True)
h = ax.hist2d(x, y, bins=bins, cmap='viridis')
cbar = fig.colorbar(h[3], ax=ax)
cbar.set_label('Counts per bin')
ax.set_xlabel('X ~ N(0, 1)')
ax.set_ylabel('Y ~ N(0, 2)')
ax.set_title(f'Bivariate Normal Samples (ρ=0.5) — N={len(x)}
Empirical Corr ≈ {corr_xy:.3f}')
fig.savefig(outfile, dpi=200)
if show:
    plt.show()
plt.close(fig)
return outfile, corr_xy

def main():
parser = argparse.ArgumentParser(description='Generate correlated normal pairs and optionally plot as a colormap.')
parser.add_argument('--n', type=int, default=None, help='Number of pairs to generate for plotting (default: None).')
parser.add_argument('--plot', action='store_true', help='If set, generate N samples and save a colormap PNG.')
parser.add_argument('--bins', type=int, default=60, help='Number of bins for 2D histogram (default: 60).')
parser.add_argument('--outfile', type=str, default='norm2_colormap.png', help='Output image filename.')
parser.add_argument('--seed', type=int, default=None, help='Optional RNG seed for reproducibility.')
parser.add_argument('--show', action='store_true', help='Show the plot window in addition to saving.')
args = parser.parse_args()

# If not plotting, produce a single pair for quick usage
if not args.plot:
    samples = draw_samples(1, seed=args.seed)
    x, y = samples[0]
    print(f"First number (mean=0, std=1): {x}")
    print(f"Second number (mean=0, std=2), corr=0.5 with first: {y}")
    return

# Plotting path: require N
n = args.n if args.n is not None else 10000
samples = draw_samples(n, seed=args.seed)
outfile, corr_xy = plot_colormap(samples, args.outfile, bins=args.bins, show=args.show)
print(f"Saved colormap to: {outfile}")
print(f"Empirical correlation over N={n}: {corr_xy:.4f}")

if __name__ == '__main__':
main()
