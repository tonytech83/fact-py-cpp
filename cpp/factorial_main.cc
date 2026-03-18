// factorial_main.cc
//
// Usage:  factorial_bin <N>
//
// Prints two lines to stdout:
//   digits <number-of-digits-in-result>
//   time_us <microseconds-taken>
//
// Python reads these two lines and uses them for the benchmark table.
// (We print digit-count, not the full number — printing millions of digits
//  would itself take longer than the calculation!)

#include "cpp/factorial.h"

#include <chrono>
#include <cstdlib>
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <N>\n";
        return 1;
    }

    int n = std::atoi(argv[1]);
    if (n < 0) {
        std::cerr << "N must be >= 0\n";
        return 1;
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    std::string result = calc::compute(n);
    auto t1 = std::chrono::high_resolution_clock::now();

    long long us = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count();

    std::cout << "digits "   << result.size() << "\n";
    std::cout << "time_us "  << us            << "\n";
    return 0;
}
