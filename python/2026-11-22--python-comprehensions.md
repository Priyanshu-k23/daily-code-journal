<!-- daily-code-journal: topic_id=python-comprehensions -->
# List comprehensions with a filter

**Date (IST):** 2026-11-22  
**Category:** Python Programming  
**Publishing method:** Automated from a curated, reviewed topic library.

## Explanation

List comprehensions transform iterables into lists. Put the expression first and the optional filtering condition after the loop. They are concise for straightforward mappings.

## Practical example

```python
numbers = [1, 2, 3, 4, 5]
evens_squared = [n * n for n in numbers if n % 2 == 0]
print(evens_squared)
```

## Expected output or usage

```text
[4, 16]
```

## Time and space complexity

Time: O(n) for n input values; auxiliary space: O(k) for k retained values.

## Key learning points

- Use a comprehension for simple transformations.
- Prefer an explicit loop for complex branching.

---

*Scheduled publication is automated; it does not imply live coding on this date.*
