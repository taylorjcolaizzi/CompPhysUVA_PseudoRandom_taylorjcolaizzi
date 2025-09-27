
"""lcg_stats.py — Generate N values in [0,1) from an LCG and report mean & std dev.

This program generates 1,000,000 pseudo-random floating-point numbers in [0, 1)
using a Linear Congruential Generator (LCG) and prints the mean and sample
standard deviation. It streams values, so it never stores the full sequence.

Usage:
    python lcg_stats.py              # defaults to 1,000,000 values, seed=12345
    python lcg_stats.py --count 5e6  # generate 5,000,000 values
    python lcg_stats.py --seed 42    # use a different seed
    python lcg_stats.py --a ... --c ... --m ...  # customize LCG parameters
"""
from __future__ import annotations
import argparse
import math

# Import the LCG from lpr.py. We only use its normalized .random() method.
try:
    from lpr import LinearCongruentialGenerator as LCG
except Exception:  # pragma: no cover
    class LCG:  # minimal fallback if lpr.py isn't present
        def __init__(self, seed: int, a: int = 1103515245, c: int = 12345, m: int = 2**31):
            self.a, self.c, self.m = int(a), int(c), int(m)
            self.current = seed % self.m
        def next(self) -> int:
            self.current = (self.a * self.current + self.c) % self.m
            return self.current
        def random(self) -> float:
            # Normalize to [0,1)
            return self.next() / self.m

class OnlineStats:
    """Welford's online algorithm for mean and (sample) standard deviation."""
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0
    def add(self, x: float):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2
    def sample_std(self) -> float:
        return math.sqrt(self.M2 / (self.n - 1)) if self.n > 1 else float('nan')


def main():
    parser = argparse.ArgumentParser(description="Generate [0,1) values with an LCG and report statistics.")
    parser.add_argument('--count', type=float, default=1_000_000, help='How many numbers to generate (default: 1,000,000)')
    parser.add_argument('--seed', type=int, default=12345, help='Seed X0 (default: 12345)')
    parser.add_argument('--a', type=int, default=1103515245, help='Multiplier a (default: 1103515245)')
    parser.add_argument('--c', type=int, default=12345, help='Increment c (default: 12345)')
    parser.add_argument('--m', type=int, default=2**31, help='Modulus m (default: 2**31)')

    args = parser.parse_args()
    count = int(args.count)

    lcg = LCG(seed=args.seed, a=args.a, c=args.c, m=args.m)

    stats = OnlineStats()
    for _ in range(count):
        x = lcg.random()  # always a float in [0,1)
        stats.add(x)

    print(f"count: {stats.n}")
    print(f"mean: {stats.mean:.12f}")
    print(f"std_dev (sample): {stats.sample_std():.12f}")

if __name__ == '__main__':
    main()
