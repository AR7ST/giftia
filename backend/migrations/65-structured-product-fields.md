# Issue #65 商品情報3列の追加案

## 列の定義

| 列 | 意味 | 値の扱い |
|---|---|---|
| `storage_method` | 商品に明記された保存方法 | 文字列。確認できるまで NULL |
| `shelf_life_days` | 商品に明記された賞味期限の日数 | 0以上の整数。0は起算日当日。起算日や日数が確定できない場合は NULL |
| `is_individually_wrapped` | 個包装の有無 | 1は個包装あり、0は個包装なし、NULLは不明 |

既存の `gift_wrap` は贈答用の包装可否を示す。個包装の有無とは別の項目として維持する。

## 適用手順

1. 管理者が検証環境の MySQL バージョンと `SHOW CREATE TABLE products` を確認する。特に同名の列・制約の有無、`CHECK` 制約の対応状況、DDL 実行時のロックを確認する。バックアップと復元手順を確認し、書き込みへの影響を見込んで実行時間を決める。
2. 適用前に、通常検索の「個包装」、送別検索のスタンプと包装可否を確認し、同じ検証データと検索入力で比較できるようにする。
3. 下記の DDL を検証環境で実行する。MySQL の DDL は暗黙のコミットを伴う。失敗時はテーブル定義を読み直してから次の操作を判断する。

```sql
ALTER TABLE products
    ADD COLUMN storage_method VARCHAR(255) NULL DEFAULT NULL,
    ADD COLUMN shelf_life_days INT UNSIGNED NULL DEFAULT NULL,
    ADD COLUMN is_individually_wrapped TINYINT UNSIGNED NULL DEFAULT NULL,
    ADD CONSTRAINT chk_products_individually_wrapped
        CHECK (is_individually_wrapped IN (0, 1));
```

4. 追加直後は既存商品の3列を NULL のままにする。説明文や `gift_wrap` からの推測で埋めず、入力する場合は確認済みの情報を使う。
5. 同じ条件で変更前後の検索結果を比較する。商品IDの並び、スタンプ、包装可否が一致し、新列に 0・1・NULL が入ることと、個包装に2を指定すると拒否されることを確認する。現行の検索処理は従来の列を参照する。構造化列の参照は後続 Issue #66 で扱う。

## 切り戻し

管理者が後続処理の参照と書き込みを確認する。追加列に値が入っていれば、商品IDと3列を復元できる形で退避する。後続の読み書きがあれば先に旧版へ切り戻し、その後に以下を実行する。

```sql
ALTER TABLE products
    DROP CHECK chk_products_individually_wrapped,
    DROP COLUMN is_individually_wrapped,
    DROP COLUMN shelf_life_days,
    DROP COLUMN storage_method;
```

元の列定義、通常検索と送別検索の結果を再確認する。
