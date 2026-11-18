#!/usr/bin/env python3
"""Render the changes to Giftia's application code as a static Pages timeline."""

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


def git(*args, **options):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, **options)


def code_history():
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
            ['git', 'diff-tree', '--quiet', '-r', '--root', *first_parent, sha, '--', *CODE_PATHS],
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
        return '<p class="card">対象のコード変更はありません。</p>'

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


def main(output_dir):
    entries = code_history()
    name = 'code-history.html'
    template = (ROOT / 'docs' / name).read_text(encoding='utf-8')
    if template.count('<!-- code-history -->') != 1:
        raise RuntimeError('コード変更履歴の挿入位置が一意に決まりません。')
    page = template.replace('<!-- code-history -->', render(entries), 1)
    (output_dir / name).write_text(page, encoding='utf-8')
    print(f'コード変更履歴: {len(entries)} 件')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
