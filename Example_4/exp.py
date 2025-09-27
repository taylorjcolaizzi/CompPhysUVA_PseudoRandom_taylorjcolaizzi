#!/usr/bin/env python3
"""
exp.py — Generate 1000 pseudo-random numbers from an exponential distribution
with lambda = 10, print them, and display a histogram with the theoretical PDF.
"""

import numpy as np
import matplotlib.pyplot as plt


def main():
    # Parameter (rate)
    lambda_param = 10.0

    # Generate samples: NumPy uses 'scale' = 1/lambda for exponential
    samples = np.random.exponential(scale=1.0 / lambda_param, size=1000)

    # Print the samples (optional: comment this out if too verbose)
    print(samples)

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
