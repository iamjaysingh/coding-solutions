#!/usr/bin/env python3
"""
Fibonacci Series
Generate Fibonacci sequence using different approaches
Category: math | Difficulty: Easy
Date: 2026-03-13 | Author: Jay Singh
"""

def fibonacci_iterative(n):
    """Generate first n Fibonacci numbers. Time: O(n), Space: O(1)"""
    if n <= 0: return []
    if n == 1: return [0]
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return fib

def fibonacci_recursive(n):
    """Get nth Fibonacci number. Time: O(2^n)"""
    if n <= 0: return 0
    if n == 1: return 1
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

if __name__ == "__main__":
    print("First 15 Fibonacci numbers:")
    print(fibonacci_iterative(15))
    print("\nUsing recursion:")
    for i in range(10):
        print(f"F({i}) = {fibonacci_recursive(i)}")
