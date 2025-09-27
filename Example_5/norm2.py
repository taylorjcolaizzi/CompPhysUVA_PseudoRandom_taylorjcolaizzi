"""
Generate correlated normal random pairs and plot as colormaps with improved visual contrast.

Marginals (fixed):
  - X ~ N(0, 1^2)
  - Y ~ N(0, 2^2)

Correlations: user-specified via --rho; special handling for ±1 if desired.

New contrast options:
  --cmap <name>          Perceptual colormap (default: magma)
  --norm <mode>          Color normalization: linear | log | gamma (default: log)
  --gamma <val>          Gamma for --norm gamma (default: 0.5)
  --contours             Overlay white contour lines (on by default; use --no-contours to disable)
  --scatter-perfect      For ρ in {+1, -1}, use scatter instead of hist2d (on by default; use --no-scatter-perfect to disable)

Grid mode: --grid arranges all requested ρ values on one canvas with a shared color scale
for the hist2d panels.

Examples
--------
# One canvas, 4 panels with better contrast
python norm2.py --plot --grid --rho 0.5 0 1 -1 --n 10000 --seed 42 --cmap magma --norm log --contours

# Separate images per rho with gamma normalization
python norm2.py --plot --rho 0.5 0 1 -1 --gamma 0.6 --norm gamma --bins 80
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Sequence, Tuple

# --------------------- Sampling ---------------------
def draw_samples(n: int, rho: float, rng: np.random.Generator) -> np.ndarray:
    """Draw n samples for correlation rho.
    For |rho| < 1: sample from bivariate normal with covariance:
      [[1, 2*rho], [2*rho, 4]]
    For rho == ±1: use deterministic linear relation Y = rho*(2/1)*X.
    Returns array (n, 2) with columns [X, Y].
    """
    std1, std2 = 1.0, 2.0
    if abs(rho) < 1:
        mean = np.array([0.0, 0.0])
        cov12 = rho * std1 * std2  # = 2*rho
        cov = np.array([[std1**2,  cov12],
                        [cov12,    std2**2]])
        samples = rng.multivariate_normal(mean=mean, cov=cov, size=n)
        return samples
    else:
        # Degenerate case: perfect (anti)correlation => line Y = rho*(std2/std1) * X
        x = rng.normal(loc=0.0, scale=std1, size=n)
        y = rho * (std2 / std1) * x
        return np.column_stack([x, y])

# --------------------- Helpers ---------------------
def build_norm(mode: str, vmax: float | None, gamma: float) -> mcolors.Normalize | None:
    if mode == 'linear' or vmax is None:
        return None
    if mode == 'log':
        # Avoid log(0): set vmin=1 count
        return mcolors.LogNorm(vmin=1, vmax=max(vmax, 1))
    if mode == 'gamma':
        # Power-law normalization (emphasizes low counts for gamma<1)
        return mcolors.PowerNorm(gamma=gamma, vmin=0, vmax=vmax)
    # Fallback
    return None


def compute_hist_stats(samples: np.ndarray, bins: int, xy_range: Tuple[Tuple[float, float], Tuple[float, float]]):
    x = samples[:, 0]
    y = samples[:, 1]
    H, xedges, yedges = np.histogram2d(x, y, bins=bins, range=xy_range)
    return H, xedges, yedges


def default_xy_range():
    return ((-4.0, 4.0), (-8.0, 8.0))

# --------------------- Plot: Single ---------------------
def plot_colormap(samples: np.ndarray, rho: float, outfile: str, *, bins: int = 60,
                  show: bool = False, xy_range=default_xy_range(), vmax=None, cmap='magma',
                  norm_mode='log', gamma=0.5, contours=True, scatter_perfect=True):
    x = samples[:, 0]
    y = samples[:, 1]
    corr_xy = float(np.corrcoef(x, y)[0, 1])

    fig, ax = plt.subplots(figsize=(6.8, 5.6), constrained_layout=True)

    # Perfect correlation panels can be more legible with scatter
    if scatter_perfect and abs(rho) == 1:
        ax.scatter(x, y, s=6, alpha=0.6, c='deepskyblue', edgecolors='none')
        # Still show a faint 2D histogram for context (optional):
        H, xedges, yedges = compute_hist_stats(samples, bins, xy_range)
        vmax_local = int(H.max())
        norm = build_norm(norm_mode, vmax_local if vmax is None else vmax, gamma)
        ax.hist2d(x, y, bins=bins, range=xy_range, cmap=cmap, weights=None,
                  cmin=1 if isinstance(norm, mcolors.LogNorm) else 0, norm=norm, alpha=0.35)
    else:
        H, xedges, yedges = compute_hist_stats(samples, bins, xy_range)
        vmax_local = int(H.max())
        norm = build_norm(norm_mode, vmax if vmax is not None else vmax_local, gamma)
        h = ax.hist2d(x, y, bins=bins, range=xy_range, cmap=cmap,
                      cmin=1 if isinstance(norm, mcolors.LogNorm) else 0,
                      norm=norm)

    # Optional contours help the eye
    if contours:
        # Use a few percentile-based levels for adaptability
        positive = H[H > 0]
        if positive.size >= 5:
            levels = np.quantile(positive, [0.2, 0.4, 0.6, 0.8, 0.92])
            ax.contour(0.5*(xedges[:-1] + xedges[1:]),
                       0.5*(yedges[:-1] + yedges[1:]),
                       H.T, levels=levels, colors='white', linewidths=0.8, alpha=0.85)

    ax.set_xlabel('X ~ N(0, 1)')
    ax.set_ylabel('Y ~ N(0, 2)')
    ax.set_title(f'Bivariate Normal Samples (ρ={rho}) — N={len(x)}\\nEmpirical Corr ≈ {corr_xy:.3f}')

    # Colorbar: only if we drew hist2d — reconstruct from last mappable
    im = None
    for artist in ax.get_children():
        if hasattr(artist, 'get_array') and hasattr(artist, 'get_cmap'):
            im = artist
    if im is not None:
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Counts per bin (normalized by color scale)')

    fig.savefig(outfile, dpi=240)
    if show:
        plt.show()
    plt.close(fig)
    return outfile, corr_xy

# --------------------- Plot: Grid ---------------------
def plot_grid_colormap(rhos: Sequence[float], n: int, seed: int | None, *, bins: int,
                       grid_outfile: str, xy_range=default_xy_range(), show: bool = False,
                       cmap='magma', norm_mode='log', gamma=0.5, contours=True, scatter_perfect=True):
    """Create a single canvas with one subplot per rho (2x2 layout for 4 rhos).
    Uses a shared color scale across hist2d subplots.
    """
    rng = np.random.default_rng(seed)

    # Draw samples for each rho
    samples_list = []
    corr_list = []
    for rho in rhos:
        samples = draw_samples(n, rho=rho, rng=rng)
        samples_list.append(samples)
        corr_list.append(float(np.corrcoef(samples[:, 0], samples[:, 1])[0, 1]))

    # Determine a common vmax for consistent color scaling across hist2d panels
    vmax = 0
    for samples in samples_list:
        H, _, _ = compute_hist_stats(samples, bins, xy_range)
        vmax = max(vmax, int(H.max()))
    if vmax == 0:
        vmax = None

    # Layout
    import math
    rows = math.ceil(len(rhos) / 2)
    cols = 2 if len(rhos) > 1 else 1
    fig, axs = plt.subplots(rows, cols, figsize=(6.8*cols, 5.6*rows), constrained_layout=True)
    axs = np.array(axs, ndmin=2)

    # Build normalization once
    norm = build_norm(norm_mode, vmax, gamma)

    # Plot each subplot
    last_im = None
    for idx, (rho, samples) in enumerate(zip(rhos, samples_list)):
        r = idx // cols
        c = idx % cols
        ax = axs[r, c]
        x = samples[:, 0]
        y = samples[:, 1]
        corr_xy = corr_list[idx]

        if scatter_perfect and abs(rho) == 1:
            ax.scatter(x, y, s=6, alpha=0.7, c='deepskyblue', edgecolors='none')
            # Add faint hist2d for shared colorbar alignment
            H, xedges, yedges = compute_hist_stats(samples, bins, xy_range)
            im = ax.hist2d(x, y, bins=bins, range=xy_range, cmap=cmap,
                           cmin=1 if isinstance(norm, mcolors.LogNorm) else 0,
                           norm=norm, alpha=0.3)[3]
        else:
            H, xedges, yedges = compute_hist_stats(samples, bins, xy_range)
            im = ax.hist2d(x, y, bins=bins, range=xy_range, cmap=cmap,
                           cmin=1 if isinstance(norm, mcolors.LogNorm) else 0,
                           norm=norm)[3]
        last_im = im

        if contours:
            positive = H[H > 0]
            if positive.size >= 5:
                levels = np.quantile(positive, [0.2, 0.4, 0.6, 0.8, 0.92])
                ax.contour(0.5*(xedges[:-1] + xedges[1:]),
                           0.5*(yedges[:-1] + yedges[1:]),
                           H.T, levels=levels, colors='white', linewidths=0.8, alpha=0.85)

        ax.set_xlabel('X ~ N(0, 1)')
        ax.set_ylabel('Y ~ N(0, 2)')
        ax.set_title(f'ρ={rho} — Empirical corr ≈ {corr_xy:.3f}')

    # Hide any unused axes
    for j in range(len(rhos), rows*cols):
        r = j // cols
        c = j % cols
        axs[r, c].axis('off')

    # Shared colorbar for hist2d mappable
    if last_im is not None:
        cbar = fig.colorbar(last_im, ax=axs.ravel().tolist(), fraction=0.035, pad=0.01)
        label = 'Counts per bin'
        if isinstance(norm, mcolors.LogNorm):
            label += ' (log scale)'
        elif isinstance(norm, mcolors.PowerNorm):
            label += f' (gamma={gamma})'
        cbar.set_label(label)

    fig.suptitle(f'Bivariate Normal: X~N(0,1), Y~N(0,4); N={n}', fontsize=14)
    fig.savefig(grid_outfile, dpi=260)
    if show:
        plt.show()
    plt.close(fig)
    return grid_outfile

# --------------------- CLI ---------------------
def main():
    parser = argparse.ArgumentParser(description='Generate correlated normal pairs and plot as colormaps (high-contrast).')
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
    # Contrast options
    parser.add_argument('--cmap', type=str, default='magma', help='Matplotlib colormap (default: magma).')
    parser.add_argument('--norm', dest='norm_mode', choices=['linear', 'log', 'gamma'], default='log',
                        help='Color normalization mode: linear | log | gamma (default: log).')
    parser.add_argument('--gamma', type=float, default=0.5, help='Gamma for --norm gamma (default: 0.5).')
    parser.add_argument('--contours', dest='contours', action='store_true', default=True, help='Overlay contour lines (default: on).')
    parser.add_argument('--no-contours', dest='contours', action='store_false', help='Disable contour overlay.')
    parser.add_argument('--scatter-perfect', dest='scatter_perfect', action='store_true', default=True,
                        help='Use scatter overlay for ρ = ±1 (default: on).')
    parser.add_argument('--no-scatter-perfect', dest='scatter_perfect', action='store_false',
                        help='Disable scatter overlay for ρ = ±1.')
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
                                          grid_outfile=args.grid_outfile, cmap=args.cmap,
                                          norm_mode=args.norm_mode, gamma=args.gamma,
                                          contours=args.contours, scatter_perfect=args.scatter_perfect,
                                          show=args.show)
        print(f"Saved grid canvas to: {grid_outfile}")
    else:
        # Separate images per rho, with a common vmax across panels
        rng = np.random.default_rng(args.seed)
        xy_range = default_xy_range()
        # Draw and compute shared vmax
        samples_by_rho = {}
        vmax = 0
        for rho in args.rho:
            samples = draw_samples(args.n, rho=rho, rng=rng)
            samples_by_rho[rho] = samples
            H, _, _ = compute_hist_stats(samples, args.bins, xy_range)
            vmax = max(vmax, int(H.max()))
        if vmax == 0:
            vmax = None
        for rho, samples in samples_by_rho.items():
            rho_tag = str(rho).replace('.', 'p').replace('-', 'neg')
            outfile = f"{args.outfile_prefix}_rho{rho_tag}.png"
            _outfile, corr_xy = plot_colormap(samples, rho, outfile, bins=args.bins, show=args.show,
                                              xy_range=xy_range, vmax=vmax, cmap=args.cmap,
                                              norm_mode=args.norm_mode, gamma=args.gamma,
                                              contours=args.contours, scatter_perfect=args.scatter_perfect)
            print(f"Saved colormap for rho={rho} to: {_outfile}")
            print(f"Empirical correlation over N={args.n}: {corr_xy:.4f}")

if __name__ == '__main__':
    main()
