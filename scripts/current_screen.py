"""Build the public screen guide from the source checked out for Pages."""

import ast
from html import escape
import re
import subprocess
from pathlib import Path


MARKER = re.compile(r'<!-- current-screen:start -->.*?<!-- current-screen:end -->', re.DOTALL)
GUIDE_PAGES = ('index.html', 'map.html', 'screen.html', 'overview.html')
APP = 'giftia-frontend/app/'
API = 'giftia-frontend/lib/api.ts'
PAGE = APP + 'page.tsx'
CARD = APP + 'ResultCard.tsx'
PANEL = APP + 'ConsultPanel.tsx'
BACKEND = 'backend/farewell.py'


def source_match(source, pattern):
    matches = list(re.finditer(pattern, source, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f'画面ガイドの参照先が一意に決まりません: {pattern}')
    return matches[0]


def line_at(source, match):
    return source.count('\n', 0, match.start()) + 1


def render_current_screen(root, repository_url):
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    sources = {
        path: (root / path).read_text(encoding='utf-8')
        for path in (PAGE, CARD, PANEL, API, BACKEND, 'backend/main.py')
    }

    def link(path, line, label):
        return f'<a class="ref" href="{repository_url}/blob/{sha}/{path}#L{line}">{escape(label)} ↗</a>'

    def code_link(path, pattern, label):
        source = sources[path]
        return link(path, line_at(source, source_match(source, pattern)), label)

    def text(pattern, path=PAGE):
        return escape(source_match(sources[path], pattern)[1].strip())

    def placeholder(field):
        return text(rf'<input\b[^<]*?\bvalue=\{{{field}\}}[^<]*?\bplaceholder="([^"]+)"')

    def first_option(field):
        return text(rf'<select\b[^<]*?\bvalue=\{{{field}\}}[^<]*>\s*<option[^>]*>([^<]+)</option>')

    page = sources[PAGE]
    nav = source_match(page, r'<nav\b[^>]*className="modes"[^>]*>([\s\S]*?)</nav>')
    tabs = list(re.finditer(r'changeMode\("([a-z]+)"\)[^>]*>\s*([^<]+)</button>', nav[1]))
    if len(tabs) != len(re.findall(r'<button\b', nav[1])) or not tabs:
        raise ValueError('画面ガイドで検索タブの名前を読み取れません')

    default_budget = int(text(r'\[budget,\s*setBudget\]\s*=\s*useState\(["\'](\d+)["\']\)'))
    budget = text(r'<label\b[^>]*>\s*([^<]+)\s*<input\b[^>]*value=\{budget\}')
    wrapping = text(r'<input\b[^<]*checked=\{indivWrap\}[^<]*?/>\s*([^<]+)</label>')
    submit = text(r'<button\b[^>]*type="submit"[^>]*>\s*([^<]+)</button>')
    rating = text(r'if \(n === null\) return "([^"]+)";', CARD)
    consult = text(r'<h2\b[^>]*>\s*([^<]+)</h2>', PANEL)
    candidate_limit = int(text(r'^const MAX_SELECT\s*=\s*(\d+)\s*;'))
    limits = {
        node.targets[0].id: node.value.value
        for node in ast.parse(sources[BACKEND]).body
        if isinstance(node, ast.Assign) and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant)
    }
    result_limit = int(limits['RESULT_LIMIT'])
    category_limit = int(limits['PER_CATEGORY_LIMIT'])

    guides = {
        'standard': f'{placeholder("keyword")}とカテゴリーを指定します。初期値は「{first_option("category")}」です。',
        'business': f'「{wrapping}」と価格帯で絞り込みます。価格帯の初期値は「{first_option("priceBand")}」です。',
        'farewell': (
            f'「{budget}」（初期値 {default_budget:,}円）と{placeholder("fKeyword")}で絞り込みます。'
            f'全体で最大{result_limit}件、同じカテゴリーは最大{category_limit}件を表示します。'
            f'レビュー件数が不明な場合は「{rating}」と表示します。'
            f'最大{candidate_limit}件を選ぶと「{consult}」に候補が入り、文面をコピーできます。'
        ),
    }

    rows = []
    for tab in tabs:
        line = page.count('\n', 0, nav.start(1) + tab.start()) + 1
        mode, title = tab.groups()
        code = link(PAGE, line, 'タブのコード')
        description = guides.get(mode, '操作の詳細はリンク先の実装を確認してください。')
        rows.append(f'      <li><b>{escape(title.strip())}</b> — {description} {code}</li>')

    links = [
        code_link(PAGE, r'^\s*async function onSearch\(', '検索ボタン'),
        code_link(API, r'^export async function searchFarewellGifts\(', '送別検索の通信'),
        code_link('backend/main.py', r'^@app\.get\("/api/search"\)', '検索APIの入口'),
        code_link(BACKEND, r'^def select_diverse\(', '検索結果の上限'),
        code_link(CARD, r'^function ratingText\(', '評価の表示'),
        code_link(PANEL, r'^export default function ConsultPanel\(', '相談文の画面'),
    ]
    rows_html = '\n'.join(rows)
    return f'''<section class="card" id="current-screen" aria-labelledby="current-screen-title">
    <h2 class="sec-title" id="current-screen-title">現在の検索画面とコード</h2>
    <p>タブで条件を選び「{submit}」を押します。この案内は、ハブ公開時点のコードから生成しています。</p>
    <ul>
{rows_html}
    </ul>
    <p class="refs">{' '.join(links)}</p>
    <p class="muted">参照したコード: <a href="{repository_url}/commit/{sha}"><code>{sha[:7]}</code></a></p>
  </section>'''


def write_screen_guides(output: Path, guide: str):
    for name in GUIDE_PAGES:
        path = output / name
        content = path.read_text(encoding='utf-8')
        replacement = f'<!-- current-screen:start -->\n  {guide}\n  <!-- current-screen:end -->'
        content, count = MARKER.subn(lambda _: replacement, content)
        if count != 1:
            raise ValueError(f'画面ガイドの挿入位置が一意に決まりません: {name}')
        path.write_text(content, encoding='utf-8')
