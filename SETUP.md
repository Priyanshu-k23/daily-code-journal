# Setup guide: Daily Code Journal

This is a one-time setup. After the first upload and successful workflow run, the repository publishes automatically on GitHub-hosted runners. You do **not** need to leave your laptop on.

## 1. GitHub identity already configured

The workflow currently uses the connected account:

| Setting | Configured value |
| --- | --- |
| GitHub username / commit author name | `Priyanshu-k23` |
| GitHub numeric user ID | `221792233` |
| Default commit email | `221792233+Priyanshu-k23@users.noreply.github.com` |
| Repository name used in this guide | `daily-code-journal` |
| Default branch | `main` |

The email follows GitHub's ID-based private email format. **Confirm it** at [GitHub email settings](https://github.com/settings/emails) under the private/noreply address displayed by GitHub. If GitHub shows a different email for you, follow section 4 and set the exact address as a repository variable. Do not use a made-up email, and do not expose your personal email unless you choose to.

The workflow sets both `user.name` and `user.email` locally before `git commit`. That metadata becomes both **author** and **committer**. The token authenticates the *push* as GitHub Actions; it does not rewrite your selected Git author identity. This is explicitly disclosed automation, not a claim of daily manual coding.

## 2. Create an empty, standalone GitHub repository

1. Sign in as `Priyanshu-k23` at [github.com/new](https://github.com/new).
2. Owner: **Priyanshu-k23**.
3. Repository name: **daily-code-journal**.
4. Choose **Public** for visibly public work. A private standalone repository can also count, but viewers may see only aggregate private contributions if you enable the private contribution display preference.
5. **Do not** initialize with a README, `.gitignore`, or license. The provided ZIP already contains the repository files.
6. Click **Create repository**. Keep this empty-repository page open.

Do not use a fork; fork commits ordinarily do not qualify for the personal contribution graph until merged upstream.

## 3. Upload the complete project ONCE

### Recommended: Git command line (Windows / macOS / Linux)

Install Git from [git-scm.com](https://git-scm.com/downloads) if needed. Extract `daily-code-journal.zip` and open a terminal **inside the extracted `daily-code-journal` folder** (the one containing `README.md`). Run these commands in order:

```bash
git init -b main
git config user.name "Priyanshu-k23"
git config user.email "221792233+Priyanshu-k23@users.noreply.github.com"
git add -A
git commit -m "chore: initialize reviewed daily code journal automation"
git remote add origin https://github.com/Priyanshu-k23/daily-code-journal.git
git push -u origin main
```

GitHub may open a secure browser sign-in window for the one-time push. Follow it; **do not put a personal access token or password into files**. An empty new repository is important so this first push does not conflict with an existing remote README. The bootstrap commit is a genuine setup commit, not a generated coding lesson.

**After upload, check the actual files on GitHub:**

- `.github/workflows/daily-commit.yml`
- `scripts/daily_update.py`
- `content/topics.json`
- `data/published.json`
- `README.md`, `SETUP.md`
- `tests/test_publisher.py`, `tests/test_topic_examples.py`, `tests/test_git_integration.py`

Git tracks hidden directories like `.github` when you run `git add -A`.

### Alternative: browser-only upload

Create the empty repository, then choose **uploading an existing file** on GitHub. Extract the ZIP first and upload **the contents of** the extracted folder, preserving `.github/workflows/` and the other folders. Some browsers do not preserve folder paths or hidden directories when uploading. If you cannot see `.github/workflows/daily-commit.yml` on GitHub afterward, use the Git method above or create the workflow manually in GitHub's web editor at that exact path. Do not upload the ZIP as one file: GitHub Actions cannot execute code inside a ZIP.

## 4. Check the Git author email and optional variables

The default author and email are already filled into `.github/workflows/daily-commit.yml`, so **no extra configuration is required** if the noreply address above matches your account's GitHub email settings.

To override either value **without editing the workflow**:

1. Open your repository → **Settings** → **Secrets and variables** → **Actions** → **Variables** tab.
2. Add `COMMIT_NAME` with the exact value `Priyanshu-k23` if you need an override.
3. Add `COMMIT_EMAIL` with the exact GitHub-provided noreply address shown in your GitHub email settings (or another email verified and associated with this GitHub account).
4. Do not use a *Secret* for the Git author email unless it actually needs to be secret: commit email metadata is stored in public Git history. Use the noreply address for privacy.

If your username changes later, update the commit name. The ID-based noreply email remains the more stable attribution format.

## 5. Enable Actions and allow the workflow to write

1. Go to the repository → **Settings** → **Actions** → **General**.
2. Under **Actions permissions**, allow the repository to run GitHub Actions and standard GitHub-maintained actions (`actions/checkout` and `actions/setup-python`).
3. Under **Workflow permissions**, select **Read and write permissions** and save if necessary to allow a `GITHUB_TOKEN` push. The workflow gives its test job only `contents: read` and its publishing job only `contents: write`; it does **not** request broad API permissions.
4. Leave **Allow GitHub Actions to create and approve pull requests** unchecked; this solution pushes directly to `main` and does not need that permission.
5. Do not set a branch protection rule that forbids GitHub Actions from pushing directly to `main`. If your repository or organization enforces protected branches, the direct-push approach will be blocked, and you will need a reviewed-PR publishing workflow instead.

No personal access token (PAT), paid AI provider, hosting, database, or extra Python package is necessary.

## 6. Test safely, then publish one entry

You may inspect the next topic on a computer with Python 3.11+ without modifying files:

```bash
python scripts/daily_update.py --validate
python scripts/daily_update.py --dry-run
python -m unittest discover -s tests -v
```

The real test is to run the **GitHub** workflow:

1. In the repository, choose the **Actions** tab.
2. Open **Publish reviewed daily coding topic** in the left sidebar.
3. Click **Run workflow**, select `main`, and click the green **Run workflow** button.
4. Open the new workflow run and check its `validate` and `publish` jobs.
5. Confirm that the `validate` job passed all offline tests and that the `publish` job successfully completed **Publish and safely push one topic**.
6. Open **Code** and check for an added Markdown entry in `python/` (first topic), an updated `data/published.json`, and an updated README topic table.
7. Open the newest commit. Its message should honestly mention the reviewed automated lesson and the **author should be `Priyanshu-k23`**, with the private noreply email configured in section 4.

The first run creates one new topic **only if no topic has already been published on that IST calendar date**. Re-running the same workflow that day is a legitimate no-op with no empty commit. The next scheduled publication on a new day proceeds to DSA, then JavaScript, and so on.

## 7. Daily schedule and missed-run behavior

| UTC cron | Local time (IST, UTC+05:30) | Purpose |
| --- | --- | --- |
| `30 3 * * *` | 09:00 every day | Primary publication attempt |
| `47 6 * * *` | 12:17 every day | Backup attempt if the first was delayed or dropped |

The script uses the *actual current IST calendar date* when deciding whether a note can be published. It never rewrites Git commit dates or creates retroactive contributions. GitHub may delay or drop a scheduled event. If both attempts fail, that day might be missed; launch `workflow_dispatch` manually that day if you notice. The next successful day **does not pretend a historical publication happened**. In public repositories, inactivity may disable scheduled workflows after 60 days, especially after the reviewed catalog is exhausted.

The GitHub workflow uses serialized concurrency and up to three push attempts. When a push is rejected, it fetches the latest default branch and regenerates only if today's entry remains unpublished. Any persistent permission or protected-branch error produces a visible failing workflow rather than a false success.

## 8. Confirm GitHub contribution attribution

After the workflow successfully pushes a commit:

1. Open the commit from `https://github.com/Priyanshu-k23/daily-code-journal/commits/main`.
2. Confirm the **author profile link** points to `Priyanshu-k23` (not `github-actions[bot]`). The **pusher/Actions actor** can still be the bot; GitHub's attribution is based on the commit identity and other eligibility conditions.
3. Open the commit `.patch` view to inspect the `From:` address if you suspect an email mismatch.
4. Open [your GitHub profile](https://github.com/Priyanshu-k23), navigate to your contribution calendar, and check the appropriate date. GitHub's display can take time to update.
5. If a commit is absent, confirm **all** of these: associated author email, standalone/non-fork repository, commit on `main` (the default branch), and repository membership/collaborator requirements. For a private repository, enable **Include private contributions on my profile** if you want the aggregate private activity visible.

Official GitHub guide: [Troubleshooting missing contributions](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions).

**Important:** No setup can guarantee 365 green squares. A scheduled workflow may be late, skipped, disabled, out of topics, or prevented from pushing; GitHub also controls attribution. The repo is intentionally transparent that reviewed lessons were published automatically.

## 9. Add topics when the catalog approaches exhaustion

The starter library contains **100 reviewed lessons**: ten in each category. At a rate of one per successful IST day, it supports up to 100 topic publications; it is deliberately finite so the system never invents or duplicates content. The README shows the remaining count.

Edit `content/topics.json` in a JSON-capable editor. New entries must have this shape (example of a *new topic format*, not a new required configuration setting):

```json
{
  "id": "python-iter-tools",
  "category": "python",
  "title": "Iterate with itertools",
  "explanation": "Explain when and why to use an iterator tool.",
  "code_language": "python",
  "code": "from itertools import chain\nprint(list(chain([1, 2], [3])))",
  "expected_output": "[1, 2, 3]",
  "complexity": "Time: O(n); auxiliary space: O(n) for the materialized list.",
  "key_points": [
    "chain combines iterables lazily.",
    "list(...) materializes the output."
  ]
}
```

Use a **never-before-used** `id` consisting of lowercase letters, digits, and hyphens. Use `python`, `dsa`, `javascript`, `sql`, `git`, `oop`, `backend`, `rest-api`, `software-engineering`, or `interview` as `category`. Review and execute examples as appropriate. Do not alter or delete previously published topics or reset `data/published.json`. Commit the catalog changes to the default branch. The publisher will resume whenever unused reviewed content is available.

## 10. Troubleshooting quick reference

| Symptom | Likely cause / what to check |
| --- | --- |
| `403` or `Write access ... not granted` | Settings → Actions → General → Workflow permissions; enterprise restrictions |
| `GH006` / `GH013` / protected branch | The default branch blocks direct workflow pushes; change rules or switch to a PR-based process |
| No scheduled runs | Workflow must exist on the default branch; check Actions is enabled and inactivity policy |
| Run succeeds, no commit | The day was already published, or the reviewed library is exhausted; inspect the workflow's summary |
| Commit shows unlinked author | Confirm author email exactly matches GitHub email settings or its noreply address |
| Wrong date in a note | The publisher uses the IST date at execution, not a faked historical scheduled time |
| JSON validation fails | Fix invalid JSON, duplicate IDs, unknown categories, or missing required fields |
| Manifest/file mismatch | Restore missing generated notes or the manifest using Git history; do not delete the ledger |
| Push fails after retry | Inspect logs for permissions, branch rules, or repeated simultaneous updates |
| Backup creates no additional commit | Intended: the first successful publication for the date wins |

## 11. Security and maintenance notes

- `GITHUB_TOKEN` is issued by GitHub for each workflow run and reused by `actions/checkout` for the authenticated push; it is not written to the repository.
- The workflow runs only on `schedule` and manual `workflow_dispatch`, not untrusted pull-request code.
- Only the README, ledger, and a topic Markdown file are expected to change during publication.
- Standard-library-only publisher, no requirements file, no paid APIs, no scheduled job on your own computer.
- Keep GitHub Actions enabled and periodically add **human-reviewed** topics before the finite catalog is depleted.
- If you want third-party contributions or protected branch rules, review and adapt permissions and merge policies before enabling direct pushes.
