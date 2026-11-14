#!/usr/bin/env python3
"""原本 Markdown (02_プロジェクト/soubetsu-gift/) から要求定義書 (request.html) と
要件定義書 (requirements.html) の閲覧用 HTML を自動生成する。

- 要求定義書: 02_プロジェクト/soubetsu-gift/要求.md -> request.html
- 要件定義書: 02_プロジェクト/soubetsu-gift/要件.md + 発展2_変更点.md -> requirements.html (#tenkai2 を維持)
- 原本ファイルのパス・最終更新日・コミット SHA・Google ドキュメント原本リンクを明記し、
  Markdown 原本と公開 HTML の二重管理・内容ズレを防ぐ。
"""
import html
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/AR7ST/giftia"
REQ_GDOC = "https://docs.google.com/document/d/1UKN-KzgEEkWoMsWDvMRQA5dOFL4MDbLSt47nyfW7B3U/edit"
SPEC_GDOC = "https://docs.google.com/document/d/17cbMGdWMRYxOWZusGtCB7o-_m6KvIX5pXz1pSerIDG4/edit"


def get_git_meta(filepath):
    """対象ファイルの最新コミット SHA (短縮) と最終コミット日 (YYYY-MM-DD) を取得する。"""
    sha = os.environ.get("GITHUB_SHA", "")[:7]
    date_str = ""
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%h|%cs", "--", str(filepath)],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if "|" in out:
            s, d = out.split("|", 1)
            if s:
                sha = s
            if d:
                date_str = d
    except Exception:
        pass
    if not sha:
        try:
            sha = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except Exception:
            sha = "main"
    if not date_str:
        date_str = "2026-11-12"
    return sha, date_str


def format_inline(text):
    """インライン記法 (<br>, コード `...`, 太字 **...**, リンク) を安全に HTML 化する。"""
    placeholders = {}

    def save_ph(val):
        key = f"__PH_{len(placeholders)}__"
        placeholders[key] = val
        return key

    # Allow literal <br> or <br/> in table cells
    text = re.sub(r"<br\s*/?>", lambda _: save_ph("<br>"), text, flags=re.IGNORECASE)

    # Inline code `...`
    def repl_code(m):
        return save_ph(f'<code class="mono">{html.escape(m.group(1))}</code>')

    text = re.sub(r"`([^`]+)`", repl_code, text)

    # Markdown links [label](url)
    def repl_link(m):
        label = html.escape(m.group(1))
        url = html.escape(m.group(2), quote=True)
        return save_ph(f'<a href="{url}" target="_blank" rel="noopener">{label}</a>')

    text = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", repl_link, text)

    # Escape remaining HTML
    escaped = html.escape(text)

    # Bold **...**
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)

    # Special link conversions for cross-references
    if "クラス5_東京Drinking Party_要件定義書" in escaped:
        escaped = escaped.replace(
            "クラス5_東京Drinking Party_要件定義書",
            '<a href="requirements.html">要件定義書（クラス5_東京Drinking Party_要件定義書）</a>',
        )
    if "クラス5_東京Drinking Party_要求定義書" in escaped:
        escaped = escaped.replace(
            "クラス5_東京Drinking Party_要求定義書",
            '<a href="request.html">要求定義書（クラス5_東京Drinking Party_要求定義書）</a>',
        )
    escaped = re.sub(
        r"PR #(\d+)（AR7ST/giftia）",
        rf'<a href="{REPO_URL}/pull/\1/files" target="_blank" rel="noopener">PR #\1（AR7ST/giftia）</a>',
        escaped,
    )

    for k, v in placeholders.items():
        escaped = escaped.replace(k, v)
    return escaped


def split_table_row(line):
    """Markdown の表の1行をセル配列に分割する（`\\|` のエスケープを保持）。"""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    s = s.replace(r"\|", "__ESCAPED_PIPE__")
    cells = [c.strip().replace("__ESCAPED_PIPE__", "|") for c in s.split("|")]
    return cells


def is_separator_row(cells):
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells)


