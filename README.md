# Daily Code Journal

A structured collection of small, practical programming lessons, published automatically by GitHub Actions from a **curated, reviewed topic library**. Each entry includes an explanation, runnable or illustrative example, expected result or usage, relevant complexity, and takeaways.

**Transparency:** This repository uses automated publishing. A commit on a given day means the publishing workflow ran and added a pre-reviewed lesson; it does **not** claim the repository owner personally wrote code that day. No AI API, paid service, or generated filler is involved.

## How publishing works

- **Primary schedule:** 09:00 India Standard Time (03:30 UTC) every day; GitHub may delay or miss scheduled jobs.
- **Recovery check:** 12:17 IST (06:47 UTC) the same day. A successful primary publication prevents a second commit.
- **Manual trigger:** Actions → **Publish reviewed daily coding topic** → **Run workflow**.
- One unpublished entry is selected from the next category in the ten-category rotation. When a category is exhausted, the script uses the next category with an unused topic.
- Existing daily entries are immutable; `data/published.json` records published topic IDs and IST dates.
- When no new topic is available or the IST date was already published, no commit is made.

## Learning dashboard

<!-- DAILY_ENTRIES_START -->
**Published topics:** 3  
**Latest update (IST):** 2026-11-25  
**Reviewed library size:** 100  
**Remaining unpublished topics:** 97

## Categories

| Category | Published | Available in library |
| --- | ---: | ---: |
| Python Programming | 1 | 10 |
| Data Structures and Algorithms | 1 | 10 |
| JavaScript | 1 | 10 |
| SQL and Databases | 0 | 10 |
| Git and GitHub | 0 | 10 |
| Object-Oriented Programming | 0 | 10 |
| Backend Development | 0 | 10 |
| REST APIs | 0 | 10 |
| Software Engineering Practices | 0 | 10 |
| Interview Preparation | 0 | 10 |

## Published learning entries

| Date (IST) | Category | Topic |
| --- | --- | --- |
| 2026-11-25 | JavaScript | [Transform arrays with map](<javascript/2026-11-25--javascript-map.md>) |
| 2026-11-24 | Data Structures and Algorithms | [Binary search on sorted data](<dsa/2026-11-24--dsa-binary-search.md>) |
| 2026-11-22 | Python Programming | [List comprehensions with a filter](<python/2026-11-22--python-comprehensions.md>) |
<!-- DAILY_ENTRIES_END -->

## Bonus lessons

- 2026-11-25 (IST) · [Count duplicates in sorted data with Python's bisect](bonus/2026-11-25--python-bisect-count.md)

## Repository contents

- `.github/workflows/daily-commit.yml`: scheduled and manual GitHub Actions publisher.
- `scripts/daily_update.py`: validated, idempotent Python publisher; standard library only.
- `content/topics.json`: reviewed topic catalog; expandable without API calls.
- `data/published.json`: append-only publication ledger; **do not clear it**.
- `python/`, `dsa/`, `javascript/`, `sql/`, `git/`, `oop/`, `backend/`, `rest-api/`, `software-engineering/`, `interview/`: category directories containing dated Markdown notes created when published.
- `tests/`: offline tests for validation and idempotency.
- [`SETUP.md`](SETUP.md): full first-time GitHub setup, testing, and attribution checklist.

## Local commands (optional)

```bash
python scripts/daily_update.py --validate
python scripts/daily_update.py --dry-run
python -m unittest discover -s tests -v
```

Running `python scripts/daily_update.py` without a flag **writes a new entry** for the current IST date, if eligible. Only do so when you intend to publish or test in a disposable copy.

## Adding reviewed lessons

Add a new, unique object to `content/topics.json` with `id`, `category`, `title`, `explanation`, `code_language`, `code`, `expected_output`, `complexity`, and 2–6 `key_points`. Use a unique lowercase hyphenated ID and one of the ten category slugs. Validate examples and run `--validate` and tests before merging. Once published, keep that topic's ID, title, and category unchanged; add a new topic rather than repurposing an old one.

**Limits:** Scheduled runs can be delayed/dropped, Actions can be disabled, and branch rules may block writes. No automation can guarantee a green square every day. A GitHub profile square also depends on GitHub's contribution-counting rules.
