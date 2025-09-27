
"""
Generate correlated normal random pairs and plot as a colormap (2D histogram).

Targets (fixed):
    - X ~ N(0, 1^2)
    - Y ~ N(0, 2^2)
    - Corr(X, Y) = ρ (user-specified; supports multiple ρ values)

Examples:
    # Single pair (default ρ=0.5):
    python norm2.py

    # Plot 10,000 samples for ρ = 0, 1, -1 (saves three PNGs)
    python norm2.py --plot --n 10000 --rho 0 1 -1 --seed 42

    # Custom output prefix and bins
    python norm2.py --plot --rho 0.0 --outfile-prefix myrun --bins 75

    # Also show the plot window
    python norm2.py --plot --rho 0 1 -1 --show
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt

def draw_samples(n: int, rho: float, seed: int | None = None) -> np.ndarray:
    """Draw n samples for given correlation rho.
    For |rho| < 1: sample from bivariate normal with covariance:
        [[1, rho*1*2], [rho*1*2, 4]]
    For rho == ±1: use deterministic linear relation Y = rho*(2/1)*X.
    Returns array shape (n, 2) with columns [X, Y].
    """
    std1, std2 = 1.0, 2.0
    rng = np.random.default_rng(seed)
    if abs(rho) < 1:
        mean = np.array([0.0, 0.0])
        cov12 = rho * std1 * std2
        cov = np.array([[std1**2,  cov12],
                        [cov12,    std2**2]])
        samples = rng.multivariate_normal(mean=mean, cov=cov, size=n)
        return samples
    else:
        # Degenerate case: perfect (anti)correlation => line Y = rho*(std2/std1) * X
        x = rng.normal(loc=0.0, scale=std1, size=n)
        y = rho * (std2 / std1) * x
        return np.column_stack([x, y])

def plot_colormap(samples: np.ndarray, rho: float, outfile: str, bins: int = 60, show: bool = False):
    x = samples[:, 0]
    y = samples[:, 1]
    corr_xy = float(np.corrcoef(x, y)[0, 1])

    fig, ax = plt.subplots(figsize=(6.4, 5.4), constrained_layout=True)
    h = ax.hist2d(x, y, bins=bins, cmap='viridis')
    cbar = fig.colorbar(h[3], ax=ax)
    cbar.set_label('Counts per bin')
    ax.set_xlabel('X ~ N(0, 1)')
    ax.set_ylabel('Y ~ N(0, 2)')
    ax.set_title(f'Bivariate Normal Samples (ρ={rho}) — N={len(x)}
Empirical Corr ≈ {corr_xy:.3f}')
    fig.savefig(outfile, dpi=200)
    if show:
        plt.show()
    plt.close(fig)
    return outfile, corr_xy

def main():
    parser = argparse.ArgumentParser(description='Generate correlated normal pairs and optionally plot as a colormap.')
    parser.add_argument('--plot', action='store_true', help='If set, generate samples and save colormap PNG(s).')
    parser.add_argument('--n', type=int, default=10000, help='Number of pairs to generate when plotting (default: 10000).')
    parser.add_argument('--bins', type=int, default=60, help='Number of bins for 2D histogram (default: 60).')
    parser.add_argument('--seed', type=int, default=None, help='Optional RNG seed for reproducibility.')
    parser.add_argument('--show', action='store_true', help='Show the plot window in addition to saving.')
    parser.add_argument('--rho', type=float, nargs='+', default=[0.5],
                        help='Correlation value(s). Supports multiple (e.g., --rho 0 1 -1). Default: 0.5')
    parser.add_argument('--outfile-prefix', type=str, default='norm2_colormap',
                        help='Prefix for output image filenames (default: norm2_colormap).')
    args = parser.parse_args()

    # If not plotting, just print one sample at first rho
    if not args.plot:
        rho = args.rho[0]
        samples = draw_samples(1, rho=rho, seed=args.seed)
        x, y = samples[0]
        print(f"First number (mean=0, std=1): {x}")
        print(f"Second number (mean=0, std=2), corr={rho} with first: {y}")
        return

    # Plot for each requested rho
    for rho in args.rho:
        samples = draw_samples(args.n, rho=rho, seed=args.seed)
        # Safe filename stub for rho values like -1, 0.5, etc.
        rho_tag = str(rho).replace('.', 'p').replace('-', 'neg')
        outfile = f"{args.outfile_prefix}_rho{rho_tag}.png"
        outfile, corr_xy = plot_colormap(samples, rho, outfile, bins=args.bins, show=args.show)
        print(f"Saved colormap for rho={rho} to: {outfile}")
        print(f"Empirical correlation over N={args.n}: {corr_xy:.4f}")

if __name__ == '__main__':
    main()
