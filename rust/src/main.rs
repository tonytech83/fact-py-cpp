// rust/main.rs
//
// Usage:  factorial_bin <N>
//
// Prints two lines to stdout, matching the C++/Go binaries:
//   digits <number-of-digits-in-result>
//   time_us <microseconds-taken>

use num_bigint::BigUint;
use num_traits::One;
use std::env;
use std::process;
use std::time::Instant;

// Compute n! and return it as a decimal string (mirrors calc::compute).
fn compute(n: u64) -> String {
    let mut result = BigUint::one();
    for i in 2..=n {
        result *= BigUint::from(i);
    }
    result.to_str_radix(10) // decimal conversion inside the timed region, like get_str()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: {} <N>", args[0]);
        process::exit(1);
    }

    // u64::parse rejects negatives and garbage, so this covers the "N must be >= 0" case.
    let n: u64 = match args[1].parse() {
        Ok(v) => v,
        Err(_) => {
            eprintln!("N must be >= 0");
            process::exit(1);
        }
    };

    let t0 = Instant::now();
    let result = compute(n);
    let us = t0.elapsed().as_micros();

    println!("digits {}", result.len());
    println!("time_us {}", us);
}