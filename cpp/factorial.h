#pragma once
#include <string>

namespace calc {

// Compute n! and return it as a decimal string.
// Uses a simple loop with a big-integer accumulator (vector of digits).
std::string compute(int n);

} // namespace calc
