# Filter missing values with SQL IS NULL

Published November 26, 2026 (IST) as a bonus lesson.

Suppose a reading tracker stores a completion date for finished books and `NULL` for books without a recorded completion date. Use `IS NULL` to find the books with missing dates.

| name | finished_at |
| --- | --- |
| Databases | NULL |
| Algorithms | 2026-11-26 |

```sql
SELECT name
FROM books
WHERE finished_at IS NULL
ORDER BY name;
```

The query returns one row, `Databases`. Replacing `IS NULL` with `= NULL` returns zero rows. An equality comparison with `NULL` evaluates to unknown, and `WHERE` keeps only rows for which the condition is true.

Use `IS NOT NULL` to find rows with a recorded date. An empty string is a separate value in SQLite, so a row containing an empty string also passes `IS NOT NULL`.
