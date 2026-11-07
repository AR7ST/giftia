# AGENTS.md — Giftia 班の AI の使い方ルール

Claude Code などの AI ツールは、作業を始める前にこのファイルを読み、ここに書いたルールを守ること。
班のルール全体は `README.md` の2章を参照する。このファイルと README がちがうときは、README を優先する。

このリポジトリはモノレポ（画面と API を1つのリポジトリに入れた形）。

- `giftia-frontend/` … 画面（Next.js）。Next.js のコードを書く前に `giftia-frontend/AGENTS.md` も読む
- `backend/` … 検索 API（FastAPI）
- コマンドは、そのフォルダに `cd` してから実行する（`npm` は `giftia-frontend/`、`uvicorn`・`pip` は `backend/`）

## 1. 秘密の情報を扱わない

- `.env`（DB のホスト名・ユーザー名・パスワード）は読まない。中身を表示しない。どこにも貼らない
- 接続情報が載ったスプレッドシートやスクリーンショットも開かない
- 設定されているかの確認が必要なときは、「設定あり／なし」だけを答える
- `.env` と `.env.local` を `.gitignore` の除外から外さない
- Tech0 の Confidential 資料（教材の PDF など）の内容を、コードやドキュメントに写さない

## 2. Git の操作は人がやる

- AI は、`git commit`・`git push`・PR の作成・Approve・merge をしない。人が中身を確かめてから行う
- `main` に直接変更しない。作業は必ずブランチで行う
- ファイルの削除・移動・上書きの前に、何をするかを説明して、使う人の OK をもらう
- 頼まれていないファイルを変えない。変えたファイルは、作業の最後に一覧で伝える

## 3. コードを書くとき

- 1回の作業は1つの変更だけにする（1つの Issue・1つの PR）
- 画面と API のつなぎ目（`giftia-frontend/lib/api.ts` の `Gift` 型と `searchGifts()`）を変えるときは、`backend/main.py` もセットで（同じ PR で）変える必要があるかを先に伝える
- SQL に入れる値は（`backend/main.py` で）`%s` と `params` で渡す。文字列に直接つなげない（SQL インジェクション対策）
- 変えたあと、`npm run dev`（giftia-frontend/）と `uvicorn main:app --reload`（backend/）で、今までどおり動くかを確かめる方法を伝える

## 4. 説明のしかた

- 説明は日本語で、専門用語には一言の言い換えを付ける
- 提案したコードは、使う人が理解してから取り入れる。分からない点は質問してよい
- AI の提案が正しいかは、公式ドキュメントや実際の動作で人が確かめる
