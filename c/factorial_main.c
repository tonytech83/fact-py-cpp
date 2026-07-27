// factorial_main.c
//
// Usage:  factorial_bin <N>
//
// Prints two lines to stdout, matching the C++/Go/Rust binaries:
//   digits <number-of-digits-in-result>
//   time_us <microseconds-taken>
#define _POSIX_C_SOURCE 200809L

#include "c/factorial.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <N>\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);
    if (n < 0) {
        fprintf(stderr, "N must be >= 0\n");
        return 1;
    }

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    char *result = compute(n);
    clock_gettime(CLOCK_MONOTONIC, &t1);

    long long us = (t1.tv_sec - t0.tv_sec) * 1000000LL
                 + (t1.tv_nsec - t0.tv_nsec) / 1000;

    printf("digits %zu\n", strlen(result));
    printf("time_us %lld\n", us);

    free(result);   // GMP allocated this in mpz_get_str
    return 0;
}