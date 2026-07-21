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


# ── find binary ───────────────────────────────────────────────────────

def _find_binary(lang: str, binary_name: str) -> str:
    repo_root = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    candidates = [
        os.path.join(repo_root, "bazel-bin", lang, binary_name),
        # rules_go nests the executable in "<name>_/" unless out= is set
        os.path.join(repo_root, "bazel-bin", lang, binary_name + "_", binary_name),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    sys.exit(f"Cannot find {lang}/{binary_name}.\nRun: bazel run //python:benchmark")


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


# ── call Go binary ────────────────────────────────────────────────────────────
def go_factorial(n: int, binary: str) -> tuple[int, float]:
    """Call the Go binary, return (digit_count, time_seconds)."""
    proc = subprocess.run(
        [binary, str(n)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"Go binary failed:\n{proc.stderr}")

    info = {}
    for line in proc.stdout.strip().splitlines():
        key, val = line.split()
        info[key] = int(val)

    return info["digits"], info["time_us"] / 1_000_000

# ── call Go binary ────────────────────────────────────────────────────────────
def rust_factorial(n: int, binary: str) -> tuple[int, float]:
    """Call the Rust binary, return (digit_count, time_seconds)."""
    proc = subprocess.run(
        [binary, str(n)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"Rust binary failed:\n{proc.stderr}")

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

def print_results(n: int, py_time: float, cpp_time: float,
                  go_time: float, rust_time: float, digit_count: int) -> None:
    rows = [("Python", py_time), ("C++", cpp_time), ("Go", go_time), ("Rust", rust_time)]
    max_t = max(t for _, t in rows)

    fmt = {name: _fmt_time(t) for name, t in rows}
    col = max(max(len(s) for s in fmt.values()), len("Time"))

    print()
    print(f"  Factorial benchmark   n = {n:,}")
    print(f"  Result has {digit_count:,} digits")
    print()
    print(f"  {'Implementation':<14}  {'Time':>{col}}  Chart")
    print(f"  {'-'*14}  {'-'*col}  {'-'*30}")
    for name, t in rows:
        print(f"  {name:<14}  {fmt[name]:>{col}}  {_bar(t, max_t)}")
    print()

    def versus(a: str, a_t: float, b: str, b_t: float) -> None:
        if a_t <= 0 or b_t <= 0:
            return
        if a_t <= b_t:
            print(f"  {a} is {b_t / a_t:.1f}x faster than {b}")
        else:
            print(f"  {b} is {a_t / b_t:.1f}x faster than {a}")

    versus("C++",  cpp_time,  "Python", py_time)
    versus("Go",   go_time,   "Python", py_time)
    versus("Rust", rust_time, "Python", py_time)
    versus("C++",  cpp_time,  "Go",     go_time)
    versus("C++",  cpp_time,  "Rust",   rust_time)
    versus("Go",   go_time,   "Rust",   rust_time)
    if py_time < cpp_time or py_time < go_time:
        print("  Note: at small n the differences are mostly timer noise, not real speed.")
    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Factorial benchmark: Python vs C++")
    parser.add_argument("--n", type=int, default=20_000,
                        help="Compute n! (default: 20000)")
    args = parser.parse_args()
    n = args.n

    cpp_binary = _find_binary("cpp", "factorial_bin")
    go_binary = _find_binary("go", "factorial_bin")
    rust_binary = _find_binary("rust", "factorial_bin")
    print(f"[benchmark] n = {n:,}")
    print(f"[benchmark] C++ binary: {cpp_binary}")
    print(f"[benchmark] Go binary: {go_binary}")
    print(f"[benchmark] Rust binary: {rust_binary}")

    # ── Python ──
    print(f"[benchmark] Running Python factorial({n:,}) ...")
    t0 = time.perf_counter()
    py_result = python_factorial(n)
    py_time = time.perf_counter() - t0
    py_digits = len(str(py_result))

    # ── C++ ──
    print(f"[benchmark] Running C++ factorial({n:,}) ...")
    cpp_digits, cpp_time = cpp_factorial(n, cpp_binary)

    # ── Go ──
    print(f"[benchmark] Running Go factorial({n:,}) ...")
    go_digits, go_time = go_factorial(n, go_binary)

    # ── Rust ──
    print(f"[benchmark] Running Rust factorial({n:,}) ...")
    rust_digits, rust_time = rust_factorial(n, rust_binary)

    if not (py_digits == cpp_digits == go_digits == rust_digits):
            print(f"  WARNING: digit count mismatch! "
                f"Python={py_digits} C++={cpp_digits} Go={go_digits} Rust={rust_digits}")

    print_results(n, py_time, cpp_time, go_time, rust_time, py_digits)


if __name__ == "__main__":
    main()