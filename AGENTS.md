# AGENTS.md — Giftia 班の AI の使い方ルール

Claude Code などの AI ツールは、作業を始める前にこのファイルを読み、ここに書いたルールを守ること。
班のルール全体は `README.md` の2章を参照する。このファイルと README がちがうときは、README を優先する。

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
- 画面と API のつなぎ目（`lib/api.ts` の `Gift` 型と `searchGifts()`）を変えるときは、`giftia-backend` もセットで変える必要があるかを先に伝える
- SQL に入れる値は `%s` と `params` で渡す。文字列に直接つなげない（SQL インジェクション対策）
- 変えたあと、`npm run dev` で画面が今までどおり動くかを確かめる方法を伝える

## 4. 説明のしかた

- 説明は日本語で、専門用語には一言の言い換えを付ける
- 提案したコードは、使う人が理解してから取り入れる。分からない点は質問してよい
- AI の提案が正しいかは、公式ドキュメントや実際の動作で人が確かめる

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
