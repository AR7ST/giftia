#!/usr/bin/env bash
set -euo pipefail
if ! command -v gitleaks >/dev/null 2>&1; then
  printf '%s\n' 'gitleaksが必要です。インストール後に再実行してください。' >&2
  exit 1
fi
# 差分の内容は表示せず、検出箇所はredactする。
git diff --cached --no-ext-diff --binary | gitleaks stdin --redact --no-banner
