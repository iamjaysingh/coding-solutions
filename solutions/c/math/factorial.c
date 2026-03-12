/*
 * Factorial
 * Calculate factorial of a number using recursion and iteration
 * Category: math | Difficulty: Easy
 * Date: 2026-03-12 | Author: Jay Singh
 */

#include <stdio.h>
#include <stdlib.h>

// Time: O(n), Space: O(1)
long long factorial_recursive(int n) {
    if (n <= 1) return 1;
    return n * factorial_recursive(n - 1);
}

long long factorial_iterative(int n) {
    long long result = 1;
    for (int i = 2; i <= n; i++) result *= i;
    return result;
}

int main() {
    int nums[] = {0, 1, 5, 10, 15, 20};
    for (int i = 0; i < 6; i++) {
        printf("%d! = %lld (recursive)\n", nums[i], factorial_recursive(nums[i]));
        printf("%d! = %lld (iterative)\n", nums[i], factorial_iterative(nums[i]));
    }
    return 0;
}
