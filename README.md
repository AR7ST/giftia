# Giftia（班のリポジトリ：画面 Next.js）

Giftia のギフト検索画面です。班で**できる日に1回**、少しずつ改善していきます（毎日でなくて OK）。
進捗は **GitHub Projects のボード「Giftia 改善ボード」** と、**班のハブページ（giftia-hub）** の2つで管理します（→ 4章）。
**作業を始める前に、このファイルを最後まで読んでください。Claude Code を使う人は、最初に「README.md を読んで、ルールを守って作業して」と伝えてください（→ 8章）。**

---

## 1. 全体の構成

```
画面（Next.js・3000番）  →  検索 API（FastAPI・8000番）  →  班の DB（Azure MySQL）
  このリポジトリ               giftia-backend                    Tech0 から配布
```

| リポジトリ | 中身 | URL |
| --- | --- | --- |
| **giftia-frontend**（ここ） | 画面（Next.js）。1週目の検索画面＋2週目の変更 | https://github.com/AR7ST/giftia-frontend |
| **giftia-backend** | 検索 API（FastAPI）。起動の手順は giftia-backend の README | https://github.com/AR7ST/giftia-backend |

- どちらも **Private**（招待されたメンバーだけが見られる）。
- 2週目の変更の内容は PR #1 にまとめてある：https://github.com/AR7ST/giftia-frontend/pull/1

### 主なファイル

| ファイル | 役割 |
| --- | --- |
| `app/page.tsx` | 検索画面の本体（タブ・入力欄・検索ボタン・結果） |
| `app/ResultCard.tsx` | 結果カード1枚の部品 |
| `lib/api.ts` | 検索 API を呼ぶ（`searchGifts()`）。`Gift` 型もここ |
| `app/globals.css` | 見た目 |

### リポジトリを2つに分けた理由
- 教材のフォルダ構成が「giftia-frontend と backend を横に並べる」形。backend を画面のリポジトリの中に入れると、フォルダを移して仮想環境（.venv）を作り直す必要があった。
- 教材と同じ形のまま使えるように、API 用に giftia-backend を別に作った。
- 「**画面を変えるなら frontend、検索の中身（SQL）を変えるなら backend**」と、役割と名前がそろう。

---

## 2. 班のルール（必ず守る）

### 秘密の情報
1. **`.env`（DB のホスト名・ユーザー名・パスワード）の中身は、GitHub・Slack・生成 AI（Claude など）に貼らない。** スクリーンショットにも写さない。
2. `.env`・`.env.local` は `.gitignore` で除外してある。**除外の設定を消さない。**
3. 教材の PDF など、**Tech0 の Confidential 資料は GitHub に上げない。**
4. `.env.local` に書くのは API の場所だけ。`NEXT_PUBLIC_` で始まる値はブラウザに配られて誰でも見られるので、**パスワードや API キーは書かない。**

### 変更のしかた
5. **`main` に直接 push しない。** 変更は必ず新しいブランチで作り、**プルリクエスト（PR）** で出す。
6. **作業を始める前に `git pull`** で最新の `main` をもらう（自動では同じにならない）。
7. **「今日はだれが何を変えるか」を Slack で軽く決めてから**始める（同じ行を2人が同時に変えると、ぶつかる）。
8. **1つの PR には、1つの変更だけ**（1回の改善の単位）。
9. PR には、**変更前／変更後のスクリーンショット**を貼る（→ 5章）。
10. PR は、**班のだれか1人以上が見て OK してから** `main` に取りこむ（merge）。
11. 画面を変えるときは、API とのつなぎ目（`lib/api.ts` の `Gift` 型・`searchGifts()`）を壊さないように注意する。API の項目を増やすときは、giftia-backend と**セットで**変える。

### コード
12. SQL に入れる値は、giftia-backend で `%s` と `params` で渡す（文字列に直接つなげない。SQL インジェクション対策）。
13. この Next.js は新しいバージョンなので、書き方が古い情報とちがうことがある（`AGENTS.md` を参照）。

---

## 3. はじめて動かすとき（Windows / PowerShell）

### 3-1. コードを自分の PC にコピーする（最初に1回だけ）
```
cd C:\Services
git clone https://github.com/AR7ST/giftia-frontend.git
git clone https://github.com/AR7ST/giftia-backend.git
```
- 置き場所は `C:\Services` などのローカルにする。**デスクトップ（OneDrive）や Google Drive の中は避ける**（npm install が失敗しやすい）。
- これで、GitHub のコードが**まるごと**自分の PC にコピーされる（これまでの記録も全部入っている）。

