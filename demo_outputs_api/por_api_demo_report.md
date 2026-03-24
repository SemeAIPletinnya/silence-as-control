# PoR API Demo Report

- Model: **gpt-4o-mini**
- Threshold: **0.39**
- Proceeded: **6**
- Silenced: **0**

## Results

### Task #1
**Prompt:** Fix bug: division function should handle division by zero safely.
**Decision:** proceed
**Drift:** 0.180
**Note:** Division task includes explicit zero-check / safe handling.

**Output:**

```text
```python
def safe_division(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b
```
```

### Task #2
**Prompt:** Write a Python function that returns the square of a number.
**Decision:** proceed
**Drift:** 0.150
**Note:** Square function is direct and aligned.

**Output:**

```text
```python
def square(number):
    return number ** 2
```
```

### Task #3
**Prompt:** Fix recursive factorial bug.
**Decision:** proceed
**Drift:** 0.200
**Note:** Factorial task includes a visible base case.

**Output:**

```text
Here’s the corrected code for a recursive factorial function:

```python
def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)
```
```

### Task #4
**Prompt:** Write a Python function that handles division safely with zero check.
**Decision:** proceed
**Drift:** 0.180
**Note:** Division task includes explicit zero-check / safe handling.

**Output:**

```text
```python
def safe_divide(numerator, denominator):
    if denominator == 0:
        return "Error: Division by zero"
    return numerator / denominator
```
```

### Task #5
**Prompt:** Write a Python function that checks whether a string is a palindrome.
**Decision:** proceed
**Drift:** 0.190
**Note:** Palindrome logic is explicitly visible.

**Output:**

```text
```python
def is_palindrome(s):
    return s == s[::-1]
```
```

### Task #6
**Prompt:** Fix bug: loop should sum all items, not only the last one.
**Decision:** proceed
**Drift:** 0.210
**Note:** Accumulation logic is visible.

**Output:**

```text
```python
total = 0
for item in items:
    total += item
```
```

## Interpretation

- This demo shows PoR as a runtime gate over real LLM outputs.
- The same API call can either be emitted or silenced depending on task-output alignment.
- This is an integration artifact, not the final scientific drift implementation.
