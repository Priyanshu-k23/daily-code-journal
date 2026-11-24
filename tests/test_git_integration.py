"""End-to-end commit and push in isolated local bare Git repository."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.fixtures import initialize_empty_journal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from daily_update import run
from datetime import date

SOURCE = Path(__file__).resolve().parents[1]


class GitIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('git'), 'Git is not installed')
    def test_publish_commit_push_author_attribution_and_same_day_noop(self):
        def command(*args, cwd=None):
            return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()

        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary)
            bare, checkout = p / 'remote.git', p / 'work'
            command('git', 'init', '--bare', str(bare))
            command('git', 'clone', str(bare), str(checkout))
            for name in ('.gitignore', 'SETUP.md'):
                shutil.copy2(SOURCE / name, checkout / name)
            for d in ('content', 'scripts', 'tests', '.github'):
                shutil.copytree(SOURCE / d, checkout / d)
            initialize_empty_journal(checkout)
            command('git', 'checkout', '-b', 'main', cwd=checkout)
            command('git', 'config', 'user.name', 'Priyanshu-k23', cwd=checkout)
            command('git', 'config', 'user.email', '221792233+Priyanshu-k23@users.noreply.github.com', cwd=checkout)
            command('git', 'add', '-A', cwd=checkout)
            command('git', 'commit', '-m', 'chore: initialize reviewed code journal', cwd=checkout)
            command('git', 'push', '-u', 'origin', 'main', cwd=checkout)
            initial = command('git', 'rev-parse', 'HEAD', cwd=checkout)

            result = run(checkout, date(2026, 11, 22))
            self.assertTrue(result.changed)
            command('git', 'add', '--', 'README.md', 'data/published.json', result.path, cwd=checkout)
            actual = set(command('git', 'diff', '--cached', '--name-only', cwd=checkout).splitlines())
            self.assertEqual(actual, {'README.md', 'data/published.json', result.path})
            command('git', 'commit', '-m', 'docs: publish reviewed learning topic on 2026-11-22 IST [automated]', cwd=checkout)
            command('git', 'push', 'origin', 'HEAD:refs/heads/main', cwd=checkout)
            final = command('git', 'rev-parse', 'HEAD', cwd=checkout)
            self.assertNotEqual(initial, final)
            identity = command('git', 'log', '-1', '--format=%an <%ae> | %cn <%ce>', cwd=checkout)
            self.assertEqual(identity, 'Priyanshu-k23 <221792233+Priyanshu-k23@users.noreply.github.com> | Priyanshu-k23 <221792233+Priyanshu-k23@users.noreply.github.com>')
            pushed = command('git', 'ls-remote', bare.as_posix(), 'refs/heads/main').split()[0]
            self.assertEqual(pushed, final)
            again = run(checkout, date(2026, 11, 22))
            self.assertFalse(again.changed)
            self.assertEqual(command('git', 'status', '--porcelain', cwd=checkout), '')
            self.assertEqual(command('git', 'rev-parse', 'HEAD', cwd=checkout), final)


if __name__ == '__main__':
    unittest.main()