### 3-2. GitHub に上がっていないので、各自で用意するもの

| もの | 作り方 |
| --- | --- |
| `giftia-backend/.env` | giftia-backend の README の手順。配布のシートから**自分で**書く |
| `giftia-backend/.venv` | `python -m venv .venv` → `pip install -r requirements.txt` |
| `giftia-frontend/.env.local` | 下の 3-3 |
| `giftia-frontend/node_modules` | `npm install` |

### 3-3. 画面の準備
```
cd C:\Services\giftia-frontend
npm install
Set-Content .env.local "NEXT_PUBLIC_API_URL=http://localhost:8000" -Encoding ascii
```

### 3-4. 起動する（ターミナルを2つ使う）

**ターミナル1：検索 API（8000番）**
```
cd C:\Services\giftia-backend
.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```
- `.venv\Scripts\Activate.ps1` は、**ターミナルを開き直すたびに必要**（行の左に `(.venv)` が付けば OK）。
- giftia-backend の `.env` に `CORS_ORIGINS=http://localhost:3000` を入れておく。

**ターミナル2：画面（3000番）**
```
cd C:\Services\giftia-frontend
npm run dev
```
- ブラウザで http://localhost:3000 を開き、「タオル」で検索して、本物の商品が並べば OK。
- 止めるときは、それぞれのターミナルで `Ctrl + C`。

### 3-5. つまずいたら

| 症状 | 原因と対処 |
| --- | --- |
| 画面に「APIにつながりません：Failed to fetch」 | ターミナル1（API）が起動しているか確かめる |
| Console（F12）に `blocked by CORS policy` | API は動いている。giftia-backend の `.env` の `CORS_ORIGINS` に `http://localhost:3000` を書いて、API を起動し直す |
| ターミナルに `>>` が出て止まる | コマンドを貼り付けたときに改行が入った。もう一度 Enter |
| そのほか API 側のエラー | giftia-backend の README の「つまずいたら」 |

---

## 4. 改善の流れ（できる日に1回）

0. **やりたいことを Issue（やることカード）にして、「Giftia 改善ボード」に貼る。** 担当を決めて「作業中」に動かす。
1. **変更する人**
   ```
   git switch main
   git pull
   git switch -c 変更の名前（例：add-rating-stars）
   ```
2. コードを変えて、自分の PC で動かして確かめる。**変更前／変更後のスクリーンショット**を撮る。
3. 記録して、GitHub に届ける
   ```
   git add 変えたファイル
   git commit -m "何を変えたか"
   git push -u origin 変更の名前
   ```
4. GitHub で **PR を作る**。説明に「何を変えたか」とスクショを貼る（画像はドラッグ＆ドロップで貼れる）。
5. **班のみんな**：GitHub で PR を見て、コメント（「いいね」「ここはこうしたら？」）。
6. OK なら **Merge pull request** で `main` に取りこむ。→ 次の日の人は、新しい `main` から始める。

- PR の記録は残るので、**改善の変化を、あとから順番に見返せる**（Giftia の成長日記）。

### 進捗の管理（2段構え・使いやすい方を残す）

| 道具 | 中身 | 見られる人 |
| --- | --- | --- |
| **Giftia 改善ボード**（GitHub Projects） | やることカード（やること／作業中／確認待ち／完了）。PR を取りこむと自動で「完了」へ | 班のメンバーだけ |
| **ハブページ**（giftia-hub） | 入口（リンク集）・全体の流れ図・ルールの要点・改善ログ | **URL を知っている人はだれでも**（公開） |

- PR を取りこんだ人は、ハブの「改善ログ」に1行足す（日付・担当・変えたこと・PR 番号）。
- Issue（やることカード）は、非公開の giftia-frontend / giftia-backend で作る（giftia-hub の Issue 機能は切っておく）。

### だれが何をできるか（班長だけではなく、みんなで改善する）

| 場所 | 班のメンバー（招待済み） | 持ち主だけ | 班の外の人 |
| --- | --- | --- | --- |
| giftia-frontend / backend | ブランチ・PR・コメント・取りこみ・Issue | 招待・設定・削除 | 見られない |
| Giftia 改善ボード | カードを足す・動かす | メンバーの追加・設定 | 見られない |
| giftia-hub | PR でページを直す（改善ログなど） | Pages の設定・招待 | **見るだけ** |

- 自分のカードは自分で動かす。担当者の名前で「だれが何をしているか」がわかる。
- 招待や設定が必要なときは、Slack で持ち主に頼む。
- **ハブは公開ページ。** `.env` の中身・教材の内容や図・本名・DB の商品データが写ったスクショは載せない。

