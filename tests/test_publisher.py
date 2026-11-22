"""Publisher invariants, using only temporary disposable repositories."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from daily_update import JournalError, read_topics, read_manifest, run, render_entry, CATEGORIES  # noqa: E402

SOURCE = Path(__file__).resolve().parents[1]
DAY = date(2026, 11, 22)


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('README.md', 'content/topics.json', 'data/published.json'):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / name, dest)
        for slug, _ in CATEGORIES:
            (self.root / slug).mkdir()

    def manifest(self):
        return json.loads((self.root / 'data/published.json').read_text(encoding='utf-8'))

    def topics(self):
        return json.loads((self.root / 'content/topics.json').read_text(encoding='utf-8'))

    def save_topics(self, topics):
        (self.root / 'content/topics.json').write_text(json.dumps(topics, indent=2) + '\n', encoding='utf-8')

    def test_catalog_has_ten_categories_and_one_hundred_unique_lessons(self):
        topics = read_topics(self.root)
        self.assertEqual(len(topics), 100)
        self.assertEqual(len({t['id'] for t in topics}), 100)
        self.assertTrue(all(sum(t['category'] == slug for t in topics) == 10 for slug, _ in CATEGORIES))

    def test_validation_does_not_modify_any_files(self):
        before = (self.root / 'README.md').read_bytes()
        r = run(self.root, DAY, validate_only=True)
        self.assertFalse(r.changed)
        self.assertEqual((self.root / 'README.md').read_bytes(), before)
        self.assertEqual(self.manifest()['entries'], [])

    def test_dry_run_is_read_only(self):
        before = (self.root / 'data/published.json').read_bytes()
        r = run(self.root, DAY, dry_run=True)
        self.assertFalse(r.changed)
        self.assertTrue(r.topic_id)
        self.assertFalse((self.root / r.path).exists())
        self.assertEqual((self.root / 'data/published.json').read_bytes(), before)

    def test_one_publish_updates_entry_manifest_and_readme(self):
        r = run(self.root, DAY)
        self.assertTrue(r.changed)
        self.assertEqual(r.topic_id, 'python-comprehensions')
        self.assertTrue((self.root / r.path).is_file())
        m = self.manifest()['entries']
        self.assertEqual(len(m), 1)
        self.assertEqual(m[0]['path'], r.path)
        index = (self.root / 'README.md').read_text(encoding='utf-8')
        self.assertIn('**Published topics:** 1', index)
        self.assertIn('**Remaining unpublished topics:** 99', index)
        self.assertIn(f'[{m[0]["title"]}](<{r.path}>)', index)

    def test_one_publication_per_ist_day_and_no_content_changes_on_second_run(self):
        r1 = run(self.root, DAY)
        manifest = (self.root / 'data/published.json').read_bytes()
        readme = (self.root / 'README.md').read_bytes()
        note = (self.root / r1.path).read_bytes()
        r2 = run(self.root, DAY)
        self.assertFalse(r2.changed)
        self.assertEqual((self.root / 'data/published.json').read_bytes(), manifest)
        self.assertEqual((self.root / 'README.md').read_bytes(), readme)
        self.assertEqual((self.root / r1.path).read_bytes(), note)

    def test_category_rotates_across_successive_days(self):
        found = []
        for i in range(11):
            result = run(self.root, DAY + timedelta(days=i))
            found.append(self.manifest()['entries'][-1]['category'])
            self.assertTrue(result.changed)
        self.assertEqual(found[:10], [slug for slug, _ in CATEGORIES])
        self.assertEqual(found[10], 'python')

    def test_catalog_duplicate_id_is_rejected(self):
        x = self.topics()
        x[1]['id'] = x[0]['id']
        self.save_topics(x)
        with self.assertRaisesRegex(JournalError, 'Duplicate topic ID'):
            run(self.root, DAY, validate_only=True)

    def test_unknown_category_is_rejected(self):
        x = self.topics()
        x[0]['category'] = 'hacking'
        self.save_topics(x)
        with self.assertRaisesRegex(JournalError, 'unknown category'):
            run(self.root, DAY, validate_only=True)

    def test_missing_required_field_is_rejected(self):
        x = self.topics()
        del x[0]['expected_output']
        self.save_topics(x)
        with self.assertRaisesRegex(JournalError, 'expected_output'):
            run(self.root, DAY, validate_only=True)

    def test_existing_path_must_not_be_overwritten(self):
        path = self.root / 'python/2026-11-22--python-comprehensions.md'
        path.write_text('Important unrelated work\n', encoding='utf-8')
        with self.assertRaisesRegex(JournalError, 'Refusing to overwrite'):
            run(self.root, DAY)
        self.assertEqual(path.read_text(encoding='utf-8'), 'Important unrelated work\n')

    def test_published_files_cannot_disappear(self):
        r = run(self.root, DAY)
        (self.root / r.path).unlink()
        with self.assertRaisesRegex(JournalError, 'Published entry missing'):
            run(self.root, DAY, validate_only=True)

    def test_cannot_reset_manifest_without_detecting_existing_notes(self):
        run(self.root, DAY)
        (self.root / 'data/published.json').write_text('{"schema_version":1,"entries":[]}\n', encoding='utf-8')
        with self.assertRaisesRegex(JournalError, 'Manifest/file mismatch'):
            run(self.root, DAY + timedelta(days=1))

    def test_published_topic_removal_is_rejected(self):
        run(self.root, DAY)
        self.save_topics(self.topics()[1:])
        with self.assertRaisesRegex(JournalError, 'removed from library'):
            run(self.root, DAY + timedelta(days=1), validate_only=True)

    def test_backward_publication_date_is_rejected(self):
        run(self.root, DAY)
        with self.assertRaisesRegex(JournalError, 'refusing to backdate'):
            run(self.root, DAY - timedelta(days=1))

    def test_exhausted_content_creates_no_new_publication(self):
        x = self.topics()
        self.save_topics([x[0]])
        self.assertTrue(run(self.root, DAY).changed)
        result = run(self.root, DAY + timedelta(days=1))
        self.assertFalse(result.changed)
        self.assertIn('exhausted', result.reason)
        self.assertEqual(len(self.manifest()['entries']), 1)

    def test_missing_readme_markers_fails(self):
        (self.root / 'README.md').write_text('# No generated section\n', encoding='utf-8')
        with self.assertRaisesRegex(JournalError, 'README.md needs exactly one'):
            run(self.root, DAY)

    def test_topic_markdown_discloses_automated_publication(self):
        topic = read_topics(self.root)[0]
        md = render_entry(topic, DAY)
        for phrase in ('automated', '## Explanation', '## Practical example', '## Expected output', '## Time and space complexity', '## Key learning points'):
            self.assertIn(phrase, md)


if __name__ == '__main__':
    unittest.main()
