# factorial — Python vs C++ vs Go vs Rust (Bazel 9)
Computes n! in Python, C++, Go and Rust and compares the time. Python orchestrates the benchmark.

### Requirements

- Linux / WSL
- GCC
- Bazel 9
- GMP library


### 1. Install Bazel
```sh
curl -L -o bazelisk https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64

sudo chmod +x bazelisk

sudo mv bazelisk /usr/local/bin/bazel
```

### 2. Install GMP
GMP is the GNU Multiple Precision library used by the C++ code.
```sh
sudo apt install libgmp-dev
```

### 3. Run the benchmark
```sh
# default: n = 20,000
bazel run //python:benchmark

# custom n
bazel run //python:benchmark -- --n 100000
bazel run //python:benchmark -- --n 500000
```
### Expected output
```sh
$ bazel run //python:benchmark -- --n 400000
INFO: Analyzed target //python:benchmark (0 packages loaded, 0 targets configured).
INFO: Found 1 target...
Target //python:benchmark up-to-date:
  bazel-bin/python/benchmark
INFO: Elapsed time: 0.365s, Critical Path: 0.00s
INFO: 1 process: 1 internal.
INFO: Build completed successfully, 1 total action
INFO: Running command line: bazel-bin/python/benchmark <args omitted>
[benchmark] Running Python factorial(400,000) ...
[benchmark] Running cpp factorial(400,000) ...
[benchmark] Running go factorial(400,000) ...
[benchmark] Running rust factorial(400,000) ...

  Factorial benchmark   n = 400,000
  Result has 2,067,110 digits

  Implementation     Time  Chart
  --------------  -------  ------------------------------
  Rust             38.20s  ██████░░░░░░░░░░░░░░░░░░░░░░░░
  C++              43.52s  ███████░░░░░░░░░░░░░░░░░░░░░░░
  Go               46.76s  ████████░░░░░░░░░░░░░░░░░░░░░░
  Python          3m 0.8s  ██████████████████████████████

  The winner is Rust with 38.198348s time.

  Rust is 1.1x faster than C++
  Rust is 1.2x faster than Go
  Rust is 4.7x faster than Python
```

> **Note:** the compiled binaries measure only the calculation time internally,
> so process-launch cost is not included. At small `n` the compiled languages
> and Python can look close because the math is trivial and timer resolution
> dominates. For large `n` the math dominates and C++/Go/Rust win clearly.

### Structure
```plain
.
├── BUILD.bazel
├── cpp
│   ├── BUILD.bazel
│   ├── factorial.cc
│   ├── factorial.h
│   └── factorial_main.cc
├── go
│   ├── BUILD.bazel
│   └── main.go
├── MODULE.bazel
├── MODULE.bazel.lock
├── python
│   ├── benchmark.py
│   └── BUILD.bazel
├── README.md
└── rust
    ├── BUILD.bazel
    ├── Cargo.toml
    └── src
        └── main.rs
```

### Why C++/Go/Rust wins
The difference is Python runs through an interpreter — every *= i has
overhead for bytecode dispatch, object allocation, and reference counting.
C++/Go/Rust compile to machine code and use tuned bignum libraries
(GMP, math/big, num-bigint). Optimized builds matter: the repo's `.bazelrc`
sets `--compilation_mode=opt` so Rust's dependencies are optimized too.