---

## 5. 変更を確かめる方法と、PC・スマホの分担

### 変更を確かめる3つの方法

| 方法 | 見られるもの | どこで |
| --- | --- | --- |
| ① PR の **Files changed** タブ | **コード**の変更（緑＝足した行、赤＝消した行）。見た目はわからない | PC・スマホ |
| ② PR に貼った **変更前／変更後のスクショ** | **画面の見た目**の変化。動かさなくても GitHub を開くだけでわかる | PC・スマホ |
| ③ **自分の PC で動かす** | 実際に触った**動き**（ボタンを押したときなど） | **PC だけ** |

③のやり方（PR #2 の場合）
```
gh pr checkout 2      ← PR #2 のコードに切りかえる（GitHub CLI が必要）
npm run dev           ← 画面で確かめる
git switch main       ← 元に戻す
```

### PC とスマホの分担

| やりたいこと | スマホ | PC |
| --- | --- | --- |
| PR を見る（説明・スクショ・コメント） | ✅（GitHub アプリ、またはブラウザ） | ✅ |
| Files changed（コードの変更）を見る | ✅（画面が小さいので少し見にくい） | ✅ |
| コメントする・「いいね」する | ✅ | ✅ |
| PR を承認する・`main` に取りこむ | ✅ | ✅ |
| **画面を実際に動かす・スクショを撮る** | ❌ | ✅ |
| **コードを変える・PR を出す** | ❌ | ✅ |

- **「見る・コメントする・取りこむ」はスマホで OK、「作る・動かす」は PC。**
- 画面を動かせるのが PC だけなのは、`localhost` が「その PC の中だけの住所」だから。

---

## 6. git のたとえ話（作業机とノートと共有本棚）

| git の言葉 | たとえ | 意味 |
| --- | --- | --- |
| フォルダ（`giftia-frontend`） | **作業机** | 自分の PC の中の作業場所 |
| ブランチ | **ノート** | `main` ＝ 班の**清書ノート**。変更は**下書きノート**で作る |
| コミット | ノートの**1ページ** | 変更を1まとまりで記録する。**前のページも全部残る**ので、どの時点にも戻れる |
| GitHub | **班の共有本棚** | みんなのノートを置く場所 |
| clone | 本棚のノートを**まるごとコピー**して自分の机に置く | 最初に1回だけ |
| push | 自分の下書きノートを本棚に**届ける** | |
| PR | 「この下書きを清書に入れていい？」という**申請** | 班で見て、OK なら取りこむ |
| pull | 清書ノートの**新しいページを、自分のコピーに書き写す** | 作業を始める前に毎回 |
| switch / checkout | 机の上の**ノートを取りかえる** | フォルダの中身が、そのノートの内容に切りかわる |

- 下書きノートに取りかえると、机の上（フォルダの中身）は入れかわる。でも、**清書ノート（`main`）は変わらない**。`git switch main` でいつでも戻れる。
- `.env`・`.env.local`・`node_modules`・`.venv` は git で運ばないので、どのノートにしても机の上に残る。
- 切りかえる前は、書きかけの変更がないこと（あると git が止める）。

---

## 7. 今後の候補：みんなが1つの URL で画面を見る（デプロイ）

- 画面と API をインターネット上のサーバーに置く（デプロイ）と、班のだれでも1つの URL で同じ画面を見られる。`main` に取りこむたびに自動で更新することもできる。
- **講師に確認してから進める：** Tech0 の DB に外のサーバーからつないでよいか／デプロイ先の指定はあるか／料金。
- それまでは、各自の PC で動かす（3章）＋ PR のスクショ（5章）で進める。

---

## 8. Claude Code（生成 AI）を使う人へ

作業を始めるとき、Claude Code に最初にこう伝える：

> README.md を読んで、2章の班のルールを守って作業してください。

Claude Code に守ってもらうこと：
- **`.env` を読まない・中身を表示しない・どこにも貼らない。** 接続情報が載ったスプレッドシートも開かない。
- `main` に直接 push しない。ブランチを作って PR で出す（2章のルール5）。
- ファイルの削除・移動・上書きの前に、何をするかを説明して、使う人の OK をもらう。
- GitHub への push や PR の作成・merge は、使う人の OK が出てから。
- コードを書く前に `AGENTS.md` を読む（この Next.js は新しいバージョン）。
- 説明は日本語で、専門用語には一言の言い換えを付ける。
