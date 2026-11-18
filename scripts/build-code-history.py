#!/usr/bin/env python3
"""Build separate timelines for application code and the Pages site."""

import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from html import escape
from itertools import groupby
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPO = 'https://github.com/AR7ST/giftia'
JST = timezone(timedelta(hours=9))
CODE_PATHS = (
    'giftia-frontend/', 'backend/', 'app/', 'lib/', 'public/',
    'package.json', 'package-lock.json', ':(glob)next.config.*',
    ':(glob)eslint.config.*', 'tsconfig.json', ':(exclude,glob)**/*.md',
)
PAGES_PATHS = (
    'docs/', '.github/workflows/pages.yml',
    'scripts/build-docs.py', 'scripts/build-progress.py',
    'scripts/current_screen.py', 'scripts/build-code-history.py',
    '02_プロジェクト/soubetsu-gift/要求.md',
    '02_プロジェクト/soubetsu-gift/要件.md',
    '02_プロジェクト/soubetsu-gift/発展2_変更点.md',
)


def git(*args, **options):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, **options)


def history(paths):
    checkout = git('rev-parse', '--is-shallow-repository', capture_output=True, text=True)
    if checkout.stdout.strip() == 'true':
        raise RuntimeError('履歴の生成には浅いクローンではなく、全履歴が必要です。')

    log = git(
        'log', '--first-parent', '-z', '--format=%H%x00%P%x00%ct%x00%s%x00%b',
        capture_output=True, text=True, encoding='utf-8', errors='replace',
    )
    fields = log.stdout.split('\0')
    if fields[-1] != '' or (len(fields) - 1) % 5:
        raise RuntimeError('コミット履歴の形式を読み取れませんでした。')
    fields.pop()
    entries = []
    for offset in range(0, len(fields), 5):
        sha, parents, timestamp, subject, body = fields[offset:offset + 5]
        first_parent = parents.split()[:1]
        diff = subprocess.run(
            ['git', 'diff-tree', '--quiet', '-r', '--root', *first_parent, sha, '--', *paths],
            cwd=ROOT,
        )
        if diff.returncode == 0:
            continue
        if diff.returncode != 1:
            diff.check_returncode()

        merge = re.match(r'Merge pull request #(\d+)\b', subject)
        pr = merge[1] if merge else None
        # GitHub's standard merge message puts the PR title on the first body line.
        title = body.strip().splitlines()[0] if merge and body.strip() else subject
        when = datetime.fromtimestamp(int(timestamp), JST)
        entries.append((when, sha, title, pr))
    return sorted(entries, key=lambda entry: entry[0], reverse=True)


def render(entries):
    if not entries:
        return '<p class="card">対象の変更はありません。</p>'

    sections = []
    for day, changes in groupby(entries, key=lambda entry: entry[0].date()):
        date_label = f'{day.year}年{day.month}月{day.day}日'
        items = []
        for when, sha, title, pr in changes:
            pr_link = f'<a href="{REPO}/pull/{pr}">PR #{pr}</a>' if pr else ''
            items.append(f'''<li>
        <time datetime="{when.isoformat()}">{when:%H:%M:%S}</time>
        <div><p>{escape(title)}</p><div class="entry-links">
          {pr_link}<a href="{REPO}/commit/{sha}" aria-label="コミット {sha[:7]} の差分を見る">差分を見る <code>{sha[:7]}</code></a>
        </div></div>
      </li>''')
        sections.append(f'''<section class="card history-day" aria-labelledby="date-{day}">
    <h2 id="date-{day}">{date_label}</h2>
    <ol class="changes">{''.join(items)}</ol>
  </section>''')
    return '\n  '.join(sections)


def write_history(output, template, title, context, paths):
    entries = history(paths)
    page = template.replace('<!-- history-title -->', escape(title))
    page = page.replace('<!-- history-context -->', context, 1)
    page = page.replace('<!-- history-entries -->', render(entries), 1)
    output.write_text(page, encoding='utf-8')
    print(f'{title}: {len(entries)} 件')


def main(output_dir):
    template = (ROOT / 'docs' / 'code-history.html').read_text(encoding='utf-8')
    for marker, count in (('history-title', 2), ('history-context', 1), ('history-entries', 1)):
        if template.count(f'<!-- {marker} -->') != count:
            raise RuntimeError(f'変更履歴の挿入位置が不正です: {marker}')

    write_history(
        output_dir / 'code-history.html', template, 'コード変更履歴',
        '<p class="lead">検索画面と検索 API の変更を、'
        '<code>main</code> のマージ・コミット日時が新しい順に表示します。日時は日本時間（JST）です。</p>',
        CODE_PATHS,
    )
    write_history(
        output_dir / 'pages-history.html', template, 'GitHub Pages の変更履歴',
        '<p class="lead">開発ハブのページ・画像・公開処理の変更を、'
        '<code>main</code> のマージ・コミット日時が新しい順に表示します。日時は日本時間（JST）です。</p>'
        '<p><a href="https://github.com/AR7ST/giftia-hub/commits/main/">統合前の開発ハブの履歴を GitHub で見る ↗</a></p>',
        PAGES_PATHS,
    )


if __name__ == '__main__':
    main(Path(sys.argv[1]))
