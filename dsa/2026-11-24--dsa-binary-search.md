<!-- daily-code-journal: topic_id=dsa-binary-search -->
# Binary search on sorted data

**Date (IST):** 2026-11-24  
**Category:** Data Structures and Algorithms  
**Publishing method:** Automated from a curated, reviewed topic library.

## Explanation

Binary search repeatedly halves a sorted search interval. It returns an index if the target is present, otherwise `-1`. The sorted-input precondition is essential.

## Practical example

```python
def binary_search(values, target):
    left, right = 0, len(values) - 1
    while left <= right:
        middle = (left + right) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    return -1

print(binary_search([2, 4, 7, 11], 7))
```

## Expected output or usage

```text
2
```

## Time and space complexity

Time: O(log n); auxiliary space: O(1).

## Key learning points

- Binary search requires a sorted sequence.
- Move one boundary after every unsuccessful comparison.

---

*Scheduled publication is automated; it does not imply live coding on this date.*
