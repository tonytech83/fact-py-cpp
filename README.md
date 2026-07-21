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
```plain
[benchmark] n = 500,000
[benchmark] C++ binary: /home/tonytech/github/bazel-factorial/bazel-bin/cpp/factorial_bin
[benchmark] Go binary: /home/tonytech/github/bazel-factorial/bazel-bin/go/factorial_bin
[benchmark] Rust binary: /home/tonytech/github/bazel-factorial/bazel-bin/rust/factorial_bin
[benchmark] Running Python factorial(500,000) ...
[benchmark] Running C++ factorial(500,000) ...
[benchmark] Running Go factorial(500,000) ...
[benchmark] Running Rust factorial(500,000) ...

  Factorial benchmark   n = 500,000
  Result has 2,632,342 digits

  Implementation      Time  Chart
  --------------  --------  ------------------------------
  Python          1m 53.8s  ██████████████████████████████
  C++               29.03s  ████████░░░░░░░░░░░░░░░░░░░░░░
  Go                56.54s  ███████████████░░░░░░░░░░░░░░░
  Rust              27.75s  ███████░░░░░░░░░░░░░░░░░░░░░░░

  C++ is 3.9x faster than Python
  Go is 2.0x faster than Python
  Rust is 4.1x faster than Python
  C++ is 1.9x faster than Go
  Rust is 1.0x faster than C++
  Rust is 2.0x faster than Go
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
