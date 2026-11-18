"""Render the public explanation page for one entry in either history."""

from collections import Counter
from html import escape
import re
from string import Template


STATUS = {'A': '追加', 'M': '変更', 'D': '削除', 'T': '種類変更'}


def changed_areas(changes, category):
    areas = set()
    for _, path in changes:
        if category == 'code':
            if path.startswith(('giftia-frontend/app/', 'app/')):
                areas.add('検索画面と表示部品')
            elif path.startswith('backend/'):
                areas.add('検索 API とサーバー側の処理')
            elif path.startswith(('giftia-frontend/lib/', 'lib/')):
                areas.add('画面の共通処理・API との通信')
            else:
                areas.add('アプリの設定・その他のファイル')
        elif path.startswith('docs/'):
            areas.add('ハブのページ・素材')
        elif path.startswith('02_プロジェクト/'):
            areas.add('公開する要求・要件等の原本')
        else:
            areas.add('ページの生成・公開処理')
    names = '、'.join(sorted(areas))
    return (f'<p>変更された範囲は「{escape(names)}」です。'
            '詳しい変更前後の説明がない項目は、タイトルと差分から内容を確認できます。</p>')


def inline(text):
    parts = re.split(r'(`[^`]+`|\*\*[^*]+\*\*)', text)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            parts[i] = escape(part)
        elif part.startswith('`'):
            parts[i] = f'<code>{escape(part[1:-1])}</code>'
        else:
            parts[i] = f'<strong>{escape(part[2:-2])}</strong>'
    return ''.join(parts)


def markdown(source):
    """A restricted format for public notes. Raw HTML is always escaped."""
    blocks = re.split(r'(^```[^\n]*\n[\s\S]*?^```[ \t]*$)', source, flags=re.MULTILINE)
    html = []
    for i, block in enumerate(blocks):
        if i % 2:
            diagram = '\n'.join(block.splitlines()[1:-1])
            html.append(f'<pre class="tree">{escape(diagram)}</pre>')
            continue
        for paragraph in re.split(r'\n[ \t]*\n', block.strip()):
            if not paragraph:
                continue
            lines = paragraph.splitlines()
            if all(line.startswith('- ') for line in lines):
                items = ''.join(f'<li>{inline(line[2:])}</li>' for line in lines)
                html.append(f'<ul>{items}</ul>')
                continue
            text = []
            for line in lines:
                heading = re.fullmatch(r'#{1,3}\s+(.+)', line)
                if heading:
                    if text:
                        html.append(f'<p>{inline(" ".join(text))}</p>')
                        text.clear()
                    html.append(f'<h3>{inline(heading[1])}</h3>')
                else:
                    text.append(line)
            if text:
                html.append(f'<p>{inline(" ".join(text))}</p>')
    return '\n'.join(html)


def file_tree(changes):
    tree = {}
    for status, path in changes:
        node = tree
        for part in path.split('/'):
            node = node.setdefault(part, {})
        node[None] = STATUS.get(status, '差分あり')

    def lines(node, indent=''):
        children = sorted(name for name in node if name is not None)
        for i, name in enumerate(children):
            child = node[name]
            last = i == len(children) - 1
            branch = '└─ ' if last else '├─ '
            label = f'（{child[None]}）' if None in child else '/'
            yield indent + branch + name + label
            yield from lines(child, indent + ('   ' if last else '│  '))

    return '\n'.join(['Giftia', *lines(tree)])


def write_details(root, output, category, history_title, repo, entries):
    template = Template((root / 'scripts' / 'change-detail.html').read_text(encoding='utf-8'))
    detail_dir = output.parent / 'changes' / category
    detail_dir.mkdir(parents=True, exist_ok=True)
    if (root / 'change-notes').is_symlink():
        raise ValueError('change-notes は実ファイルのディレクトリにしてください。')
    for when, sha, title, pr, changes, notes in entries:
        candidates = ([f'change-notes/pr-{pr}.md'] if pr else []) + [f'change-notes/commit-{sha}.md', *notes]
        paths = (root / path for path in candidates)
        note = next((path for path in paths if path.is_file() and not path.is_symlink()), None)
        explanation = markdown(note.read_text(encoding='utf-8')) if note else changed_areas(changes, category)
        counts = Counter(STATUS.get(status, 'その他') for status, _ in changes)
        summary = '、'.join(f'{name} {amount} 件' for name, amount in sorted(counts.items()))
        pr_link = f'<a href="{repo}/pull/{pr}">PR #{pr} を開く</a>' if pr else ''
        page = template.substitute(
            title=escape(title), date=when.isoformat(), time=when.strftime('%Y/%m/%d %H:%M:%S JST'),
            history_file=output.name, history_title=escape(history_title), explanation=explanation,
            summary=summary, tree=escape(file_tree(changes)), commit=f'{repo}/commit/{sha}', pr_link=pr_link,
        )
        (detail_dir / f'{sha}.html').write_text(page, encoding='utf-8')
