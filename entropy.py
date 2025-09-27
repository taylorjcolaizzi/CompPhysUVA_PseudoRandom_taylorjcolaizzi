#!/usr/bin/env python3
"""
entropy.py — Compute the Shannon entropy of one or more files.

Shannon entropy (base-2) measures the average information content per symbol.
For byte-oriented files (256 possible symbols), the maximum entropy is 8 bits/byte.

Usage examples:
  python entropy.py path/to/file.bin
  python entropy.py --base 2 file1.bin file2.txt
  python entropy.py --table 10 file.bin     # Show top 10 most frequent bytes
  python entropy.py -                        # Read from STDIN

Exit codes:
  0 on success, 2 if one or more files could not be processed.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from collections import Counter
from typing import Dict, Iterable, Tuple


def _log(p: float, base_flag: str) -> float:
    """Compute log(p) in the requested base.

    base_flag: one of {"2", "e", "10"}
    """
    if base_flag == "2":
        return math.log2(p)
    elif base_flag == "10":
        return math.log10(p)
    else:  # "e"
        return math.log(p)


def entropy_from_counts(counts: Dict[int, int], base_flag: str = "2") -> float:
    """Return Shannon entropy from a dict of byte->count.

    The result is expressed in the units of the chosen base (e.g., bits when base 2).
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c == 0:
            continue
        p = c / total
        h -= p * _log(p, base_flag)
    return h


def byte_counts_from_stream(stream, chunk_size: int = 4 * 1024 * 1024) -> Counter:
    """Count byte occurrences from a binary stream in chunks.

    Returns a Counter mapping byte (0..255) to count.
    """
    counts: Counter = Counter()
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        counts.update(chunk)
    return counts


def byte_counts_from_file(path: str, chunk_size: int = 4 * 1024 * 1024) -> Tuple[Counter, int]:
    """Count byte occurrences in a file. Returns (counts, total_bytes). Supports '-' for STDIN."""
    if path == "-":
        # Read from STDIN (binary)
        data_stream = getattr(sys.stdin, "buffer", sys.stdin)
        counts = byte_counts_from_stream(data_stream, chunk_size)
        total = sum(counts.values())
        return counts, total

    with open(path, "rb") as f:
        counts = byte_counts_from_stream(f, chunk_size)
    total = sum(counts.values())
    return counts, total


def human_size(n: int) -> str:
    """Return a human-friendly size for n bytes."""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(n)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{n} B"


def print_table(counts: Counter, total: int, top: int) -> None:
    """Print a table of the top-N most frequent bytes."""
    if total == 0:
        print("(empty input — no byte frequencies to display)")
        return

    print()
    print(f"Top {top if top > 0 else 'all'} byte frequencies:")
    print("Byte  Hex  Count       Prob       ")
    print("----  ---  ----------  ----------")

    items = counts.most_common(top if top > 0 else None)
    for b, c in items:
        p = c / total
        # Show printable ASCII where reasonable, else dot
        if 32 <= b <= 126 and b not in (34, 39, 92):  # avoid quotes/backslash
            byte_repr = chr(b)
        else:
            byte_repr = "."
        print(f"{byte_repr:>4}  {b:02X}  {c:10d}  {p:10.6f}")


def parse_args(argv: Iterable[str]):
    parser = argparse.ArgumentParser(
        description=(
            "Compute Shannon entropy for byte values in file(s). Maximum for bytes is 8 bits/byte."
        )
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="+",
        help=(
            "Path to input file(s). Use '-' to read from STDIN (only once in the list)."
        ),
    )
    parser.add_argument(
        "--base",
        choices=["2", "e", "10"],
        default="2",
        help="Logarithm base for entropy units: 2=bits (default), e=nats, 10=bans",
    )
    parser.add_argument(
        "--table",
        type=int,
        default=0,
        metavar="N",
        help="Show a frequency table of the top N most common bytes (0 to disable)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=4 * 1024 * 1024,
        help="Chunk size (bytes) for streaming reads; default is 4 MiB",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    had_error = False
    multiple = len(args.files) > 1

    for path in args.files:
        try:
            counts, total = byte_counts_from_file(path, args.chunk_size)
            H = entropy_from_counts(counts, base_flag=args.base)

            if args.base == "2":
                # For byte symbols, maximum is log2(256) = 8 bits/byte
                max_entropy = 8.0
                normalized = (H / max_entropy * 100.0) if max_entropy > 0 else 0.0
                unit = "bits/byte"
            elif args.base == "10":
                # log10(256)
                max_entropy = math.log10(256)
                normalized = (H / max_entropy * 100.0) if max_entropy > 0 else 0.0
                unit = "bans/byte"
            else:  # nats
                max_entropy = math.log(256)
                normalized = (H / max_entropy * 100.0) if max_entropy > 0 else 0.0
                unit = "nats/byte"

            label = path if path != "-" else "<stdin>"
            size_str = human_size(total)

            if multiple:
                print(f"{label}: {H:.6f} {unit}  (size: {size_str}, {normalized:.2f}% of max)")
            else:
                print(f"File: {label}")
                print(f"Size: {total} bytes ({size_str})")
                print(f"Entropy: {H:.6f} {unit}")
                print(f"Max ({unit}): {max_entropy:.6f}")
                print(f"Normalized: {normalized:.2f}% of maximum")

            if args.table:
                print_table(counts, total, args.table)

        except FileNotFoundError:
            had_error = True
            print(f"error: file not found: {path}", file=sys.stderr)
        except PermissionError:
            had_error = True
            print(f"error: permission denied: {path}", file=sys.stderr)
        except IsADirectoryError:
            had_error = True
            print(f"error: is a directory, not a file: {path}", file=sys.stderr)
        except Exception as e:
            had_error = True
            print(f"error processing '{path}': {e}", file=sys.stderr)

    return 2 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
