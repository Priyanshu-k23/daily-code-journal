# Count duplicates in sorted data with Python's bisect

Published November 25, 2026 (IST) as a bonus lesson.

A binary search can locate a match, but you need both boundaries to count every occurrence without scanning the matching items. In Python, `bisect_left` finds the first index whose value is at least the target. `bisect_right` finds the first index whose value is greater. The difference is the count. If the target is absent, both functions return the same insertion point.

```python
from bisect import bisect_left, bisect_right

scores = [50, 70, 70, 70, 90]
start = bisect_left(scores, 70)
stop = bisect_right(scores, 70)
count = stop - start
print(count)
assert count == 3
assert bisect_right(scores, 80) - bisect_left(scores, 80) == 0
```

The example prints `3`. A target of `80` has a count of zero because its left and right insertion points are both index `4`.

For an already sorted list, the two searches together take **O(log n)** time and **O(1)** extra space. Use the index difference directly when you only need a count. Slicing `scores[start:stop]` would copy the matching elements.
