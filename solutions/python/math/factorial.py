#!/usr/bin/env python3
"""
Factorial
Calculate factorial of a number using recursion and iteration
Category: math | Difficulty: Easy
Date: 2026-03-07 | Author: Jay Singh
"""

def factorial_recursive(n):
    """Calculate factorial using recursion. Time: O(n), Space: O(n)"""
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

def factorial_iterative(n):
    """Calculate factorial using iteration. Time: O(n), Space: O(1)"""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    for num in [0, 1, 5, 10, 15]:
        print(f"{num}! = {factorial_recursive(num)} (recursive)")
        print(f"{num}! = {factorial_iterative(num)} (iterative)")
