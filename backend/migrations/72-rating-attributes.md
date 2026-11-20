# #72 評価集計と商品属性の移行案
#69 の数値ID移行後、検証環境でレビューの評価列と対象状態を確認する。有効な個票（評価1〜5、業務上の集計対象）を同じ条件で抽出し、SUM と COUNT を同じ集合から計算する。0件の場合は rating_sum と平均は NULL、件数は0。既存の平均値から合計を逆算しない。合計は丸めず、平均は表示時だけ既存の表示精度に合わせる。キャッシュする場合はレビューの追加・変更・削除と同じトランザクションで更新し、元の個票との不一致を監査する。

```sql
CREATE TABLE product_attributes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT UNSIGNED NOT NULL,
    fact_key VARCHAR(64) NOT NULL,
    unit VARCHAR(24) NULL,
    bool_value TINYINT NULL,
    int_value BIGINT NULL,
    text_value VARCHAR(255) NULL,
    UNIQUE KEY uq_product_attribute (product_id, fact_key),
    CONSTRAINT fk_product_attribute_product FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT chk_product_attribute_value CHECK (
        ((bool_value IS NOT NULL) + (int_value IS NOT NULL) + (text_value IS NOT NULL)) = 1
        AND (bool_value IS NULL OR bool_value IN (0, 1))
        AND (unit IS NULL OR int_value IS NOT NULL)
    )
) ENGINE=InnoDB;
```

属性キーごとの型・単位を管理者と確定し、確認済みの値を登録する。レビューなし、範囲外、更新・削除後の集計、属性の0・false、値なし、複数同時入力、存在しない商品IDを架空データで検証する。切り戻しは新規参照と書き込みを先に止め、既存集計へ戻し、新属性を退避してから追加表を撤去する。実データベースへの適用は管理者が行う。
