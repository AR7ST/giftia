-- 02：#64（索引）・#63（カテゴリ・ブランドのマスタ）・#68（全文検索の索引）
-- 実行の前に：右上の接続名を確かめる。本番は @@version が 8.4.9
SELECT @@version;

-- #64 在庫・価格の索引
CREATE INDEX idx_products_stock_price ON giftia_t503.products (stock, price);

-- #63 マスタ表（照合順序は products と同じ utf8mb4_ja_0900_as_cs）
CREATE TABLE giftia_t503.categories (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    sort_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_ja_0900_as_cs;
CREATE TABLE giftia_t503.brands (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_ja_0900_as_cs;
ALTER TABLE giftia_t503.products
    ADD COLUMN category_id BIGINT UNSIGNED NULL,
    ADD COLUMN brand_id BIGINT UNSIGNED NULL;

SET SQL_SAFE_UPDATES = 0;
START TRANSACTION;
INSERT INTO giftia_t503.categories (name) SELECT DISTINCT category FROM giftia_t503.products WHERE category IS NOT NULL ORDER BY category;
INSERT INTO giftia_t503.brands (name) SELECT DISTINCT brand FROM giftia_t503.products WHERE brand IS NOT NULL ORDER BY brand;
UPDATE giftia_t503.products AS p
  LEFT JOIN giftia_t503.categories AS c ON c.name = p.category
  LEFT JOIN giftia_t503.brands AS b ON b.name = p.brand
  SET p.category_id = c.id, p.brand_id = b.id;
COMMIT;
ALTER TABLE giftia_t503.products
    ADD CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES giftia_t503.categories (id) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_products_brand FOREIGN KEY (brand_id) REFERENCES giftia_t503.brands (id) ON DELETE RESTRICT;

-- #64 の残り：カテゴリ・売れた数の索引（#63 の後）
CREATE INDEX idx_products_cat_sales ON giftia_t503.products (category_id, sales_count DESC);
-- #68 全文検索の索引
CREATE FULLTEXT INDEX idx_products_search ON giftia_t503.products (product_name, brand, description) WITH PARSER ngram;

-- 確かめる：最後の表がすべて「OK」なら次へ。1つでも「NG」なら、そこで止める
SELECT
  IF((SELECT COUNT(*) FROM giftia_t503.categories) = (SELECT COUNT(DISTINCT category) FROM giftia_t503.products), 'OK', 'NG') AS カテゴリの数,
  IF((SELECT COUNT(*) FROM giftia_t503.brands) = (SELECT COUNT(DISTINCT brand) FROM giftia_t503.products), 'OK', 'NG') AS ブランドの数,
  IF((SELECT COUNT(*) FROM giftia_t503.products AS p
        LEFT JOIN giftia_t503.categories AS c ON c.id = p.category_id
        LEFT JOIN giftia_t503.brands AS b ON b.id = p.brand_id
        WHERE NOT (c.name <=> p.category) OR NOT (b.name <=> p.brand)) = 0, 'OK', 'NG') AS 名前の食い違い0,
  IF((SELECT COUNT(DISTINCT index_name) FROM information_schema.statistics
        WHERE table_schema = 'giftia_t503' AND table_name = 'products'
          AND index_name IN ('idx_products_stock_price', 'idx_products_cat_sales', 'idx_products_search')) = 3, 'OK', 'NG') AS 索引3つ;
