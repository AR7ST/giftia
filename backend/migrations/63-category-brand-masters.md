# Issue #63 カテゴリ・ブランドのマスタ移行案

## 適用前

DB 管理者が MySQL 8.0 の検証環境で試す。開始前にバックアップと復元を確認し、`SHOW CREATE TABLE products` でエンジン、列長、文字セット、照合順序、既存のキーを確認する。下記の `VARCHAR(255)` と `utf8mb4_0900_bin` は案。旧列が utf8mb4 で、値が255文字以内であることを確認し、違う場合は実行前に調整する。比較・検索には旧列と同じ照合順序を別途使う。

適用中は商品を書き込む処理を止める。旧列は切り戻しのため保持する。MySQL の DDL は暗黙にコミットされるため、各段階の完了を記録し、中断後は実行済みの定義を確認して再開する。

## 1. テーブルと参照列を追加する

```sql
CREATE TABLE categories (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    sort_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

CREATE TABLE brands (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

ALTER TABLE products
    ADD COLUMN category_id BIGINT UNSIGNED NULL,
    ADD COLUMN brand_id BIGINT UNSIGNED NULL;
```

## 2. 既存の商品にマスタIDを設定する

完全一致で対応付けし、表記ゆれを勝手に統合しない。旧列の NULL は参照列でも NULL とする。空文字は旧データの値として保持する。

```sql
START TRANSACTION;

INSERT INTO categories (name)
SELECT DISTINCT category COLLATE utf8mb4_0900_bin
FROM products WHERE category IS NOT NULL;

INSERT INTO brands (name)
SELECT DISTINCT brand COLLATE utf8mb4_0900_bin
FROM products WHERE brand IS NOT NULL;

UPDATE products AS p
LEFT JOIN categories AS c ON c.name = p.category COLLATE utf8mb4_0900_bin
LEFT JOIN brands AS b ON b.name = p.brand COLLATE utf8mb4_0900_bin
SET p.category_id = c.id, p.brand_id = b.id;

SELECT COUNT(*) AS mismatches
FROM products AS p
LEFT JOIN categories AS c ON c.id = p.category_id
LEFT JOIN brands AS b ON b.id = p.brand_id
WHERE NOT (c.name <=> p.category COLLATE utf8mb4_0900_bin)
   OR NOT (b.name <=> p.brand COLLATE utf8mb4_0900_bin);
```

不一致が0件なら `COMMIT`、それ以外は `ROLLBACK` して原因を確認する。その後、参照制約を付ける。

```sql
ALTER TABLE products
    ADD CONSTRAINT fk_products_category FOREIGN KEY (category_id)
        REFERENCES categories (id) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_products_brand FOREIGN KEY (brand_id)
        REFERENCES brands (id) ON DELETE RESTRICT;
```

## 3. アプリの切替と受入確認

- `backend/main.py` の通常検索と `backend/farewell.py` の送別検索で、商品からマスタを ID で左結合する。通常検索の件数と明細、送別検索の件数・候補ID・明細で同じ結合を使う。検索用の比較・部分一致には旧列それぞれの照合順序を指定する。
- マスタ名は `category`、`brand` として返し、通常検索の `category` パラメータは既存の表示名を受け付ける。画面のカテゴリ値と表示はこの契約で既存のまま動く。移行時点では `is_active` で検索結果を除外しない。
- 同じ架空データで切替前後の件数・商品IDの順序・カテゴリ名・ブランド名を比較する。カテゴリ完全一致、ブランド名を含むキーワード、表記ゆれ、NULL・空文字、在庫・価格の境界、送別検索の上位10件を確認する。
- 書き込み再開前に、取込や運用ツールが旧名とIDを同じトランザクションで更新できることを確認する。観察期間はマスタ名変更を保留する。

## 切り戻し

商品への書き込みを止め、アプリを旧列で読む版へ戻す。旧列の値と検索結果を切替前と照合する。追加した表・列は残したまま復旧できる。物理的な撤去を行う場合は、参照を持つ後続変更がないことを確認し、名前とIDの対応を退避したうえで、外部キー、商品側の2列、マスタ表の順に削除する。途中で失敗した場合は適用済みの DDL を確認する。

[MySQL の外部キー](https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html) · [暗黙のコミットが発生する文](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html)
