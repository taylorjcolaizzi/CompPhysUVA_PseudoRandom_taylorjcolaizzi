#!/usr/bin/env python3
"""
exp.py — Generate 1000 pseudo-random numbers from an exponential distribution
with lambda = 10, print summary statistics, and display a histogram with the
theoretical PDF for comparison.
"""

import numpy as np
import matplotlib.pyplot as plt


def main():
    # Parameter (rate)
    lambda_param = 10.0

    # Generate samples: NumPy uses 'scale' = 1/lambda for exponential
    samples = np.random.exponential(scale=1.0 / lambda_param, size=1000)

    # --- Summary statistics ---
    mean = np.mean(samples)
    std_pop = np.std(samples, ddof=0)      # population std (NumPy default)
    std_sample = np.std(samples, ddof=1)   # sample std (unbiased)

    print("Summary statistics for 1000 Exponential(λ=10) samples:")
    print(f"  Mean: {mean:.6f}")
    print(f"  Std dev (sample, ddof=1): {std_sample:.6f}")
    print(f"  Std dev (population, ddof=0): {std_pop:.6f}")

    # (Optional) Theoretical values for reference
    theo_mean = 1.0 / lambda_param
    theo_std = 1.0 / lambda_param
    print(f"  Theoretical mean/std: {theo_mean:.6f} / {theo_std:.6f}\n")

    # (Optional) Print all samples — comment out if too verbose
    # print(samples)

    # Plot histogram (density=True to show probability density)
    plt.figure(figsize=(8, 5))
    n, bins, patches = plt.hist(
        samples,
        bins=30,
        density=True,
        color="#7ec8e3",
        edgecolor="#1f4e5f",
        alpha=0.85,
        label="Histogram (density)"
    )

    # Overlay theoretical PDF: f(x) = lambda * exp(-lambda * x), x >= 0
    x = np.linspace(0, max(samples.max(), bins[-1]), 500)
    pdf = lambda_param * np.exp(-lambda_param * x)
    plt.plot(x, pdf, color="#d62728", linewidth=2.0, label="Theoretical PDF")

    # Labels and title
    plt.title("Exponential(λ=10) — 1000 samples")
    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()

    # Show the plot window
    plt.show()


if __name__ == "__main__":
    main()
