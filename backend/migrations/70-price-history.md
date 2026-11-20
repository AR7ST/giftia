# #70 価格履歴と税区分の移行案
#69 の products.id が BIGINT UNSIGNED になった検証環境で試す。現行価格の型と税込・税抜の意味を確認する。例は整数円を前提とする。

```sql
ALTER TABLE products ADD COLUMN tax_category ENUM('standard_10', 'reduced_8') NULL;
CREATE TABLE product_price_histories (
    product_id BIGINT UNSIGNED NOT NULL,
    effective_from DATETIME(6) NOT NULL,
    effective_to DATETIME(6) NULL,
    price BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (product_id, effective_from),
    CONSTRAINT fk_price_history_product FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT chk_price_history_period CHECK (effective_to IS NULL OR effective_to > effective_from)
) ENGINE=InnoDB;
```

初回は既存価格を切替時刻から登録する。過去の価格は根拠がある期間だけ入れ、税区分の不明値は NULL。既存売上は order_items.unit_price を使用する。期間は UTC の開始を含み、終了を含まない。価格更新は親商品を SELECT FOR UPDATE でロックし、現在の区間を新価格の開始時刻で閉じ、同時刻から新しい区間を開き、products.price の更新と同じトランザクションで確定する。書き込み経路をこの処理に集約する。単一行の CHECK だけでは行間の重複・欠落は防げないので、有効な終端が1行、隣接行の終了と次の開始が一致することを更新時および検証時に確認する。

架空データで境界時刻、同時更新、途中の失敗、過去売上を確認する。切り戻しは旧価格更新経路へ切り替え、履歴と税区分を退避し、履歴表、追加の税列の順で撤去する。
