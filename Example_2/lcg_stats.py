"""lcg_stats.py — Generate N values in [0,1) from an LCG and report mean, std dev, and first four moments.

This program generates pseudo-random floating-point numbers in [0, 1) using a
Linear Congruential Generator (LCG) and prints:
- count
- mean (sample)
- standard deviation (sample)
- first four raw moments m_k = E[X^k] for k = 1..4 (sample), plus Uniform(0,1) expected values

It streams values using online updates—no need to store the sequence.

Usage:
    python lcg_stats.py                      # defaults: count=1_000_000, seed=12345
    python lcg_stats.py --count 5000000      # generate 5,000,000 values
    python lcg_stats.py --seed 42            # use a different seed
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

class OnlineRawMoments:
    """Track raw moments m_k = E[X^k] via running power sums up to k=4."""
    def __init__(self):
        self.n = 0
        self.s1 = 0.0
        self.s2 = 0.0
        self.s3 = 0.0
        self.s4 = 0.0
    def add(self, x: float):
        self.n += 1
        x2 = x * x
        x3 = x2 * x
        x4 = x2 * x2
        self.s1 += x
        self.s2 += x2
        self.s3 += x3
        self.s4 += x4
    def moment1(self) -> float:
        return self.s1 / self.n if self.n else float('nan')
    def moment2(self) -> float:
        return self.s2 / self.n if self.n else float('nan')
    def moment3(self) -> float:
        return self.s3 / self.n if self.n else float('nan')
    def moment4(self) -> float:
        return self.s4 / self.n if self.n else float('nan')

def main():
    parser = argparse.ArgumentParser(description="Generate [0,1) values with an LCG and report statistics & moments.")
    parser.add_argument('--count', type=float, default=1_000_000, help='How many numbers to generate (default: 1,000,000)')
    parser.add_argument('--seed', type=int, default=12345, help='Seed X0 (default: 12345)')
    parser.add_argument('--a', type=int, default=1103515245, help='Multiplier a (default: 1103515245)')
    parser.add_argument('--c', type=int, default=12345, help='Increment c (default: 12345)')
    parser.add_argument('--m', type=int, default=2**31, help='Modulus m (default: 2**31)')

    args = parser.parse_args()
    count = int(args.count)

    lcg = LCG(seed=args.seed, a=args.a, c=args.c, m=args.m)

    stats = OnlineStats()
    moments = OnlineRawMoments()

    for _ in range(count):
        x = lcg.random()  # always a float in [0,1)
        stats.add(x)
        moments.add(x)

    # Expected raw moments for Uniform(0,1): E[X^k] = 1/(k+1)
    expected = {
        1: 1.0/2.0,
        2: 1.0/3.0,
        3: 1.0/4.0,
        4: 1.0/5.0,
    }

    print(f"count: {stats.n}")
    print(f"mean: {stats.mean:.12f}")
    print(f"std_dev (sample): {stats.sample_std():.12f}")
    print()
    print("Raw moments m_k = E[X^k] (sample vs expected for Uniform(0,1)):")
    print(f"m1 (E[X])   : {moments.moment1():.12f} | expected {expected[1]:.12f}")
    print(f"m2 (E[X^2]) : {moments.moment2():.12f} | expected {expected[2]:.12f}")
    print(f"m3 (E[X^3]) : {moments.moment3():.12f} | expected {expected[3]:.12f}")
    print(f"m4 (E[X^4]) : {moments.moment4():.12f} | expected {expected[4]:.12f}")

if __name__ == '__main__':
    main()
