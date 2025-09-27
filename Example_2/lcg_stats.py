
"""lcg_stats.py — Generate N values from LCG and report mean & standard deviation.

By default, generates 1,000,000 normalized values in [0, 1) and prints:
- count
- mean
- standard deviation (sample, ddof=1)

Usage:
    python lcg_stats.py
    python lcg_stats.py --count 1000000 --seed 12345
    python lcg_stats.py --integers              # use raw integers instead of [0,1) floats
    python lcg_stats.py --a 1103515245 --c 12345 --m 2147483648
"""
from __future__ import annotations
import argparse
import math

# Try to import the provided LCG; if not present, define a fallback.
try:
    from lpr import LinearCongruentialGenerator as LCG
except Exception:  # pragma: no cover
    class LCG:  # minimal fallback
        def __init__(self, seed: int, a: int = 1103515245, c: int = 12345, m: int = 2**31):
            self.a, self.c, self.m = int(a), int(c), int(m)
            self.current = seed % self.m
        def next(self) -> int:
            self.current = (self.a * self.current + self.c) % self.m
            return self.current
        def random(self) -> float:
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
    def population_std(self) -> float:
        return math.sqrt(self.M2 / self.n) if self.n > 0 else float('nan')


def main():
    parser = argparse.ArgumentParser(description="Generate pseudo-random numbers with an LCG and report statistics.")
    parser.add_argument('--count', type=int, default=1_000_000, help='How many numbers to generate (default: 1,000,000)')
    parser.add_argument('--seed', type=int, default=12345, help='Seed X0 (default: 12345)')
    parser.add_argument('--a', type=int, default=1103515245, help='Multiplier a (default: 1103515245)')
    parser.add_argument('--c', type=int, default=12345, help='Increment c (default: 12345)')
    parser.add_argument('--m', type=int, default=2**31, help='Modulus m (default: 2**31)')
    parser.add_argument('--integers', action='store_true', help='Use raw integers instead of normalized [0,1) floats')

    args = parser.parse_args()

    lcg = LCG(seed=args.seed, a=args.a, c=args.c, m=args.m)

    stats = OnlineStats()
    if args.integers:
        # Use integers in [0, m-1]
        for _ in range(args.count):
            stats.add(float(lcg.next()))
    else:
        # Use normalized floats in [0, 1)
        for _ in range(args.count):
            stats.add(lcg.random())

    print(f"count: {stats.n}")
    print(f"mean: {stats.mean:.12f}")
    print(f"std_dev (sample): {stats.sample_std():.12f}")

if __name__ == '__main__':
    main()
