"""lpr.py — Linear Congruential Pseudo-Random Number Generator (LCG)

Formula: X_{n+1} = (a * X_n + c) mod m

Default parameters below match a common LCG (glibc-like):
    a = 1103515245
    c = 12345
    m = 2**31

Example:
    from lpr import LinearCongruentialGenerator as LCG
    lcg = LCG(seed=12345)
    print(lcg.next())
    print(lcg.generate_sequence(5))
"""
from __future__ import annotations
from typing import List

class LinearCongruentialGenerator:
    def __init__(self, seed: int, a: int = 1103515245, c: int = 12345, m: int = 2**31):
        """
        Initialize the LCG with parameters.

        Args:
            seed: Initial state X_0 (must be an integer >= 0)
            a: Multiplier
            c: Increment
            m: Modulus (> 0)
        """
        if m <= 0:
            raise ValueError("Modulus m must be > 0")
        if not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be a non-negative integer")
        self.a = int(a)
        self.c = int(c)
        self.m = int(m)
        self.current = seed % self.m

    def next(self) -> int:
        """Generate and return the next pseudo-random integer in [0, m-1]."""
        self.current = (self.a * self.current + self.c) % self.m
        return self.current

    def random(self) -> float:
        """Return a float in [0.0, 1.0) by scaling the next() value by m."""
        return self.next() / self.m

    def generate_sequence(self, n: int) -> List[int]:
        """Generate a list of n pseudo-random integers."""
        return [self.next() for _ in range(n)]
