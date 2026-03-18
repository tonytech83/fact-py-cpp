#include "cpp/factorial.h"
#include <gmpxx.h>

namespace calc {

// We store the big number as a vector of digits in base 10000.
// Each element holds a value 0..9999.
// digits[0] is the least significant chunk.
std::string compute(int n) {
    mpz_class result = 1;
    for (int i = 2; i <= n; i++)
        result *= i;
    return result.get_str();
}

} // namespace calc
