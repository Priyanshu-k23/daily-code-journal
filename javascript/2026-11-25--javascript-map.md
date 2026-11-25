<!-- daily-code-journal: topic_id=javascript-map -->
# Transform arrays with map

**Date (IST):** 2026-11-25  
**Category:** JavaScript  
**Publishing method:** Automated from a curated, reviewed topic library.

## Explanation

`Array.prototype.map` returns a new array with one transformed result per input. It does not change the original array.

## Practical example

```javascript
const values = [1, 2, 3];
const doubled = values.map(value => value * 2);
console.log(doubled);
```

## Expected output or usage

```text
[ 2, 4, 6 ]
```

## Time and space complexity

Time: O(n); auxiliary space: O(n) for the new array.

## Key learning points

- Use map for one-to-one transformations.
- Avoid side effects in the mapping callback.

---

*Scheduled publication is automated; it does not imply live coding on this date.*
