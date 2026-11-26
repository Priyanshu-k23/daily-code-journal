# Count missing values with SQL COUNT

Published November 26, 2026 (IST) as a bonus lesson.

`COUNT(*)` counts every row. `COUNT(column)` counts only rows where that column has a non-NULL value. Subtract them to count rows with a missing value in that column. This follows the [lesson on filtering with IS NULL](2026-11-26--sql-filter-null.md).

```sql
CREATE TABLE books (title TEXT NOT NULL, finished_at TEXT);
INSERT INTO books VALUES ('Databases', NULL), ('Algorithms', '2026-11-26');
SELECT COUNT(*) AS total, COUNT(finished_at) AS finished,
       COUNT(*) - COUNT(finished_at) AS missing_date
FROM books;
```

The result is `(2, 1, 1)`. There are two books, one recorded completion date, and one missing completion date. The same rule applies to each group when you use `GROUP BY`. An empty string is counted by `COUNT(column)` because it is a value in SQLite.
