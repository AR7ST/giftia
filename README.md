# Giftia（班のリポジトリ：画面 Next.js ＋ 検索 API FastAPI）

Giftia のギフト検索アプリです。画面（Next.js）と検索 API（FastAPI）を、この1つのリポジトリにまとめています（モノレポ）。班で**できる日に1回**、少しずつ改善していきます（毎日でなくて OK）。
進捗は **[Giftia 改善ボード](https://github.com/users/AR7ST/projects/1)**（GitHub Projects）と、**[ハブページ](https://ar7st.github.io/giftia-hub/)**（giftia-hub）の2つで管理します（→ 4章）。
**作業を始める前に、このファイルを最後まで読んでください。Claude Code を使う人は、最初に「README.md を読んで、ルールを守って作業して」と伝えてください（→ 8章）。**

---

## 1. 全体の構成

```
画面（Next.js・3000番）  →  検索 API（FastAPI・8000番）  →  班の DB（Azure MySQL）
  giftia-frontend/             backend/                          Tech0 から配布
```

このリポジトリは**モノレポ**（画面と API を、1つのリポジトリの中にフォルダを分けて入れた形）です。

```
giftia/（このリポジトリ）
├── giftia-frontend/   ← 画面（Next.js）。npm のコマンドはここで打つ
├── backend/           ← 検索 API（FastAPI）。uvicorn・pip のコマンドはここで打つ
├── README.md          ← このファイル（班の案内とルール）
├── AGENTS.md          ← 班の AI の使い方ルール
└── .gitignore         ← GitHub に上げないファイル（.env など）
```

| リポジトリ | 中身 | URL |
| --- | --- | --- |
| **giftia**（ここ。Private） | 画面と検索 API | https://github.com/AR7ST/giftia |
| **giftia-hub**（公開） | 班のハブページ（入口・改善ログ）。GitHub Pages で公開 | https://github.com/AR7ST/giftia-hub → https://ar7st.github.io/giftia-hub/ |

- giftia は **Private**（招待されたメンバーだけが見られる）。giftia-hub だけ **Public**（だれでも見られる）なので、秘密は置かない。
- 2週目の変更の内容は PR #1 にまとめてある：https://github.com/AR7ST/giftia/pull/1
- 前は画面（giftia-frontend）と API（giftia-backend）を別々のリポジトリにしていた。講師の指摘を受けて、モノレポに組みかえた（Issue #5）。giftia-backend はアーカイブ（読み取り専用）にして残している。

### 主なファイル

| ファイル | 役割 |
| --- | --- |
| `giftia-frontend/app/page.tsx` | 検索画面の本体（タブ・入力欄・検索ボタン・結果） |
| `giftia-frontend/app/ResultCard.tsx` | 結果カード1枚の部品 |
| `giftia-frontend/lib/api.ts` | 検索 API を呼ぶ（`searchGifts()`）。`Gift` 型もここ |
| `giftia-frontend/app/globals.css` | 見た目 |
| `backend/main.py` | 検索 API の窓口（`/api/search`）。条件から SQL を組み立てる |
| `backend/database.py` | `.env` を読んで班の DB につなぐ |

### モノレポにした理由
- 課題「班の開発環境を GitHub で共有する」は、Next.js と FastAPI のフォルダを1つのリポジトリに push する形。教材のフォルダ構成（giftia-frontend と backend を横に並べる）とも同じ。
- clone が1回で済み、画面と API の両方がそろう。
- 画面と API をセットで変えるときも、**PR 1つ**で済む（つなぎ目がずれにくい）。

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
9. PR には、**変更前／変更後のスクリーンショット**を貼る（→ 5章）。本文に `Closes #Issue番号` を書く（→ 4-5）。
10. PR は、**班のだれか1人以上が見て OK してから** `main` に取りこむ（merge）。
11. 画面を変えるときは、API とのつなぎ目（`giftia-frontend/lib/api.ts` の `Gift` 型・`searchGifts()`）を壊さないように注意する。API の項目を増やすときは、`backend/` と**セットで（同じ PR で）**変える。

### コード
12. SQL に入れる値は、`backend/main.py` で `%s` と `params` で渡す（文字列に直接つなげない。SQL インジェクション対策）。
13. この Next.js は新しいバージョンなので、書き方が古い情報とちがうことがある（`giftia-frontend/AGENTS.md` を参照）。

---

## 3. はじめて動かすとき（Windows / PowerShell）

### 3-1. コードを自分の PC にコピーする（最初に1回だけ）
```
cd C:\Services
git clone https://github.com/AR7ST/giftia.git
cd giftia
```
- 置き場所は `C:\Services` などのローカルにする。**デスクトップ（OneDrive）や Google Drive の中は避ける**（npm install が失敗しやすい）。
- これで、GitHub のコードが**まるごと**自分の PC にコピーされる（これまでの記録も全部入っている）。

### 3-2. GitHub に上がっていないので、各自で用意するもの

| もの | 作り方 |
| --- | --- |
| `backend/.env` | `backend/README.md` の手順。配布のシートから**自分で**書く |
| `backend/.venv` | `backend` で `python -m venv .venv` → `pip install -r requirements.txt` |
| `giftia-frontend/.env.local` | 下の 3-3 |
| `giftia-frontend/node_modules` | `npm install` |

### 3-3. 画面の準備
```
cd C:\Services\giftia\giftia-frontend
npm install
Set-Content .env.local "NEXT_PUBLIC_API_URL=http://localhost:8000" -Encoding ascii
```

### 3-4. 起動する（ターミナルを2つ使う）

**ターミナル1：検索 API（8000番）**
```
cd C:\Services\giftia\backend
.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```
- `.venv\Scripts\Activate.ps1` は、**ターミナルを開き直すたびに必要**（行の左に `(.venv)` が付けば OK）。
- `backend/.env` に `CORS_ORIGINS=http://localhost:3000` を入れておく。

**ターミナル2：画面（3000番）**
```
cd C:\Services\giftia\giftia-frontend
npm run dev
```
- ブラウザで http://localhost:3000 を開き、「タオル」で検索して、本物の商品が並べば OK。
- 止めるときは、それぞれのターミナルで `Ctrl + C`。

### 3-5. つまずいたら

| 症状 | 原因と対処 |
| --- | --- |
| 画面に「APIにつながりません：Failed to fetch」 | ターミナル1（API）が起動しているか確かめる |
| Console（F12）に `blocked by CORS policy` | API は動いている。`backend/.env` の `CORS_ORIGINS` に `http://localhost:3000` を書いて、API を起動し直す |
| ターミナルに `>>` が出て止まる | コマンドを貼り付けたときに改行が入った。もう一度 Enter |
| そのほか API 側のエラー | `backend/README.md` の「つまずいたら」 |

---

## 4. 改善の進め方（ボード・Issue・PR・ハブ）

改善は**できる日に1回**で OK。1回の改善は「Issue 1枚 → PR 1つ」で進める。

### 4-1. 使う道具と URL

| 道具 | たとえ | URL | 見られる人 |
| --- | --- | --- | --- |
| **ハブページ** | 班の**玄関**（毎日ここから） | https://ar7st.github.io/giftia-hub/ | URL を知っている人はだれでも（公開） |
| **Giftia 改善ボード**（GitHub Projects） | 付せんを貼る**ホワイトボード** | https://github.com/users/AR7ST/projects/1 | 班のメンバーだけ |
| **Issue** | 付せん1枚＝**やることカード** | https://github.com/AR7ST/giftia/issues | 班のメンバーだけ |
| **PR**（プルリクエスト） | 「清書に入れていい？」の**申請** | https://github.com/AR7ST/giftia/pulls | 班のメンバーだけ |

### 4-2. 1回の改善の流れ（全体図）

```
思いつく
  ↓ ① Issue を作って、ボードに貼る           … 列「やること」
  ↓ ② 担当を決めて、カードを動かす           … 列「作業中」（Slack に一言）
  ↓ ③ ブランチを作って、コードを変える
  ↓ ④ PR を出す（本文に Closes #番号）       … 列「確認待ち」
  ↓ ⑤ 班のだれか1人以上が見て OK
  ↓ ⑥ merge（main に取りこむ）               … 列「完了」に自動で動く
  ↓ ⑦ ハブの「改善ログ」に1行足す
おしまい（次の人は、新しい main から始める）
```

### 4-3. Issue（やることカード）の作り方

**どこに作る？**
- 画面も API も、Issue は**このリポジトリ（giftia）に1枚**。本文の「変えそうなファイル」に、`giftia-frontend/…` か `backend/…` かを書く

**作り方（ブラウザ。スマホでもできる）**
1. リポジトリの **Issues** タブ → **New issue**
2. **Title**（タイトル）：何をするかを1行で。例「結果カードに星の評価を表示する」
3. 本文：下の型をコピーして埋める
4. 右側の **Assignees**（担当）：やる人を選ぶ（まだ決まっていなければ空でよい）
5. 右側の **Projects**：**Giftia 改善ボード** を選ぶ ← **忘れずに**（ボードに貼られる）
6. **Create** を押す

**本文の型**
```
## やりたいこと
（例）結果カードに、評価を ★ の数で表示したい

## なぜ
（例）数字だけだと、パッと見て良さがわからない

## 終わりの目安
（例）カードに ★★★★☆ のように出る

## 変えそうなファイル
（例）giftia-frontend/app/ResultCard.tsx
```

**コツ**
- **1回（1日）で終わる大きさ**にする。大きいときは Issue を分ける。
- 思いついただけのアイデアも、担当なしで Issue にして「やること」に置いてよい（アイデア置き場になる）。
- Issue は非公開だが、**パスワードなどの秘密は書かない**（ルール1）。

### 4-4. ボード（Giftia 改善ボード）の使い方

| 列 | 意味 | だれが動かす | いつ |
| --- | --- | --- | --- |
| **やること** | まだ始めていない | Issue を作った人 | Issue を作ったとき |
| **作業中** | 手をつけている | 担当の人 | 作業を始めるとき（Slack にも一言） |
| **確認待ち** | PR を出して、見てもらっている | 担当の人 | PR を出したとき |
| **完了** | main に取りこみ済み | **自動** | Issue が閉じたとき |

- カードは**ドラッグ**で別の列へ動かす（スマホは、カードを開いて Status を変える）。
- **作業中は1人1枚まで。** 終わってから次を取る。
- カードを押すと、Issue の本文やコメントが横に開く。
- **自動で「完了」へ動くしくみ**：PR の本文に `Closes #番号` と書いておくと、PR を merge したときに Issue が自動で閉じ、カードが「完了」に動く。（Issue も PR も giftia にあるので、いつも使える）
- ボードの「+ Add item」で直接メモ（Draft）も書ける。作業するときは、カードの「⋯」→ **Convert to issue** で Issue にする。
- 見方を変える：上の **New view → Table** で一覧表にもできる。上の検索欄に `assignee:@me` と入れると、自分のカードだけになる。

### 4-5. PR の出し方（Issue とつなぐ）

**ブランチ名**：`Issue番号-内容`（英語・小文字・ハイフン）　例 `12-rating-stars`

```
git switch main
git pull
git switch -c 12-rating-stars
（コードを変えて、npm run dev などで確かめる。変更前／変更後のスクショを撮る）
git add 変えたファイル
git commit -m "結果カードに星の評価を表示"
git push -u origin 12-rating-stars
```

GitHub に「Compare & pull request」の黄色い帯が出るので押す。**PR の本文の型**：
```
Closes #12

## 変えたこと
（例）結果カードの評価を ★ で表示した

## 変更前 / 変更後
（スクショをドラッグ＆ドロップで貼る）

## 確かめたこと
（例）タオルで検索して、★ が出ることを確かめた
```
- PR を出したら、カードを「**確認待ち**」へ動かし、Slack で「PR 出しました、見てください」と一言。
- **見る人**：PR の **Files changed** → 右上の **Review changes** → **Approve**（OK）か、**Comment**（気になる点）。
- OK が1人以上ついたら、**Merge pull request** → **Confirm merge**。そのあと出る **Delete branch** は押してよい（下書きノートの片付け）。
- 自分の PC も片付ける：`git switch main` → `git pull`

**画面（giftia-frontend）と API（backend）をセットで変えるとき**
- モノレポなので、**Issue 1枚・PR 1つ**で、両方のフォルダをまとめて変えられる。
- PR の「確かめたこと」に、画面（`npm run dev`）と API（`/docs`）の両方で確かめたことを書く。

### 4-6. ハブページの更新（改善ログを1行足す）

merge した人が、ハブの「改善ログ」に1行足す。**ブラウザだけでできる**（コマンド不要）。

1. https://github.com/AR7ST/giftia-hub を開く → **index.html** を押す
2. 右上の **鉛筆マーク**（Edit this file）を押す
3. 「改善ログ」の表（`<table>` の中）の**最後の行の下**に、1行足す
   ```
       <tr><td>2026-11-05</td><td>結果カードに星の評価を表示した</td><td>giftia #3</td></tr>
   ```
   （日付・変えたこと・PR 番号。**名前は書かない**）
4. 右上の **Commit changes...** → **Create a new branch for this commit and start a pull request** を選ぶ → **Propose changes** → **Create pull request**
5. 自分で中身を確かめて **Merge**（ログの追加だけなら、班の OK を待たなくてよい）
6. 1〜2分でページに反映される（**Actions** タブに緑のチェックが付けば完了）。古いままなら `Ctrl + F5`

**ハブに載せてはいけないもの（公開ページ）**
- `.env` の中身（DB のホスト名・ユーザー名・パスワード）、API キー
- 教材（PDF など）の内容や図
- 本名などの個人情報
- DB の商品データが写った画面のスクショ（載せたいときは講師に確認）

**ハブのリンクやルールの要点を変えるとき**は、ふつうの改善と同じく、Slack で一言 → PR → 班の OK → merge。

### 4-7. 週1回のふりかえり（おすすめ・5分）

ボードを見ながら、Slack かミーティングで話す。
- 今週「完了」になったカードは？（ハブの改善ログとも照らし合わせる）
- 「作業中」のまま止まっているカードは？ 困っていることは？
- 次にやる「やること」はどれ？ 担当はだれ？
- 「完了」のカードがたまったら、カードの「⋯」→ **Archive** で片付けてよい（消えるのではなく、しまうだけ）

### 4-8. 2段構えの見直し

ボードとハブは**お試し**で始めた。2週間ほど使ったら、班で話して決める。
- 両方使う／ボードだけにする／ハブだけにする
- ハブの更新が面倒になったら、Issue や PR から自動で進捗ページを作る（GitHub Actions）ことも考える

### 4-9. だれが何をできるか（班長だけではなく、みんなで改善する）

| 場所 | 班のメンバー（招待済み） | 持ち主だけ | 班の外の人 |
| --- | --- | --- | --- |
| giftia（画面と API） | ブランチ・PR・レビュー・merge・Issue | 招待・設定・削除 | 見られない |
| Giftia 改善ボード | カードを足す・動かす・Archive | メンバーの追加・列や自動の設定 | 見られない |
| giftia-hub | ページを直す（改善ログなど） | Pages の設定・招待 | **見るだけ** |

- 自分のカードは自分で動かす。担当者のアイコンで「だれが何をしているか」がわかる。
- 招待や設定が必要なときは、Slack で持ち主に頼む。

### 4-10. 困ったとき

| こまりごと | 対処 |
| --- | --- |
| merge したのに、カードが「完了」に動かない | PR 本文に `Closes #番号` がない。カードを手で「完了」へ動かす |
| Issue を作ったのに、ボードに出ない | Issue の右側の **Projects** で「Giftia 改善ボード」を選ぶ |
| ハブを直したのに、ページが変わらない | 1〜2分待って `Ctrl + F5`。giftia-hub の **Actions** タブで赤い × が出ていたら持ち主に連絡 |
| 2人が同じところを変えそう | Slack で相談して、どちらかが先に merge。あとの人は `git pull` してから続ける |
| Issue をまちがえて作った | Issue の下の **Close issue ▼** → **Close as not planned**（理由を一言） |
| 自分の PC に変更が来ない | 作業の前に `git switch main` → `git pull`（自動では同じにならない） |

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
| フォルダ（`giftia`） | **作業机** | 自分の PC の中の作業場所 |
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
- コードを書く前に `AGENTS.md`（一番上）と `giftia-frontend/AGENTS.md`（Next.js の注意）を読む。
- 説明は日本語で、専門用語には一言の言い換えを付ける。
