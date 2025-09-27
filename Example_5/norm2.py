"""
Generate a pair of normally distributed random numbers (X, Y) such that:
  - X ~ N(mean=0, std=1)
  - Y ~ N(mean=0, std=2)
  - Corr(X, Y) = 0.5

By default, prints a single draw (x, y).
Optional: use --check N to draw N samples and report empirical stats.
Optional: use --seed SEED for reproducibility.
"""

import argparse
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Generate correlated normal random numbers.")
    parser.add_argument('--check', type=int, default=None,
                        help='If provided, draw this many samples to empirically check moments.')
    parser.add_argument('--seed', type=int, default=None,
                        help='Optional RNG seed for reproducibility.')
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)

    # Target parameters
    mean = np.array([0.0, 0.0])
    std1, std2 = 1.0, 2.0
    rho = 0.5  # desired linear correlation

    # Construct covariance matrix from stds and correlation
    cov12 = rho * std1 * std2
    cov = np.array([[std1**2,  cov12],
                    [cov12,    std2**2]])

    if args.check is not None and args.check > 0:
        # Draw many samples and report empirical moments to verify
        samples = rng.multivariate_normal(mean=mean, cov=cov, size=args.check)
        x = samples[:, 0]
        y = samples[:, 1]
        # Empirical stats
        mean_x = float(x.mean())
        mean_y = float(y.mean())
        std_x = float(x.std(ddof=1))
        std_y = float(y.std(ddof=1))
        corr_xy = float(np.corrcoef(x, y)[0, 1])
        print(f"Empirical check over N={args.check} samples:")
        print(f"  E[X] ≈ {mean_x:.4f},  SD[X] ≈ {std_x:.4f}")
        print(f"  E[Y] ≈ {mean_y:.4f},  SD[Y] ≈ {std_y:.4f}")
        print(f"  Corr[X,Y] ≈ {corr_xy:.4f}")
    else:
        # Single draw from the specified bivariate normal
        x, y = rng.multivariate_normal(mean=mean, cov=cov)
        print(f"First number (mean=0, std=1): {x}")
        print(f"Second number (mean=0, std=2), corr=0.5 with first: {y}")

if __name__ == '__main__':
    main()