def render_table(table_lines, is_meta_kv=False):
    rows = [split_table_row(ln) for ln in table_lines]
    if len(rows) >= 2 and is_separator_row(rows[1]):
        header = rows[0]
        body = rows[2:]
    else:
        header = []
        body = rows

    # 2列の「項目 | 内容」またはメタ情報テーブルは左列を <th> にする
    if is_meta_kv:
        all_rows = ([header] if header else []) + body
        tr_html = [
            f"    <tr><th>{format_inline(r[0])}</th><td>{format_inline(r[1] if len(r) > 1 else '')}</td></tr>"
            for r in all_rows
            if len(r) >= 2
        ]
        return "  <table>\n" + "\n".join(tr_html) + "\n  </table>"

    if header == ["項目", "内容"] and all(len(r) == 2 for r in body):
        tr_html = [
            f"    <tr><th>{format_inline(r[0])}</th><td>{format_inline(r[1])}</td></tr>"
            for r in body
        ]
        return "  <table>\n" + "\n".join(tr_html) + "\n  </table>"

    out = ["  <table>"]
    if header:
        ths = "".join(f"<th>{format_inline(c)}</th>" for c in header)
        out.append(f"    <tr>{ths}</tr>")
    for r in body:
        if not any(r):
            continue
        tds = []
        for idx, c in enumerate(r):
            if idx == 0 and header and header[0] == "":
                tds.append(f"<th>{format_inline(c)}</th>")
            else:
                tds.append(f"<td>{format_inline(c)}</td>")
        out.append("    <tr>" + "".join(tds) + "</tr>")
    out.append("  </table>")
    return "\n".join(out)


def convert_markdown_blocks(md_text, skip_h1=True):
    lines = md_text.splitlines()
    out = []
    i = 0
    seen_first_table = False
    lead_emitted = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Horizontal rule and trailing citation line
        if stripped == "---":
            i += 1
            continue
        if stripped.startswith("*出典:") and stripped.endswith("*"):
            i += 1
            continue

        # H1
        if stripped.startswith("# "):
            i += 1
            continue

        # Lead paragraph right after H1
        if not lead_emitted and not stripped.startswith(("#", "|", "-", ">", "```")):
            lead_emitted = True
            out.append(f'  <p class="lead">{format_inline(stripped)}</p>')
            i += 1
            continue

        # Fenced code block (e.g. ```mermaid)
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            if lang == "mermaid":
                out.append('  <div class="card">\n    <pre class="mermaid">\n' + "\n".join(code_lines) + "\n    </pre>\n  </div>")
            else:
                out.append('  <pre class="mono">' + html.escape("\n".join(code_lines)) + "</pre>")
            continue

        # H2
        if stripped.startswith("## "):
            title = stripped[3:].strip()
            out.append(f'  <h2 class="sec-title">{format_inline(title)}</h2>')
            i += 1
            continue

        # H3
        if stripped.startswith("### "):
            title = stripped[4:].strip()
            out.append(f'  <h3>{format_inline(title)}</h3>')
            i += 1
            continue

        # Table
        if stripped.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            is_meta = not seen_first_table
            seen_first_table = True
            out.append(render_table(tbl, is_meta_kv=is_meta))
            continue

        # Blockquote
        if stripped.startswith(">"):
            q_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f'  <div class="card"><p class="muted">{format_inline(" ".join(q_lines))}</p></div>')
            continue

        # Bracketed subhead + bullet list group (e.g. 【Giftiaの現状（事実）】)
        if stripped.startswith("【") and stripped.endswith("】"):
            card_parts = []
            while i < len(lines):
                cur = lines[i].strip()
                if not cur:
                    i += 1
                    if i < len(lines) and (lines[i].strip().startswith("【") or lines[i].strip().startswith("- ")):
                        continue
                    break
                if cur.startswith("【") and cur.endswith("】"):
                    card_parts.append(f"    <p><b>{format_inline(cur)}</b></p>")
                    i += 1
                elif cur.startswith("- "):
                    ul = ["    <ul>"]
                    while i < len(lines) and lines[i].strip().startswith("- "):
                        ul.append(f"      <li>{format_inline(lines[i].strip()[2:].strip())}</li>")
                        i += 1
                    ul.append("    </ul>")
                    card_parts.append("\n".join(ul))
                else:
                    break
            out.append('  <div class="card">\n' + "\n".join(card_parts) + "\n  </div>")
            continue

        # Standalone bullet list
        if stripped.startswith("- "):
            ul = ['  <div class="card">\n    <ul>']
            while i < len(lines) and lines[i].strip().startswith("- "):
                ul.append(f"      <li>{format_inline(lines[i].strip()[2:].strip())}</li>")
                i += 1
            ul.append("    </ul>\n  </div>")
            out.append("\n".join(ul))
            continue

        # Italic note *...*
        if stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 2:
            inner = stripped[1:-1].strip()
            out.append(f'  <p class="muted">{format_inline(inner)}</p>')
            i += 1
            continue

        # Regular paragraph
        if stripped.startswith(("※", "生成AI利用", "試算：")):
            out.append(f'  <p class="muted">{format_inline(stripped)}</p>')
        elif stripped.startswith("（") and stripped.endswith("）"):
            out.append(f'  <div class="card"><p class="muted">{format_inline(stripped)}</p></div>')
        else:
            out.append(f'  <div class="card"><p>{format_inline(stripped)}</p></div>')
        i += 1

    return "\n\n".join(out)


