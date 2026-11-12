#!/usr/bin/env python3
"""Issueの集計ページを生成。公開フラグが無ければ件数を公開しない。"""
import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch_counts(repo, token):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not token:
        raise ValueError("リポジトリ名またはトークンが不正です")
    counts = {"open": 0, "closed": 0}
    for page in range(1, 101):
        url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}"
        req = Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "giftia-progress",
        })
        try:
            with urlopen(req, timeout=30) as response:
                items = json.load(response)
        except HTTPError as exc:
            raise RuntimeError(f"GitHub API HTTP {exc.code}") from None
        except (URLError, TimeoutError, json.JSONDecodeError):
            raise RuntimeError("GitHub APIの取得または解析に失敗") from None
        if not isinstance(items, list):
            raise RuntimeError("GitHub API応答形式が不正です")
        for item in items:
            if not isinstance(item, dict):
                raise RuntimeError("GitHub APIの項目が不正です")
            if "pull_request" in item:
                continue
            state = item.get("state")
            if state not in counts:
                raise RuntimeError("Issue状態が不正です")
            counts[state] += 1
        if len(items) < 100:
            return counts
    raise RuntimeError("ページ取得上限に達したため処理を中止しました")


def main():
    target = Path("_site/progress.html")
    if not target.parent.is_dir() or target.exists():
        raise RuntimeError("_siteがないか、progress.htmlが既に存在します")
    publish = os.environ.get("PUBLISH_ISSUE_COUNTS", "false").lower() == "true"
    if publish:
        counts = fetch_counts(os.environ.get("GITHUB_REPOSITORY", ""),
                               os.environ.get("GITHUB_TOKEN", ""))
        content = f'<p>未完了: {counts["open"]}件／完了: {counts["closed"]}件</p>'
    else:
        content = "<p>進捗情報は公開していません。</p>"
    updated = html.escape(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    result = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>進捗概要 | Giftia</title></head><body>
<main><h1>進捗概要</h1>{content}
<p>Issue件数は成果や進捗率そのものではありません。PRは含みません。</p>
<p>生成日時: {updated}</p><p><a href="./index.html">ハブへ戻る</a></p>
</main></body></html>"""
    target.write_text(result, encoding="utf-8")
    print("進捗ページを生成しました")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"進捗ページを生成できません: {exc}", file=sys.stderr)
        sys.exit(1)
