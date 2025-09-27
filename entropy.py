#!/usr/bin/env python3
import sys
import math
from collections import Counter

def compute_entropy(file_path):
    try:
        # Open in binary mode to handle any file type
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not data:
        print("Entropy: 0.0 bits/byte (empty file)")
        return

    counts = Counter(data)
    total = len(data)
    entropy = 0.0

    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)

    print(f"Entropy: {entropy:.6f} bits/byte")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python entropy.py <file_path>")
    else:
        compute_entropy(sys.argv[1])
