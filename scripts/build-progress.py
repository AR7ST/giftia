#!/usr/bin/env python3
"""GitHub Issue を集計し、ハブ用の進捗データ (_site/assets/progress.json) と
進捗概要ページ (_site/progress.html) を生成する。

集計ルール:
- 対象: GitHub Issues のみ（pull_request キーを持つ PR は除外）
- 除外: state_reason == "not_planned"（誤作成・取り下げ）または "duplicate" ラベル付き Issue
- 完了: state == "closed"（かつ not_planned でないもの）
- 担当者別内訳:
  - assignees が設定されている場合は、該当する各メンバーに 1 件としてカウント
  - assignees が未設定（空）の場合は、Issue 作成者 (user.login) のメンバーにフォールバック集計
  - いずれのメンバーにも該当しない場合は「未割当」枠に集計（0件の場合は非表示）
"""
import html
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

JST = timezone(timedelta(hours=9))

RULE_TEXT = (
    "対象：PR・誤作成(not_planned)を除くGitHub Issue／"
    "完了：state=closed／複数担当は各担当者に計上・担当未設定はIssue作成者(または未割当)で集計"
)

MEMBERS_DEF = [
    {"name": "タケ", "role": "班長", "github": "AR7ST"},
    {"name": "むっちゃん", "role": "コード長", "github": "tabidance"},
    {"name": "まいまい", "role": "発表長", "github": ""},
]


def fetch_issues(repo, token=""):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("リポジトリ名が不正です")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "giftia-progress",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    issues = []
    for page in range(1, 101):
        url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}"
        req = Request(url, headers=headers)
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
            # PR は除外
            if "pull_request" in item:
                continue
            # 誤作成・取り下げ (not_planned) は除外
            if item.get("state_reason") == "not_planned":
                continue
            labels = [
                lbl.get("name", "").lower()
                for lbl in item.get("labels", [])
                if isinstance(lbl, dict)
            ]
            if "duplicate" in labels or "invalid" in labels or "wontfix" in labels:
                continue
            state = item.get("state")
            if state not in ("open", "closed"):
                raise RuntimeError("Issue状態が不正です")
            issues.append(item)
        if len(items) < 100:
            return issues
    raise RuntimeError("ページ取得上限に達したため処理を中止しました")


def aggregate_progress(issues, repo, updated_jst):
    members = [
        {
            "name": m["name"],
            "role": m["role"],
            "github": m["github"],
            "done": 0,
            "total": 0,
        }
        for m in MEMBERS_DEF
    ]
    login_to_member = {
        m["github"].lower(): m for m in members if m["github"]
    }
    unassigned = {"name": "未割当", "role": "共通", "github": "", "done": 0, "total": 0}

    open_count = 0
    closed_count = 0

    for item in issues:
        is_closed = item.get("state") == "closed"
        if is_closed:
            closed_count += 1
        else:
            open_count += 1

        assignees = item.get("assignees") or []
        matched_members = []
        for a in assignees:
            if isinstance(a, dict) and a.get("login"):
                m = login_to_member.get(a["login"].lower())
                if m and m not in matched_members:
                    matched_members.append(m)

        # 担当者未設定の場合は Issue 作成者 (user.login) にフォールバック
        if not matched_members and not assignees:
            creator = (item.get("user") or {}).get("login", "")
            if creator:
                m = login_to_member.get(creator.lower())
                if m:
                    matched_members.append(m)

        if matched_members:
            for m in matched_members:
                m["total"] += 1
                if is_closed:
                    m["done"] += 1
        else:
            unassigned["total"] += 1
            if is_closed:
                unassigned["done"] += 1

    if unassigned["total"] > 0:
        members.append(unassigned)

    total_issues = open_count + closed_count
    pct_all = round(closed_count / total_issues * 100) if total_issues else 0

    return {
        "updatedAt": updated_jst,
        "repo": repo,
        "rule": RULE_TEXT,
        "done": closed_count,
        "total": total_issues,
        "open": open_count,
        "pct": pct_all,
        "members": members,
    }


