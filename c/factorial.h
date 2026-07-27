#pragma once

// Compute n! and return it as a newly-allocated decimal string.
// The caller owns the returned pointer and must free() it.
char *compute(int n);