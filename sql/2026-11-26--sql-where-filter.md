<!-- daily-code-journal: topic_id=sql-where-filter -->
# Filter database rows with WHERE

**Date (IST):** 2026-11-26  
**Category:** SQL and Databases  
**Publishing method:** Automated from a curated, reviewed topic library.

## Explanation

Use `WHERE` to restrict rows before selecting the final result. Text values are written in single quotes. In application code, bind untrusted values as parameters.

## Practical example

```sql
CREATE TABLE products (name TEXT, price INTEGER);
INSERT INTO products VALUES ('Pen', 10), ('Book', 80);
SELECT name FROM products WHERE price >= 50;
```

## Expected output or usage

```text
Book
```

## Time and space complexity

Query cost: O(n) without an index; result space depends on matching rows.

## Key learning points

- WHERE filters individual rows.
- Use bound parameters for user-supplied values.

---

*Scheduled publication is automated; it does not imply live coding on this date.*
