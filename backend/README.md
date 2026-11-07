# backend（Giftia 検索 API・FastAPI）

Giftia の検索画面（同じリポジトリの [`giftia-frontend/`](../giftia-frontend)）から呼ばれる検索 API です。
班のルールと全体の起動手順は、リポジトリの一番上の [README.md](../README.md) を見てください。
画面から条件を受け取り、班の DB（Azure Database for MySQL）を検索して、結果を JSON で返します。

```
画面（Next.js・3000番） → この API（FastAPI・8000番） → 班の DB（Azure MySQL）
```

## ファイル

| ファイル | 役割 |
| --- | --- |
| `main.py` | API の窓口。`/api/health`（接続確認）と `/api/search`（商品検索） |
| `database.py` | `.env` の接続情報を読んで DB につなぐ |
| `requirements.txt` | 使うライブラリの一覧 |
| `.env.example` | 接続情報の型紙。これをコピーして `.env` を作る |

## はじめて動かすとき（Windows / PowerShell）

1. フォルダに移動する（リポジトリの一番上から）
   ```
   cd backend
   ```
2. 仮想環境（このフォルダ専用の部品箱）を作る
   ```
   python -m venv .venv
   ```
3. 仮想環境を有効にする（行の左に `(.venv)` が付けば OK。**ターミナルを開き直すたびに必要**）
   ```
   .venv\Scripts\Activate.ps1
   ```
4. ライブラリを入れる
   ```
   pip install -r requirements.txt
   ```
5. `.env` を作る
   ```
   Copy-Item .env.example .env
   ```
   `.env` を開いて、配布された自分の班の接続情報を書く。
   - `=` から先を、かっこ（説明）ごと書きかえる。`=` の前後にスペースを入れない
   - `DB_NAME` は `giftia_t` ＋ クラス番号 ＋ 班番号 の形
   - `DB_SSL_CA` は証明書ファイルの場所。区切りは `/`（例 `C:/Users/<自分>/certs/DigiCertGlobalRootG2.crt.pem`）
   - 画面とつなぐときは `CORS_ORIGINS=http://localhost:3000`
6. 起動する
   ```
   uvicorn main:app --reload
   ```
7. ブラウザで確かめる
   - http://localhost:8000/api/health … 班の DB 名と商品数が出れば接続 OK
   - http://localhost:8000/docs … API を画面なしで試せる（`/api/search` → Try it out → q に「タオル」→ Execute）

止めるときは `Ctrl + C`。`.env` を変えたら、止めてもう一度起動する（`--reload` は `.env` の変更に気づかない）。

## 注意

- **`.env`（DB のパスワードなど）は GitHub に上げない・生成 AI やチャットに貼らない。** `.gitignore` で除外してある
- SQL に入れる値は `%s` と `params` で渡す（文字列に直接つなげない。SQL インジェクション対策）

## つまずいたら

| 症状 | 原因と対処 |
| --- | --- |
| `ModuleNotFoundError: No module named 'fastapi'` | `(.venv)` が付いていない、または `pip install -r requirements.txt` をしていない |
| `OSError: .env に設定がありません: …` | `.env` のその項目が空。書いて保存し、起動し直す |
| `Access denied … to database '…'`（1044） | パスワードは合っている。`DB_NAME` がちがう |
| `Access denied for user …`（1045） | ユーザー名かパスワードがちがう |
| 画面に「APIにつながりません」、Console に `blocked by CORS policy` | API は動いている。`.env` の `CORS_ORIGINS` に画面の URL を書いて、起動し直す |
