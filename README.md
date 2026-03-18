# factorial — Python vs C++ benchmark (Bazel 9 + GMP)
Computes n! in both Python and C++ and compares the time.
Python orchestrates the benchmark. C++ does the calculation using the GMP
big-integer library.

### Requirements

- Linux / WSL
- GCC
- Bazel 9
- GMP library


### 1. Install Bazel
The easiest way is via Bazelisk — a small tool that downloads the correct
Bazel version automatically.
bashsudo apt install npm
sudo npm install -g @bazel/bazelisk
Check it works:
bashbazel version

### 2. Install GMP
GMP is the GNU Multiple Precision library used by the C++ code.
bashsudo apt install libgmp-dev

### 3. Run the benchmark
```sh
# default: n = 20,000
bazel run //python:benchmark

# custom n
bazel run //python:benchmark -- --n 100000
bazel run //python:benchmark -- --n 500000
```
### Expected output
```plain
[benchmark] n = 20,000
[benchmark] C++ binary: .../bazel-bin/cpp/factorial_bin
[benchmark] Running Python factorial(20,000) ...
[benchmark] Running C++ factorial(20,000) ...

  Factorial benchmark   n = 20,000
  Result has 77,338 digits

  Implementation    Time  Chart
  --------------  ------  ------------------------------
  Python          106ms   ██████████████████████████████
  C++              44ms   █████████████░░░░░░░░░░░░░░░░░

  C++ is 2.4x faster than pure Python
```
The larger n is, the bigger the gap — try --n 500000 to really see C++ pull ahead.

> [!tip] Note
> For small values of `n` (roughly n < 500), Python may appear faster.
> This is not because Python arithmetic is faster — it is because the C++ binary
> runs as a separate process, and launching that process costs ~20µs regardless
> of how fast the math is. For large `n` the math dominates and C++ wins clearly.

### Structure
```plain
factorial/
├── MODULE.bazel              # Bazel 9 module (rules_cc, rules_python)
├── cpp/
│   ├── BUILD.bazel           # cc_library + cc_binary
│   ├── factorial.h           # declares calc::compute(n)
│   ├── factorial.cc          # GMP implementation
│   └── factorial_main.cc     # CLI: takes N, prints digits + time
└── python/
    ├── BUILD.bazel           # py_binary
    └── benchmark.py          # times both, prints comparison table
```

### Why C++ wins
Both Python and C++ use GMP internally for big-integer multiplication.
The difference is Python runs through an interpreter — every *= i has
overhead for bytecode dispatch, object allocation, and reference counting.
C++ compiles directly to machine code with none of that overhead.
The larger n gets, the more loop iterations there are, and the more
that interpreter overhead adds up.