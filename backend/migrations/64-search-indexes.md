# #64 検索索引の導入案
検証環境で既存索引と MySQL のバージョンを確認し、通常・送別検索の件数取得と結果取得それぞれの EXPLAIN を記録する。

```sql
CREATE INDEX idx_products_stock_price ON products (stock, price);
-- #63 の適用、カテゴリIDで検索する処理の検証後に実行
CREATE INDEX idx_products_cat_sales ON products (category_id, sales_count DESC);
```

カテゴリ索引は検索条件が category_id の等価比較になってから評価する。#63 の外部キーを支える索引が別にあるかも確認する。stock > 0 は範囲条件なので、後続の price が検索範囲の絞り込みに使われるとは限らない。複数の予算帯・カテゴリ・キーワード条件で、選択索引、走査行数、ソート、実行時間を適用前後で比較する。商品ID、順序、件数の一致を確認する。効果が得られない候補は採用を保留する。

切り戻しは追加した索引だけを DROP INDEX する。カテゴリ索引が外部キーに必要な場合は、同じ先頭列の代替索引を先に用意し、制約を維持する。DDL 適用と実行計画の確認は管理者が行う。
