# Issue #67 商品の数量・単位の移行案

`quantity_value` は商品の数量、`quantity_unit` はその単位。初期の許容値案は `piece`（個）、`g`（グラム）、`ml`（ミリリットル）。確定前に改善計画・ER図・要件定義書の列名と単位をこの表記にそろえる。個数は整数、重量・容量は小数第3位までとする。既存の `size` などから数量を確定できない場合は、両列を NULL のままにする。

## 移行手順

1. 管理者が検証環境で MySQL のバージョン、`SHOW CREATE TABLE products`、同名の列・制約の有無、CHECK 制約の有効性を確認する。バックアップと復元手順を検証し、DDL による書き込みへの影響を確認する。
2. 次の定義案を検証環境で実行する。既存行は両列とも NULL で開始する。

```sql
ALTER TABLE products
    ADD COLUMN quantity_value DECIMAL(12,3) NULL DEFAULT NULL,
    ADD COLUMN quantity_unit VARCHAR(8) CHARACTER SET ascii COLLATE ascii_bin NULL DEFAULT NULL,
    ADD CONSTRAINT chk_products_quantity CHECK (
        (quantity_value IS NULL AND quantity_unit IS NULL)
        OR (
            quantity_value IS NOT NULL AND quantity_unit IS NOT NULL
            AND quantity_value > 0
            AND quantity_unit IN ('piece', 'g', 'ml')
            AND (quantity_unit <> 'piece' OR quantity_value = FLOOR(quantity_value))
        )
    );
```

3. 根拠を確認できた値だけ、対象の商品IDを指定して数量と単位を同じ更新で登録する。kg から g など同じ種類の単位は換算できる。個数と重量の換算は行わない。導入直後は旧列も維持する。

## 検索の切り替えと確認

数量条件を使う場合は、許容リストにある単位を必須とする。最小値の条件例は `quantity_unit = %s AND quantity_value >= %s`。パラメータに単位と数値を渡す。範囲の上限を設ける場合も同じ単位内で比較する。通常検索の件数・明細、送別検索の件数・候補取得で条件を一致させる。数量条件がない既存検索には両列の条件を追加しない。

架空データで、10個・10g・10mlを用意し、10個以上の検索で10個の商品だけが出ることを確認する。単位なし・未知の単位・片方だけNULL・小数の個数は拒否し、単位指定時は数量不明の商品を除く。数量条件なしの場合は、適用前と商品ID・件数・並び順を比較する。データベースに列が追加されたことを確認してから検索変更を有効にする。

## 切り戻し

数量列を参照するアプリを先に旧版へ戻す。追加列に値が入っていれば、管理者が商品IDと2列を退避してから、次の定義変更を行う。DDL は暗黙のコミットを伴うため、失敗後は定義を確認して再開する。

```sql
ALTER TABLE products
    DROP CHECK chk_products_quantity,
    DROP COLUMN quantity_unit,
    DROP COLUMN quantity_value;
```

旧版の検索と商品表示を再確認する。