def convert_tenkai2_markdown(md_text):
    """発展2_変更点.md を #tenkai2 セクションの HTML に変換する。"""
    lines = md_text.splitlines()
    out = [
        '  <h2 class="sec-title" id="tenkai2">発展2：要件定義をもとにGiftiaを更新した記録 <span class="pill css">完了</span></h2>'
    ]
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped == "---" or stripped.startswith("*出典:"):
            i += 1
            continue
        if stripped.startswith("# "):
            i += 1
            continue
        if stripped.startswith("発展2「"):
            out.append(f'  <p class="muted">{format_inline(stripped)}</p>')
            i += 1
            continue
        if stripped.startswith("## "):
            sec = stripped[3:].strip()
            sec_clean = re.sub(r"^\d+\.\s*", "", sec)
            out.append(f"  <h3>{format_inline(sec_clean)}</h3>")
            i += 1
            continue
        if stripped.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            out.append(render_table(tbl, is_meta_kv=False))
            continue
        if stripped.startswith("- "):
            ul = ['  <div class="card">\n    <ul>']
            while i < len(lines) and lines[i].strip().startswith("- "):
                ul.append(f"      <li>{format_inline(lines[i].strip()[2:].strip())}</li>")
                i += 1
            ul.append("    </ul>\n  </div>")
            out.append("\n".join(ul))
            continue
        out.append(f'  <p class="muted">{format_inline(stripped)}</p>')
        i += 1
    return "\n\n".join(out)


def build_request_page(req_md_path):
    sha, date_str = get_git_meta(req_md_path)
    md_text = req_md_path.read_text(encoding="utf-8")
    body_html = convert_markdown_blocks(md_text)
    rel_path = "02_プロジェクト/soubetsu-gift/要求.md"
    blob_url = f"{REPO_URL}/blob/main/02_%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88/soubetsu-gift/%E8%A6%81%E6%B1%82.md"

    return f"""<!DOCTYPE html>
<!-- 自動生成ファイル: scripts/build-docs.py により {rel_path} から生成 -->
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>要求定義書 ｜ 東京 Drinking Party</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/map.css">
<style>
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0 18px; font-size: .92rem; }}
  th, td {{ border: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: rgba(255,255,255,.06); }}
  .src {{ font-size: .85rem; color: var(--muted); }}
  .source-banner {{ margin: 10px 0 16px; padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(56,225,255,.4); background: rgba(56,225,255,.07); font-size: .84rem; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="top"><span class="kicker">GIFTIA ・ 要求定義書</span><a href="./">← ハブにもどる</a></div>
  <h1><span class="p">要求定義書</span></h1>
  <div class="source-banner">
    📄 <b>原本 Markdown から自動生成</b>：<a class="mono" href="{blob_url}" target="_blank" rel="noopener">{rel_path} ↗</a>（最終更新：{date_str} ／ コミット：<code class="mono">{sha}</code>）
  </div>

{body_html}

  <p class="src">原本: <a href="{REQ_GDOC}" target="_blank" rel="noopener">クラス5_東京Drinking Party_要求定義書（提出用）</a>（Googleドキュメント）／ リポジトリ内のMarkdown原本: <a class="mono" href="{blob_url}" target="_blank" rel="noopener">{rel_path}</a>（コミット <code class="mono">{sha}</code>）</p>
  <footer>Giftia 班（クラス5・東京 Drinking Party）</footer>
</div>
</body>
</html>
"""


