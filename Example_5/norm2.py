
"""
Generate correlated normal random pairs and plot as colormaps.

Marginals (fixed):
    - X ~ N(0, 1^2)
    - Y ~ N(0, 2^2)

Correlations: user-specified via --rho; supports special handling for ±1.

New: --grid will arrange multiple ρ values on a single canvas (2x2 by default).

Examples
--------
# Single pair (default ρ=0.5)
python norm2.py

# Separate PNGs for each ρ
python norm2.py --plot --n 10000 --rho 0.5 0 1 -1 --seed 42

# One canvas with 4 subplots (ρ = 0.5, 0, 1, -1)
python norm2.py --plot --grid --n 10000 --rho 0.5 0 1 -1 --seed 42

# Customize output filenames and bins
python norm2.py --plot --grid --outfile-prefix run --grid-outfile run_grid.png --bins 75
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import Sequence

def draw_samples(n: int, rho: float, rng: np.random.Generator) -> np.ndarray:
    """Draw n samples for correlation rho.
    For |rho| < 1: sample from bivariate normal with covariance:
        [[1, rho*1*2], [rho*1*2, 4]]
    For rho == ±1: use deterministic linear relation Y = rho*(2/1)*X.
    Returns array (n, 2) with columns [X, Y].
    """
    std1, std2 = 1.0, 2.0
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

def plot_colormap(samples: np.ndarray, rho: float, outfile: str, bins: int = 60, show: bool = False,
                    xy_range=((-
4.0, 4.0), (-8.0, 8.0)), vmax=None):
    x = samples[:, 0]
    y = samples[:, 1]
    corr_xy = float(np.corrcoef(x, y)[0, 1])

    fig, ax = plt.subplots(figsize=(6.4, 5.4), constrained_layout=True)
    h = ax.hist2d(x, y, bins=bins, range=xy_range, cmap='viridis', vmin=0, vmax=vmax)
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

def plot_grid_colormap(rhos: Sequence[float], n: int, seed: int | None, bins: int,
                        grid_outfile: str, xy_range=((-
4.0, 4.0), (-8.0, 8.0)), show: bool = False):
    """Create a single canvas with one subplot per rho (2x2 layout for 4 rhos).
    Uses a shared color scale across subplots.
    """
    rng = np.random.default_rng(seed)

    # Draw samples for each rho
    samples_list = []
    corr_list = []
    for rho in rhos:
        samples = draw_samples(n, rho=rho, rng=rng)
        samples_list.append(samples)
        corr_list.append(float(np.corrcoef(samples[:, 0], samples[:, 1])[0, 1]))

    # Determine a common vmax for consistent color scaling
    # Compute 2D hist counts with the chosen bins/range
    x_edges = np.linspace(xy_range[0][0], xy_range[0][1], bins + 1)
    y_edges = np.linspace(xy_range[1][0], xy_range[1][1], bins + 1)
    vmax = 0
    for samples in samples_list:
        H, _, _ = np.histogram2d(samples[:, 0], samples[:, 1], bins=[x_edges, y_edges])
        vmax = max(vmax, int(H.max()))
    if vmax == 0:
        vmax = None  # fallback

    # Create grid
    import math
    rows = math.ceil(len(rhos) / 2)
    cols = 2 if len(rhos) > 1 else 1
    fig, axs = plt.subplots(rows, cols, figsize=(6.4*cols, 5.2*rows), constrained_layout=True)
    axs = np.array(axs, ndmin=2)

    # Plot each subplot
    imgs = []
    for idx, (rho, samples) in enumerate(zip(rhos, samples_list)):
        r = idx // cols
        c = idx % cols
        ax = axs[r, c]
        x = samples[:, 0]
        y = samples[:, 1]
        corr_xy = corr_list[idx]
        h = ax.hist2d(x, y, bins=bins, range=xy_range, cmap='viridis', vmin=0, vmax=vmax)
        imgs.append(h[3])
        ax.set_xlabel('X ~ N(0, 1)')
        ax.set_ylabel('Y ~ N(0, 2)')
        ax.set_title(f'ρ={rho} — Empirical corr ≈ {corr_xy:.3f}')

    # Hide any unused axes
    for j in range(len(rhos), rows*cols):
        r = j // cols
        c = j % cols
        axs[r, c].axis('off')

    # Shared colorbar
    cbar = fig.colorbar(imgs[-1], ax=axs.ravel().tolist(), fraction=0.035, pad=0.01)
    cbar.set_label('Counts per bin')
    fig.suptitle(f'Bivariate Normal: X~N(0,1), Y~N(0,4); N={n}', fontsize=14)
    fig.savefig(grid_outfile, dpi=220)
    if show:
        plt.show()
    plt.close(fig)
    return grid_outfile

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
                        help='Prefix for output image filenames when saving separate plots.')
    parser.add_argument('--grid', action='store_true', help='If set, arrange all requested ρ values on one canvas.')
    parser.add_argument('--grid-outfile', type=str, default='norm2_grid.png',
                        help='Filename for the multi-plot canvas (default: norm2_grid.png).')
    args = parser.parse_args()

    if not args.plot:
        # Single draw at first rho
        rng = np.random.default_rng(args.seed)
        rho = args.rho[0]
        samples = draw_samples(1, rho=rho, rng=rng)
        x, y = samples[0]
        print(f"First number (mean=0, std=1): {x}")
        print(f"Second number (mean=0, std=2), corr={rho} with first: {y}")
        return

    if args.grid:
        # Grid canvas with all requested rhos
        rhos = args.rho
        grid_outfile = plot_grid_colormap(rhos=rhos, n=args.n, seed=args.seed, bins=args.bins,
                                            grid_outfile=args.grid_outfile, show=args.show)
        print(f"Saved grid canvas to: {grid_outfile}")
    else:
        # Separate images per rho
        rng = np.random.default_rng(args.seed)
        xy_range = ((-4.0, 4.0), (-8.0, 8.0))

        # Optionally compute a common vmax across all rhos for comparability
        # First, draw and store samples for all rhos
        samples_by_rho = {}
        for rho in args.rho:
            samples_by_rho[rho] = draw_samples(args.n, rho=rho, rng=rng)

        # Compute common vmax
        x_edges = np.linspace(xy_range[0][0], xy_range[0][1], args.bins + 1)
        y_edges = np.linspace(xy_range[1][0], xy_range[1][1], args.bins + 1)
        vmax = 0
        for samples in samples_by_rho.values():
            H, _, _ = np.histogram2d(samples[:, 0], samples[:, 1], bins=[x_edges, y_edges])
            vmax = max(vmax, int(H.max()))
        if vmax == 0:
            vmax = None

        for rho, samples in samples_by_rho.items():
            rho_tag = str(rho).replace('.', 'p').replace('-', 'neg')
            outfile = f"{args.outfile_prefix}_rho{rho_tag}.png"
            # Use the single-plot function with shared vmax
            _outfile, corr_xy = plot_colormap(samples, rho, outfile, bins=args.bins, show=args.show,
                                                xy_range=xy_range, vmax=vmax)
            print(f"Saved colormap for rho={rho} to: {_outfile}")
            print(f"Empirical correlation over N={args.n}: {corr_xy:.4f}")

if __name__ == '__main__':
    main()
