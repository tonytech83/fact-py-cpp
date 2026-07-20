// go/main.go
//
// Usage:  factorial_bin <N>
//
// Prints two lines to stdout, matching the C++ binary:
//   digits <number-of-digits-in-result>
//   time_us <microseconds-taken>

package main

import (
	"fmt"
	"math/big"
	"os"
	"strconv"
	"time"
)

// Compute n! and return it as a decimal string (mirrors calc::compute).
func compute(n int) string {
	result := big.NewInt(1)
	tmp := new(big.Int)
	for i := 2; i <= n; i++ {
		tmp.SetInt64(int64(i))
		result.Mul(result, tmp)
	}
	return result.String() // decimal conversion inside the timed region, like get_str()
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <N>\n", os.Args[0])
		os.Exit(1)
	}

	n, err := strconv.Atoi(os.Args[1])
	if err != nil || n < 0 {
		fmt.Fprintln(os.Stderr, "N must be >= 0")
		os.Exit(1)
	}

	t0 := time.Now()
	result := compute(n)
	us := time.Since(t0).Microseconds()

	fmt.Printf("digits %d\n", len(result))
	fmt.Printf("time_us %d\n", us)
}