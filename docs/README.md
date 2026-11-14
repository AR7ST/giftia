# Giftia 開発ハブ（`docs/`）

Giftia 班の入口ページです。このリポジトリ（`AR7ST/giftia`）の `docs/` を GitHub Pages（`.github/workflows/pages.yml`）で公開しています。

- **正式公開 URL**：https://ar7st.github.io/giftia/
  （旧 `giftia-hub` リポジトリの内容は 2026-11-12 にこの `docs/` フォルダへ統合しました）

## 構成と使い方

- トップは `index.html`（東京の夜景デザイン）。最上部から「要求定義書（`request.html`／原本 `02_プロジェクト/soubetsu-gift/要求.md`）」「要件定義書（`requirements.html`／原本 `02_プロジェクト/soubetsu-gift/要件.md`）」へ進めます。
- `assignments.html` は各課題の進み具合まとめ、`overview.html` は現在の仕組み、`vision.html` はこれから作るアプリの設計、`map.html` からはコードの地図（10ページ）へ進めます。
- 進捗ダッシュボード（開発タスク完了率）は `assets/progress.json` を読み込んで表示します（日程経過率とは区別して表示し、タスク完了率は登録済み Issue の集計であり製品全体の完成度を意味しません）。
- `map.html` の学習コースは、地図を読んだか手動でチェックできます。`assets/course.js` と `assets/course.css` を使い、進捗はこの端末・ブラウザの `localStorage` に保存します（班の進捗とは別です。保存できない環境でも、そのページ内では操作できます）。
- 改善を取りこんだら、`index.html` の「改善ログ」の表に1行足します（ブランチ＋PR で更新）。
- **公開ページなので、秘密の情報（`.env` の中身など）・教材の内容や図・本名・DB の実データが写ったスクショは載せない。**
- 班のルールとコードは、同じリポジトリ `AR7ST/giftia`（2026-11-12 から Public 公開）にあります（画面は `giftia-frontend/`、API は `backend/`、ルールは `README.md` と `AGENTS.md`）。