def build_requirements_page(spec_md_path, tenkai2_md_path):
    sha_spec, date_spec = get_git_meta(spec_md_path)
    sha_t2, date_t2 = get_git_meta(tenkai2_md_path)
    spec_text = spec_md_path.read_text(encoding="utf-8")
    tenkai2_text = tenkai2_md_path.read_text(encoding="utf-8")

    spec_html = convert_markdown_blocks(spec_text)
    tenkai2_html = convert_tenkai2_markdown(tenkai2_text)

    rel_spec = "02_プロジェクト/soubetsu-gift/要件.md"
    rel_t2 = "02_プロジェクト/soubetsu-gift/発展2_変更点.md"
    blob_spec = f"{REPO_URL}/blob/main/02_%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88/soubetsu-gift/%E8%A6%81%E4%BB%B6.md"
    blob_t2 = f"{REPO_URL}/blob/main/02_%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88/soubetsu-gift/%E7%99%BA%E5%B1%952_%E5%A4%89%E6%9B%B4%E7%82%B9.md"

    return f"""<!DOCTYPE html>
<!-- 自動生成ファイル: scripts/build-docs.py により {rel_spec} および {rel_t2} から生成 -->
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>要件定義書 ｜ 東京 Drinking Party</title>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/map.css">
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0 18px; font-size: .92rem; }}
  th, td {{ border: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: rgba(255,255,255,.06); }}
  .src {{ font-size: .85rem; color: var(--muted); }}
  .source-banner {{ margin: 10px 0 16px; padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(56,225,255,.4); background: rgba(56,225,255,.07); font-size: .84rem; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="top"><span class="kicker">GIFTIA ・ 要件定義書</span><a href="./">← ハブにもどる</a></div>
  <h1><span class="p">要件定義書</span></h1>
  <div class="source-banner">
    📄 <b>原本 Markdown から自動生成</b>：<a class="mono" href="{blob_spec}" target="_blank" rel="noopener">{rel_spec} ↗</a>（最終更新：{date_spec} ／ コミット：<code class="mono">{sha_spec}</code>）・<a class="mono" href="{blob_t2}" target="_blank" rel="noopener">{rel_t2} ↗</a>（コミット：<code class="mono">{sha_t2}</code>）
  </div>

{spec_html}

{tenkai2_html}

  <p class="src">出典: 「要件定義書_変更点（東京Drinking Party・発展2）.docx」／ リポジトリ内のMarkdown原本: <a class="mono" href="{blob_t2}" target="_blank" rel="noopener">{rel_t2}</a>（コミット <code class="mono">{sha_t2}</code>）</p>
  <p class="src">原本: <a href="{SPEC_GDOC}" target="_blank" rel="noopener">クラス5_東京Drinking Party_要件定義書（提出用）</a>（Googleドキュメント）／ リポジトリ内のMarkdown原本: <a class="mono" href="{blob_spec}" target="_blank" rel="noopener">{rel_spec}</a>（コミット <code class="mono">{sha_spec}</code>）</p>
  <footer>Giftia 班（クラス5・東京 Drinking Party）</footer>
</div>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: "dark" }});
</script>
</body>
</html>
"""


def main():
    root = Path(__file__).resolve().parent.parent
    req_md = root / "02_プロジェクト" / "soubetsu-gift" / "要求.md"
    spec_md = root / "02_プロジェクト" / "soubetsu-gift" / "要件.md"
    tenkai2_md = root / "02_プロジェクト" / "soubetsu-gift" / "発展2_変更点.md"

    for p in (req_md, spec_md, tenkai2_md):
        if not p.is_file():
            raise RuntimeError(f"原本 Markdown が見つかりません: {p}")

    req_html = build_request_page(req_md)
    spec_html = build_requirements_page(spec_md, tenkai2_md)

    out_dirs = []
    if len(sys.argv) > 1:
        out_dirs = [Path(arg) for arg in sys.argv[1:]]
    else:
        default_site = Path(os.environ.get("SITE_DIR", "_site"))
        if default_site.is_dir():
            out_dirs.append(default_site)
        else:
            out_dirs.append(root / "docs")

    for d in out_dirs:
        if not d.is_dir():
            raise RuntimeError(f"出力先ディレクトリが存在しません: {d}")
        (d / "request.html").write_text(req_html, encoding="utf-8")
        (d / "requirements.html").write_text(spec_html, encoding="utf-8")
        print(f"要求・要件定義書HTMLを生成しました: {d / 'request.html'}, {d / 'requirements.html'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"要求・要件定義書HTMLの生成に失敗しました: {exc}", file=sys.stderr)
        sys.exit(1)
