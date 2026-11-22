# 班の DB の変更 SQL（#63〜#72）

改善計画の DB の変更を、MySQL Workbench でそのまま実行できる形にまとめたものです。
手元の PC に本番の写しの DB を作り、この順番で流して、すべての確認が「OK」になることを確かめました（2026-11-22）。

## 実行する順番

| 順 | ファイル | 中身 |
|---|---|---|
| 0 | （バックアップ） | 実行の直前に、mysqldump で DB を書き出す（下の「バックアップ」） |
| 1 | `01_65_67.sql` | #65 保存方法・賞味期限・個包装の列／#67 数量・単位の列 |
| 2 | `02_64_63_68.sql` | #64 索引／#63 カテゴリ・ブランドのマスタ／#68 全文検索の索引 |
| 3 | `03_69.sql` | #69 商品の主キーを数字の `id` に移す（子の4表を含む） |
| 4 | `04_70_71_72.sql` | #70 税区分・価格履歴／#71 生年・監査列・状態／#72 属性表・評価の集計 |
| 5 | `05_check.sql` | できあがりの照合（列・索引・制約・データを短い記号にする） |

- 各ファイルの最後に、確認の表が出ます。**すべて「OK」なら次へ。1つでも「NG」なら、そこで止めて相談する**
- 本当の件数は書いていません。元のデータと数が合っているかで確かめます
- `05_check.sql` の結果を、手元で作った DB の結果と比べると、同じ DB になったかがわかります

## 実行の前に

- 右上の接続名と `SELECT @@version;` の結果で、**どの DB サーバーにつないでいるか**を毎回確かめる
- DB のユーザーはクラス全体で共有です。SQL はすべて `giftia_t503.表名` と DB 名を付けて書いてあります
- `ALTER TABLE` などは、実行したその場で確定し、`ROLLBACK` では戻りません。元に戻すときは、バックアップから戻します
- `#70` の税区分は、カテゴリから決めた**仮の値**です（食品・飲料は 8%、ほかは 10%）

## バックアップ（PowerShell）

ホスト名・ユーザー名・パスワードは、実行するときに入力します。どこにも書かないでください。

```powershell
$h = Read-Host "ホスト名"; $u = Read-Host "ユーザー名"; & "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe" --host=$h --user=$u -p --single-transaction --no-tablespaces --set-gtid-purged=OFF --skip-triggers --default-character-set=utf8mb4 --result-file="C:\Services\giftia-localdb\giftia_t503_backup.sql" giftia_t503
```

書き出したファイルは、GitHub に上げないでください（DB の本当のデータが入っています）。

## 手元の PC に、同じ DB を作るとき

1. PC に MySQL 8.4 を入れる
2. 上の「バックアップ」と同じ方法で、班の DB を書き出す
3. PC の MySQL に読み込む

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" --host=127.0.0.1 --user=root -p --default-character-set=utf8mb4 -e "CREATE DATABASE giftia_t503 CHARACTER SET utf8mb4 COLLATE utf8mb4_ja_0900_as_cs; USE giftia_t503; source C:/Services/giftia-localdb/giftia_t503_backup.sql"
```

4. この順番で `01`〜`04` を流し、`05_check.sql` で確かめる

PC と本番は DB 名が同じです。`SELECT @@version;` の結果で見分けてください。
