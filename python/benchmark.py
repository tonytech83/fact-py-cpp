"""
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


# ── languages ───────────────────────────────────────────────────────

LANGS: {str, str} = {
    "cpp": "C++",
    "go": "Go",
    "rust": "Rust"
}

# ── find binary ───────────────────────────────────────────────────────

def _find_binary(lang: str) -> str:
    repo_root = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    candidates = [
        os.path.join(repo_root, "bazel-bin", lang, "factorial_bin"),
        # rules_go nests the executable in "<name>_/" unless out= is set
        os.path.join(repo_root, "bazel-bin", lang, "factorial_bin" + "_", "factorial_bin"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    sys.exit(f"Cannot find {lang}/factorial_bin.\nRun: bazel run //python:benchmark")


# ── pure Python factorial ─────────────────────────────────────────────────────

def python_factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# ── call binary ────────────────────────────────────────────────────────────

def run_binary(lang: str, n: int, binary: str) -> tuple[int, float]:
    """Call the binary (C++, Go, Rust) and return (digit_count, time_seconds)."""
    proc = subprocess.run(
        [binary, str(n)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"{lang} binary failed:\n{proc.stderr}")

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

def print_results(n: int,digit_count: int, langs_time) -> None:
    results_sorted_by_time = sorted(langs_time, key=lambda time: time[1])
    max_t = max(t for _, t in results_sorted_by_time)

    fmt = {name: _fmt_time(t) for name, t in results_sorted_by_time}
    col = max(max(len(s) for s in fmt.values()), len("Time"))

    print()
    print(f"  Factorial benchmark n = {n:,}")
    print(f"  Result has {digit_count:,} digits")
    print()
    print(f"  {'Implementation':<14}  {'Time':>{col}}  Chart")
    print(f"  {'-'*14}  {'-'*col}  {'-'*30}")
    for name, t in results_sorted_by_time:
        print(f"  {name:<14}  {fmt[name]:>{col}}  {_bar(t, max_t)}")
    print()

    def versus(a: str, a_t: float, b: str, b_t: float) -> None:
        if a_t <= 0 or b_t <= 0:
            return
        if a_t <= b_t:
            print(f"  {a} is {b_t / a_t:.1f}x faster than {b}")
        else:
            print(f"  {b} is {a_t / b_t:.1f}x faster than {a}")

    # ── The winner is ... ──
    winner_lang = results_sorted_by_time[0][0]
    winner_time = results_sorted_by_time[0][1]
    print(f"  The winner is {winner_lang} with {_fmt_time(winner_time)} time.")
    print()

    # ── Print winner vs. each other lang ──
    for i in range(1, len(results_sorted_by_time)):
        versus(winner_lang,  winner_time,  results_sorted_by_time[i][0], results_sorted_by_time[i][1])
    print()

    if winner_lang == "Python":
        print("  Note: at small n the differences are mostly timer noise, not real speed.")

    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Factorial benchmark: Python vs C++ vs Go vs Rust")
    parser.add_argument("--n", type=int, default=20_000,
                        help="Compute n! (default: 20000)")
    args = parser.parse_args()
    n = args.n

    # ── Calculate factorial of n with Python ──
    print(f"[benchmark] Running Python factorial({n:,}) ...")
    t0 = time.perf_counter()
    py_result = python_factorial(n)
    py_time = time.perf_counter() - t0
    py_digits = len(str(py_result))

    # ── Calculate factorial of n for each language in LANGS mapper ──
    results: {str, str} = []
    all_langs_digits: {float} = set()
    results.append(("Python", py_time))

    for lang, lang_name in LANGS.items():
        print(f"[benchmark] Running {lang} factorial({n:,}) ...")
        curr_calc = (lang_name,n, _find_binary(lang))
        lang_digits, lang_time = run_binary(*curr_calc)

        all_langs_digits.add(lang_digits)
        results.append((lang_name, lang_time))

    
    if len(all_langs_digits) > 1:
        print(f"  WARNING: digit count mismatch between languages!")

    print_results(n,py_digits, results)


if __name__ == "__main__":
    main()