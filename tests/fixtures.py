"""Create the initial publication state in an isolated test checkout."""
from pathlib import Path


def initialize_empty_journal(root: Path) -> None:
    data = root / 'data'
    data.mkdir()
    (data / 'published.json').write_text(
        '{"schema_version": 1, "entries": []}\n', encoding='utf-8'
    )
    (root / 'README.md').write_text(
        '# Daily Code Journal\n\n<!-- DAILY_ENTRIES_START -->\n<!-- DAILY_ENTRIES_END -->\n',
        encoding='utf-8',
    )