def render_progress_html(progress_data, publish, updated_utc, error_note=""):
    if not publish:
        content = "<p>進捗情報は公開していません。</p>"
    elif error_note:
        content = f"<p>⚠ {html.escape(error_note)}</p>"
    elif progress_data:
        done = int(progress_data.get("done", 0))
        total = int(progress_data.get("total", 0))
        open_cnt = int(progress_data.get("open", max(0, total - done)))
        pct = round(done / total * 100) if total else 0
        rows = "".join(
            f"<li>{html.escape(m.get('name', ''))}（{html.escape(m.get('role', ''))}）: "
            f"{int(m.get('done', 0))} / {int(m.get('total', 0))} 件</li>"
            for m in progress_data.get("members", [])
        )
        content = (
            f"<p>完了: {done}件 ／ 未完了: {open_cnt}件 ／ 合計: {total}件（完了率 {pct}%）</p>"
            f"<ul>{rows}</ul>"
            f"<p><small>{html.escape(progress_data.get('rule', RULE_TEXT))}</small></p>"
        )
    else:
        content = "<p>⚠ 進捗データを取得できませんでした。</p>"

    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>進捗概要 | Giftia</title></head><body>
<main><h1>進捗概要</h1>{content}
<p>※登録済みIssueの完了数であり、未登録タスクや未検証機能を含む製品全体の完成度を意味しません。PRは含みません。</p>
<p>生成日時: {html.escape(updated_utc)}</p><p><a href="./index.html">ハブへ戻る</a></p>
</main></body></html>"""


def main():
    site_dir = Path(os.environ.get("SITE_DIR", "_site"))
    if not site_dir.is_dir():
        raise RuntimeError(f"{site_dir} ディレクトリが存在しません")

    target_html = site_dir / "progress.html"
    target_json = site_dir / "assets" / "progress.json"
    target_json.parent.mkdir(parents=True, exist_ok=True)

    publish = os.environ.get("PUBLISH_ISSUE_COUNTS", "true").lower() == "true"
    repo = os.environ.get("GITHUB_REPOSITORY", "") or "AR7ST/giftia"
    token = os.environ.get("GITHUB_TOKEN", "")
    now_utc = datetime.now(timezone.utc)
    updated_utc = now_utc.strftime("%Y-%m-%d %H:%M UTC")
    updated_jst = now_utc.astimezone(JST).strftime("%Y/%m/%d %H:%M")

    progress_data = None
    error_note = ""

    if publish:
        try:
            issues = fetch_issues(repo, token)
            progress_data = aggregate_progress(issues, repo, updated_jst)
            target_json.write_text(
                json.dumps(progress_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"進捗JSONを生成しました: {target_json} (完了 {progress_data['done']}/{progress_data['total']} 件)")
        except (ValueError, RuntimeError, OSError) as exc:
            error_note = f"GitHub APIからの自動集計に失敗したため、保存済みデータを維持しました ({exc})"
            print(f"警告: {error_note}", file=sys.stderr)
            if target_json.is_file():
                try:
                    progress_data = json.loads(target_json.read_text(encoding="utf-8"))
                    if isinstance(progress_data, dict):
                        done = sum(int(m.get("done", 0)) for m in progress_data.get("members", []))
                        total = sum(int(m.get("total", 0)) for m in progress_data.get("members", []))
                        progress_data.setdefault("done", done)
                        progress_data.setdefault("total", total)
                        progress_data.setdefault("open", max(0, total - done))
                except (OSError, json.JSONDecodeError):
                    progress_data = None

    result_html = render_progress_html(progress_data, publish, updated_utc, error_note)
    target_html.write_text(result_html, encoding="utf-8")
    print(f"進捗ページを生成しました: {target_html}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"進捗ページを生成できません: {exc}", file=sys.stderr)
        sys.exit(1)
