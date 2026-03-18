"""
benchmark.py — compare pure-Python factorial vs C++ factorial (GMP).

Run:
    bazel run //python:benchmark              # default N = 20000
    bazel run //python:benchmark -- --n 100000
"""

import argparse
import os
import subprocess
import sys
import time

# Python 3.11+ limits int→str conversion to 4300 digits by default.
# Factorials of large numbers exceed this, so we remove the limit.
sys.set_int_max_str_digits(0)


# ── find the C++ binary ───────────────────────────────────────────────────────

def _find_binary() -> str:
    repo_root = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    binary = os.path.join(repo_root, "bazel-bin", "cpp", "factorial_bin")
    if not os.path.isfile(binary):
        sys.exit("Cannot find factorial_bin.\nRun: bazel run //python:benchmark")
    return binary


# ── pure Python factorial ─────────────────────────────────────────────────────

def python_factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# ── call C++ binary ───────────────────────────────────────────────────────────

def cpp_factorial(n: int, binary: str) -> tuple[int, float]:
    """Call the C++ binary, return (digit_count, time_seconds)."""
    proc = subprocess.run(
        [binary, str(n)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"C++ binary failed:\n{proc.stderr}")

    info = {}
    for line in proc.stdout.strip().splitlines():
        key, val = line.split()
        info[key] = int(val)

    return info["digits"], info["time_us"] / 1_000_000


# ── formatting ────────────────────────────────────────────────────────────────

def _fmt_time(t: float) -> str:
    if t >= 60:   return f"{int(t)//60}m {t%60:.1f}s"
    if t >= 1:    return f"{t:.2f}s"
    if t >= 0.001: return f"{t*1000:.1f}ms"
    return f"{t*1e6:.0f}µs"

def _bar(value: float, max_value: float, width: int = 30) -> str:
    filled = int(round(value / max_value * width)) if max_value > 0 else 0
    return "█" * filled + "░" * (width - filled)

def print_results(n: int, py_time: float, cpp_time: float, digit_count: int) -> None:
    speedup = py_time / cpp_time if cpp_time > 0 else float("inf")

    if speedup < 1:
        msg = f"  Python is {1/speedup:.1f}x faster than C++"
        note = "  Note: for small n, C++ loses because subprocess launch overhead (~20µs) dominates the actual calculation time."
    else:
        msg = f"  C++ is {speedup:.1f}x faster than Python"
        note = ""

    max_t   = max(py_time, cpp_time)

    py_str  = _fmt_time(py_time)
    cpp_str = _fmt_time(cpp_time)
    col     = max(len(py_str), len(cpp_str))  # align column to widest time

    print()
    print(f"  Factorial benchmark   n = {n:,}")
    print(f"  Result has {digit_count:,} digits")
    print()
    print(f"  {'Implementation':<14}  {'Time':>{col}}  Chart")
    print(f"  {'-'*14}  {'-'*col}  {'-'*30}")
    print(f"  {'Python':<14}  {py_str:>{col}}  {_bar(py_time, max_t)}")
    print(f"  {'C++':<14}  {cpp_str:>{col}}  {_bar(cpp_time, max_t)}")
    print()
    print(msg)
    if note:
        print(note)
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Factorial benchmark: Python vs C++")
    parser.add_argument("--n", type=int, default=20_000,
                        help="Compute n! (default: 20000)")
    args = parser.parse_args()
    n = args.n

    binary = _find_binary()
    print(f"[benchmark] n = {n:,}")
    print(f"[benchmark] C++ binary: {binary}")

    # ── Python ──
    print(f"[benchmark] Running Python factorial({n:,}) ...")
    t0 = time.perf_counter()
    py_result = python_factorial(n)
    py_time = time.perf_counter() - t0
    py_digits = len(str(py_result))

    # ── C++ ──
    print(f"[benchmark] Running C++ factorial({n:,}) ...")
    cpp_digits, cpp_time = cpp_factorial(n, binary)

    if py_digits != cpp_digits:
        print(f"  WARNING: digit count mismatch! Python={py_digits} C++={cpp_digits}")

    print_results(n, py_time, cpp_time, cpp_digits)


if __name__ == "__main__":
    main()