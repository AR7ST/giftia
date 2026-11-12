# scripts/

| ファイル | 役割 |
|---|---|
| `build-progress.py` | `.github/workflows/pages.yml` から呼ばれ、`docs/progress.html` を生成する（GitHub Issue集計。標準ライブラリのみで動作） |
| `pre-commit.sh` | コミット前にステージした差分を [gitleaks](https://github.com/gitleaks/gitleaks) で検査する（秘密情報の誤コミット防止） |

## pre-commit.sh の使い方（各自のPCで、任意）

1. [gitleaks](https://github.com/gitleaks/gitleaks) をインストールする
2. リポジトリ直下で以下を実行し、Gitのフックとして有効化する（`.git/hooks/` はコミット対象外なので、各自のPCで1回だけ設定する）
   ```
   cp scripts/pre-commit.sh .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```
3. 以降、`git commit` のたびに自動でステージ内容がスキャンされる

このフックはローカルの予防策であり、回避可能です。公開前の監査（履歴全体のスキャン）やレビューと組み合わせて使ってください。
