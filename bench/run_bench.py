#!/usr/bin/env python3
"""Compile once and report median runtime for the regex benchmark workload."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import statistics
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=7)
    args = parser.parse_args()
    tokac_env = os.environ.get("TOKAC")
    toka_lib_env = os.environ.get("TOKA_LIB")
    if tokac_env and toka_lib_env:
        tokac = Path(tokac_env).resolve()
        toka_lib = Path(toka_lib_env).resolve()
    else:
        toka_root = Path(os.environ.get("TOKA_ROOT", "")).resolve()
        tokac = toka_root / "build" / "bin" / "tokac"
        toka_lib = toka_root / "lib"
    if args.samples < 1 or not tokac.is_file() or not toka_lib.is_dir():
        raise SystemExit("TOKA_ROOT or TOKAC/TOKA_LIB must identify a built Toka checkout; --samples must be positive")

    with tempfile.TemporaryDirectory(prefix="toka-regex-bench-") as temporary:
        binary = Path(temporary) / "regex_bench"
        subprocess.run([
            str(tokac), "-I", str(toka_lib), "-I", str(ROOT / "lib"),
            str(ROOT / "bench" / "regex_bench.tk"), "-o", str(binary),
        ], check=True)
        durations: list[float] = []
        for _ in range(args.samples):
            started = time.perf_counter()
            subprocess.run([str(binary)], check=True, stdout=subprocess.DEVNULL)
            durations.append(time.perf_counter() - started)

    print("regex-bench-v1", "samples=%d" % args.samples,
          "median_ms=%.2f" % (statistics.median(durations) * 1000),
          "min_ms=%.2f" % (min(durations) * 1000))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
