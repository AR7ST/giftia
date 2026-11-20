# #68 日本語全文検索の導入案
#63 のブランド移行後に検証する。FULLTEXT の索引と MATCH は同じ表の同じ列組とする。ブランドマスタの表示名を products.brand に検索用として同期する案。改名時に親と商品側を同じトランザクションで更新できることを確認し、同期差分があれば有効化を保留する。

```sql
CREATE FULLTEXT INDEX idx_products_search
ON products (product_name, brand, description) WITH PARSER ngram;
```

検索条件の候補は `MATCH(product_name, brand, description) AGAINST (%s IN BOOLEAN MODE)`。語ごとに条件を組み、AND で結び、値はパラメータで渡す。構文記号の扱い、ngram のサイズ、ストップワード、照合順序を検証する。1文字、記号、部分一致、語が別列にまたがるケースで旧 LIKE と一致する保証はないため、旧 LIKE を比較基準にし、同等性が確認できない条件は従来検索を使う。検索結果の順位は従来の販売数等を使う。

架空データで単語・複数語・短語・ブランド変更を比較し、件数、ID順、EXPLAIN、実行時間を確認する。切り戻しは先に旧 LIKE へ戻し、管理者が `DROP INDEX idx_products_search ON products` を実行する。
