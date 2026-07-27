#include "c/factorial.h"

#include <gmp.h>

// Compute n! with a big-integer accumulator (mirrors the C++ mpz_class version).
// The decimal conversion (mpz_get_str) is done here, inside what main() times,
// to match the C++ binary which converts via get_str() in the timed region.
char *compute(int n) {
    mpz_t result;
    mpz_init_set_ui(result, 1);          // result = 1

    for (int i = 2; i <= n; i++)
        mpz_mul_ui(result, result, i);   // result *= i  (multiply by unsigned int)

    // Passing NULL makes GMP allocate the string; caller must free() it.
    char *str = mpz_get_str(NULL, 10, result);

    mpz_clear(result);
    return str;
}