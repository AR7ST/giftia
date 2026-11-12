# giftia-hub（Giftia 班のハブページ）

Giftia 班の入口ページです。GitHub Pages で公開しています。
https://ar7st.github.io/giftia-hub/

- トップは `index.html`（東京の夜景デザイン）。`map.html` から10ページの案内へ進めます。`overview.html` は現在の仕組み、`vision.html` はこれから作るアプリの設計です。班の進捗は `index.html` の `HUB` の値を手で書きかえます。
- `map.html` の学習コースは、6つの地図を読んだか手動でチェックできます。`assets/course.js` と `assets/course.css` を使い、進捗はこの端末・ブラウザの localStorage に保存します。班の進捗とは別です。保存できない環境でも、そのページ内では操作できます。
- 改善を取りこんだら、`index.html` の「改善ログ」の表に1行足す（これも PR で）。
- **公開ページなので、秘密の情報（.env の中身など）・教材の内容や図・本名・データが写ったスクショは載せない。**
- 班のルールとコードは、非公開のリポジトリ giftia にあります（画面は `giftia-frontend/`、API は `backend/`。2026-11-07 にモノレポにまとめ、giftia-backend はアーカイブ済み）。
