# Issue #69 商品の主キーを数値IDに移行する案

DB管理者が検証環境で各段階を実行する。最初に `SHOW CREATE TABLE` と外部キーの一覧で参照元を確認し、以下の3表以外の参照や既存の自動採番列が見つかれば手順を見直す。バックアップからの復元を確認し、定義変更に必要な時間とロックを測る。商品・注文明細・シーン・レビューの書き込みは、移行中に停止するか、旧・新のキーを同じトランザクションで更新できるようにする。

## 1. 商品に数値IDを追加する

```sql
ALTER TABLE products
    ADD COLUMN id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ADD UNIQUE KEY uq_products_numeric_id (id),
    ADD UNIQUE KEY uq_products_product_code (product_id);
```

既存の主キーはこの段階では商品コードのまま。既存商品への採番後、商品コードと数値IDの対応を保存し、重複や欠損がないことを確認する。

## 2. 子テーブルへ数値IDを追加する

```sql
ALTER TABLE order_items ADD COLUMN product_numeric_id BIGINT UNSIGNED NULL;
ALTER TABLE product_scenes ADD COLUMN product_numeric_id BIGINT UNSIGNED NULL;
ALTER TABLE reviews ADD COLUMN product_numeric_id BIGINT UNSIGNED NULL;
```

以下を3表に適用する。表名は `order_items`、`product_scenes`、`reviews` の固定値から選ぶ。必要に応じ、各表の主キー範囲で分割し、再開位置を記録する。

```sql
UPDATE order_items AS child
JOIN products AS p ON p.product_id = child.product_id
SET child.product_numeric_id = p.id
WHERE NOT (child.product_numeric_id <=> p.id);

SELECT COUNT(*) AS mismatches
FROM order_items AS child
LEFT JOIN products AS p ON p.product_id = child.product_id
WHERE (child.product_id IS NOT NULL AND p.id IS NULL)
   OR NOT (child.product_numeric_id <=> p.id);
```

不一致が0件になるまで制約付与・切替を行わない。既存参照が NULL を許容する表は新列も NULL を維持する。必須の表は、書き込み側の切替後に NOT NULL を検討する。

```sql
ALTER TABLE order_items
    ADD CONSTRAINT fk_order_items_product_numeric
    FOREIGN KEY (product_numeric_id) REFERENCES products (id);
ALTER TABLE product_scenes
    ADD CONSTRAINT fk_product_scenes_product_numeric
    FOREIGN KEY (product_numeric_id) REFERENCES products (id);
ALTER TABLE reviews
    ADD CONSTRAINT fk_reviews_product_numeric
    FOREIGN KEY (product_numeric_id) REFERENCES products (id);
```

適用前に、各表の削除・更新ルールを既存の外部キーと照合する。上記の既定動作が既存ルールと異なる場合は、二重参照が既存処理を阻害しないよう検証環境で確認し、定義を揃える。

## 3. 主キーを切り替える

数値IDの外部キー、商品コードの一意索引、既存の外部キーを確認してから、検証環境で次を実行する。

```sql
ALTER TABLE products DROP PRIMARY KEY, ADD PRIMARY KEY (id);
```

既存の外部キーが旧主キーの索引に依存して切替が拒否された場合は、移行を中断する。検証環境で依存関係と参照オプションを控え、書き込みを止めた上で既存制約を一意索引に付け直せることを確認する。外部キー検査を無効にして回避しない。後続 #70・#72 の新規テーブルは `products.id` と同じ `BIGINT UNSIGNED` を参照する。

公開の通常検索と送別検索が返す商品IDは既存の `product_id` とする。テーブル操作の前後で検索結果の件数・ID・順序、新規注文、既存注文の明細、レビュー・タグ参照、既存の削除動作を検証環境で比較する。この案ではテーブルごとの既存の複合キーを保持する。

## 切り戻し

書き込みを停止し、利用中の処理を旧商品コード参照へ切り戻す。後続の数値ID参照があれば先に解除または切替し、数値IDと商品コードの対応を退避する。主キー切替済みなら、数値ID側の一意索引が残っていることを確認し、`ALTER TABLE products DROP PRIMARY KEY, ADD PRIMARY KEY (product_id)` で旧主キーを戻す。ここで運用を復旧できる場合、追加列は残せる。撤去する場合は3表の新規外部キーと列、新たに作成された不要な索引、親の数値IDの順に撤去し、既存制約と検索・注文を再確認する。DDL は暗黙にコミットされるため、途中失敗時は実施済みの定義を確認してから再開する。

[MySQL の外部キー](https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html) · [暗黙のコミット](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html)
