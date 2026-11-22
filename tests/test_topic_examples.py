"""Static and representative executable checks of the reviewed catalog."""
from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = json.loads((ROOT / 'content/topics.json').read_text(encoding='utf-8'))
BY_ID = {t['id']: t for t in TOPICS}


class ExampleTests(unittest.TestCase):
    def test_every_python_example_compiles(self):
        examples = [t for t in TOPICS if t['code_language'] == 'python']
        self.assertGreaterEqual(len(examples), 50)
        for t in examples:
            with self.subTest(topic=t['id']):
                compile(t['code'], f'{t["id"]}.py', 'exec')

    def test_representative_python_lessons_print_documented_output(self):
        for key in ('python-comprehensions', 'dsa-binary-search', 'oop-inheritance', 'backend-health-check', 'interview-anagram', 'software-engineering-guard-clauses'):
            t = BY_ID[key]
            with self.subTest(topic=key):
                p = subprocess.run([sys.executable, '-I', '-c', t['code']], text=True, capture_output=True, timeout=3, check=True)
                self.assertEqual(p.stdout.strip(), t['expected_output'].strip())

    def test_all_sql_examples_execute_and_return_expected_output(self):
        sql_examples = [t for t in TOPICS if t['code_language'] == 'sql']
        self.assertEqual(len(sql_examples), 10)
        for t in sql_examples:
            with self.subTest(topic=t['id']):
                with sqlite3.connect(':memory:') as con:
                    pieces = [p.strip() for p in t['code'].split(';') if p.strip()]
                    rows = []
                    for command in pieces:
                        rows = con.execute(command).fetchall()
                    actual = '\n'.join(' | '.join('NULL' if v is None else str(v) for v in row) for row in rows)
                    self.assertEqual(actual, t['expected_output'].strip())

    @unittest.skipUnless(shutil.which('node'), 'Node.js not installed; JavaScript check skipped')
    def test_all_javascript_examples_parse_and_run(self):
        examples = [t for t in TOPICS if t['code_language'] == 'javascript']
        self.assertEqual(len(examples), 10)
        for t in examples:
            with self.subTest(topic=t['id']):
                result = subprocess.run(['node', '-e', t['code']], text=True, capture_output=True, timeout=3, check=True)
                self.assertEqual(result.stdout.strip(), t['expected_output'].strip())

    def test_topic_categories_have_equal_distribution(self):
        counts = Counter(t['category'] for t in TOPICS)
        self.assertEqual(len(counts), 10)
        self.assertEqual(set(counts.values()), {10})


if __name__ == '__main__':
    unittest.main()
